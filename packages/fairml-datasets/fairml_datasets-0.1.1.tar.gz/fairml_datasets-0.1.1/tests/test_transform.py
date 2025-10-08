"""
Tests for the transform module functions.
"""

import pytest
import pandas as pd
import numpy as np

from fairml_datasets.transform import (
    filter_columns,
    transform,
    PreprocessingInfo,
    limit_categorical_levels,
)


@pytest.fixture
def sample_df():
    """Create a sample DataFrame for testing transformations."""
    return pd.DataFrame(
        {
            "sensitive_1": ["A", "B", "A", "B", "A", "A", "A", np.nan],
            "sensitive_2": [1, 0, 1, 1, 0, 0, 0, 1],
            "feature_1": [10.5, 20.3, 15.7, 8.2, 12.1, np.nan, 9.8, 14.2],
            "feature_2": ["cat", "dog", "cat", "bird", "dog", "cat", "dog", "dog"],
            "feature_3": [1, 2, 3, 4, 5, 6, 7, 8],
            "target": ["good", "bad", "good", "good", "bad", "good", "good", "bad"],
            "extra_col": [100, 200, 300, 400, 500, 600, 700, 800],
        }
    )


def test_filter_columns(sample_df):
    """Test filtering columns in a DataFrame."""
    sensitive_columns = ["sensitive_1", "sensitive_2"]
    feature_columns = ["feature_1", "feature_2"]
    target_column = "target"

    filtered_df = filter_columns(
        sample_df,
        sensitive_columns=sensitive_columns,
        feature_columns=feature_columns,
        target_column=target_column,
    )

    # Check that only the specified columns are included
    expected_columns = set(sensitive_columns + feature_columns + [target_column])
    assert set(filtered_df.columns) == expected_columns

    # Check that the data remains intact
    for col in expected_columns:
        pd.testing.assert_series_equal(filtered_df[col], sample_df[col])


def test_transform_select_columns(sample_df):
    """Test column selection during transformation."""
    sensitive_columns = ["sensitive_1", "sensitive_2"]
    feature_columns = ["feature_1", "feature_2", "feature_3"]
    target_column = "target"

    # Test with typical_only (default)
    df_transformed, info = transform(
        sample_df,
        sensitive_columns=sensitive_columns,
        feature_columns=feature_columns,
        target_column=target_column,
        select_columns="typical_only",
    )

    # Should not include extra_col
    assert "extra_col" not in df_transformed.columns

    # Test with keep_all
    df_transformed_all, info_all = transform(
        sample_df,
        sensitive_columns=sensitive_columns,
        feature_columns=feature_columns,
        target_column=target_column,
        select_columns="keep_all",
    )

    # Should include extra_col
    assert "extra_col" in df_transformed_all.columns


def test_transform_na_numerical(sample_df):
    """Test handling of missing values in numerical columns."""
    sensitive_columns = [
        "sensitive_2"
    ]  # Using only numeric sensitive col for simplicity
    feature_columns = ["feature_1", "feature_3"]
    target_column = "target"

    # Test with impute_median (default)
    df_imputed, info_imputed = transform(
        sample_df,
        sensitive_columns=sensitive_columns,
        feature_columns=feature_columns,
        target_column=target_column,
        transform_na_numerical="impute_median",
    )

    # Check that the NA in feature_1 was replaced with median
    assert not df_imputed["feature_1"].isna().any()
    assert df_imputed["feature_1"].iloc[5] == sample_df["feature_1"].median()

    # Test with drop_rows
    df_drop_rows, info_drop_rows = transform(
        sample_df,
        sensitive_columns=sensitive_columns,
        feature_columns=feature_columns,
        target_column=target_column,
        transform_na_numerical="drop_rows",
    )

    # Check that the row with NA in feature_1 was dropped
    assert len(df_drop_rows) == len(sample_df) - 1
    assert not df_drop_rows["feature_1"].isna().any()

    # Test with drop_columns
    df_drop_cols, info_drop_cols = transform(
        sample_df,
        sensitive_columns=sensitive_columns,
        feature_columns=feature_columns,
        target_column=target_column,
        transform_na_numerical="drop_columns",
    )

    # Check that feature_1 was dropped
    assert "feature_1" not in df_drop_cols.columns
    assert "feature_3" in df_drop_cols.columns  # This column had no NAs


def test_transform_na_character(sample_df):
    """Test handling of missing values in character columns."""
    sensitive_columns = ["sensitive_1"]
    feature_columns = ["feature_2"]
    target_column = "target"

    # Test with new_value (default)
    df_new_value, info_new_value = transform(
        sample_df,
        sensitive_columns=sensitive_columns,
        feature_columns=feature_columns,
        target_column=target_column,
        transform_na_character="new_value",
        transform_sensitive_columns="intersection_binary",
        transform_sensitive_values="majority_minority",
    )

    # Check that the NA value was handled and sensitive_intersection was created
    # The original sensitive column is dropped after intersection_binary transformation
    assert "sensitive_intersection" in df_new_value.columns
    assert not df_new_value["sensitive_intersection"].isna().any()

    # Test with drop_rows
    df_drop_rows, info_drop_rows = transform(
        sample_df,
        sensitive_columns=sensitive_columns,
        feature_columns=feature_columns,
        target_column=target_column,
        transform_na_character="drop_rows",
        transform_sensitive_columns="intersection_binary",
        transform_sensitive_values="majority_minority",
    )

    # Check that the row with NA in sensitive_1 was dropped
    assert len(df_drop_rows) == len(sample_df) - 1
    assert "sensitive_intersection" in df_drop_rows.columns

    # Test with drop_columns - when columns are dropped, we can't use transform_sensitive_columns="none"
    # because the columns we're trying to transform will be gone
    df_drop_cols, info_drop_cols = transform(
        sample_df,
        sensitive_columns=["sensitive_2"],  # Use a column without NAs for this test
        feature_columns=feature_columns,
        target_column=target_column,
        transform_na_character="drop_columns",
    )

    # The sensitive_1 column should be dropped since it has NAs
    assert "sensitive_1" not in df_drop_cols.columns
    assert "feature_2" not in df_drop_cols.columns  # It's one-hot encoded
    assert any(col.startswith("feature_2_") for col in df_drop_cols.columns)


def test_transform_target(sample_df):
    """Test transformation of target column."""
    sensitive_columns = ["sensitive_2"]
    feature_columns = ["feature_3"]
    target_column = "target"

    # Test with majority_minority
    df_majority, info_majority = transform(
        sample_df,
        sensitive_columns=sensitive_columns,
        feature_columns=feature_columns,
        target_column=target_column,
        transform_target="majority_minority",
    )

    # Check that target was transformed to 0/1 with majority class as 1
    assert set(df_majority[target_column].unique()) == {0, 1}
    assert (
        df_majority[target_column].sum() > len(df_majority) / 2
    )  # Majority should be coded as 1

    # Test with good_bad
    df_good_bad, info_good_bad = transform(
        sample_df,
        sensitive_columns=sensitive_columns,
        feature_columns=feature_columns,
        target_column=target_column,
        transform_target="good_bad",
        target_lvl_good_bad="good",
    )

    # Check that target was transformed with "good" as 1 and "bad" as 0
    assert df_good_bad[target_column].iloc[0] == 1  # "good"
    assert df_good_bad[target_column].iloc[1] == 0  # "bad"


def test_transform_sensitive_values(sample_df):
    """Test transformation of sensitive attributes."""
    sensitive_columns = ["sensitive_1", "sensitive_2"]
    feature_columns = ["feature_3"]
    target_column = "target"

    # Before transformation, count occurrences of "A" in sensitive_1
    a_count = (sample_df["sensitive_1"] == "A").sum()

    df_transformed, info = transform(
        sample_df,
        sensitive_columns=sensitive_columns,
        feature_columns=feature_columns,
        target_column=target_column,
        transform_sensitive_columns="intersection_binary",
        transform_sensitive_values="majority_minority",
    )

    # When using intersection_binary (default), a new column should be created
    assert "sensitive_intersection" in df_transformed.columns
    assert set(df_transformed["sensitive_intersection"].unique()) == {0, 1}

    # Original sensitive columns should be dropped
    assert "sensitive_1" not in df_transformed.columns
    assert "sensitive_2" not in df_transformed.columns

    # Test without intersection
    df_no_intersection, info_no_intersection = transform(
        sample_df,
        sensitive_columns=sensitive_columns,
        feature_columns=feature_columns,
        target_column=target_column,
        transform_sensitive_columns="none",
        transform_sensitive_values="majority_minority",
    )

    # Original sensitive columns should be retained
    assert "sensitive_1" in df_no_intersection.columns
    assert "sensitive_2" in df_no_intersection.columns

    # Values should be transformed to 0/1
    assert set(df_no_intersection["sensitive_1"].unique()) == {0, 1}
    assert set(df_no_intersection["sensitive_2"].unique()) == {0, 1}

    # For sensitive_1, "A" was the majority class, so it should be coded as 1
    ones_count = df_no_intersection["sensitive_1"].sum()
    assert ones_count >= a_count - 1  # Account for the NA value


def test_transform_categorical(sample_df):
    """Test transformation of categorical features."""
    sensitive_columns = ["sensitive_2"]
    feature_columns = ["feature_2"]
    target_column = "target"

    df_transformed, info = transform(
        sample_df,
        sensitive_columns=sensitive_columns,
        feature_columns=feature_columns,
        target_column=target_column,
    )

    # Check that categorical column was one-hot encoded
    assert "feature_2_cat" in df_transformed.columns
    assert "feature_2_dog" in df_transformed.columns
    assert "feature_2_bird" in df_transformed.columns
    assert "feature_2" not in df_transformed.columns

    # Check that one-hot encoding was done correctly
    assert df_transformed["feature_2_cat"].iloc[0] == 1  # First row had "cat"
    assert df_transformed["feature_2_dog"].iloc[1] == 1  # Second row had "dog"
    assert df_transformed["feature_2_bird"].iloc[3] == 1  # Fourth row had "bird"


def test_transform_invalid_options(sample_df):
    """Test that invalid transformation options raise appropriate errors."""
    sensitive_columns = ["sensitive_1"]
    feature_columns = ["feature_1"]
    target_column = "target"

    # Test invalid select_columns
    with pytest.raises(ValueError, match="Unknown column filter option"):
        transform(
            sample_df,
            sensitive_columns=sensitive_columns,
            feature_columns=feature_columns,
            target_column=target_column,
            select_columns="invalid_option",
        )

    # Test invalid transform_na_numerical
    with pytest.raises(ValueError, match="Unknown NA transformation"):
        transform(
            sample_df,
            sensitive_columns=sensitive_columns,
            feature_columns=feature_columns,
            target_column=target_column,
            transform_na_numerical="invalid_option",
        )

    # Test invalid transform_na_character
    with pytest.raises(ValueError, match="Unknown NA transformation"):
        transform(
            sample_df,
            sensitive_columns=sensitive_columns,
            feature_columns=feature_columns,
            target_column=target_column,
            transform_na_character="invalid_option",
        )

    # Test invalid transform_target
    with pytest.raises(ValueError, match="Unknown label transformation"):
        transform(
            sample_df,
            sensitive_columns=sensitive_columns,
            feature_columns=feature_columns,
            target_column=target_column,
            transform_target="invalid_option",
        )

    # Test invalid transform_sensitive_columns
    with pytest.raises(ValueError, match="Unknown sensitive transformation"):
        transform(
            sample_df,
            sensitive_columns=sensitive_columns,
            feature_columns=feature_columns,
            target_column=target_column,
            transform_sensitive_columns="invalid_option",
        )

    # Test invalid transform_sensitive_values
    with pytest.raises(ValueError, match="Unknown sensitive transformation"):
        transform(
            sample_df,
            sensitive_columns=sensitive_columns,
            feature_columns=feature_columns,
            target_column=target_column,
            transform_sensitive_values="invalid_option",
        )

    # Test invalid transform_categorical
    with pytest.raises(ValueError, match="Unknown categorical transformation"):
        transform(
            sample_df,
            sensitive_columns=sensitive_columns,
            feature_columns=feature_columns,
            target_column=target_column,
            transform_categorical="invalid_option",
        )


def test_preprocessing_info(sample_df):
    """Test that PreprocessingInfo is correctly returned."""
    sensitive_columns = ["sensitive_1"]
    feature_columns = ["feature_1"]
    target_column = "target"

    df_transformed, info = transform(
        sample_df,
        sensitive_columns=sensitive_columns,
        feature_columns=feature_columns,
        target_column=target_column,
        transform_sensitive_columns="intersection_binary",
        transform_sensitive_values="majority_minority",
    )

    assert isinstance(info, PreprocessingInfo)
    assert info.sensitive_columns == ["sensitive_intersection"]
    assert len(info.col_na_indicator) == len(sample_df)
    assert info.col_na_indicator.iloc[5] == 1  # Row with NA in feature_1
    assert info.col_na_indicator.iloc[7] == 1  # Row with NA in sensitive_1


def test_limit_categorical_levels():
    """Test the limit_categorical_levels function."""
    # Create a sample DataFrame with categorical columns
    df = pd.DataFrame(
        {
            "cat1": ["A", "B", "C", "A", "B", "D", "E", "A", "B", "F"],
            "cat2": ["X", "Y", "X", "Z", "X", "Y", "X", "Z", "Y", "W"],
            "num": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        }
    )

    # Test limiting to top 2 categories
    result = limit_categorical_levels(df, ["cat1", "cat2"], 2)

    # For cat1, top 2 are A and B
    assert set(result["cat1"].unique()) == {"A", "B", "OTHER"}
    assert result["cat1"].value_counts()["OTHER"] == 4  # C, D, E, F -> OTHER

    # For cat2, top 2 are X and Y
    assert set(result["cat2"].unique()) == {"X", "Y", "OTHER"}
    assert result["cat2"].value_counts()["OTHER"] == 3  # Z, Z, W -> OTHER

    # Test with column not in DataFrame
    with pytest.raises(KeyError):
        limit_categorical_levels(df, ["cat1", "non_existent"], 2)

    # Test with max_unique larger than number of categories
    result = limit_categorical_levels(df, ["cat2"], 10)
    assert set(result["cat2"].unique()) == {"X", "Y", "Z", "W"}  # No change

    # Test with pandas Categorical column type
    df_cat = pd.DataFrame(
        {
            "cat_col": pd.Categorical(
                ["A", "B", "C", "A", "B", "D", "E", "A", "B", "F"]
            ),
            "num": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        }
    )

    result_cat = limit_categorical_levels(df_cat, ["cat_col"], 2)

    # Check that categorical type is preserved
    assert pd.api.types.is_categorical_dtype(result_cat["cat_col"])

    # Check that only top categories plus OTHER remain
    assert set(result_cat["cat_col"].unique()) == {"A", "B", "OTHER"}
    assert result_cat["cat_col"].value_counts()["OTHER"] == 4  # C, D, E, F -> OTHER


def test_transform_limit_categorical_levels(sample_df):
    """Test the limit_categorical_levels parameter in transform function."""
    sensitive_columns = ["sensitive_2"]
    feature_columns = ["feature_2"]
    target_column = "target"

    # Add more categories to feature_2 for better testing
    extended_df = sample_df.copy()
    extended_df["feature_2"] = [
        "cat",
        "dog",
        "cat",
        "bird",
        "dog",
        "fish",
        "snake",
        "hamster",
    ]

    # Transform with limit_categorical_levels = 2 (keep only top 2 categories)
    df_limited, info_limited = transform(
        extended_df,
        sensitive_columns=sensitive_columns,
        feature_columns=feature_columns,
        target_column=target_column,
        max_categorical_levels=2,
        transform_categorical="dummy",
    )

    # Check that only 3 dummy columns were created (cat, dog, OTHER)
    feature2_cols = [col for col in df_limited.columns if col.startswith("feature_2_")]
    assert set(feature2_cols) == {"feature_2_cat", "feature_2_dog", "feature_2_OTHER"}

    # Check that the values were encoded correctly
    assert df_limited["feature_2_cat"].iloc[0] == 1  # First row had "cat"
    assert df_limited["feature_2_dog"].iloc[1] == 1  # Second row had "dog"
    assert (
        df_limited["feature_2_OTHER"].iloc[5] == 1
    )  # Sixth row had "fish" which should be OTHER

    # Test without limiting
    df_unlimited, info_unlimited = transform(
        extended_df,
        sensitive_columns=sensitive_columns,
        feature_columns=feature_columns,
        target_column=target_column,
        transform_categorical="dummy",
    )

    # Check that all categories have dummy columns
    feature2_cols_unlimited = [
        col for col in df_unlimited.columns if col.startswith("feature_2_")
    ]
    assert set(feature2_cols_unlimited) == {
        "feature_2_cat",
        "feature_2_dog",
        "feature_2_bird",
        "feature_2_fish",
        "feature_2_snake",
        "feature_2_hamster",
    }


def test_transform_categorical_none(sample_df):
    """Test the 'none' option for transform_categorical."""
    sensitive_columns = ["sensitive_2"]
    feature_columns = ["feature_2", "feature_3"]
    target_column = "target"

    # Transform with transform_categorical="none"
    df_none, info_none = transform(
        sample_df,
        sensitive_columns=sensitive_columns,
        feature_columns=feature_columns,
        target_column=target_column,
        transform_categorical="none",
    )

    # Check that categorical column remains as is
    assert "feature_2" in df_none.columns
    assert set(df_none["feature_2"].unique()) == {"cat", "dog", "bird"}

    # The numerical columns should still be present
    assert "feature_3" in df_none.columns

    # Compare with dummy encoding
    df_dummy, info_dummy = transform(
        sample_df,
        sensitive_columns=sensitive_columns,
        feature_columns=feature_columns,
        target_column=target_column,
        transform_categorical="dummy",
    )

    # Check that dummy encoding creates the expected columns
    assert "feature_2" not in df_dummy.columns
    assert "feature_2_cat" in df_dummy.columns
    assert "feature_2_dog" in df_dummy.columns
    assert "feature_2_bird" in df_dummy.columns


def test_combined_limit_and_none_transform(sample_df):
    """Test combining limit_categorical_levels with transform_categorical='none'."""
    sensitive_columns = ["sensitive_2"]
    feature_columns = ["feature_2"]
    target_column = "target"

    # Add more categories to feature_2 for better testing
    extended_df = sample_df.copy()
    extended_df["feature_2"] = [
        "cat",
        "dog",
        "cat",
        "bird",
        "dog",
        "fish",
        "snake",
        "hamster",
    ]

    # Transform with limit_categorical_levels = 2 and transform_categorical="none"
    df_limited_none, info = transform(
        extended_df,
        sensitive_columns=sensitive_columns,
        feature_columns=feature_columns,
        target_column=target_column,
        max_categorical_levels=2,
        transform_categorical="none",
    )

    # Check that feature_2 is still a categorical column (not dummy encoded)
    assert "feature_2" in df_limited_none.columns

    # But it should only have 3 unique values (top 2 plus OTHER)
    assert set(df_limited_none["feature_2"].unique()) == {"cat", "dog", "OTHER"}

    # Verify the counts
    value_counts = df_limited_none["feature_2"].value_counts()
    assert value_counts["cat"] == 2
    assert value_counts["dog"] == 2
    assert value_counts["OTHER"] == 4  # bird, fish, snake, hamster
