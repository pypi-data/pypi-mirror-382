"""
Performance visualization functions for model evaluation.

This module contains functions for creating performance summary plots,
model comparison plots, and performance radar charts.
"""

import pandas as pd
import numpy as np
from typing import Optional, Tuple, List, Dict, Any
import warnings

from .._plotting_backend import get_matplotlib, require_matplotlib


@require_matplotlib
def create_performance_summary_plot(
    results: pd.DataFrame,
    title: Optional[str] = None,
    figsize: Tuple[int, int] = (10, 6),
) -> None:
    """
    Create a bar plot visualization of model performance metrics.

    Parameters
    ----------
    results : pd.DataFrame
        Results DataFrame from evaluate_model_with_cross_validation or
        evaluate_classification_model_with_cross_validation
    title : str, optional
        Custom title for the plot
    figsize : tuple, optional
        Figure size as (width, height)
    """
    plt = get_matplotlib()

    # Validate input
    required_columns = {"Metric", "Value", "Performance"}
    if not required_columns.issubset(results.columns):
        raise ValueError(f"Results DataFrame must contain columns: {required_columns}")

    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

    # Plot 1: Metric values
    metrics = results["Metric"].tolist()
    values = results["Value"].tolist()

    bars1 = ax1.bar(range(len(metrics)), values, alpha=0.7, color="skyblue")
    ax1.set_xticks(range(len(metrics)))
    ax1.set_xticklabels(metrics, rotation=45, ha="right")
    ax1.set_ylabel("Metric Value")
    ax1.set_title("Metric Values")
    ax1.grid(True, alpha=0.3)

    # Add value labels on bars
    for i, (bar, value) in enumerate(zip(bars1, values)):
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.01,
            f"{value:.4f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    # Plot 2: Performance categories
    performance_categories = results["Performance"].tolist()

    # Color mapping for performance
    performance_colors = {
        "Excellent": "green",
        "Good": "lightgreen",
        "Acceptable": "yellow",
        "Moderate": "orange",
        "Poor": "red",
        "Very Poor": "darkred",
    }

    colors = [performance_colors.get(perf, "gray") for perf in performance_categories]

    bars2 = ax2.bar(range(len(metrics)), [1] * len(metrics), color=colors, alpha=0.7)
    ax2.set_xticks(range(len(metrics)))
    ax2.set_xticklabels(metrics, rotation=45, ha="right")
    ax2.set_ylabel("Performance Category")
    ax2.set_title("Performance Assessment")
    ax2.set_ylim(0, 1.2)

    # Add performance labels
    for i, (bar, perf) in enumerate(zip(bars2, performance_categories)):
        ax2.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() / 2,
            perf,
            ha="center",
            va="center",
            fontsize=9,
            fontweight="bold",
        )

    # Remove y-ticks for performance plot
    ax2.set_yticks([])

    # Overall title
    if title is None:
        title = "Model Performance Summary"
    fig.suptitle(title, fontsize=14, fontweight="bold")

    plt.tight_layout()
    plt.show()


@require_matplotlib
def create_model_comparison_plot(
    results_dict: dict, figsize: Tuple[int, int] = (12, 8)
) -> None:
    """
    Create a comparison plot for multiple models.

    Parameters
    ----------
    results_dict : dict
        Dictionary where keys are model names and values are results DataFrames
    figsize : tuple, optional
        Figure size as (width, height)
    """
    plt = get_matplotlib()

    if len(results_dict) < 2:
        raise ValueError("At least 2 models required for comparison")

    # Extract metrics and values
    model_names = list(results_dict.keys())

    # Get unique metrics across all models
    all_metrics = set()
    for results in results_dict.values():
        all_metrics.update(results["Metric"].tolist())
    all_metrics = sorted(list(all_metrics))

    # Create comparison matrix
    comparison_data = []
    for model_name in model_names:
        results = results_dict[model_name]
        model_values = []
        for metric in all_metrics:
            metric_data = results[results["Metric"] == metric]
            if len(metric_data) > 0:
                model_values.append(metric_data["Value"].iloc[0])
            else:
                model_values.append(0)  # Missing metric
        comparison_data.append(model_values)

    # Create grouped bar chart
    fig, ax = plt.subplots(figsize=figsize)

    x = np.arange(len(all_metrics))
    width = 0.8 / len(model_names)

    colors = plt.cm.Set3(np.linspace(0, 1, len(model_names)))

    for i, (model_name, values) in enumerate(zip(model_names, comparison_data)):
        offset = (i - len(model_names) / 2 + 0.5) * width
        bars = ax.bar(
            x + offset, values, width, label=model_name, color=colors[i], alpha=0.8
        )

        # Add value labels on bars
        for bar, value in zip(bars, values):
            if value > 0:  # Only show non-zero values
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.01,
                    f"{value:.3f}",
                    ha="center",
                    va="bottom",
                    fontsize=8,
                )

    ax.set_xlabel("Metrics")
    ax.set_ylabel("Values")
    ax.set_title("Model Performance Comparison")
    ax.set_xticks(x)
    ax.set_xticklabels(all_metrics, rotation=45, ha="right")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


@require_matplotlib
def create_performance_radar_chart(
    results: pd.DataFrame,
    title: Optional[str] = None,
    figsize: Tuple[int, int] = (8, 8),
) -> None:
    """
    Create a radar chart visualization of model performance.

    Parameters
    ----------
    results : pd.DataFrame
        Results DataFrame from evaluation functions
    title : str, optional
        Custom title for the plot
    figsize : tuple, optional
        Figure size as (width, height)
    """
    plt = get_matplotlib()

    # Validate input
    required_columns = {"Metric", "Value"}
    if not required_columns.issubset(results.columns):
        raise ValueError(f"Results DataFrame must contain columns: {required_columns}")

    metrics = results["Metric"].tolist()
    values = results["Value"].tolist()

    # Normalize values to 0-1 scale for radar chart
    normalized_values = []
    for i, (metric, value) in enumerate(zip(metrics, values)):
        if metric in ["RMSE", "MAE"]:
            # For error metrics, invert (lower is better)
            # Assume reasonable range and cap at 1
            normalized_val = max(0, 1 - min(value, 1))
        elif metric in [
            "R²",
            "Explained Variance",
            "Accuracy",
            "Precision",
            "Recall",
            "F1-Score",
            "ROC AUC",
        ]:
            # For score metrics, use as-is (higher is better)
            normalized_val = max(0, min(value, 1))
        else:
            # Unknown metric, assume 0-1 scale
            normalized_val = max(0, min(value, 1))
        normalized_values.append(normalized_val)

    # Number of metrics
    N = len(metrics)

    # Compute angle for each metric
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]  # Complete the circle

    # Add first value at the end to complete the circle
    normalized_values += normalized_values[:1]

    # Create radar chart
    fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(projection="polar"))

    # Plot the values
    ax.plot(angles, normalized_values, "o-", linewidth=2, label="Performance")
    ax.fill(angles, normalized_values, alpha=0.25)

    # Add metric labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(metrics)

    # Set y-axis limits and labels
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(["0.2", "0.4", "0.6", "0.8", "1.0"])
    ax.grid(True)

    # Title
    if title is None:
        title = "Model Performance Radar Chart"
    ax.set_title(title, size=16, fontweight="bold", pad=20)

    plt.tight_layout()
    plt.show()
