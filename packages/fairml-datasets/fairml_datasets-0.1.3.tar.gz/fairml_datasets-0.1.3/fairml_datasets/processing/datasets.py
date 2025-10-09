"""
Utility functions for dataset processing and manipulation.

This module provides functions that handle common dataset processing tasks,
such as loading processing scripts, binarizing columns, and filtering
feature columns based on specified criteria.
"""

from importlib import import_module
from typing import Optional, Set
import logging

import pandas as pd

from . import ProcessingScript

logger = logging.getLogger(__name__)


def get_processing_script(id: str) -> Optional[ProcessingScript]:
    """
    Load the processing script for a dataset (if it exists).

    Attempts to import a dataset-specific processing script based on the dataset ID.
    If no script exists for the specified dataset, returns None.

    Args:
        id: Dataset identifier

    Returns:
        Optional[ProcessingScript]: Processing script class for the dataset, or None if not found

    Raises:
        AssertionError: If the script exists but is not a ProcessingScript subclass
    """
    try:
        module = import_module(f".{id}", package="fairml_datasets.processing.scripts")
        script = getattr(module, "Script")

        assert issubclass(
            script, ProcessingScript
        ), f"Processing script for {id} must be a ProcessingScript subclass"

        return script
    except ImportError:
        return None


def binarize_column(
    column: pd.Series, condition: str, val_success=1, val_failed=0
) -> pd.Series:
    """
    Binarize a column based on a specified condition.

    Converts the values in a column to binary (0 or 1) based on the provided condition.
    The condition can be a direct value, a list of values, or a numerical comparison.

    Args:
        column: Pandas Series to be binarized
        condition: Condition for binarization (e.g., 'value', 'value1,value2', '>value', '<value', 'lower-upper')
        val_success: Value to assign if the condition is met (default is 1)
        val_failed: Value to assign if the condition is not met (default is 0)

    Returns:
        pd.Series: Binarized column
    """
    # Strip strings if applicable
    if column.dtype in ["object", "string"]:
        column = column.str.strip()

    if condition in set(column.astype(str)):
        # Value is present directly
        # Encode it as 1, everything else as 0
        column = column.astype(str).apply(
            lambda x: val_success if x == condition else val_failed
        )
    else:
        # Value is not present directly -> try to parse value specification
        if "," in condition:
            # Found a comma, use a list of values
            conditions = condition.split(",")

            # Encode it as 1, everything else as 0
            column = column.astype(str).apply(
                lambda x: val_success if x in conditions else val_failed
            )
        elif condition.startswith((">", "<")):
            # Numerical one-sided comparison
            # Check for whether second character is = (for >=, <=)
            includes_equal = condition[1] == "="

            # Extract the numerical value
            condition_num = condition[2:] if includes_equal else condition[1:]
            condition_num = float(condition_num)

            # Encode it as 1, everything else as 0
            # Choose the corect comparison
            if condition[0] == ">":
                if includes_equal:
                    column = column.apply(
                        lambda x: val_success if x >= condition_num else val_failed
                    )
                else:
                    column = column.apply(
                        lambda x: val_success if x > condition_num else val_failed
                    )
            elif condition[0] == "<":
                if includes_equal:
                    column = column.apply(
                        lambda x: val_success if x <= condition_num else val_failed
                    )
                else:
                    column = column.apply(
                        lambda x: val_success if x < condition_num else val_failed
                    )
            else:
                raise ValueError(f"Unknown numerical comparison: '{condition}'.")
        elif "-" in condition:
            # Range of values (numerical two-sided comparison)
            lower, upper = condition.split("-")

            # Encode it as 1, everything else as 0
            column = column.apply(
                lambda x: val_success
                if float(lower) <= x <= float(upper)
                else val_failed
            )
        else:
            raise ValueError(
                f"Unable to find / decode '{condition}' when binarizing column."
            )

    return column


def parse_feature_column_filter(
    all_columns: Set[str],
    target_column: Set[str],
    sensitive_columns,
    filter: str | None,
) -> Set[str]:
    """
    Parse and filter feature columns based on specified criteria.

    Determines which columns should be used as features based on the provided filter criteria.
    The filter can specify columns to include or exclude, or use all columns except target and sensitive columns.

    Args:
        all_columns: Set of all column names in the dataset
        target_column: Set containing the target column name
        sensitive_columns: Set of sensitive column names
        filter: Filter criteria for feature columns (e.g., '-', '-col1;col2', 'col1;col2')

    Returns:
        Set[str]: Set of feature column names

    Raises:
        AssertionError: If any specified columns are not found in the dataset
    """
    potential_feature_columns = all_columns - target_column

    # Note: Use all columns as features if information is missing (this is an opnionated choice!)
    if filter is None:
        filter = "-"

    if filter == "-":
        # Use all columns as features
        feature_columns = potential_feature_columns
    elif filter.startswith("-"):
        # Use all columns except the ones listed here
        columns_to_exclude = set(filter[1:].split(";"))
        feature_columns = potential_feature_columns - columns_to_exclude
    elif len(filter) > 0:
        # Use only the columns listed here
        feature_columns = set(filter.split(";"))
    else:
        # Empty string: use all columns except target and sensitive (but give a warning)
        logger.warning(
            "No typical feature columns specified. Using all columns except target and sensitive."
        )
        feature_columns = potential_feature_columns - sensitive_columns

    # Validate columns
    assert target_column.issubset(
        all_columns
    ), f"Sensitive column not found in dataset: {target_column - all_columns}."
    assert sensitive_columns.issubset(
        all_columns
    ), f"Sensitive columns not found in dataset: {sensitive_columns - all_columns}."
    assert feature_columns.issubset(
        all_columns
    ), f"Feature columns not found in dataset: {feature_columns - all_columns}."
    assert len(feature_columns) > 0, "No feature columns selected."

    return feature_columns
