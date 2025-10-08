import pytest
import pandas as pd
from pathlib import Path
from typing import List
from unittest.mock import patch, MagicMock
from fairml_datasets.processing import (
    ProcessingScript,
    LoadingScript,
    PreparationScript,
)
from fairml_datasets.dataset import Dataset


class SimpleProcessingScript(ProcessingScript):
    default_options = {"option1": "default1", "option2": 100}


class SimpleLoadingScript(LoadingScript):
    default_options = {"delimiter": ",", "skiprows": 0}

    def load(self, locations: List[Path]) -> pd.DataFrame:
        # Simulate loading with options
        data = {"col1": [1, 2, 3], "col2": ["a", "b", "c"]}

        # Apply any transformations based on options
        if self.options.get("skiprows", 0) > 0:
            # Simulate skipping rows by removing the first row
            for col in data:
                data[col] = data[col][self.options["skiprows"] :]

        return pd.DataFrame(data)


class SimplePreparationScript(PreparationScript):
    default_options = {"drop_na": False, "transform_col": None}

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        result = df.copy()

        # Apply options-based transformations
        if self.options.get("drop_na", False):
            result = result.dropna()

        if self.options.get("transform_col") is not None:
            col = self.options["transform_col"]
            if col in result.columns:
                result[col] = result[col] * 2

        return result


def test_processing_script_default_options():
    """Test that default options are set correctly in ProcessingScript."""
    script = SimpleProcessingScript()
    assert script.options == {"option1": "default1", "option2": 100}


def test_processing_script_override_options():
    """Test that options can be overridden in ProcessingScript."""
    script = SimpleProcessingScript(processing_options={"option1": "custom1"})
    assert script.options == {"option1": "custom1", "option2": 100}


def test_processing_script_add_options():
    """Test that new options can be added in ProcessingScript."""
    script = SimpleProcessingScript(processing_options={"option3": "new_option"})
    assert script.options == {
        "option1": "default1",
        "option2": 100,
        "option3": "new_option",
    }


def test_processing_script_no_default_options_warning():
    """Test warning when providing options but no defaults are defined."""

    class NoDefaultsScript(ProcessingScript):
        pass

    with pytest.warns(
        UserWarning, match="Processing options provided but no default options defined"
    ):
        NoDefaultsScript(processing_options={"option1": "value1"})


def test_loading_script_with_options():
    """Test that LoadingScript uses options when loading data."""
    # Default behavior
    script = SimpleLoadingScript()
    df = script.load([])
    assert len(df) == 3

    # With skiprows option
    script = SimpleLoadingScript(processing_options={"skiprows": 1})
    df = script.load([])
    assert len(df) == 2


def test_preparation_script_with_options():
    """Test that PreparationScript uses options when preparing data."""
    # Create a test dataframe
    test_df = pd.DataFrame({"col1": [1, 2, None], "col2": ["a", "b", "c"]})

    # Default behavior (no transformations)
    script = SimplePreparationScript()
    result = script.prepare(test_df)
    assert len(result) == 3
    # Use pd.isna to correctly compare None/NaN values
    assert pd.isna(result["col1"].iloc[2])
    assert result["col1"].iloc[0] == 1
    assert result["col1"].iloc[1] == 2

    # With drop_na option
    script = SimplePreparationScript(processing_options={"drop_na": True})
    result = script.prepare(test_df)
    assert len(result) == 2

    # With transform_col option
    script = SimplePreparationScript(processing_options={"transform_col": "col1"})
    result = script.prepare(test_df)
    assert result["col1"].iloc[0] == 2
    assert result["col1"].iloc[1] == 4
    assert pd.isna(result["col1"].iloc[2])


def test_loading_script_default_options():
    """Test that default options are set correctly in LoadingScript."""
    script = SimpleLoadingScript()
    assert script.options == {"delimiter": ",", "skiprows": 0}


def test_preparation_script_default_options():
    """Test that default options are set correctly in PreparationScript."""
    script = SimplePreparationScript()
    assert script.options == {"drop_na": False, "transform_col": None}


@patch("fairml_datasets.dataset.get_processing_script")
def test_processing_options_in_dataset_get_script(mock_get_processing_script):
    """Test that Dataset correctly passes processing options to the get_processing_script method."""
    # Set up mock
    mock_script_class = MagicMock()
    mock_get_processing_script.return_value = mock_script_class

    # Create test info Series
    info = pd.Series(
        {
            "dataset_name": "Test Dataset",
            "download_url": "http://example.com/test.csv",
            "format": "csv",
            "colnames": None,
            "is_zip": False,
            "custom_download": False,
            "typical_col_target": "target",
            "typical_col_sensitive": '{"sex": "sex"}',
            "typical_col_features": "-",
            "target_lvl_good": "1",
        },
        name="test_dataset",
    )

    # Create dataset and call get_processing_script
    dataset = Dataset(info)
    processing_options = {"option1": "value1", "option2": 42}
    dataset.get_processing_script(processing_options=processing_options)

    # Assert script was called with correct options
    mock_get_processing_script.assert_called_once()
    mock_script_class.assert_called_once_with(processing_options=processing_options)


@patch("fairml_datasets.dataset.get_processing_script")
@patch("fairml_datasets.dataset.download_dataset")
@patch("fairml_datasets.dataset.load_dataset")
def test_processing_options_in_dataset_load(
    mock_load_dataset, mock_download_dataset, mock_get_processing_script
):
    """Test that Dataset.load correctly passes processing options to processing scripts."""
    # Set up mocks
    mock_script_class = MagicMock()
    mock_script_instance = MagicMock()
    mock_get_processing_script.return_value = mock_script_class
    mock_script_class.return_value = mock_script_instance

    # Make sure our mock script acts like a PreparationScript
    mock_script_instance.prepare.return_value = pd.DataFrame({"col1": [1, 2, 3]})
    # Set up other mocks to make load() work
    mock_download_dataset.return_value = [Path("/fake/path/file.csv")]
    mock_load_dataset.return_value = pd.DataFrame({"col1": [4, 5, 6]})

    # Create test info Series
    info = pd.Series(
        {
            "dataset_name": "Test Dataset",
            "download_url": "http://example.com/test.csv",
            "format": "csv",
            "colnames": None,
            "is_zip": False,
            "custom_download": False,
            "typical_col_target": "target",
            "typical_col_sensitive": '{"sex": "sex"}',
            "typical_col_features": "-",
            "target_lvl_good": "1",
            "filename_raw": "test.csv",  # Added missing filename_raw field
        },
        name="test_dataset",
    )

    # Test with default preparation script
    dataset = Dataset(info)
    # Mock issubclass to return True for our mock being a PreparationScript
    with patch("fairml_datasets.dataset.isinstance", return_value=True):
        processing_options = {"option1": "value1", "option2": 42}
        dataset.load(
            stage="prepared", check_cache=False, processing_options=processing_options
        )

    # Assert script was initialized with correct options and prepare was called
    mock_script_class.assert_called_once_with(processing_options=processing_options)
    mock_script_instance.prepare.assert_called_once()


@patch("fairml_datasets.processing.datasets.get_processing_script")
def test_dataset_warns_on_unused_processing_options(mock_get_processing_script):
    """Test that Dataset warns when processing_options are provided but no script is available."""
    # Set up mock to return None (no script available)
    mock_get_processing_script.return_value = None

    # Create test info Series
    info = pd.Series(
        {
            "dataset_name": "Test Dataset",
            "download_url": None,
            "format": "csv",
            "colnames": None,
            "is_zip": False,
            "custom_download": False,
            "typical_col_target": "target",
            "typical_col_sensitive": '{"sex": "sex"}',
            "typical_col_features": "-",
            "target_lvl_good": "1",
        },
        name="test_dataset",
    )

    # Create dataset and call get_processing_script with options
    dataset = Dataset(info)

    # Should warn when processing_options are provided but no script exists
    with pytest.warns(
        UserWarning,
        match="Processing_options provided, but no processing script available",
    ):
        dataset.get_processing_script(processing_options={"option1": "value1"})
