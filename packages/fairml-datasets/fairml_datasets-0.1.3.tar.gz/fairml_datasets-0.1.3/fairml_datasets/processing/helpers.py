"""
Helper functions for processing fairness datasets.

This module provides utility functions for common data transformations
and conversions used in fairness-related data processing.
"""

from typing import Tuple
import pandas as pd
import numpy as np
from aif360.datasets import StandardDataset


def encode_majority_minority(
    column: pd.Series, label_majority=1, label_minority=0
) -> pd.Series:
    """
    Encode a column into majority (1) and minority (0) values.

    This function identifies the most common value in a column and assigns
    label_majority (default 1) to it, and label_minority (default 0) to all other values.

    Args:
        column: Series to encode
        label_majority: Label to assign to the most common value
        label_minority: Label to assign to all other values

    Returns:
        pd.Series: Encoded series with binary values
    """
    most_common_value = column.mode()[0]
    return np.where(column == most_common_value, label_majority, label_minority)


def aif_to_pandas(
    aif_dataset: StandardDataset,
) -> Tuple[pd.DataFrame, pd.Series, pd.Series]:
    """Convert an AIF360 dataset to a pandas DataFrame and Series.

    Args:
        aif_dataset: An AIF360 dataset.

    Returns:
        (X, y, s): A tuple containing the features, labels, and protected attributes.
    """
    X = pd.DataFrame(aif_dataset.features, columns=aif_dataset.feature_names)
    y = pd.Series(aif_dataset.labels.flatten())
    s = pd.Series(aif_dataset.protected_attributes.flatten())
    return (X, y, s)
