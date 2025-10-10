"""
Comprehensive evaluation and dashboard visualization functions.

This module contains functions for creating multi-panel evaluation plots
and comprehensive model assessment dashboards.
"""

import pandas as pd
import numpy as np
from typing import Optional, Tuple, List, Dict, Any
import warnings

from .._plotting_backend import get_matplotlib, require_matplotlib


@require_matplotlib
def create_comprehensive_evaluation_plots(
    evaluation_results: Dict[str, Any], figsize: Tuple[int, int] = (16, 12)
) -> None:
    """
    Create comprehensive evaluation plots for final model assessment.

    Parameters
    ----------
    evaluation_results : dict
        Results from final_model_evaluation function
    figsize : tuple, optional
        Figure size as (width, height)
    """
    plt = get_matplotlib()

    # Determine number of subplots needed
    n_plots = 0
    if "feature_importance" in evaluation_results:
        n_plots += 1
    if "error_analysis" in evaluation_results:
        n_plots += 1
    if "fairness_analysis" in evaluation_results:
        n_plots += 1
    if "cv_stability" in evaluation_results:
        n_plots += 1

    if n_plots == 0:
        print("No data available for plotting")
        return

    # Create subplots
    if n_plots <= 2:
        fig, axes = plt.subplots(1, n_plots, figsize=figsize)
    else:
        fig, axes = plt.subplots(2, 2, figsize=figsize)

    if n_plots == 1:
        axes = [axes]
    else:
        axes = axes.flatten()

    plot_idx = 0

    # 1. Feature Importance Plot
    if "feature_importance" in evaluation_results:
        _plot_feature_importance(evaluation_results, axes[plot_idx])
        plot_idx += 1

    # 2. Error Analysis Plot
    if "error_analysis" in evaluation_results:
        _plot_error_analysis(evaluation_results, axes[plot_idx])
        plot_idx += 1

    # 3. Fairness Analysis Plot
    if "fairness_analysis" in evaluation_results:
        _plot_fairness_analysis(evaluation_results, axes[plot_idx])
        plot_idx += 1

    # 4. CV Stability Plot
    if "cv_stability" in evaluation_results:
        _plot_cv_stability(evaluation_results, axes[plot_idx])
        plot_idx += 1

    # Remove any unused subplots
    for i in range(plot_idx, len(axes)):
        fig.delaxes(axes[i])

    plt.tight_layout()
    plt.show()


def _plot_feature_importance(evaluation_results: Dict[str, Any], ax) -> None:
    """Plot feature importance analysis."""
    fi = evaluation_results["feature_importance"]

    # Use permutation importance if available, otherwise built-in
    if "permutation_importance" in fi:
        importances = fi["permutation_importance"]["importances_mean"]
        features = fi["permutation_importance"]["features"]
        errors = fi["permutation_importance"].get("importances_std", None)
        title_suffix = "(Permutation)"
    elif "builtin_importance" in fi:
        importances = fi["builtin_importance"]["values"]
        features = fi["builtin_importance"]["features"]
        errors = None
        title_suffix = "(Built-in)"
    else:
        ax.text(
            0.5,
            0.5,
            "No feature importance data",
            ha="center",
            va="center",
            transform=ax.transAxes,
        )
        ax.set_title("Feature Importance")
        return

    # Get top 10 features
    n_show = min(10, len(importances))
    top_indices = np.argsort(importances)[-n_show:]

    top_importances = [importances[i] for i in top_indices]
    top_features = [features[i] for i in top_indices]
    top_errors = [errors[i] for i in top_indices] if errors else None

    # Create horizontal bar plot
    y_pos = np.arange(len(top_features))
    bars = ax.barh(y_pos, top_importances, xerr=top_errors, alpha=0.8, capsize=3)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(top_features)
    ax.set_xlabel("Importance")
    ax.set_title(f"Top {n_show} Important Features {title_suffix}")
    ax.grid(True, alpha=0.3)

    # Color bars by importance
    try:
        plt = get_matplotlib()
        norm = plt.Normalize(vmin=min(top_importances), vmax=max(top_importances))
        for bar, importance in zip(bars, top_importances):
            bar.set_color(plt.cm.viridis(norm(importance)))
    except:
        pass


def _plot_error_analysis(evaluation_results: Dict[str, Any], ax) -> None:
    """Plot error analysis."""
    error = evaluation_results["error_analysis"]
    task_type = evaluation_results["task_type"]

    if task_type == "classification":
        # Plot confusion matrix if available
        if "confusion_matrix" in error:
            cm = np.array(error["confusion_matrix"])

            im = ax.imshow(cm, interpolation="nearest", cmap="Blues")
            ax.set_title("Confusion Matrix")

            # Add text annotations
            thresh = cm.max() / 2.0
            for i in range(cm.shape[0]):
                for j in range(cm.shape[1]):
                    ax.text(
                        j,
                        i,
                        format(cm[i, j], "d"),
                        ha="center",
                        va="center",
                        color="white" if cm[i, j] > thresh else "black",
                    )

            ax.set_xlabel("Predicted Label")
            ax.set_ylabel("True Label")
            try:
                plt = get_matplotlib()
                plt.colorbar(im, ax=ax)
            except:
                pass
        else:
            # Show misclassification rate
            if "misclassification_rate" in error:
                rate = error["misclassification_rate"]
                ax.bar(
                    ["Correct", "Misclassified"],
                    [1 - rate, rate],
                    color=["green", "red"],
                    alpha=0.7,
                )
                ax.set_ylabel("Proportion")
                ax.set_title("Classification Accuracy")
                ax.set_ylim(0, 1)
            else:
                ax.text(
                    0.5,
                    0.5,
                    "No error data available",
                    ha="center",
                    va="center",
                    transform=ax.transAxes,
                )
                ax.set_title("Error Analysis")

    else:  # regression
        # Plot residual statistics
        residual_metrics = [
            "residuals_mean",
            "residuals_std",
            "abs_residuals_mean",
            "abs_residuals_median",
        ]
        available_metrics = [m for m in residual_metrics if m in error]

        if available_metrics:
            values = [error[m] for m in available_metrics]
            labels = [m.replace("_", " ").title() for m in available_metrics]

            bars = ax.bar(range(len(labels)), values, alpha=0.7)
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(labels, rotation=45, ha="right")
            ax.set_ylabel("Value")
            ax.set_title("Residual Statistics")
            ax.grid(True, alpha=0.3)

            # Color bars
            try:
                plt = get_matplotlib()
                for i, bar in enumerate(bars):
                    bar.set_color(plt.cm.viridis(i / len(bars)))
            except:
                pass
        else:
            ax.text(
                0.5,
                0.5,
                "No residual data available",
                ha="center",
                va="center",
                transform=ax.transAxes,
            )
            ax.set_title("Error Analysis")


def _plot_fairness_analysis(evaluation_results: Dict[str, Any], ax) -> None:
    """Plot fairness analysis."""
    fairness = evaluation_results["fairness_analysis"]
    task_type = evaluation_results["task_type"]

    # Collect fairness metrics for plotting
    attr_names = []
    disparity_ratios = []

    for attr_name, attr_results in fairness.items():
        if "disparities" in attr_results:
            disparities = attr_results["disparities"]

            # Find the main disparity ratio to plot
            ratio_metrics = [k for k in disparities.keys() if "ratio" in k]
            if ratio_metrics:
                main_metric = ratio_metrics[0]  # Use first ratio metric
                attr_names.append(attr_name)
                disparity_ratios.append(disparities[main_metric])

    if attr_names and disparity_ratios:
        # Create bar plot of disparity ratios
        bars = ax.bar(range(len(attr_names)), disparity_ratios, alpha=0.7)

        # Color bars based on fairness level
        for bar, ratio in zip(bars, disparity_ratios):
            if ratio > 1.5:
                bar.set_color("red")
            elif ratio > 1.2:
                bar.set_color("orange")
            else:
                bar.set_color("green")

        ax.set_xticks(range(len(attr_names)))
        ax.set_xticklabels(attr_names)
        ax.set_ylabel("Disparity Ratio")
        ax.set_title("Fairness Analysis - Group Disparities")
        ax.axhline(
            y=1.0, color="black", linestyle="--", alpha=0.5, label="Perfect Fairness"
        )
        ax.axhline(
            y=1.2, color="orange", linestyle="--", alpha=0.5, label="Concern Threshold"
        )
        ax.legend()
        ax.grid(True, alpha=0.3)
    else:
        ax.text(
            0.5,
            0.5,
            "No fairness disparity data available",
            ha="center",
            va="center",
            transform=ax.transAxes,
        )
        ax.set_title("Fairness Analysis")


def _plot_cv_stability(evaluation_results: Dict[str, Any], ax) -> None:
    """Plot cross-validation stability."""
    cv_results = evaluation_results["cv_stability"]

    # Get metrics and their CV (coefficient of variation)
    metrics = []
    cv_values = []

    for metric, stats in cv_results.items():
        if isinstance(stats, dict) and "cv" in stats:
            metrics.append(metric.replace("_", " ").title())
            cv_values.append(stats["cv"])

    if metrics and cv_values:
        bars = ax.bar(range(len(metrics)), cv_values, alpha=0.7)

        # Color bars based on stability
        for bar, cv_val in zip(bars, cv_values):
            if cv_val < 0.05:
                bar.set_color("green")
            elif cv_val < 0.1:
                bar.set_color("yellow")
            elif cv_val < 0.2:
                bar.set_color("orange")
            else:
                bar.set_color("red")

        ax.set_xticks(range(len(metrics)))
        ax.set_xticklabels(metrics, rotation=45, ha="right")
        ax.set_ylabel("Coefficient of Variation")
        ax.set_title("Model Stability (Cross-Validation)")
        ax.axhline(
            y=0.1,
            color="orange",
            linestyle="--",
            alpha=0.5,
            label="Stability Threshold",
        )
        ax.legend()
        ax.grid(True, alpha=0.3)
    else:
        ax.text(
            0.5,
            0.5,
            "No CV stability data available",
            ha="center",
            va="center",
            transform=ax.transAxes,
        )
        ax.set_title("Cross-Validation Stability")
