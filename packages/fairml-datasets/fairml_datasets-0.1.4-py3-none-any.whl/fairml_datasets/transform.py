"""
Data transformation utilities for fairness datasets.

This module provides functions to transform datasets into formats suitable for
fairness analysis, including handling of sensitive attributes, target variables,
missing values, and categorical features.
"""

from dataclasses import dataclass
import logging
import pandas as pd
from typing import List, Literal, Optional


from .processing.datasets import (
    binarize_column,
)
from .processing.helpers import encode_majority_minority


@dataclass
class PreprocessingInfo:
    """
    Class to store information about preprocessing steps applied to a dataset.

    Attributes:
        sensitive_columns: List of column names identified as sensitive attributes
        col_na_indicator: Series indicating rows with missing values in the original dataset
    """

    sensitive_columns: List[str]
    col_na_indicator: pd.Series


logger = logging.getLogger(__name__)


MISSING_VALUE = "MISSING"


def limit_categorical_levels(
    df: pd.DataFrame, columns: List[str], max_unique: int, other_value: str = "OTHER"
) -> pd.DataFrame:
    """
    Limit the number of unique values in categorical columns by combining less frequent
    values into an 'other' category.

    Args:
        df: DataFrame containing categorical columns
        columns: List of categorical column names to transform
        max_unique: Maximum number of unique values to keep (most frequent)
        other_value: Value to use for the combined less frequent categories

    Returns:
        pd.DataFrame: DataFrame with limited categorical levels
    """
    df = df.copy()

    for col in columns:
        # Only transform if column has more unique values than max_unique
        value_counts = df[col].value_counts()
        if len(value_counts) > max_unique:
            logger.debug(
                f"Limiting categorical values in column '{col}' from {len(value_counts)} to {max_unique} unique values."
            )

            # Get the top max_unique most frequent values
            top_values = value_counts.nlargest(max_unique).index.tolist()

            # Check if column is categorical and handle differently
            if pd.api.types.is_categorical_dtype(df[col]):
                # Get all current categories
                current_categories = list(df[col].cat.categories)

                # Add 'OTHER' to categories if it's not already there
                if other_value not in current_categories:
                    new_categories = current_categories + [other_value]
                    df[col] = df[col].cat.set_categories(new_categories)

            mask = ~df[col].isin(top_values)
            df.loc[mask, col] = other_value

    return df


def filter_columns(
    df: pd.DataFrame,
    sensitive_columns: List[str],
    feature_columns: List[str],
    target_column: str,
) -> pd.DataFrame:
    """
    Filter a DataFrame to include only specified columns.

    Args:
        df: DataFrame to filter
        sensitive_columns: List of sensitive attribute column names to include
        feature_columns: List of feature column names to include
        target_column: Target column name to include

    Returns:
        pd.DataFrame: Filtered DataFrame with only the specified columns
    """
    set_sensitive = set(sensitive_columns)
    set_features = set(feature_columns)
    set_target = set([target_column])

    # Combine all columns
    final_columns = list(set_sensitive | set_features | set_target)
    return df[final_columns]


def transform(
    df: pd.DataFrame,
    sensitive_columns: List[str],
    feature_columns: List[str],
    target_column: str,
    target_lvl_good_bad: Optional[str] = None,
    select_columns: Literal["keep_all", "typical_only"] = "typical_only",
    transform_na_numerical: Literal[
        "drop_columns", "drop_rows", "impute_median"
    ] = "impute_median",
    transform_na_character: Literal[
        "drop_columns", "drop_rows", "new_value"
    ] = "new_value",
    transform_target: Literal["auto", "good_bad", "majority_minority"] = "auto",
    transform_sensitive_columns: Literal["none", "intersection_binary"] = "none",
    transform_sensitive_values: Literal["majority_minority", "none"] = "none",
    transform_categorical: Literal["dummy", "none"] = "dummy",
    max_categorical_levels: Optional[int] = 200,
) -> tuple[pd.DataFrame, PreprocessingInfo]:
    """
    Transform a DataFrame for fairness analysis.

    Args:
        df: DataFrame to transform
        sensitive_columns: List of sensitive attribute column names
        feature_columns: List of feature column names
        target_column: Target column name
        target_lvl_good_bad: Optional string specifying the "good" level for the target column
        select_columns: Strategy for selecting columns ("keep_all" or "typical_only")
        transform_na_numerical: Strategy for handling missing values in numerical columns
        transform_na_character: Strategy for handling missing values in categorical columns
        transform_target: Strategy for transforming the target column
        transform_sensitive_columns: Strategy for handling multiple sensitive columns
        transform_sensitive_values: Strategy for transforming sensitive values
        transform_categorical: Strategy for transforming categorical columns
        max_categorical_levels: Limit the number of unique values in categorical columns. Set to None to disable.

    Returns:
        tuple[pd.DataFrame, PreprocessingInfo]: Transformed DataFrame and preprocessing information
    """
    # Prevent modifying the original DataFrame
    df = df.copy()

    logger.debug(f"select_columns: {select_columns}")
    if select_columns == "typical_only":
        # Keep only the correct columns
        df = filter_columns(
            df=df,
            sensitive_columns=sensitive_columns,
            feature_columns=feature_columns,
            target_column=target_column,
        )
    elif select_columns == "keep_all":
        pass
    else:
        raise ValueError(f"Unknown column filter option: {filter_columns}")

    logger.debug(f"columns - target: {target_column} | sensitive: {sensitive_columns}")

    # How to handle NAs
    # Create an indicator column to check whether any row contains NAs
    COLNAME_NA_INDICATOR = "__TEMP_HAS_NA__"
    df[COLNAME_NA_INDICATOR] = df.isna().any(axis=1).astype(int)
    # Handle missing values in numerical columns
    numerical_cols = df.select_dtypes(include=["number"]).columns
    logger.debug(
        f"Transforming NAs in numerical cols (strategy: {transform_na_numerical} | columns: {numerical_cols})"
    )
    if transform_na_numerical == "drop_columns":
        df = df.drop(columns=[col for col in numerical_cols if df[col].isna().any()])
    elif transform_na_numerical == "drop_rows":
        df = df.dropna(subset=numerical_cols)
    elif transform_na_numerical == "impute_median":
        for col in numerical_cols:
            if df[col].isna().any():
                df[col] = df[col].fillna(df[col].median())
    else:
        raise ValueError(f"Unknown NA transformation: {transform_na_numerical}")

    # Handle missing values in categorical columns
    character_cols = df.select_dtypes(include=["object", "category", "string"]).columns
    logger.debug(
        f"Transforming NAs in character cols (strategy: {transform_na_character} | columns: {character_cols})"
    )
    if transform_na_character == "drop_columns":
        df = df.drop(columns=[col for col in character_cols if df[col].isna().any()])
    elif transform_na_character == "drop_rows":
        df = df.dropna(subset=character_cols)
    elif transform_na_character == "new_value":
        categorical_cols = df.select_dtypes(include=["category"]).columns
        noncategorical_cols = list(set(character_cols) - set(categorical_cols))

        df[noncategorical_cols] = df[noncategorical_cols].fillna(MISSING_VALUE)
        # Note casting to string here to avoid issues with categoricals rejecting a new item
        df[categorical_cols] = (
            df[categorical_cols].astype("str").fillna(MISSING_VALUE).astype("category")
        )
    else:
        raise ValueError(f"Unknown NA transformation: {transform_na_character}")

    # Pre-Validation
    cols_with_na_first = df.isna().sum() > 0
    if cols_with_na_first.any():
        logger.warning(
            f"Detected columns with lingering NAs after NA processing: {','.join(cols_with_na_first.index)}"
        )

    # Turn target column into 0 / 1
    logger.debug(f"Transforming target: {transform_target}")
    if transform_target == "auto":
        transform_target = (
            "good_bad" if target_lvl_good_bad is not None else "majority_minority"
        )

    if transform_target == "good_bad":
        # Use the annotated information on "good" and "bad" values
        assert target_lvl_good_bad is not None, "No target value specified."
        df[target_column] = binarize_column(
            column=df[target_column],
            condition=target_lvl_good_bad,
            val_success=1,
            val_failed=0,
        )
        assert 1 in set(df[target_column]), "No positive class found in target column."
    elif transform_target == "majority_minority":
        # MAJOR ASSUMPTION: the majority class is always the positive class
        df[target_column] = encode_majority_minority(df[target_column])
    else:
        raise ValueError(f"Unknown label transformation: {transform_target}")

    # Turn sensitive column(s) into 0 / 1
    logger.debug(f"Transforming sensitive values: {transform_sensitive_values}")
    if transform_sensitive_values == "majority_minority":
        # MAJOR ASSUMPTION: the majority class is always the positive class
        for sensitive_column in sensitive_columns:
            df[sensitive_column] = encode_majority_minority(df[sensitive_column])
    elif transform_sensitive_values == "none":
        pass
    else:
        raise ValueError(
            f"Unknown sensitive transformation: {transform_sensitive_values}"
        )

    # Handle multiple sensitive columns
    logger.debug(f"Transforming sensitive columns: {transform_sensitive_columns}")
    if transform_sensitive_columns == "intersection_binary":
        # Compute intersection of all sensitive columns
        df["sensitive_intersection"] = df[sensitive_columns].all(axis=1).astype(int)
        df.drop(columns=sensitive_columns, inplace=True)
        sensitive_columns = ["sensitive_intersection"]
    elif transform_sensitive_columns == "none":
        pass
    else:
        raise ValueError(
            f"Unknown sensitive transformation: {transform_sensitive_columns}"
        )

    cat_columns = df.select_dtypes(include=["object", "category", "string"]).columns
    cat_columns = [col for col in cat_columns if col not in sensitive_columns + [target_column]]
    logger.debug(f"Transforming cat. columns: {transform_categorical} ({cat_columns})")

    # Limit categorical values if specified
    if max_categorical_levels is not None and len(cat_columns) > 0:
        logger.debug(f"Limiting categorical values to top {max_categorical_levels}")
        df = limit_categorical_levels(df, cat_columns, max_categorical_levels)

    if transform_categorical == "dummy":
        # Dummy code all categorical columns (so everything is numerical)
        df = pd.get_dummies(df, columns=cat_columns)
    elif transform_categorical == "none":
        # Do nothing to categorical columns
        pass
    else:
        raise ValueError(f"Unknown categorical transformation: {transform_categorical}")

    # Remove NA indicator column
    col_na_indicator = df[COLNAME_NA_INDICATOR]
    df = df.drop(columns=[COLNAME_NA_INDICATOR])

    # Validation
    cols_with_na_final = df.isna().sum() > 0
    if cols_with_na_final.any():
        logger.warning(
            f"Detected columns with lingering NAs after all preprocessing: {','.join(cols_with_na_final.index)}"
        )

    # Do some final checks
    n_rows, n_cols = df.shape
    if n_rows < 2:
        logger.warning(f"Dataset has only {n_rows} row left after preprocessing.")
    n_positive = df[target_column].sum()
    n_negative = n_rows - n_positive
    if ((n_positive / n_rows) < 0.01) or ((n_negative / n_rows) < 0.01):
        logger.warning(
            f"Dataset is very imbalanced (target: {n_positive} pos | {n_negative} neg)."
        )

    return (
        df,
        PreprocessingInfo(
            sensitive_columns=sensitive_columns, col_na_indicator=col_na_indicator
        ),
    )
