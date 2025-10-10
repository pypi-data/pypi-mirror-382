"""
ROC curve and precision-recall visualization functions.

This module contains functions for creating ROC curves, precision-recall curves,
multiclass ROC plots, and threshold analysis plots.
"""

import pandas as pd
import numpy as np
from typing import Optional, Tuple, List, Dict, Any
import warnings

from .._plotting_backend import get_matplotlib, require_matplotlib


@require_matplotlib
def create_roc_curve_plot(
    roc_metrics: Dict[str, Any],
    title: Optional[str] = None,
    figsize: Tuple[int, int] = (8, 6),
    show_threshold_points: bool = True,
    highlight_optimal: bool = True,
) -> None:
    """
    Create ROC curve plot with optional threshold analysis.

    Parameters
    ----------
    roc_metrics : dict
        Results from calculate_roc_metrics
    title : str, optional
        Custom title for the plot
    figsize : tuple, optional
        Figure size as (width, height)
    show_threshold_points : bool, default=True
        Whether to show threshold points on the curve
    highlight_optimal : bool, default=True
        Whether to highlight the optimal threshold point
    """
    plt = get_matplotlib()

    fig, ax = plt.subplots(figsize=figsize)

    # Plot ROC curve
    fpr = roc_metrics["fpr"]
    tpr = roc_metrics["tpr"]
    auc_score = roc_metrics["roc_auc"]

    ax.plot(
        fpr, tpr, color="darkorange", lw=2, label=f"ROC curve (AUC = {auc_score:.3f})"
    )

    # Plot diagonal line (random classifier)
    ax.plot(
        [0, 1],
        [0, 1],
        color="navy",
        lw=2,
        linestyle="--",
        alpha=0.6,
        label="Random classifier (AUC = 0.500)",
    )

    # Highlight optimal threshold point
    if highlight_optimal:
        optimal_fpr = roc_metrics["optimal_fpr"]
        optimal_tpr = roc_metrics["optimal_tpr"]
        optimal_threshold = roc_metrics["optimal_threshold"]

        ax.plot(
            optimal_fpr,
            optimal_tpr,
            "ro",
            markersize=8,
            label=f"Optimal threshold = {optimal_threshold:.3f}",
        )

        # Add annotation for optimal point
        ax.annotate(
            f"Optimal\n({optimal_fpr:.3f}, {optimal_tpr:.3f})",
            xy=(optimal_fpr, optimal_tpr),
            xytext=(optimal_fpr + 0.1, optimal_tpr - 0.1),
            arrowprops=dict(arrowstyle="->", color="red", alpha=0.7),
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
        )

    # Show threshold points
    if show_threshold_points:
        # Show every 10th threshold point to avoid clutter
        thresholds = roc_metrics["thresholds"]
        step = max(1, len(thresholds) // 10)
        for i in range(0, len(thresholds), step):
            if i < len(fpr) and i < len(tpr):
                ax.plot(fpr[i], tpr[i], "o", markersize=3, alpha=0.6, color="gray")

    # Formatting
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel("False Positive Rate (1 - Specificity)")
    ax.set_ylabel("True Positive Rate (Sensitivity)")

    if title is None:
        title = f"ROC Curve Analysis (n={roc_metrics['n_samples']})"
    ax.set_title(title)

    ax.legend(loc="lower right")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


@require_matplotlib
def create_precision_recall_plot(
    pr_metrics: Dict[str, Any],
    title: Optional[str] = None,
    figsize: Tuple[int, int] = (8, 6),
    highlight_optimal: bool = True,
) -> None:
    """
    Create Precision-Recall curve plot.

    Parameters
    ----------
    pr_metrics : dict
        Results from calculate_precision_recall_metrics
    title : str, optional
        Custom title for the plot
    figsize : tuple, optional
        Figure size as (width, height)
    highlight_optimal : bool, default=True
        Whether to highlight the optimal F1 threshold point
    """
    plt = get_matplotlib()

    fig, ax = plt.subplots(figsize=figsize)

    # Plot PR curve
    precision = pr_metrics["precision"]
    recall = pr_metrics["recall"]
    pr_auc = pr_metrics["pr_auc"]

    ax.plot(
        recall, precision, color="blue", lw=2, label=f"PR curve (AUC = {pr_auc:.3f})"
    )

    # Plot baseline (random classifier for imbalanced data)
    y_true = pr_metrics["y_true"]
    pos_label = pr_metrics["pos_label"]
    baseline = np.sum(y_true == pos_label) / len(y_true)
    ax.axhline(
        y=baseline,
        color="red",
        linestyle="--",
        alpha=0.6,
        label=f"Random classifier (AUC = {baseline:.3f})",
    )

    # Highlight optimal F1 threshold point
    if highlight_optimal:
        optimal_precision = pr_metrics["optimal_precision"]
        optimal_recall = pr_metrics["optimal_recall"]
        optimal_f1 = pr_metrics["optimal_f1"]
        optimal_threshold = pr_metrics["optimal_threshold"]

        ax.plot(
            optimal_recall,
            optimal_precision,
            "ro",
            markersize=8,
            label=f"Optimal F1 = {optimal_f1:.3f}",
        )

        # Add annotation
        ax.annotate(
            f"Optimal F1\n({optimal_recall:.3f}, {optimal_precision:.3f})",
            xy=(optimal_recall, optimal_precision),
            xytext=(optimal_recall - 0.1, optimal_precision + 0.05),
            arrowprops=dict(arrowstyle="->", color="red", alpha=0.7),
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
        )

    # Formatting
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel("Recall (Sensitivity)")
    ax.set_ylabel("Precision")

    if title is None:
        title = f"Precision-Recall Curve (n={pr_metrics['n_samples']})"
    ax.set_title(title)

    ax.legend(loc="lower left")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


@require_matplotlib
def create_multiclass_roc_plot(
    multiclass_metrics: Dict[str, Any],
    title: Optional[str] = None,
    figsize: Tuple[int, int] = (10, 8),
) -> None:
    """
    Create multiclass ROC curve plot with one-vs-rest curves.

    Parameters
    ----------
    multiclass_metrics : dict
        Results from calculate_multiclass_roc_metrics
    title : str, optional
        Custom title for the plot
    figsize : tuple, optional
        Figure size as (width, height)
    """
    plt = get_matplotlib()
    import matplotlib.colors as mcolors

    fig, ax = plt.subplots(figsize=figsize)

    # Get colors for different classes
    colors = list(mcolors.TABLEAU_COLORS.values())
    class_labels = multiclass_metrics["class_labels"]
    class_results = multiclass_metrics["class_results"]

    # Plot ROC curve for each class
    for i, class_label in enumerate(class_labels):
        class_data = class_results[class_label]
        color = colors[i % len(colors)]

        ax.plot(
            class_data["fpr"],
            class_data["tpr"],
            color=color,
            lw=2,
            label=f"Class {class_label} (AUC = {class_data['roc_auc']:.3f})",
        )

    # Plot micro-average ROC curve
    micro_avg = multiclass_metrics["micro_average"]
    ax.plot(
        micro_avg["fpr"],
        micro_avg["tpr"],
        color="deeppink",
        linestyle=":",
        linewidth=4,
        label=f"Micro-average (AUC = {micro_avg['roc_auc']:.3f})",
    )

    # Plot macro-average ROC curve
    macro_avg = multiclass_metrics["macro_average"]
    ax.plot(
        macro_avg["fpr"],
        macro_avg["tpr"],
        color="navy",
        linestyle=":",
        linewidth=4,
        label=f"Macro-average (AUC = {macro_avg['roc_auc']:.3f})",
    )

    # Plot diagonal line (random classifier)
    ax.plot([0, 1], [0, 1], "k--", alpha=0.6, label="Random classifier")

    # Formatting
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")

    if title is None:
        title = f"Multiclass ROC Curves (n={multiclass_metrics['n_samples']}, {multiclass_metrics['n_classes']} classes)"
    ax.set_title(title)

    ax.legend(loc="lower right")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


@require_matplotlib
def create_threshold_analysis_plot(
    roc_metrics: Dict[str, Any],
    pr_metrics: Optional[Dict[str, Any]] = None,
    title: Optional[str] = None,
    figsize: Tuple[int, int] = (15, 10),
) -> None:
    """
    Create comprehensive threshold analysis plot with multiple subplots.

    Parameters
    ----------
    roc_metrics : dict
        Results from calculate_roc_metrics
    pr_metrics : dict, optional
        Results from calculate_precision_recall_metrics
    title : str, optional
        Custom title for the plot
    figsize : tuple, optional
        Figure size as (width, height)
    """
    plt = get_matplotlib()

    # Determine subplot layout
    if pr_metrics is not None:
        fig, axes = plt.subplots(2, 3, figsize=figsize)
        axes = axes.flatten()
    else:
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        axes = axes.flatten()

    # 1. ROC Curve
    ax1 = axes[0]
    fpr, tpr = roc_metrics["fpr"], roc_metrics["tpr"]
    auc_score = roc_metrics["roc_auc"]

    ax1.plot(fpr, tpr, "b-", lw=2, label=f"ROC (AUC={auc_score:.3f})")
    ax1.plot([0, 1], [0, 1], "k--", alpha=0.6)
    ax1.plot(roc_metrics["optimal_fpr"], roc_metrics["optimal_tpr"], "ro", markersize=8)
    ax1.set_xlabel("False Positive Rate")
    ax1.set_ylabel("True Positive Rate")
    ax1.set_title("ROC Curve")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # 2. Threshold vs TPR/FPR
    ax2 = axes[1]
    thresholds = roc_metrics["thresholds"]
    ax2.plot(thresholds, tpr, "b-", label="TPR (Sensitivity)", alpha=0.8)
    ax2.plot(thresholds, fpr, "r-", label="FPR", alpha=0.8)
    ax2.plot(thresholds, 1 - fpr, "g-", label="TNR (Specificity)", alpha=0.8)
    ax2.axvline(
        roc_metrics["optimal_threshold"],
        color="orange",
        linestyle="--",
        label="Optimal Threshold",
    )
    ax2.set_xlabel("Threshold")
    ax2.set_ylabel("Rate")
    ax2.set_title("Threshold vs Classification Rates")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # 3. Youden Index vs Threshold
    ax3 = axes[2] if len(axes) > 2 else None
    if ax3 is not None:
        youden_indices = tpr - fpr
        ax3.plot(thresholds, youden_indices, "purple", lw=2)
        ax3.axvline(
            roc_metrics["optimal_threshold"],
            color="orange",
            linestyle="--",
            label="Optimal Threshold",
        )
        optimal_youden = roc_metrics["optimal_youden_index"]
        ax3.axhline(optimal_youden, color="orange", linestyle="--", alpha=0.5)
        ax3.set_xlabel("Threshold")
        ax3.set_ylabel("Youden Index (TPR - FPR)")
        ax3.set_title(f"Youden Index vs Threshold (Max = {optimal_youden:.3f})")
        ax3.legend()
        ax3.grid(True, alpha=0.3)

    # 4. Score Distribution
    ax4 = axes[3] if len(axes) > 3 else axes[2]
    y_scores = roc_metrics["y_scores"]
    y_true = roc_metrics["y_true"]
    pos_label = roc_metrics["pos_label"]

    # Separate scores by true class
    pos_scores = y_scores[y_true == pos_label]
    neg_scores = y_scores[y_true != pos_label]

    ax4.hist(neg_scores, bins=30, alpha=0.7, label="Negative Class", color="red")
    ax4.hist(pos_scores, bins=30, alpha=0.7, label="Positive Class", color="blue")
    ax4.axvline(
        roc_metrics["optimal_threshold"],
        color="orange",
        linestyle="--",
        label="Optimal Threshold",
    )
    ax4.set_xlabel("Predicted Score/Probability")
    ax4.set_ylabel("Frequency")
    ax4.set_title("Score Distribution by True Class")
    ax4.legend()
    ax4.grid(True, alpha=0.3)

    # 5. Precision-Recall Curve (if available)
    if pr_metrics is not None and len(axes) > 4:
        ax5 = axes[4]
        precision, recall = pr_metrics["precision"], pr_metrics["recall"]
        pr_auc = pr_metrics["pr_auc"]

        ax5.plot(recall, precision, "g-", lw=2, label=f"PR (AUC={pr_auc:.3f})")
        ax5.plot(
            pr_metrics["optimal_recall"],
            pr_metrics["optimal_precision"],
            "ro",
            markersize=8,
        )

        # Baseline
        baseline = np.sum(y_true == pos_label) / len(y_true)
        ax5.axhline(baseline, color="red", linestyle="--", alpha=0.6, label="Baseline")

        ax5.set_xlabel("Recall")
        ax5.set_ylabel("Precision")
        ax5.set_title("Precision-Recall Curve")
        ax5.legend()
        ax5.grid(True, alpha=0.3)

        # 6. F1 Score vs Threshold
        if len(axes) > 5:
            ax6 = axes[5]
            thresholds_pr = pr_metrics["thresholds"]
            precision_pr = pr_metrics["precision"][
                :-1
            ]  # Remove last element for threshold alignment
            recall_pr = pr_metrics["recall"][:-1]
            f1_scores = (
                2 * (precision_pr * recall_pr) / (precision_pr + recall_pr + 1e-8)
            )

            ax6.plot(thresholds_pr, f1_scores, "orange", lw=2)
            ax6.axvline(
                pr_metrics["optimal_threshold"],
                color="red",
                linestyle="--",
                label="Optimal F1 Threshold",
            )
            ax6.set_xlabel("Threshold")
            ax6.set_ylabel("F1 Score")
            ax6.set_title(
                f"F1 Score vs Threshold (Max = {pr_metrics['optimal_f1']:.3f})"
            )
            ax6.legend()
            ax6.grid(True, alpha=0.3)

    # Remove any unused subplots
    for i in range(len(axes)):
        if i >= (6 if pr_metrics is not None else 4):
            fig.delaxes(axes[i])

    if title is None:
        title = f"Comprehensive Threshold Analysis (n={roc_metrics['n_samples']})"
    fig.suptitle(title, fontsize=16)

    plt.tight_layout()
    plt.show()
