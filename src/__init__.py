"""Fraud detection source package.

Submodules are imported directly to keep optional plotting/modeling
dependencies from being loaded during lightweight tests.
"""

__all__ = [
    "eda_utils",
    "feature_engineering",
    "geolocation",
    "preprocessing",
]
