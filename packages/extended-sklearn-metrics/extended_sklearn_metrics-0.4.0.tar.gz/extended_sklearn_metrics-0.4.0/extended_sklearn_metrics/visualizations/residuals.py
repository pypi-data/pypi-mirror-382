"""
Residual diagnostic visualization functions.

This module contains functions for creating comprehensive residual diagnostic plots
for regression model evaluation.
"""

import pandas as pd
import numpy as np
from typing import Optional, Tuple, List, Dict, Any
import warnings

from .._plotting_backend import get_matplotlib, require_matplotlib


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
