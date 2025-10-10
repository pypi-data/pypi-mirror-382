"""
Visualization utilities for extended-sklearn-metrics.

This package provides comprehensive visualization functions for model evaluation,
including performance plots, ROC/AUC curves, residual diagnostics, and fairness analysis.

The visualizations are organized into sub-modules for better maintainability:
- _base: Common utilities and console reporting
- performance: Performance summary and comparison plots
- roc_curves: ROC, Precision-Recall, and threshold analysis
- residuals: Residual diagnostic plots for regression
- comprehensive: Multi-panel evaluation dashboards
- fairness: Feature importance and fairness comparison plots
"""

# Import all public functions from sub-modules for backward compatibility
from ._base import print_performance_report

from .performance import (
    create_performance_summary_plot,
    create_model_comparison_plot,
    create_performance_radar_chart,
)

from .roc_curves import (
    create_roc_curve_plot,
    create_precision_recall_plot,
    create_multiclass_roc_plot,
    create_threshold_analysis_plot,
)

from .residuals import create_residual_plots, create_residual_summary_plot

from .comprehensive import create_comprehensive_evaluation_plots

from .fairness import create_feature_importance_plot, create_fairness_comparison_plot

# Define public API
__all__ = [
    # Base
    "print_performance_report",
    # Performance plots
    "create_performance_summary_plot",
    "create_model_comparison_plot",
    "create_performance_radar_chart",
    # ROC/AUC plots
    "create_roc_curve_plot",
    "create_precision_recall_plot",
    "create_multiclass_roc_plot",
    "create_threshold_analysis_plot",
    # Residual plots
    "create_residual_plots",
    "create_residual_summary_plot",
    # Comprehensive evaluation
    "create_comprehensive_evaluation_plots",
    # Fairness and feature importance
    "create_feature_importance_plot",
    "create_fairness_comparison_plot",
]
