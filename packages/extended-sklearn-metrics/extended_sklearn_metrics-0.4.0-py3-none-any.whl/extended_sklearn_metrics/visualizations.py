"""
Visualization utilities for extended-sklearn-metrics
"""

import pandas as pd
import numpy as np
from typing import Optional, Tuple, List, Dict, Any
import warnings

from ._plotting_backend import get_matplotlib, require_matplotlib


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


def print_performance_report(results: pd.DataFrame) -> None:
    """
    Print a nicely formatted performance report to console.

    Parameters
    ----------
    results : pd.DataFrame
        Results DataFrame from evaluation functions
    """
    print("=" * 80)
    print("MODEL PERFORMANCE REPORT")
    print("=" * 80)

    # Overall assessment
    performances = results["Performance"].tolist()
    performance_counts = pd.Series(performances).value_counts()

    print(f"OVERALL ASSESSMENT:")
    print("-" * 20)
    for perf, count in performance_counts.items():
        print(f"  {perf}: {count} metric(s)")

    print(f"\nDETAILED METRICS:")
    print("-" * 20)

    # Print each metric with formatting
    for _, row in results.iterrows():
        metric = row["Metric"]
        value = row["Value"]
        performance = row["Performance"]

        # Performance indicator
        perf_indicators = {
            "Excellent": "🟢",
            "Good": "🟢",
            "Acceptable": "🟡",
            "Moderate": "🟡",
            "Poor": "🔴",
            "Very Poor": "🔴",
        }
        indicator = perf_indicators.get(performance, "⚪")

        print(f"  {indicator} {metric:15}: {value:8.4f} ({performance})")

    # Recommendations
    print(f"\nRECOMMENDAIONS:")
    print("-" * 15)

    poor_metrics = results[results["Performance"].isin(["Poor", "Very Poor"])]
    if len(poor_metrics) > 0:
        print("  ⚠️  Consider improving the following metrics:")
        for _, row in poor_metrics.iterrows():
            print(f"     - {row['Metric']}: Currently {row['Performance'].lower()}")
        print(
            "  💡 Suggestions: Feature engineering, hyperparameter tuning, different algorithms"
        )
    else:
        good_metrics = results[results["Performance"].isin(["Good", "Excellent"])]
        if len(good_metrics) == len(results):
            print("  ✅ All metrics show good performance!")
            print(
                "  💡 Consider this model ready for deployment or further validation."
            )
        else:
            print("  ✅ Most metrics show acceptable performance.")
            print("  💡 Consider minor improvements or validate with additional data.")

    print("=" * 80)


@require_matplotlib
def create_residual_plots(
    diagnostics: Dict[str, Any], figsize: Tuple[int, int] = (15, 10)
) -> None:
    """
    Create comprehensive residual diagnostic plots.

    Parameters
    ----------
    diagnostics : dict
        Results from calculate_residual_diagnostics
    figsize : tuple, optional
        Figure size as (width, height)
    """
    plt = get_matplotlib()

    try:
        from scipy import stats
    except ImportError:
        warnings.warn(
            "Scipy is required for residual plots. Install with: pip install scipy",
            UserWarning,
        )
        return

    residuals = diagnostics["residuals"]
    predictions = diagnostics["predictions"]
    true_values = diagnostics["true_values"]

    # Create subplot layout
    fig, axes = plt.subplots(2, 3, figsize=figsize)
    fig.suptitle("Residual Diagnostic Plots", fontsize=16, fontweight="bold")

    # 1. Residuals vs Fitted Values
    ax1 = axes[0, 0]
    ax1.scatter(predictions, residuals, alpha=0.6, s=30)
    ax1.axhline(y=0, color="r", linestyle="--", alpha=0.7)
    ax1.set_xlabel("Fitted Values")
    ax1.set_ylabel("Residuals")
    ax1.set_title("Residuals vs Fitted")
    ax1.grid(True, alpha=0.3)

    # Add trend line
    try:
        z = np.polyfit(predictions, residuals, 1)
        p = np.poly1d(z)
        ax1.plot(predictions, p(predictions), "r-", alpha=0.8, linewidth=2)
    except:
        pass

    # 2. Q-Q Plot for Normality
    ax2 = axes[0, 1]
    stats.probplot(residuals, dist="norm", plot=ax2)
    ax2.set_title("Q-Q Plot (Normality Check)")
    ax2.grid(True, alpha=0.3)

    # 3. Scale-Location Plot (sqrt of standardized residuals vs fitted)
    ax3 = axes[0, 2]
    std_residuals = residuals / np.std(residuals, ddof=1)
    sqrt_abs_std_resid = np.sqrt(np.abs(std_residuals))
    ax3.scatter(predictions, sqrt_abs_std_resid, alpha=0.6, s=30)
    ax3.set_xlabel("Fitted Values")
    ax3.set_ylabel("√|Standardized Residuals|")
    ax3.set_title("Scale-Location Plot")
    ax3.grid(True, alpha=0.3)

    # Add trend line
    try:
        z = np.polyfit(predictions, sqrt_abs_std_resid, 1)
        p = np.poly1d(z)
        ax3.plot(predictions, p(predictions), "r-", alpha=0.8, linewidth=2)
    except:
        pass

    # 4. Histogram of Residuals
    ax4 = axes[1, 0]
    ax4.hist(
        residuals, bins=30, alpha=0.7, density=True, color="skyblue", edgecolor="black"
    )

    # Overlay normal distribution
    mu, sigma = np.mean(residuals), np.std(residuals, ddof=1)
    x = np.linspace(residuals.min(), residuals.max(), 100)
    ax4.plot(
        x, stats.norm.pdf(x, mu, sigma), "r-", linewidth=2, label="Normal Distribution"
    )
    ax4.set_xlabel("Residuals")
    ax4.set_ylabel("Density")
    ax4.set_title("Residuals Distribution")
    ax4.legend()
    ax4.grid(True, alpha=0.3)

    # 5. Residuals vs Order (Time series check)
    ax5 = axes[1, 1]
    ax5.scatter(range(len(residuals)), residuals, alpha=0.6, s=30)
    ax5.axhline(y=0, color="r", linestyle="--", alpha=0.7)
    ax5.set_xlabel("Observation Order")
    ax5.set_ylabel("Residuals")
    ax5.set_title("Residuals vs Order")
    ax5.grid(True, alpha=0.3)

    # 6. Leverage vs Standardized Residuals (if available)
    ax6 = axes[1, 2]
    # For now, just show actual vs predicted
    ax6.scatter(true_values, predictions, alpha=0.6, s=30)

    # Perfect prediction line
    min_val = min(true_values.min(), predictions.min())
    max_val = max(true_values.max(), predictions.max())
    ax6.plot([min_val, max_val], [min_val, max_val], "r--", linewidth=2, alpha=0.7)

    ax6.set_xlabel("True Values")
    ax6.set_ylabel("Predicted Values")
    ax6.set_title("Actual vs Predicted")
    ax6.grid(True, alpha=0.3)

    # Calculate and display R²
    r_squared = np.corrcoef(true_values, predictions)[0, 1] ** 2
    ax6.text(
        0.05,
        0.95,
        f"R² = {r_squared:.4f}",
        transform=ax6.transAxes,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue"),
    )

    plt.tight_layout()
    plt.show()


@require_matplotlib
def create_residual_summary_plot(
    diagnostics: Dict[str, Any], figsize: Tuple[int, int] = (12, 8)
) -> None:
    """
    Create a summary plot showing key residual diagnostic information.

    Parameters
    ----------
    diagnostics : dict
        Results from calculate_residual_diagnostics
    figsize : tuple, optional
        Figure size as (width, height)
    """
    plt = get_matplotlib()

    residuals = diagnostics["residuals"]
    predictions = diagnostics["predictions"]
    stats = diagnostics["residual_statistics"]

    fig, axes = plt.subplots(2, 2, figsize=figsize)
    fig.suptitle("Residual Diagnostics Summary", fontsize=14, fontweight="bold")

    # 1. Residuals vs Fitted with statistics
    ax1 = axes[0, 0]
    ax1.scatter(predictions, residuals, alpha=0.6, s=20, color="steelblue")
    ax1.axhline(y=0, color="r", linestyle="--", alpha=0.7)
    ax1.set_xlabel("Fitted Values")
    ax1.set_ylabel("Residuals")
    ax1.set_title("Residuals vs Fitted")
    ax1.grid(True, alpha=0.3)

    # Add statistics text
    stats_text = f"Mean: {stats['mean']:.4f}\nStd: {stats['std']:.4f}\nMedian: {stats['median']:.4f}"
    ax1.text(
        0.05,
        0.95,
        stats_text,
        transform=ax1.transAxes,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.8),
        verticalalignment="top",
        fontsize=9,
    )

    # 2. Residuals distribution with normality info
    ax2 = axes[0, 1]
    ax2.hist(
        residuals,
        bins=25,
        alpha=0.7,
        density=True,
        color="lightcoral",
        edgecolor="black",
    )
    ax2.set_xlabel("Residuals")
    ax2.set_ylabel("Density")
    ax2.set_title("Residuals Distribution")
    ax2.grid(True, alpha=0.3)

    # Add normality test results if available
    if "normality_tests" in diagnostics and diagnostics["normality_tests"]:
        norm_text = "Normality Tests:\n"
        norm_tests = diagnostics["normality_tests"]

        if "shapiro_wilk" in norm_tests:
            sw = norm_tests["shapiro_wilk"]
            result = "✓" if sw["is_normal"] else "✗"
            norm_text += f"Shapiro-W: {result} (p={sw['p_value']:.3f})\n"

        if "anderson_darling" in norm_tests:
            ad = norm_tests["anderson_darling"]
            result = "✓" if ad["is_normal"] else "✗"
            norm_text += f"Anderson-D: {result}\n"

        ax2.text(
            0.95,
            0.95,
            norm_text.strip(),
            transform=ax2.transAxes,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.8),
            verticalalignment="top",
            horizontalalignment="right",
            fontsize=8,
        )

    # 3. Standardized residuals with outlier info
    ax3 = axes[1, 0]
    std_residuals = residuals / np.std(residuals, ddof=1)
    ax3.scatter(
        range(len(std_residuals)), std_residuals, alpha=0.6, s=20, color="green"
    )
    ax3.axhline(y=0, color="r", linestyle="-", alpha=0.7)
    ax3.axhline(y=2, color="orange", linestyle="--", alpha=0.7, label="±2σ")
    ax3.axhline(y=-2, color="orange", linestyle="--", alpha=0.7)
    ax3.axhline(y=3, color="red", linestyle="--", alpha=0.7, label="±3σ")
    ax3.axhline(y=-3, color="red", linestyle="--", alpha=0.7)
    ax3.set_xlabel("Observation Index")
    ax3.set_ylabel("Standardized Residuals")
    ax3.set_title("Standardized Residuals")
    ax3.legend(loc="upper right")
    ax3.grid(True, alpha=0.3)

    # Add outlier info
    if "outlier_analysis" in diagnostics:
        outliers = diagnostics["outlier_analysis"]
        outlier_text = f"Outliers (>2σ): {outliers['outliers_2std']}\nOutliers (>3σ): {outliers['outliers_3std']}"
        ax3.text(
            0.05,
            0.95,
            outlier_text,
            transform=ax3.transAxes,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightpink", alpha=0.8),
            verticalalignment="top",
            fontsize=9,
        )

    # 4. Test results summary
    ax4 = axes[1, 1]
    ax4.axis("off")  # Turn off axis

    # Create summary text
    summary_text = "DIAGNOSTIC SUMMARY\n" + "=" * 20 + "\n\n"

    # Check each diagnostic
    issues = []

    if abs(stats["mean"]) > 0.01:
        issues.append("⚠ Mean not close to 0")
    else:
        issues.append("✓ Mean close to 0")

    # Normality
    if "normality_tests" in diagnostics and diagnostics["normality_tests"]:
        norm_tests = diagnostics["normality_tests"]
        normal_count = sum(
            1
            for test in norm_tests.values()
            if isinstance(test, dict) and test.get("is_normal", False)
        )
        total_tests = len([t for t in norm_tests.values() if isinstance(t, dict)])

        if total_tests > 0 and normal_count >= total_tests / 2:
            issues.append("✓ Residuals appear normal")
        else:
            issues.append("⚠ Normality questionable")

    # Homoscedasticity
    if (
        "heteroscedasticity_tests" in diagnostics
        and diagnostics["heteroscedasticity_tests"]
    ):
        hetero_tests = diagnostics["heteroscedasticity_tests"]
        homo_count = sum(
            1
            for test in hetero_tests.values()
            if isinstance(test, dict) and test.get("is_homoscedastic", False)
        )
        total_tests = len([t for t in hetero_tests.values() if isinstance(t, dict)])

        if total_tests > 0 and homo_count >= total_tests / 2:
            issues.append("✓ Homoscedastic")
        else:
            issues.append("⚠ Possible heteroscedasticity")

    # Outliers
    if "outlier_analysis" in diagnostics:
        outliers = diagnostics["outlier_analysis"]
        if outliers["outliers_3std"] == 0:
            issues.append("✓ No extreme outliers")
        else:
            issues.append(f"⚠ {outliers['outliers_3std']} extreme outliers")

    summary_text += "\n".join(issues)

    # Overall assessment
    warning_count = sum(1 for issue in issues if issue.startswith("⚠"))
    summary_text += f"\n\n{'=' * 20}\n"

    if warning_count == 0:
        summary_text += "✅ GOOD: No major issues\nModel assumptions appear satisfied"
        color = "lightgreen"
    elif warning_count <= 2:
        summary_text += "⚠️  CAUTION: Some issues detected\nConsider model improvements"
        color = "lightyellow"
    else:
        summary_text += "❌ CONCERN: Multiple issues\nModel needs attention"
        color = "lightcoral"

    ax4.text(
        0.05,
        0.95,
        summary_text,
        transform=ax4.transAxes,
        bbox=dict(boxstyle="round,pad=0.5", facecolor=color, alpha=0.8),
        verticalalignment="top",
        fontsize=10,
        family="monospace",
    )

    plt.tight_layout()
    plt.show()


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
