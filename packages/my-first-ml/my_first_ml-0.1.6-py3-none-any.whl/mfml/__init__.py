"""
my-first-ml (mfml)
A test package for ML explanation utilities
"""

__version__ = "0.1.6"

from .core import describe, wine_classification, iris_classification, matplotlib_sb, numpy_basic, scipy_eda, imbalance

__all__ = ["describe", "wine_classification", "iris_classification", "matplotlib_sb", "numpy_basic", "scipy_eda", "imbalance"]
