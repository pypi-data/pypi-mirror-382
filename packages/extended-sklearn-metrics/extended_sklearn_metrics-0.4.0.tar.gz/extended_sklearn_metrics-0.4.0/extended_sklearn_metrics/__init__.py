"""
extended-sklearn-metrics - A Python package for enhanced scikit-learn model evaluation metrics
"""

__version__: str = "0.4.0"

from .model_evaluation import evaluate_model_with_cross_validation, CustomThresholds
from .classification_evaluation import (
    evaluate_classification_model_with_cross_validation,
)
from .visualizations import (
    create_performance_summary_plot,
    create_model_comparison_plot,
    create_performance_radar_chart,
    print_performance_report,
    create_residual_plots,
    create_residual_summary_plot,
    create_roc_curve_plot,
    create_precision_recall_plot,
    create_multiclass_roc_plot,
    create_threshold_analysis_plot,
    create_comprehensive_evaluation_plots,
    create_feature_importance_plot,
    create_fairness_comparison_plot,
)
from .residual_diagnostics import (
    calculate_residual_diagnostics,
    create_residual_summary_report,
    print_residual_diagnostics_report,
)
from .roc_auc_analysis import (
    calculate_roc_metrics,
    calculate_multiclass_roc_metrics,
    calculate_precision_recall_metrics,
    find_optimal_thresholds,
    create_threshold_analysis_report,
    print_roc_auc_summary,
)
from .comprehensive_evaluation import final_model_evaluation
from .evaluation_reporting import (
    create_evaluation_report,
    print_evaluation_summary,
    create_feature_importance_report,
    create_fairness_report,
)

__all__: list[str] = [
    "evaluate_model_with_cross_validation",
    "evaluate_classification_model_with_cross_validation",
    "CustomThresholds",
    "create_performance_summary_plot",
    "create_model_comparison_plot",
    "create_performance_radar_chart",
    "print_performance_report",
    "create_residual_plots",
    "create_residual_summary_plot",
    "calculate_residual_diagnostics",
    "create_residual_summary_report",
    "print_residual_diagnostics_report",
    "create_roc_curve_plot",
    "create_precision_recall_plot",
    "create_multiclass_roc_plot",
    "create_threshold_analysis_plot",
    "calculate_roc_metrics",
    "calculate_multiclass_roc_metrics",
    "calculate_precision_recall_metrics",
    "find_optimal_thresholds",
    "create_threshold_analysis_report",
    "print_roc_auc_summary",
    "final_model_evaluation",
    "create_evaluation_report",
    "print_evaluation_summary",
    "create_feature_importance_report",
    "create_fairness_report",
    "create_comprehensive_evaluation_plots",
    "create_feature_importance_plot",
    "create_fairness_comparison_plot",
]
