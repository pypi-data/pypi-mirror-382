"""Dataset calibration utilities (AutoCal-R API).

This module provides the main AutoCal-R entry points for calibrating datasets
with judge scores to match oracle labels, creating calibrated rewards for CJE
analysis. AutoCal-R automatically selects between monotone and flexible
calibration based on the relationship structure.
"""

from typing import Dict, List, Any, Optional, Tuple, Literal, cast
from copy import deepcopy
import numpy as np
from ..data.models import Dataset, Sample
from .judge import JudgeCalibrator, CalibrationResult


def calibrate_dataset(
    dataset: Dataset,
    judge_field: str = "judge_score",
    oracle_field: str = "oracle_label",
    enable_cross_fit: bool = False,
    n_folds: int = 5,
    calibration_mode: Optional[str] = None,
    random_seed: int = 42,
) -> Tuple[Dataset, CalibrationResult]:
    """Calibrate judge scores in a dataset to match oracle labels (AutoCal-R).

    This is the main AutoCal-R entry point. It extracts judge scores and oracle
    labels from the dataset, applies AutoCal-R to learn a mean-preserving calibration
    function, and returns a new dataset with calibrated rewards. By default, uses
    'auto' mode to automatically select between monotone and flexible calibration.

    Args:
        dataset: Dataset containing judge scores and oracle labels
        judge_field: Field name in metadata containing judge scores
        oracle_field: Field name in metadata containing oracle labels
        enable_cross_fit: If True, also fits cross-fitted models for DR
        n_folds: Number of CV folds (only used if enable_cross_fit=True)
        calibration_mode: Calibration mode ('auto', 'monotone', 'two_stage').
                         If None, defaults to 'auto' for cross-fit, 'monotone' otherwise.

    Returns:
        Tuple of (calibrated_dataset, calibration_result)

    Example:
        >>> # Load dataset with judge scores
        >>> dataset = load_dataset_from_jsonl("data.jsonl", reward_field="judge_score")
        >>>
        >>> # Calibrate judge scores to oracle labels
        >>> calibrated_dataset, stats = calibrate_dataset(
        ...     dataset,
        ...     judge_field="judge_score",
        ...     oracle_field="oracle_label"
        ... )
    """
    # Extract judge scores, oracle labels, and prompt_ids
    judge_scores = []
    oracle_labels = []
    oracle_mask = []
    prompt_ids = []

    # Forbid judge_field="reward" to avoid confusion
    if judge_field == "reward":
        raise ValueError(
            "judge_field='reward' is not allowed to avoid confusion between "
            "raw and calibrated values. Use a different field name in metadata."
        )

    for i, sample in enumerate(dataset.samples):
        # Get judge score - must be top-level field for standard "judge_score"
        # (Custom field names could be in metadata, but standard fields are always top-level after loading)
        if judge_field == "judge_score":
            if not hasattr(sample, "judge_score") or sample.judge_score is None:
                raise ValueError(
                    f"Judge field 'judge_score' not found or is None for sample {i}. "
                    f"Ensure data was loaded through DatasetLoader which promotes judge_score to top-level."
                )
            judge_score = sample.judge_score
        else:
            # Custom field name - check metadata
            if judge_field not in sample.metadata:
                raise ValueError(
                    f"Custom judge field '{judge_field}' not found in sample metadata"
                )
            judge_score = sample.metadata[judge_field]
            if judge_score is None:
                raise ValueError(f"Judge score is None for sample {i}")

        judge_scores.append(float(judge_score))
        prompt_ids.append(sample.prompt_id)

        # Get oracle label - must be top-level field for standard "oracle_label"
        oracle_value = None
        if oracle_field == "oracle_label":
            oracle_value = sample.oracle_label  # Can be None - that's OK
        else:
            # Custom field name - check metadata
            oracle_value = sample.metadata.get(oracle_field)

        # Only add if present and not None
        if oracle_value is not None:
            oracle_labels.append(float(oracle_value))
            oracle_mask.append(i)  # Store index instead of boolean

    # Convert to arrays
    judge_scores_array = np.array(judge_scores)
    oracle_labels_array = np.array(oracle_labels) if oracle_labels else np.array([])
    oracle_mask_array = (
        np.array(oracle_mask, dtype=int) if oracle_mask else np.array([], dtype=int)
    )

    if len(oracle_labels_array) == 0:
        raise ValueError(f"No oracle labels found in field '{oracle_field}'")

    # Check if we have 100% oracle coverage
    oracle_coverage = len(oracle_labels_array) / len(dataset.samples)
    has_full_coverage = oracle_coverage >= 1.0

    # Determine calibration mode
    if calibration_mode is None:
        # Default to auto for cross-fit (better for DR), monotone otherwise
        calibration_mode = "auto" if enable_cross_fit else "monotone"

    # Calibrate judge scores (even with 100% coverage, we need f̂ for DR models)
    calibrator = JudgeCalibrator(
        calibration_mode=cast(
            Literal["monotone", "two_stage", "auto"], calibration_mode
        ),
        random_seed=random_seed,
    )
    if enable_cross_fit:
        # Use cross-fitted calibration for DR support
        # Pass prompt_ids to enable unified fold system
        result = calibrator.fit_cv(
            judge_scores_array,
            oracle_labels_array,
            oracle_mask_array,
            n_folds,
            prompt_ids=prompt_ids,
        )
    else:
        # Use standard calibration (backward compatible)
        result = calibrator.fit_transform(
            judge_scores_array, oracle_labels_array, oracle_mask_array
        )

    # Create new samples with calibrated rewards
    calibrated_samples = []
    oracle_labels_dict = dict(zip(oracle_mask_array, oracle_labels_array))
    for i, sample in enumerate(dataset.samples):
        # Get judge_score and oracle_label for this sample
        judge_score_value = judge_scores[i]
        oracle_label_value = oracle_labels_dict.get(i)  # None if not in oracle set

        # Choose reward based on oracle coverage
        if has_full_coverage and i in oracle_labels_dict:
            # With 100% coverage, use oracle labels directly
            reward_value = float(oracle_labels_dict[i])
        else:
            # With partial coverage or no oracle for this sample, use calibrated score
            reward_value = float(result.calibrated_scores[i])

        # Create new sample with calibrated reward and preserved judge_score/oracle_label
        calibrated_sample = Sample(
            prompt_id=sample.prompt_id,
            prompt=sample.prompt,
            response=sample.response,
            reward=reward_value,
            base_policy_logprob=sample.base_policy_logprob,
            target_policy_logprobs=sample.target_policy_logprobs,
            judge_score=judge_score_value,
            oracle_label=oracle_label_value,
            metadata=sample.metadata.copy(),  # Preserve other metadata
        )
        calibrated_samples.append(calibrated_sample)

    # Create new dataset with calibration info in metadata
    dataset_metadata = dataset.metadata.copy()

    # Add calibration summary for downstream diagnostics
    dataset_metadata["calibration_info"] = {
        "rmse": result.calibration_rmse,
        "coverage": result.coverage_at_01,
        "n_oracle": result.n_oracle,
        "n_total": len(judge_scores),
        "oracle_coverage": oracle_coverage,
        "using_direct_oracle": has_full_coverage,
        "method": (
            "direct_oracle"
            if has_full_coverage
            else ("cross_fitted_isotonic" if enable_cross_fit else "isotonic")
        ),  # Will be updated below
        "n_folds": n_folds if enable_cross_fit else None,
        "oof_rmse": result.oof_rmse if enable_cross_fit else None,
        "oof_coverage": result.oof_coverage_at_01 if enable_cross_fit else None,
        "calibration_mode": calibration_mode,
    }

    # Lightweight calibration-floor instrumentation
    try:
        # Build boolean oracle mask aligned with dataset order
        n_total = len(judge_scores_array)
        oracle_bool = np.zeros(n_total, dtype=bool)
        if oracle_mask_array.size > 0:
            oracle_bool[oracle_mask_array] = True

        # f_min/f_max computed on oracle subset predictions
        if result.calibrated_scores is not None and oracle_bool.any():
            cal_scores = np.asarray(result.calibrated_scores)
            oracle_cal = cal_scores[oracle_bool]
            f_min = float(np.min(oracle_cal))
            f_max = float(np.max(oracle_cal))
            # Number of unique isotonic levels on oracle subset (rounded to avoid FP noise)
            levels = np.unique(np.round(oracle_cal, 6))
            n_levels = int(len(levels))
        else:
            f_min = float("nan")
            f_max = float("nan")
            n_levels = 0

        # Low-S label coverage (bottom deciles of S over all rows)
        q10 = float(np.quantile(judge_scores_array, 0.10))
        q20 = float(np.quantile(judge_scores_array, 0.20))

        def _coverage(threshold: float) -> float:
            sel = judge_scores_array <= threshold
            denom = int(np.sum(sel))
            if denom <= 0:
                return 0.0
            return float(np.sum(oracle_bool & sel) / denom)

        cov_b10 = _coverage(q10)
        cov_b20 = _coverage(q20)

        dataset_metadata["calibration_info"].update(
            {
                "f_min": f_min,
                "f_max": f_max,
                "n_isotonic_levels_on_oracle": n_levels,
                "low_s_label_coverage_bottom10": cov_b10,
                "low_s_label_coverage_bottom20": cov_b20,
                "s_q10": q10,
                "s_q20": q20,
            }
        )
    except Exception:
        # Best effort only; do not fail calibration if instrumentation fails
        pass

    # Store fold configuration for reproducibility
    dataset_metadata["n_folds"] = n_folds
    dataset_metadata["fold_seed"] = random_seed

    # Store selected calibration mode and update method field
    selected_mode: Optional[str] = calibration_mode  # Default to the requested mode
    if (
        hasattr(calibrator, "_flexible_calibrator")
        and calibrator._flexible_calibrator is not None
    ):
        selected_mode = calibrator._flexible_calibrator.selected_mode
        if selected_mode is not None:
            dataset_metadata["calibration_info"]["selected_mode"] = selected_mode
    elif calibration_mode == "auto" and hasattr(calibrator, "selected_mode"):
        selected_mode = calibrator.selected_mode
        if selected_mode is not None:
            dataset_metadata["calibration_info"]["selected_mode"] = selected_mode

    # Update method field to reflect actual calibration mode used
    if has_full_coverage:
        # With 100% coverage, we use oracle labels directly
        dataset_metadata["calibration_info"]["method"] = "direct_oracle"
    elif selected_mode:
        dataset_metadata["calibration_info"]["method"] = (
            f"cross_fitted_{selected_mode}" if enable_cross_fit else selected_mode
        )

    calibrated_dataset = Dataset(
        samples=calibrated_samples,
        target_policies=dataset.target_policies,
        metadata=dataset_metadata,
    )

    return calibrated_dataset, result


def calibrate_from_raw_data(
    data: List[Dict[str, Any]],
    judge_field: str = "judge_score",
    oracle_field: str = "oracle_label",
    reward_field: str = "reward",
    calibration_mode: Optional[Literal["auto", "monotone", "two_stage"]] = "monotone",
    random_seed: int = 42,
) -> Tuple[List[Dict[str, Any]], CalibrationResult]:
    """Calibrate judge scores in raw data to create calibrated rewards.

    This is a lower-level function that works with raw dictionaries
    instead of Dataset objects.

    Args:
        data: List of dictionaries containing judge scores and oracle labels
        judge_field: Field name containing judge scores
        oracle_field: Field name containing oracle labels
        reward_field: Field name to store calibrated rewards
        calibration_mode: Calibration mode ('auto', 'monotone', 'two_stage').
                         Defaults to 'monotone' for backward compatibility.

    Returns:
        Tuple of (calibrated_data, calibration_result)
    """
    # Extract judge scores and oracle labels
    judge_scores = []
    oracle_labels = []
    oracle_mask = []

    for idx, record in enumerate(data):
        # Extract judge score
        judge_score = record.get(judge_field)
        if judge_score is None:
            raise ValueError(f"Judge field '{judge_field}' not found in record {idx}")

        if isinstance(judge_score, dict):
            judge_score = judge_score.get("mean", judge_score.get("value"))
        if judge_score is None:
            raise ValueError(f"Judge score is None for record {idx}")
        judge_scores.append(float(judge_score))

        # Check for oracle label
        oracle_label = record.get(oracle_field)
        if oracle_label is not None:
            oracle_labels.append(float(oracle_label))
            oracle_mask.append(True)
        else:
            oracle_mask.append(False)

    # Convert to arrays
    judge_scores_array = np.array(judge_scores)
    oracle_labels_array = np.array(
        oracle_labels
    )  # Now always same length as judge_scores
    oracle_mask_array = np.array(oracle_mask)

    if len(oracle_labels_array) == 0:
        raise ValueError(f"No oracle labels found in field '{oracle_field}'")

    # Calibrate judge scores
    calibrator = JudgeCalibrator(
        calibration_mode=cast(
            Literal["monotone", "two_stage", "auto"], calibration_mode
        ),
        random_seed=random_seed,
    )
    result = calibrator.fit_transform(
        judge_scores_array, oracle_labels_array, oracle_mask_array
    )

    # Add calibrated rewards to data
    calibrated_data = []
    for i, record in enumerate(data):
        record_copy = record.copy()
        record_copy[reward_field] = float(result.calibrated_scores[i])

        # Deep copy metadata to avoid mutating caller's nested dict
        metadata = deepcopy(record_copy.get("metadata", {}))
        metadata[judge_field] = judge_scores[i]
        if oracle_mask[i]:
            # Find the index of this oracle label
            oracle_idx = np.sum(oracle_mask_array[: i + 1]) - 1
            metadata[oracle_field] = (
                float(oracle_labels_array[oracle_idx])
                if oracle_labels_array is not None
                else None
            )
        record_copy["metadata"] = metadata

        calibrated_data.append(record_copy)

    return calibrated_data, result
