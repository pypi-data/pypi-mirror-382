"""
Tests for the Scenario class.
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

from fairml_datasets.scenario import Scenario
from fairml_datasets.dataset import Dataset


@pytest.fixture
def mock_dataset():
    """Create a mock dataset for testing."""
    mock = MagicMock(spec=Dataset)
    # Create a pd.Series for the info attribute
    mock.info = pd.Series(
        {
            "dataset_id": "test_dataset",
            "dataset_name": "Test Dataset",
            "sensitive_cols": "original_sensitive_col_1;original_sensitive_col_2",
        }
    )
    mock.sensitive_columns = ["original_sensitive_col_1", "original_sensitive_col_2"]
    return mock


@pytest.fixture
def mock_dataset_class():
    """Create a mock Dataset class with from_id method."""
    with patch("fairml_datasets.scenario.Dataset") as mock_dataset_cls:
        mock_instance = MagicMock(spec=Dataset)
        # Create a pd.Series for the info attribute
        mock_instance.info = pd.Series(
            {
                "dataset_id": "test_dataset_id",
                "dataset_name": "Test Dataset From ID",
                "sensitive_cols": "original_sensitive_col_1;original_sensitive_col_2",
            }
        )
        mock_instance.sensitive_columns = [
            "original_sensitive_col_1",
            "original_sensitive_col_2",
        ]
        mock_dataset_cls.from_id.return_value = mock_instance
        yield mock_dataset_cls


def test_scenario_init_with_dataset_instance(mock_dataset):
    """Test initializing a Scenario with a Dataset instance."""
    new_sensitive_columns = ["new_sensitive_col_1", "new_sensitive_col_2"]
    scenario = Scenario(mock_dataset, sensitive_columns=new_sensitive_columns)

    # Check that the Scenario was initialized correctly
    assert scenario._sensitive_columns == new_sensitive_columns
    assert scenario.info.equals(mock_dataset.info)


def test_scenario_init_with_dataset_id(mock_dataset_class):
    """Test initializing a Scenario with a dataset ID string."""
    dataset_id = "test_dataset_id"
    new_sensitive_columns = ["new_sensitive_col_1", "new_sensitive_col_2"]

    # Fix the isinstance check in Scenario's __init__ method
    with patch("fairml_datasets.scenario.isinstance", return_value=False):
        scenario = Scenario(dataset_id, sensitive_columns=new_sensitive_columns)

    # Check that Dataset.from_id was called with the correct ID
    mock_dataset_class.from_id.assert_called_once_with(dataset_id)

    # Check that the Scenario was initialized correctly
    assert scenario._sensitive_columns == new_sensitive_columns
    assert scenario.info.equals(mock_dataset_class.from_id.return_value.info)


def test_scenario_sensitive_columns_override():
    """Test that Scenario overrides the sensitive_columns property from Dataset."""

    # Create a minimal concrete Dataset subclass for testing
    class TestDataset(Dataset):
        def __init__(self):
            # Create a pd.Series for info instead of a dict
            self.info = pd.Series(
                {
                    "dataset_id": "test_dataset",
                    "dataset_name": "Test Dataset",
                    "sensitive_cols": "original_sensitive_col_1;original_sensitive_col_2",
                }
            )
            self._sensitive_columns = None

        @property
        def sensitive_columns(self):
            return ["original_sensitive_col_1", "original_sensitive_col_2"]

    # Create a test dataset and scenario
    test_dataset = TestDataset()
    new_sensitive_columns = ["new_sensitive_col_1", "new_sensitive_col_2"]

    # Initialize the Scenario with the dataset
    scenario = Scenario(test_dataset, sensitive_columns=new_sensitive_columns)

    # Verify that scenario.sensitive_columns returns the new columns
    assert scenario._sensitive_columns == new_sensitive_columns
