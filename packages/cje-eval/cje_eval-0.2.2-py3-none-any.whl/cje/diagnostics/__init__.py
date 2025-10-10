"""CJE Diagnostics System.

Consolidated module for all diagnostic functionality:
- Data models (IPSDiagnostics, DRDiagnostics)
- Weight diagnostics computation
- DR-specific diagnostics
- Stability and drift detection
- Display utilities
- Robust inference tools
"""

# Data models
from .models import (
    IPSDiagnostics,
    DRDiagnostics,
    CJEDiagnostics,
    Status,
    GateState,
)

# Weight diagnostics
from .weights import (
    compute_weight_diagnostics,
    effective_sample_size,
    compute_ess,
    hill_tail_index,
    hill_tail_index_stable,
    tail_weight_ratio,
    mass_concentration,
)

# DR diagnostics
from .dr import (
    compute_dr_policy_diagnostics,
    compute_dr_diagnostics_all,
    compute_dm_ips_decomposition,
    compute_orthogonality_score,
)

# Stability diagnostics
from .stability import (
    kendall_tau_drift,
    sequential_drift_detection,
    reliability_diagram,
    eif_qq_plot_data,
    compute_stability_diagnostics,
)

# Display utilities
from .display import (
    create_weight_summary_table,
    format_dr_diagnostic_summary,
    format_diagnostic_comparison,
)

# Robust inference
from .robust_inference import (
    stationary_bootstrap_se,
    moving_block_bootstrap_se,
    cluster_robust_se,
    two_way_cluster_se,
    compose_se_components,
    benjamini_hochberg_correction,
    compute_simultaneous_bands,
    compute_robust_inference,
)

__all__ = [
    # Data models
    "IPSDiagnostics",
    "DRDiagnostics",
    "CJEDiagnostics",
    "Status",
    "GateState",
    # Weight diagnostics
    "compute_weight_diagnostics",
    "effective_sample_size",
    "compute_ess",
    "hill_tail_index",
    "hill_tail_index_stable",
    "tail_weight_ratio",
    "mass_concentration",
    # DR diagnostics
    "compute_dr_policy_diagnostics",
    "compute_dr_diagnostics_all",
    "compute_dm_ips_decomposition",
    "compute_orthogonality_score",
    # Stability
    "kendall_tau_drift",
    "sequential_drift_detection",
    "reliability_diagram",
    "eif_qq_plot_data",
    "compute_stability_diagnostics",
    # Display
    "create_weight_summary_table",
    "format_dr_diagnostic_summary",
    "format_diagnostic_comparison",
    # Robust inference
    "stationary_bootstrap_se",
    "moving_block_bootstrap_se",
    "cluster_robust_se",
    "two_way_cluster_se",
    "compose_se_components",
    "benjamini_hochberg_correction",
    "compute_simultaneous_bands",
    "compute_robust_inference",
]
