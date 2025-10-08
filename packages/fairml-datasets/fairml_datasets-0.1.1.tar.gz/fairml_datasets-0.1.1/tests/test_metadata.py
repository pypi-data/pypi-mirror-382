"""
Tests for the metadata module functions.
"""

import pytest
import pandas as pd
import numpy as np
import logging

from fairml_datasets.metadata import (
    generate_general_descriptives,
    generate_binarized_descriptives,
)


@pytest.fixture
def sample_df_raw():
    """Create a sample raw DataFrame for testing metadata functions."""
    # Create high cardinality column with >100 unique values
    high_card_values = [f"val_{i}" for i in range(150)]

    df = pd.DataFrame(
        {
            "sensitive_attr": ["A", "B", "A", "B", "A", None, "B", "A", "B", "A"],
            "target": [
                "good",
                "bad",
                "good",
                "good",
                "bad",
                "good",
                "bad",
                "good",
                "bad",
                "good",
            ],
            "numerical_feat": [1.0, 2.0, np.nan, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
            "categorical_feat": [
                "cat1",
                "cat2",
                "cat1",
                "cat2",
                "cat1",
                "cat2",
                "cat3",
                "cat1",
                "cat2",
                "cat1",
            ],
            "high_cardinality": high_card_values[:10],
        }
    )

    # Create actually high cardinality column by adding more rows
    extended_df = pd.DataFrame(
        {
            "sensitive_attr": ["A"] * 150,
            "target": ["good"] * 150,
            "numerical_feat": list(range(150)),
            "categorical_feat": ["cat1"] * 150,
            "high_cardinality": high_card_values,
        }
    )

    return pd.concat([df, extended_df], ignore_index=True)


@pytest.fixture
def sample_df_binarized():
    """Create a sample binarized DataFrame for testing metadata functions."""
    return pd.DataFrame(
        {
            "sensitive_attr": [0, 1, 0, 1, 0, 0, 1, 0, 1, 0],
            "target": [1, 0, 1, 1, 0, 1, 0, 1, 0, 1],
            "numerical_feat": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
            "cat1": [1, 0, 1, 0, 1, 0, 0, 1, 0, 1],
            "cat2": [0, 1, 0, 1, 0, 1, 0, 0, 1, 0],
            "cat3": [0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        }
    )


@pytest.fixture
def col_na_indicator():
    """Create a sample NA indicator series."""
    return pd.Series(
        [False, False, True, False, False, False, False, False, False, False]
    )


def test_generate_general_descriptives(sample_df_raw, caplog):
    """Test the generate_general_descriptives function."""
    caplog.set_level(logging.WARNING)

    # Basic functionality test
    metadata = generate_general_descriptives(
        df_raw=sample_df_raw,
        sensitive_columns=["sensitive_attr"],
        target_column="target",
        target_lvl_good_value="good",
    )

    # Check returned metadata
    assert isinstance(metadata, dict)
    assert metadata["meta_pretrans_n_rows"] == 160
    assert metadata["meta_pretrans_n_cols"] == 5
    assert metadata["meta_pretrans_prop_NA_rows"] > 0
    assert metadata["meta_pretrans_prop_NA_cells"] > 0
    assert metadata["meta_pretrans_unique_group_counts_pre_agg"] == 2
    # High cardinality check
    assert "high_cardinality" in metadata["debug_meta_high_cardinality_strings"]

    # Test with incorrect column names
    with pytest.raises(AssertionError, match="Sensitive columns not found"):
        generate_general_descriptives(
            df_raw=sample_df_raw,
            sensitive_columns=["nonexistent_column"],
            target_column="target",
            target_lvl_good_value="good",
        )

    # Test with incorrect target column
    with pytest.raises(AssertionError, match="Target column not found"):
        generate_general_descriptives(
            df_raw=sample_df_raw,
            sensitive_columns=["sensitive_attr"],
            target_column="nonexistent_column",
            target_lvl_good_value="good",
        )

    # Test with missing target_lvl_good_value
    metadata = generate_general_descriptives(
        df_raw=sample_df_raw,
        sensitive_columns=["sensitive_attr"],
        target_column="target",
        target_lvl_good_value=None,
    )
    assert (
        "Missing information on which target value would be considered 'good'"
        in caplog.text
    )

    # Test with empty sensitive columns list
    metadata = generate_general_descriptives(
        df_raw=sample_df_raw,
        sensitive_columns=[],
        target_column="target",
        target_lvl_good_value="good",
    )
    assert "Missing information on sensitive columns" in caplog.text

    # Test with very small dataset
    small_df = sample_df_raw.iloc[:1]
    metadata = generate_general_descriptives(
        df_raw=small_df,
        sensitive_columns=["sensitive_attr"],
        target_column="target",
        target_lvl_good_value="good",
    )
    assert "Dataset has only 1 rows" in caplog.text


def test_generate_binarized_descriptives(sample_df_binarized, col_na_indicator, caplog):
    """Test the generate_binarized_descriptives function."""
    caplog.set_level(logging.WARNING)

    # Basic functionality test
    metadata = generate_binarized_descriptives(
        df=sample_df_binarized,
        sensitive_columns=["sensitive_attr"],
        target_column="target",
        col_na_indicator=col_na_indicator,
    )

    # Check returned metadata
    assert isinstance(metadata, dict)
    assert metadata["meta_n_rows"] == 10
    assert metadata["meta_n_cols"] == 6
    assert abs(metadata["meta_prev_sens_minority"] - 0.6) < 1e-10  # 6 out of 10 are '0'
    assert abs(metadata["meta_prev_sens_majority"] - 0.4) < 1e-10  # 4 out of 10 are '1'
    assert abs(metadata["meta_prev_sens_difference"] - 0.2) < 1e-10
    assert metadata["meta_prop_NA_sens_minority"] > 0

    # Test with multiple sensitive columns warning
    generate_binarized_descriptives(
        df=sample_df_binarized,
        sensitive_columns=["sensitive_attr", "cat1"],
        target_column="target",
        col_na_indicator=col_na_indicator,
    )
    assert "Only one sensitive column is supported" in caplog.text

    # Test with very small dataset
    small_df = sample_df_binarized.iloc[:1]
    metadata = generate_binarized_descriptives(
        df=small_df,
        sensitive_columns=["sensitive_attr"],
        target_column="target",
        col_na_indicator=col_na_indicator[:1],
    )
    assert "Dataset has only 1 rows" in caplog.text


def test_correlation_calculations(sample_df_binarized, col_na_indicator):
    """Test the correlation calculations in generate_binarized_descriptives."""
    # Create a dataset with known correlations
    df_correlated = sample_df_binarized.copy()
    df_correlated["numerical_feat"] = df_correlated[
        "sensitive_attr"
    ] * 10 + np.random.normal(0, 0.1, 10)

    metadata = generate_binarized_descriptives(
        df=df_correlated,
        sensitive_columns=["sensitive_attr"],
        target_column="target",
        col_na_indicator=col_na_indicator,
    )

    # The correlation should be very high
    assert metadata["meta_maximum_absolute_correlation"] > 0.95

    # Now create a dataset with negative correlation
    df_neg_correlated = sample_df_binarized.copy()
    df_neg_correlated["numerical_feat"] = (
        1 - df_neg_correlated["sensitive_attr"]
    ) * 10 + np.random.normal(0, 0.1, 10)

    metadata = generate_binarized_descriptives(
        df=df_neg_correlated,
        sensitive_columns=["sensitive_attr"],
        target_column="target",
        col_na_indicator=col_na_indicator,
    )

    # The correlation should be very negative
    assert metadata["meta_maximum_absolute_correlation"] > 0.95


def test_base_rate_calculations(col_na_indicator):
    """Test the base rate calculations in generate_binarized_descriptives."""
    # Create a dataset with known base rates
    df = pd.DataFrame(
        {
            "sensitive_attr": [0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
            "target": [1, 1, 1, 1, 0, 0, 0, 0, 0, 1],
            "feature1": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        }
    )

    metadata = generate_binarized_descriptives(
        df=df,
        sensitive_columns=["sensitive_attr"],
        target_column="target",
        col_na_indicator=col_na_indicator,
    )

    # Check base rates with floating point tolerance
    assert abs(metadata["meta_base_rate_target"] - 0.5) < 1e-10  # 5 out of 10
    assert (
        abs(metadata["meta_base_rate_target_sens_minority"] - 0.8) < 1e-10
    )  # 4 out of 5
    assert (
        abs(metadata["meta_base_rate_target_sens_majority"] - 0.2) < 1e-10
    )  # 1 out of 5
    assert abs(metadata["meta_base_rate_difference"] - 0.6) < 1e-10
    assert abs(metadata["meta_base_rate_ratio"] - 4.0) < 1e-10
