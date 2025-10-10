"""
Fairness and feature importance visualization functions.

This module contains functions for creating detailed feature importance plots
and fairness comparison visualizations.
"""

import pandas as pd
import numpy as np
from typing import Optional, Tuple, List, Dict, Any
import warnings

from .._plotting_backend import get_matplotlib, require_matplotlib


@require_matplotlib
def create_feature_importance_plot(
    evaluation_results: Dict[str, Any],
    top_n: int = 15,
    figsize: Tuple[int, int] = (10, 8),
) -> None:
    """
    Create detailed feature importance plot.

    Parameters
    ----------
    evaluation_results : dict
        Results from final_model_evaluation function
    top_n : int, default=15
        Number of top features to display
    figsize : tuple, optional
        Figure size as (width, height)
    """
    plt = get_matplotlib()

    if "feature_importance" not in evaluation_results:
        print("No feature importance data available")
        return

    fi = evaluation_results["feature_importance"]

    fig, axes = plt.subplots(1, 2, figsize=figsize)

    # Plot 1: Main importance method
    ax1 = axes[0]
    if "permutation_importance" in fi:
        importances = fi["permutation_importance"]["importances_mean"]
        features = fi["permutation_importance"]["features"]
        errors = fi["permutation_importance"].get("importances_std", None)
        title = "Permutation Importance"
    elif "builtin_importance" in fi:
        importances = fi["builtin_importance"]["values"]
        features = fi["builtin_importance"]["features"]
        errors = None
        title = "Built-in Feature Importance"
    else:
        ax1.text(
            0.5,
            0.5,
            "No importance data",
            ha="center",
            va="center",
            transform=ax1.transAxes,
        )
        ax1.set_title("Feature Importance")
        return

    # Get top features
    n_show = min(top_n, len(importances))
    top_indices = np.argsort(importances)[-n_show:]

    top_importances = [importances[i] for i in top_indices]
    top_features = [features[i] for i in top_indices]
    top_errors = [errors[i] for i in top_indices] if errors else None

    y_pos = np.arange(len(top_features))
    ax1.barh(y_pos, top_importances, xerr=top_errors, alpha=0.8, capsize=3)
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(top_features)
    ax1.set_xlabel("Importance")
    ax1.set_title(title)
    ax1.grid(True, alpha=0.3)

    # Plot 2: Feature correlations (if available)
    ax2 = axes[1]
    if "feature_correlations" in fi:
        correlations = fi["feature_correlations"]["correlations"]
        corr_features = fi["feature_correlations"]["features"]

        # Get features with highest absolute correlations
        abs_correlations = [abs(c) for c in correlations]
        top_corr_indices = np.argsort(abs_correlations)[-n_show:]

        top_correlations = [correlations[i] for i in top_corr_indices]
        top_corr_features = [corr_features[i] for i in top_corr_indices]

        y_pos = np.arange(len(top_corr_features))
        colors = ["red" if c < 0 else "blue" for c in top_correlations]
        ax2.barh(y_pos, top_correlations, color=colors, alpha=0.8)
        ax2.set_yticks(y_pos)
        ax2.set_yticklabels(top_corr_features)
        ax2.set_xlabel("Correlation with Target")
        ax2.set_title("Feature-Target Correlations")
        ax2.axvline(x=0, color="black", linestyle="-", alpha=0.5)
        ax2.grid(True, alpha=0.3)
    else:
        ax2.text(
            0.5,
            0.5,
            "No correlation data",
            ha="center",
            va="center",
            transform=ax2.transAxes,
        )
        ax2.set_title("Feature Correlations")

    plt.tight_layout()
    plt.show()


@require_matplotlib
def create_fairness_comparison_plot(
    evaluation_results: Dict[str, Any], figsize: Tuple[int, int] = (12, 8)
) -> None:
    """
    Create detailed fairness comparison plot.

    Parameters
    ----------
    evaluation_results : dict
        Results from final_model_evaluation function
    figsize : tuple, optional
        Figure size as (width, height)
    """
    plt = get_matplotlib()

    if "fairness_analysis" not in evaluation_results:
        print("No fairness analysis data available")
        return

    fairness = evaluation_results["fairness_analysis"]
    task_type = evaluation_results["task_type"]

    n_attributes = len(fairness)
    fig, axes = plt.subplots(1, n_attributes, figsize=figsize)

    if n_attributes == 1:
        axes = [axes]

    for idx, (attr_name, attr_results) in enumerate(fairness.items()):
        ax = axes[idx]

        if "group_metrics" in attr_results:
            group_metrics = attr_results["group_metrics"]

            groups = list(group_metrics.keys())

            if task_type == "classification":
                metric_name = "accuracy"
                ylabel = "Accuracy"
            else:
                metric_name = "r2"
                ylabel = "R² Score"

            values = [group_metrics[group].get(metric_name, 0) for group in groups]
            sizes = [group_metrics[group].get("size", 0) for group in groups]

            # Create bar plot with error bars representing group sizes
            bars = ax.bar(range(len(groups)), values, alpha=0.8)

            # Color bars based on performance
            if task_type == "classification":
                for bar, value in zip(bars, values):
                    if value >= 0.8:
                        bar.set_color("green")
                    elif value >= 0.6:
                        bar.set_color("orange")
                    else:
                        bar.set_color("red")
            else:
                for bar, value in zip(bars, values):
                    if value >= 0.7:
                        bar.set_color("green")
                    elif value >= 0.5:
                        bar.set_color("orange")
                    else:
                        bar.set_color("red")

            ax.set_xticks(range(len(groups)))
            ax.set_xticklabels(groups)
            ax.set_ylabel(ylabel)
            ax.set_title(f"{attr_name}\nFairness by Group")
            ax.grid(True, alpha=0.3)

            # Add sample size annotations
            for i, (bar, size) in enumerate(zip(bars, sizes)):
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height + 0.01,
                    f"n={size}",
                    ha="center",
                    va="bottom",
                    fontsize=8,
                )
        else:
            ax.text(
                0.5,
                0.5,
                f"No group metrics for {attr_name}",
                ha="center",
                va="center",
                transform=ax.transAxes,
            )
            ax.set_title(f"{attr_name}")

    plt.tight_layout()
    plt.show()
