import pytest
from unittest.mock import patch
import pandas as pd
from fairml_datasets import Datasets
from fairml_datasets.dataset import Dataset


@pytest.fixture
def mock_annotations_data():
    """Mock dataframe returned by annotations.load()"""
    # Create a mock DataFrame with a few datasets
    df = pd.DataFrame(
        {
            "dataset_name": ["dataset1", "dataset2", "dataset3", "dataset4"],
            "is_large": [False, True, False, True],
        },
        index=["dataset1", "dataset2", "dataset3", "dataset4"],
    )
    return df


@patch("fairml_datasets.datasets.annotations.load")
def test_datasets_init_default(mock_load, mock_annotations_data):
    """Test initialization with default parameters."""
    mock_load.return_value = mock_annotations_data

    datasets = Datasets()

    # Should include only non-large datasets
    assert len(datasets) == 2
    assert "dataset1" in datasets.get_ids()
    assert "dataset3" in datasets.get_ids()
    assert "dataset2" not in datasets.get_ids()
    assert "dataset4" not in datasets.get_ids()


@patch("fairml_datasets.datasets.annotations.load")
def test_datasets_init_include_large(mock_load, mock_annotations_data):
    """Test initialization with large datasets included."""
    mock_load.return_value = mock_annotations_data

    datasets = Datasets(inclue_large_datasets=True)

    # Should include all datasets
    assert len(datasets) == 4
    assert set(datasets.get_ids()) == {"dataset1", "dataset2", "dataset3", "dataset4"}


@patch("fairml_datasets.datasets.annotations.load")
def test_datasets_init_with_ids(mock_load, mock_annotations_data):
    """Test initialization with specific dataset IDs."""
    mock_load.return_value = mock_annotations_data

    datasets = Datasets(ids=["dataset1", "dataset2"])

    # Should include only the specified datasets
    assert len(datasets) == 2
    assert set(datasets.get_ids()) == {"dataset1", "dataset2"}


@patch("fairml_datasets.datasets.annotations.load")
def test_datasets_init_with_df_info(mock_load):
    """Test initialization with provided df_info."""
    # Create a custom df_info
    df_info = pd.DataFrame(
        {
            "dataset_name": ["custom1", "custom2"],
            "is_large": [False, False],
        },
        index=["custom1", "custom2"],
    )

    datasets = Datasets(df_info=df_info)

    # Should use the provided df_info
    assert len(datasets) == 2
    assert set(datasets.get_ids()) == {"custom1", "custom2"}

    # The load method should not have been called
    mock_load.assert_not_called()


def test_datasets_getitem():
    """Test getting datasets by index and id."""
    # Create a custom df_info
    df_info = pd.DataFrame(
        {
            "dataset_name": ["dataset1", "dataset2"],
            "is_large": [False, False],
        },
        index=["dataset1", "dataset2"],
    )

    datasets = Datasets(df_info=df_info)

    # Get by integer index
    dataset0 = datasets[0]
    assert isinstance(dataset0, Dataset)
    assert dataset0.info.name == "dataset1"

    # Get by id
    dataset_by_id = datasets["dataset2"]
    assert isinstance(dataset_by_id, Dataset)
    assert dataset_by_id.info.name == "dataset2"

    # Test wrong type
    with pytest.raises(AssertionError, match="index must be a string or integer"):
        datasets[1.5]


def test_datasets_iteration():
    """Test iterating through datasets."""
    # Create a custom df_info
    df_info = pd.DataFrame(
        {
            "dataset_name": ["dataset1", "dataset2", "dataset3"],
            "is_large": [False, False, False],
        },
        index=["dataset1", "dataset2", "dataset3"],
    )

    datasets = Datasets(df_info=df_info)

    # Test iteration
    count = 0
    for dataset in datasets:
        assert isinstance(dataset, Dataset)
        count += 1

    assert count == 3
