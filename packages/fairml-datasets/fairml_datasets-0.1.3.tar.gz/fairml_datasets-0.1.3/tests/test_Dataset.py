import json
import pytest
from pathlib import Path
from unittest.mock import patch
import pandas as pd
from aif360.datasets import BinaryLabelDataset
from fairml_datasets import Dataset


@pytest.fixture
def mock_info_valid():
    return pd.Series(
        {
            "dataset_name": "test_dataset",
            "filename_raw": None,
            "download_url": "http://example.com/data.csv",
            "is_zip": False,
            "format": "csv",
            "colnames": None,
            "custom_download": False,
            "typical_col_sensitive": json.dumps({"sensitive_col": "sensitive_value"}),
            "typical_col_features": "-",
            "typical_col_target": "target_col",
            "target_lvl_good": "awesome",
            "default_scenario_sensitive_cols": "sensitive_col",
        },
        name="test_dataset",
    )


@pytest.fixture
def mock_df():
    return pd.DataFrame(
        {
            "col1": [1, None, 3],
            "sensitive_col": ["a", "b", "a"],
            "target_col": ["awesome", "horrible", "horrible"],
            "categorical_col": ["cat1", "cat2", "cat1"],
        }
    )


@pytest.fixture
def mock_info_metadata_error():
    return pd.Series(
        {
            "dataset_name": "test_dataset",
            "filename_raw": None,
            "download_url": "http://example.com/data.csv",
            "is_zip": False,
            "format": "csv",
            "colnames": None,
            "custom_download": False,
            "typical_col_target": "col1",
            "target_lvl_good": "1",
            "typical_col_sensitive": json.dumps(
                {"non_existent_col": "sensitive_value"}
            ),
            "typical_col_features": "-",
            "default_scenario_sensitive_cols": "non_existent_col",
        },
        name="test_dataset",
    )


@pytest.fixture
def mock_df_for_split(size=30):
    """Provides a DataFrame with sufficient samples for stratified splitting.
    Contains at least 2 samples for each combination of sensitive_col and target_col.

    Args:
        size: Number of rows to generate in the DataFrame (default: 30)
    """
    # Original patterns to repeat
    sensitive_pattern = [
        "a",
        "b",
        "a",
        "b",
        "a",
        "b",
        "a",
        "b",
    ]
    target_pattern = [
        "awesome",
        "awesome",
        "horrible",
        "horrible",
        "awesome",
        "awesome",
        "horrible",
        "horrible",
    ]
    categorical_pattern = [
        "cat1",
        "cat2",
        "cat1",
        "cat2",
        "cat1",
        "cat2",
        "cat1",
        "cat2",
    ]

    return pd.DataFrame(
        {
            "col1": list(range(1, size + 1)),
            "sensitive_col": [
                sensitive_pattern[i % len(sensitive_pattern)] for i in range(size)
            ],
            "target_col": [
                target_pattern[i % len(target_pattern)] for i in range(size)
            ],
            "categorical_col": [
                categorical_pattern[i % len(categorical_pattern)] for i in range(size)
            ],
        }
    )


@patch.object(Dataset, "load")
def test_generate_metadata_valid(mock_load, mock_info_valid):
    # Mock the load method to return a valid DataFrame
    mock_load.return_value = pd.DataFrame(
        {
            "col1": [1, 2, 3],
            "sensitive_col": ["a", "b", "c"],
            "target_col": ["awesome", "horrible", "horrible"],
        }
    )

    dataset = Dataset(info=mock_info_valid)
    metadata = dataset.generate_metadata()

    assert metadata["debug_meta_status"] == "OK"
    assert metadata["meta_n_rows"] == 3
    assert metadata["meta_n_cols"] == 3


@patch.object(Dataset, "load")
def test_generate_metadata_metadata_error(mock_load, mock_info_metadata_error):
    # Mock the load method to return a DataFrame missing the sensitive column
    mock_load.return_value = pd.DataFrame({"col1": [1, 2, 3]})

    dataset = Dataset(info=mock_info_metadata_error)
    metadata = dataset.generate_metadata()

    assert "debug_meta_error_message" in metadata
    assert (
        "Sensitive columns not found in dataset" in metadata["debug_meta_error_message"]
    )


@patch.object(Dataset, "load")
def test_preprocess_default(mock_load, mock_info_valid, mock_df):
    mock_load.return_value = mock_df

    dataset = Dataset(info=mock_info_valid)
    preprocessed_df, info = dataset.binarize(
        dataset.load(),
    )
    sensitive_columns = info.sensitive_columns

    assert "sensitive_intersection" in preprocessed_df.columns
    assert "target_col" in preprocessed_df.columns
    assert "categorical_col_cat1" in preprocessed_df.columns
    assert "categorical_col_cat2" in preprocessed_df.columns
    assert preprocessed_df["target_col"].tolist() == [1, 0, 0]
    assert "sensitive_intersection" in sensitive_columns


@patch.object(Dataset, "load")
def test_preprocess_impute_median(mock_load, mock_info_valid, mock_df):
    mock_load.return_value = mock_df

    dataset = Dataset(info=mock_info_valid)
    preprocessed_df, info = dataset.binarize(
        dataset.load(), transform_na_numerical="impute_median"
    )
    sensitive_columns = info.sensitive_columns

    assert "sensitive_intersection" in preprocessed_df.columns
    assert "target_col" in preprocessed_df.columns
    assert "col1" in preprocessed_df.columns
    assert preprocessed_df["col1"].tolist() == [1, 2, 3]
    assert "sensitive_intersection" in sensitive_columns


@patch.object(Dataset, "load")
def test_preprocess_drop_rows(mock_load, mock_info_valid, mock_df):
    mock_load.return_value = mock_df

    dataset = Dataset(info=mock_info_valid)
    preprocessed_df, info = dataset.binarize(
        dataset.load(),
        transform_na_numerical="drop_rows",
        transform_na_character="drop_rows",
    )
    sensitive_columns = info.sensitive_columns

    assert len(preprocessed_df) == 2
    assert "sensitive_intersection" in preprocessed_df.columns
    assert "target_col" in preprocessed_df.columns
    assert "sensitive_intersection" in sensitive_columns


@patch.object(Dataset, "load")
def test_preprocess_target_majority_minority(mock_load, mock_info_valid, mock_df):
    mock_load.return_value = mock_df

    dataset = Dataset(info=mock_info_valid)
    preprocessed_df, info = dataset.binarize(
        dataset.load(), transform_target="majority_minority"
    )
    sensitive_columns = info.sensitive_columns

    assert "sensitive_intersection" in preprocessed_df.columns
    assert "target_col" in preprocessed_df.columns
    assert preprocessed_df["target_col"].tolist() == [0, 1, 1]
    assert "sensitive_intersection" in sensitive_columns


@patch.object(Dataset, "load")
def test_preprocess_unknown_na_transform(mock_load, mock_info_valid, mock_df):
    mock_load.return_value = mock_df

    dataset = Dataset(info=mock_info_valid)
    with pytest.raises(ValueError, match="Unknown NA transformation"):
        dataset.transform(dataset.load(), transform_na_character="unknown")


@patch.object(Dataset, "load")
def test_preprocess_unknown_target_transform(mock_load, mock_info_valid, mock_df):
    mock_load.return_value = mock_df

    dataset = Dataset(info=mock_info_valid)
    with pytest.raises(ValueError, match="Unknown label transformation"):
        dataset.transform(dataset.load(), transform_target="unknown")


@patch.object(Dataset, "load")
def test_preprocess_unknown_sensitive_transform(mock_load, mock_info_valid, mock_df):
    mock_load.return_value = mock_df

    dataset = Dataset(info=mock_info_valid)
    with pytest.raises(ValueError, match="Unknown sensitive transformation"):
        dataset.transform(dataset.load(), transform_sensitive_columns="unknown")


@patch.object(Dataset, "load")
def test_preprocess_unknown_categorical_transform(mock_load, mock_info_valid, mock_df):
    mock_load.return_value = mock_df

    dataset = Dataset(info=mock_info_valid)
    with pytest.raises(ValueError, match="Unknown categorical transformation"):
        dataset.transform(dataset.load(), transform_categorical="unknown")


def test_generate_sensitive_combinations():
    info = pd.Series(
        {
            "dataset_name": "test_dataset",
            "typical_col_sensitive": json.dumps({"gender": "Gender", "race": "Race"}),
            "typical_col_target": "outcome",
            "target_lvl_good": "1",
            "default_scenario_sensitive_cols": "gender;race",
        }
    )
    dataset = Dataset(info=info)
    expected_combinations = [["gender"], ["race"], ["gender", "race"]]
    assert dataset.generate_sensitive_intersections() == expected_combinations


def test_generate_sensitive_combinations_three_attributes():
    info = pd.Series(
        {
            "dataset_name": "test_dataset",
            "typical_col_sensitive": json.dumps({"A": "A", "B": "B", "C": "C"}),
            "typical_col_target": "outcome",
            "target_lvl_good": "1",
            "default_scenario_sensitive_cols": "A;B;C",
        }
    )
    dataset = Dataset(info=info)
    expected_combinations = [
        ["A"],
        ["B"],
        ["C"],
        ["A", "B"],
        ["A", "C"],
        ["B", "C"],
        ["A", "B", "C"],
    ]
    assert dataset.generate_sensitive_intersections() == expected_combinations


def test_generate_sensitive_combinations_no_sensitive_columns():
    info = pd.Series(
        {
            "dataset_name": "test_dataset",
            "typical_col_sensitive": None,
            "typical_col_target": "outcome",
            "target_lvl_good": "1",
        }
    )
    dataset = Dataset(info=info)
    assert dataset.generate_sensitive_intersections() == []


@patch.object(Dataset, "load")
def test_split_dataset(mock_load, mock_info_valid, mock_df_for_split):
    mock_load.return_value = mock_df_for_split

    dataset = Dataset(info=mock_info_valid)

    # Basic split test
    splits = (0.6, 0.4)
    df_split = dataset.split_dataset(
        mock_df_for_split, splits=splits, seed=42, stratify=False
    )

    assert len(df_split) == 2
    assert len(df_split[0]) == 18
    assert len(df_split[1]) == 12

    # Test with stratification
    splits = (0.6, 0.4)
    df_split_stratified = dataset.split_dataset(
        mock_df_for_split, splits=splits, seed=42, stratify=True
    )

    assert len(df_split_stratified) == 2
    assert len(df_split_stratified[0]) == 18
    assert len(df_split_stratified[1]) == 12

    # Test with manual stratification column
    splits = (0.6, 0.4)
    df_split_manual = dataset.split_dataset(
        mock_df_for_split,
        splits=splits,
        seed=42,
        stratify=True,
        stratify_manual="categorical_col",
    )

    assert len(df_split_manual) == 2

    # Test with 3-way split
    splits = (0.4, 0.3, 0.3)
    df_split_three = dataset.split_dataset(
        mock_df_for_split, splits=splits, seed=42, stratify=True
    )

    assert len(df_split_three) == 3
    assert sum(len(split) for split in df_split_three) == len(mock_df_for_split)


@patch.object(Dataset, "load")
def test_split_dataset_validation(mock_load, mock_info_valid, mock_df_for_split):
    mock_load.return_value = mock_df_for_split
    dataset = Dataset(info=mock_info_valid)

    # Test with invalid splits (don't sum to 1)
    with pytest.raises(ValueError, match="Split values must sum to 1.0"):
        dataset.split_dataset(mock_df_for_split, splits=(0.3, 0.3))

    # Test with invalid stratify_manual column
    with pytest.raises(ValueError, match="Stratify column nonexistent not found"):
        dataset.split_dataset(
            mock_df_for_split,
            splits=(0.5, 0.5),
            stratify=True,
            stratify_manual="nonexistent",
        )


@patch.object(Dataset, "load")
def test_train_test_split(mock_load, mock_info_valid, mock_df_for_split):
    mock_load.return_value = mock_df_for_split
    dataset = Dataset(info=mock_info_valid)

    # Basic train-test split
    train, test = dataset.train_test_split(
        mock_df_for_split, test_size=0.4, seed=42, stratify=True
    )

    assert isinstance(train, pd.DataFrame)
    assert isinstance(test, pd.DataFrame)
    assert len(train) + len(test) == len(mock_df_for_split)
    assert len(test) == 12


@patch.object(Dataset, "load")
def test_train_test_val_split(mock_load, mock_info_valid, mock_df_for_split):
    mock_load.return_value = mock_df_for_split
    dataset = Dataset(info=mock_info_valid)

    # Basic train-val-test split with stratification
    train, val, test = dataset.train_test_val_split(
        mock_df_for_split, test_size=0.25, val_size=0.25, seed=42, stratify=True
    )

    assert isinstance(train, pd.DataFrame)
    assert isinstance(val, pd.DataFrame)
    assert isinstance(test, pd.DataFrame)
    assert len(train) + len(val) + len(test) == len(mock_df_for_split)
    assert len(train) == 15
    assert len(val) == 7
    assert len(test) == 8  # Slightly larger as it was the last rest


@patch.object(Dataset, "load")
def test_split_with_aif360_dataset(mock_load, mock_info_valid, mock_df_for_split):
    mock_load.return_value = mock_df_for_split

    # Create a mock for BinaryLabelDataset that will pass isinstance check
    dataset = Dataset(info=mock_info_valid)
    df_aif360 = dataset.to_aif360_BinaryLabelDataset()

    # Test the method with a real instance that isinstance can check correctly
    splits = dataset.split_dataset(
        df_aif360, splits=(0.6, 0.4), seed=42, stratify=False
    )

    assert len(splits) == 2
    assert isinstance(splits[0], BinaryLabelDataset)
    assert isinstance(splits[1], BinaryLabelDataset)
    assert splits[0].features.shape[0] == 18
    assert splits[1].features.shape[0] == 12


@patch.object(Dataset, "load")
def test_train_test_split_reproducibility(
    mock_load, mock_info_valid, mock_df_for_split
):
    mock_load.return_value = mock_df_for_split
    dataset = Dataset(info=mock_info_valid)

    # First split with seed 42
    train1, test1 = dataset.train_test_split(
        mock_df_for_split, test_size=0.4, seed=42, stratify=True
    )

    # Second split with the same seed should be identical
    train2, test2 = dataset.train_test_split(
        mock_df_for_split, test_size=0.4, seed=42, stratify=True
    )

    # Verify splits are identical
    pd.testing.assert_frame_equal(train1, train2)
    pd.testing.assert_frame_equal(test1, test2)

    # Split with a different seed
    train3, test3 = dataset.train_test_split(
        mock_df_for_split, test_size=0.4, seed=24, stratify=True
    )

    # Verify splits are different
    assert not train1.equals(train3)
    assert not test1.equals(test3)


def test_realworld_synth_dataset_load():
    dataset = Dataset.from_id("synth")
    df = dataset.load()

    assert isinstance(df, pd.DataFrame)
    assert not df.empty


def test_realworld_synth_example_split():
    # Get the dataset
    dataset = Dataset.from_id("synth")

    # Load as pandas DataFrame
    df = dataset.load()  # or df = dataset.to_pandas()
    print(f"Dataset shape: {df.shape}")

    # Get the target column
    target_column = dataset.get_target_column()
    print(f"Target column: {target_column}")

    # Get sensitive attributes (before transformation)
    sensitive_columns_org = dataset.sensitive_columns

    # Transform to e.g. impute missing data
    df_transformed, transformation_info = dataset.transform(df)
    # Sensitive columns may change due to transformation
    sensitive_columns = transformation_info.sensitive_columns

    # Split into train and test sets
    train_df, test_df = dataset.train_test_split(df, test_size=0.3)

    # Assertions to verify the operations work correctly
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert target_column is not None
    assert isinstance(sensitive_columns_org, list)
    assert isinstance(df_transformed, pd.DataFrame)
    assert transformation_info is not None
    assert isinstance(sensitive_columns, list)
    assert isinstance(train_df, pd.DataFrame)
    assert isinstance(test_df, pd.DataFrame)
    assert len(train_df) + len(test_df) == len(df)
    assert (len(test_df) - int(len(df) * 0.3)) in (-1, 0, 1)


def test_realworld_synth_dataset_train_test_val_split():
    dataset = Dataset.from_id("synth")

    # Load the dataset
    df = dataset.load()

    # Check sensitive attributes
    print(f"Sensitive columns: {dataset.sensitive_columns}")

    # Transform the dataset
    df_transformed, info = dataset.transform(df)

    # Create train/test/validation split
    df_train, df_test, df_val = dataset.train_test_val_split(df_transformed)

    # Assertions to verify the operations work correctly
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert isinstance(dataset.sensitive_columns, list)
    assert isinstance(df_transformed, pd.DataFrame)
    assert info is not None
    assert isinstance(df_train, pd.DataFrame)
    assert isinstance(df_test, pd.DataFrame)
    assert isinstance(df_val, pd.DataFrame)
    assert len(df_train) + len(df_test) + len(df_val) == len(df_transformed)
    # Verify that each split is non-empty
    assert len(df_train) > 0
    assert len(df_test) > 0
    assert len(df_val) > 0
    # Verify that all splits have the same columns
    assert list(df_train.columns) == list(df_transformed.columns)
    assert list(df_test.columns) == list(df_transformed.columns)
    assert list(df_val.columns) == list(df_transformed.columns)


@patch(
    "fairml_datasets.file_handling.DATASET_CACHE_DIR", Path("tests/mock_cache/datasets")
)
@patch("fairml_datasets.dataset.DATASET_CACHE_DIR", Path("tests/mock_cache/datasets"))
def test_realworld_folktables_acsincome_small_dataset_train_test_val_split():
    dataset = Dataset.from_id("folktables_acsincome_small")

    # Load the dataset
    df = dataset.load()

    # Transform the dataset
    df_transformed, info = dataset.transform(df)

    # Create train/test/validation split
    df_train, df_test, df_val = dataset.train_test_val_split(df_transformed)

    # Assertions to verify the operations work correctly
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert isinstance(dataset.sensitive_columns, list)
    assert isinstance(df_transformed, pd.DataFrame)
    assert info is not None
    assert isinstance(df_train, pd.DataFrame)
    assert isinstance(df_test, pd.DataFrame)
    assert isinstance(df_val, pd.DataFrame)
    assert len(df_train) + len(df_test) + len(df_val) == len(df_transformed)
    # Verify that each split is non-empty
    assert len(df_train) > 0
    assert len(df_test) > 0
    assert len(df_val) > 0
    # Verify that all splits have the same columns
    assert list(df_train.columns) == list(df_transformed.columns)
    assert list(df_test.columns) == list(df_transformed.columns)
    assert list(df_val.columns) == list(df_transformed.columns)
