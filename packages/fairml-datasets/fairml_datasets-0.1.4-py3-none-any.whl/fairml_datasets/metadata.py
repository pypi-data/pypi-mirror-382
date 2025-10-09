"""
Module for generating metadata and descriptive statistics for fairness datasets.

This module provides functions to analyze fairness datasets and generate
descriptive statistics about their properties, such as base rates across
sensitive groups, correlations, and other fairness-relevant metrics.
"""

import logging
import pandas as pd
import numpy as np

from typing import List, Optional

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score

logger = logging.getLogger(__name__)


def generate_general_descriptives(
    df_raw: pd.DataFrame,
    sensitive_columns: List[str],
    target_column: str,
    target_lvl_good_value: str,
    feature_columns: Optional[List[str]] = None,
    prefix: str = "meta_pretrans_",
    debug_prefix: str = "debug_meta_",
) -> dict:
    """
    Generate general descriptive statistics for a dataset before preprocessing.

    Args:
        df_raw: Raw DataFrame to analyze
        sensitive_columns: List of sensitive attribute column names
        target_column: Target column name
        target_lvl_good_value: Value in target column representing a favorable outcome
        prefix: Prefix to use for metadata column names (default: "meta_pretrans_")
        debug_prefix: Prefix to use for debug metadata column names (default: "debug_meta_")

    Returns:
        dict: Dictionary of descriptive statistics

    Raises:
        AssertionError: If specified columns don't exist in the dataset
    """
    warnings = []

    # Descriptives that could be computed on any dataset
    n_rows_raw, n_cols_raw = df_raw.shape

    # Find string columns within features with high cardinality (>100 unique values)
    cols_to_check = feature_columns if feature_columns else df_raw.columns
    string_cols = (
        df_raw[cols_to_check]
        .select_dtypes(include=["object", "string", "category"])
        .columns
    )
    high_cardinality_strings = {
        col: df_raw[col].nunique() for col in string_cols if df_raw[col].nunique() > 100
    }

    if n_rows_raw < 2:
        warnings.append(f"Dataset has only {n_rows_raw} rows (before processing).")
    if n_cols_raw < 2:
        warnings.append(f"Dataset has only {n_cols_raw} columns (before processing).")

    # Extract information on sensitive columns
    sensitive_columns = sensitive_columns
    if not sensitive_columns:
        sensitive_columns = []
        warnings.append("Missing information on sensitive columns.")

    # Check whether columns / values exist in the dataset
    missing_columns = [col for col in sensitive_columns if col not in df_raw.columns]
    assert (
        len(missing_columns) == 0
    ), f"Sensitive columns not found in dataset: {missing_columns}. Existing columns: {list(df_raw.columns)}."

    assert (
        target_column in df_raw.columns
    ), f"Target column not found in dataset: {target_column}"

    if target_lvl_good_value is None:
        warnings.append(
            "Missing information on which target value would be considered 'good'."
        )

    # Unique group counts
    raw_unique_group_counts_pre_agg = (
        (df_raw.groupby(sensitive_columns, observed=True).size().nunique())
        if sensitive_columns
        else pd.NA
    )

    if warnings:
        logger.warning(
            f"There were potential problems when generating general descriptives: {','.join(warnings)}"
        )

    return {
        f"{prefix}unique_group_counts_pre_agg": raw_unique_group_counts_pre_agg,
        f"{prefix}n_rows": n_rows_raw,
        f"{prefix}n_cols": n_cols_raw,
        f"{prefix}prop_NA_rows": (n_rows_raw - df_raw.dropna().shape[0]) / n_rows_raw,
        f"{prefix}prop_NA_cols": (n_cols_raw - df_raw.dropna(axis=1).shape[1])
        / n_cols_raw,
        f"{prefix}prop_NA_cells": df_raw.isna().sum().sum() / (n_rows_raw * n_cols_raw),
        f"{debug_prefix}high_cardinality_strings": ";".join(
            list(high_cardinality_strings.keys())
        ),
        f"{debug_prefix}high_cardinality_strings_and_counts": ";".join(
            [f"{k} ({v})" for k, v in high_cardinality_strings.items()]
        ),
    }


def generate_binarized_descriptives(
    df: pd.DataFrame,
    sensitive_columns: List[str],
    target_column: str,
    col_na_indicator: pd.Series,
    classifier_seed: int = 80539,
    prefix: str = "meta_",
) -> dict:
    """
    Generate descriptive statistics for a preprocessed dataset with binarized attributes.

    This function computes fairness-relevant metrics such as base rates, prevalence differences,
    correlation between sensitive attributes and other features, and sensitive attribute predictability.

    Args:
        df: Preprocessed DataFrame with binarized attributes
        sensitive_columns: List of sensitive attribute column names
        target_column: Target column name
        col_na_indicator: Series indicating rows with missing values in the original dataset
        classifier_seed: Random seed for the classifier used to predict sensitive attributes
        prefix: Prefix to use for metadata column names (default: "meta_")

    Returns:
        dict: Dictionary of fairness-relevant metrics and descriptive statistics
    """
    warnings = []

    n_rows, n_cols = df.shape
    if n_rows < 2:
        warnings.append(f"Dataset has only {n_rows} rows.")
    if n_cols < 2:
        warnings.append(f"Dataset has only {n_cols} columns.")

    if len(sensitive_columns) != 1:
        warnings.append(
            f"Only one sensitive column is supported, but found {len(sensitive_columns)}."
        )
    sensitive_attr = sensitive_columns[0]

    # Calculate prevalence-based metrics (dist of sens attr)
    prev_sens_minority = (df[sensitive_attr] == 0).mean()
    prev_sens_majority = (df[sensitive_attr] == 1).mean()
    prev_sens_difference = abs(prev_sens_majority - prev_sens_minority)
    prev_sens_ratio = prev_sens_minority / prev_sens_majority
    # Gini-Simpson index
    prev_sens_gini = 1 - (prev_sens_minority**2 + prev_sens_majority**2)

    # Calculate base base-rate metrics (dist of target)
    base_rate_target = df[target_column].mean()
    base_rate_target_sens_minority = df[df[sensitive_attr] == 0][target_column].mean()
    base_rate_target_sens_majority = df[df[sensitive_attr] == 1][target_column].mean()
    base_rate_difference = abs(
        base_rate_target_sens_majority - base_rate_target_sens_minority
    )
    base_rate_ratio = base_rate_target_sens_minority / base_rate_target_sens_majority
    base_rate_sens_gini = 1 - (
        base_rate_target_sens_minority**2 + base_rate_target_sens_majority**2
    )

    # Convert sensitive to numeric (if it isn't already)
    sensitive_num = df[sensitive_attr]
    if sensitive_num.dtype.kind not in "biufc":
        sensitive_num = sensitive_num.astype("category").cat.codes

    # Calculate correlations between sensitive attribute and rest of dataframe
    correlations = df.drop(columns=[sensitive_attr, target_column]).corrwith(
        sensitive_num, numeric_only=True
    )

    average_absolute_correlation = correlations.abs().mean()
    maximum_absolute_correlation = correlations.abs().max()

    # Calculate how predictable the sensitive attribute is from other features
    sens_roc_auc = None
    try:
        X = df.drop(columns=[sensitive_attr, target_column])
        y = df[sensitive_attr].values
        if len(np.unique(y)) == 2:  # Only for binary sensitive attributes
            model = RandomForestClassifier(
                n_estimators=50, max_depth=5, random_state=classifier_seed
            )
            model.fit(X, y)
            y_pred_proba = model.predict_proba(X)[:, 1]
            sens_roc_auc = roc_auc_score(y, y_pred_proba)
    except Exception as e:
        logger.error(f"Could not calculate sensitive attribute AUC: {str(e)}")

    if warnings:
        logger.warning(
            f"There were potential problems when generating general descriptives: {','.join(warnings)}"
        )

    return {
        # Metdata based on "raw" data (i.e. not preprocessed)
        f"{prefix}prop_NA_sens_majority": col_na_indicator[
            df[sensitive_attr] == 1
        ].mean(),
        f"{prefix}prop_NA_sens_minority": col_na_indicator[
            df[sensitive_attr] == 0
        ].mean(),
        # Metadata based on preprocessed data
        f"{prefix}n_rows": n_rows,
        f"{prefix}n_cols": n_cols,
        f"{prefix}sens_predictability_roc_auc": sens_roc_auc,
        f"{prefix}prop_cols_int": sum(df[col].dtype.kind == "i" for col in df.columns)
        / len(df.columns),
        f"{prefix}prop_cols_float": sum(df[col].dtype.kind == "f" for col in df.columns)
        / len(df.columns),
        f"{prefix}prop_cols_bool": sum(df[col].dtype.kind == "b" for col in df.columns)
        / len(df.columns),
        f"{prefix}average_absolute_correlation": average_absolute_correlation,
        f"{prefix}maximum_absolute_correlation": maximum_absolute_correlation,
        f"{prefix}prev_sens_minority": prev_sens_minority,
        f"{prefix}prev_sens_majority": prev_sens_majority,
        f"{prefix}prev_sens_difference": prev_sens_difference,
        f"{prefix}prev_sens_ratio": prev_sens_ratio,
        f"{prefix}prev_sens_gini": prev_sens_gini,
        f"{prefix}base_rate_target": base_rate_target,
        f"{prefix}base_rate_target_sens_minority": base_rate_target_sens_minority,
        f"{prefix}base_rate_target_sens_majority": base_rate_target_sens_majority,
        f"{prefix}base_rate_difference": base_rate_difference,
        f"{prefix}base_rate_ratio": base_rate_ratio,
        f"{prefix}base_rate_sens_gini": base_rate_sens_gini,
    }
