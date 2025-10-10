"""
Visualization utilities for extended-sklearn-metrics
"""

import pandas as pd
import numpy as np
from typing import Optional, Tuple, List, Dict, Any
import warnings

from .._plotting_backend import get_matplotlib, require_matplotlib


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
