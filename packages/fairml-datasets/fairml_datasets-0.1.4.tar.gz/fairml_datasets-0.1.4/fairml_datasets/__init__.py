"""
FairML Datasets - A package for managing and processing datasets for fairness research in machine learning.

This package provides tools and interfaces to download, load, transform, and analyze datasets
commonly used in algorithmic fairness research. It handles sensitive attributes and facilitates
fairness-aware machine learning experiments.
"""

from .dataset import Dataset
from .datasets import Datasets
from .scenario import Scenario

__all__ = ["Dataset", "Datasets", "Scenario"]
