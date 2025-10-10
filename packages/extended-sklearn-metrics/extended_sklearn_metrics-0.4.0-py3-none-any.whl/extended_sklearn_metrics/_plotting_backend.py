"""
Lazy matplotlib import and plotting utilities.

This module provides a centralized way to handle matplotlib imports,
reducing code duplication and import overhead across visualization functions.
"""

import warnings
from typing import Optional, Any
from functools import wraps


# Global state for matplotlib availability
_matplotlib_available: Optional[bool] = None
_plt: Optional[Any] = None


def get_matplotlib():
    """
    Lazily import matplotlib and return pyplot module.

    This function caches the matplotlib module on first import to avoid
    repeated import checks across multiple visualization calls.

    Returns
    -------
    matplotlib.pyplot module

    Raises
    ------
    ImportError
        If matplotlib is not available

    Examples
    --------
    >>> plt = get_matplotlib()
    >>> fig, ax = plt.subplots()
    """
    global _matplotlib_available, _plt

    if _matplotlib_available is None:
        try:
            import matplotlib.pyplot as plt

            _plt = plt
            _matplotlib_available = True
        except ImportError:
            _matplotlib_available = False
            _plt = None

    if not _matplotlib_available:
        raise ImportError(
            "Matplotlib is required for visualizations. "
            "Install with: pip install matplotlib"
        )

    return _plt


def check_matplotlib_available() -> bool:
    """
    Check if matplotlib is available without raising error.

    Returns
    -------
    bool
        True if matplotlib is available, False otherwise

    Examples
    --------
    >>> if check_matplotlib_available():
    ...     create_plot()
    ... else:
    ...     print("Matplotlib not available")
    """
    try:
        get_matplotlib()
        return True
    except ImportError:
        return False


def require_matplotlib(func):
    """
    Decorator to check matplotlib availability before function execution.

    If matplotlib is not available, the function will return None and emit
    a warning instead of raising an error.

    Parameters
    ----------
    func : callable
        The visualization function to decorate

    Returns
    -------
    callable
        Wrapped function with matplotlib check

    Examples
    --------
    >>> @require_matplotlib
    ... def my_plot():
    ...     plt = get_matplotlib()
    ...     plt.plot([1, 2, 3])
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not check_matplotlib_available():
            warnings.warn(
                f"Function '{func.__name__}' requires matplotlib. "
                "Install with: pip install matplotlib",
                UserWarning,
            )
            return None
        return func(*args, **kwargs)

    return wrapper


def reset_matplotlib_cache():
    """
    Reset the matplotlib import cache.

    This is primarily useful for testing purposes, allowing tests to simulate
    matplotlib being unavailable even if it's installed.

    Examples
    --------
    >>> reset_matplotlib_cache()
    >>> # matplotlib will be re-imported on next get_matplotlib() call
    """
    global _matplotlib_available, _plt
    _matplotlib_available = None
    _plt = None
