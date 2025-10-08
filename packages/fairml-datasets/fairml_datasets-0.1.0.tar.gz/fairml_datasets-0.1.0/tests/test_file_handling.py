"""
Tests for the file_handling module functions.
"""

import pytest
import pandas as pd
import zipfile
import tempfile
import shutil
import os
from pathlib import Path
from unittest.mock import patch

from fairml_datasets.file_handling import (
    load_text_file,
    search_zip_archive,
    search_nested_zip_archives,
    extract_result,
    load_dataset,
    make_temp_directory,
)


@pytest.fixture
def mock_csv_content():
    """Create mock CSV content for testing."""
    return "col1,col2,col3\n1,2,3\n4,5,6"


@pytest.fixture
def mock_tsv_content():
    """Create mock TSV content for testing."""
    return "col1\tcol2\tcol3\n1\t2\t3\n4\t5\t6"


@pytest.fixture
def temp_zip_file():
    """Create a temporary zip file with test files."""
    temp_dir = tempfile.mkdtemp()
    zip_path = Path(temp_dir) / "test.zip"

    # Create files to add to the zip
    test_file_path = Path(temp_dir) / "test.txt"
    nested_zip_dir = Path(temp_dir) / "nested"
    nested_zip_dir.mkdir(exist_ok=True)
    nested_zip_path = nested_zip_dir / "nested.zip"

    # Create content for test file
    with open(test_file_path, "w") as f:
        f.write("test content")

    # Create nested zip with a test file
    with zipfile.ZipFile(nested_zip_path, "w") as nested_zip:
        nested_zip.writestr("nested_test.txt", "nested test content")

    # Create main zip with test file and nested zip
    with zipfile.ZipFile(zip_path, "w") as test_zip:
        test_zip.write(test_file_path, arcname="test.txt")
        test_zip.write(nested_zip_path, arcname="nested.zip")

    yield zip_path

    # Cleanup
    shutil.rmtree(temp_dir)


def test_make_temp_directory():
    """Test the make_temp_directory context manager."""
    with make_temp_directory() as temp_dir:
        assert temp_dir.exists()
        assert temp_dir.is_dir()

        # Create a file in the temp directory
        test_file = temp_dir / "test.txt"
        with open(test_file, "w") as f:
            f.write("test")

        assert test_file.exists()

    # After exiting the context, the directory should be deleted
    assert not temp_dir.exists()


def test_load_text_file(mock_csv_content):
    """Test loading a text file with specified delimiter."""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(mock_csv_content.encode())
        tmp_path = Path(tmp.name)

    try:
        # Test basic loading with comma delimiter
        df = load_text_file(tmp_path, delimiter=",", verify_colnames=False)
        assert isinstance(df, pd.DataFrame)
        assert df.shape == (2, 3)
        assert list(df.columns) == ["col1", "col2", "col3"]

        # Test with specified column names
        colnames = ["a", "b", "c"]
        df = load_text_file(
            tmp_path, delimiter=",", colnames=colnames, verify_colnames=True
        )
        assert list(df.columns) == colnames
    finally:
        os.unlink(tmp_path)


def test_load_text_file_verify_colnames_mismatch(mock_csv_content):
    """Test that verify_colnames raises an assertion error when column counts don't match."""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(mock_csv_content.encode())
        tmp_path = Path(tmp.name)

    try:
        # Test with too many column names
        colnames = ["a", "b", "c", "d"]
        with pytest.raises(AssertionError):
            load_text_file(
                tmp_path, delimiter=",", colnames=colnames, verify_colnames=True
            )
    finally:
        os.unlink(tmp_path)


def test_search_zip_archive(temp_zip_file):
    """Test searching for files in a zip archive."""
    # Test exact match
    results = search_zip_archive(temp_zip_file, "test.txt")
    assert len(results) == 1
    zip_file, file_name = results[0]
    assert isinstance(zip_file, zipfile.ZipFile)
    assert file_name == "test.txt"

    # Test partial match
    results = search_zip_archive(temp_zip_file, "test")
    assert len(results) == 1

    # Test regex search
    results = search_zip_archive(temp_zip_file, "^test.*txt$", regex=True)
    assert len(results) == 1

    # Test no match
    results = search_zip_archive(temp_zip_file, "nonexistent")
    assert len(results) == 0


def test_search_nested_zip_archives(temp_zip_file):
    """Test searching for files in nested zip archives."""
    results = search_nested_zip_archives(temp_zip_file, "nested_test.txt")
    assert len(results) == 1
    zip_file, file_name = results[0]
    assert isinstance(zip_file, zipfile.ZipFile)
    assert file_name == "nested_test.txt"


def test_extract_result(temp_zip_file):
    """Test extracting a file from a zip archive."""
    with make_temp_directory() as temp_dir:
        # Find the test.txt file
        results = search_zip_archive(temp_zip_file, "test.txt")
        assert len(results) == 1

        # Extract to the default location
        extracted_path = extract_result(results[0], temp_dir)
        assert extracted_path.exists()
        assert extracted_path.name == "test.txt"

        # Extract to a specific location
        target_file = temp_dir / "renamed.txt"
        extracted_path = extract_result(results[0], temp_dir, target_file)
        assert extracted_path.exists()
        assert extracted_path.name == "renamed.txt"
        assert extracted_path == target_file


def test_load_dataset_csv(mock_csv_content):
    """Test loading a CSV dataset."""
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        tmp.write(mock_csv_content.encode())
        tmp_path = Path(tmp.name)

    try:
        df = load_dataset(tmp_path, "csv")
        assert isinstance(df, pd.DataFrame)
        assert df.shape == (2, 3)
        assert list(df.columns) == ["col1", "col2", "col3"]
    finally:
        os.unlink(tmp_path)


def test_load_dataset_tsv(mock_tsv_content):
    """Test loading a TSV dataset."""
    with tempfile.NamedTemporaryFile(suffix=".tsv", delete=False) as tmp:
        tmp.write(mock_tsv_content.encode())
        tmp_path = Path(tmp.name)

    try:
        df = load_dataset(tmp_path, "tsv")
        assert isinstance(df, pd.DataFrame)
        assert df.shape == (2, 3)
        assert list(df.columns) == ["col1", "col2", "col3"]
    finally:
        os.unlink(tmp_path)


@patch("pandas.read_excel")
def test_load_dataset_excel(mock_read_excel):
    """Test loading an Excel dataset."""
    mock_df = pd.DataFrame({"col1": [1, 4], "col2": [2, 5], "col3": [3, 6]})
    mock_read_excel.return_value = mock_df

    df = load_dataset(Path("dummy.xlsx"), "xlsx")
    mock_read_excel.assert_called_once()
    assert df.equals(mock_df)


def test_load_dataset_unsupported_format():
    """Test that unsupported formats raise NotImplementedError."""
    with pytest.raises(
        NotImplementedError, match="Loading of 'xyz' files is not yet implemented"
    ):
        load_dataset(Path("dummy.xyz"), "xyz")


def test_load_dataset_unsupported_modifier():
    """Test that unsupported modifiers raise NotImplementedError."""
    with pytest.raises(NotImplementedError, match="Modifier 'abc' is not supported"):
        load_dataset(Path("dummy.csv"), "csv--abc")


def test_load_dataset_compressed():
    """Test loading a compressed dataset."""
    # Since actual compression testing would be complex, we'll mock the load_text_file function
    with patch("fairml_datasets.file_handling.load_text_file") as mock_load_text_file:
        mock_df = pd.DataFrame({"col1": [1, 4], "col2": [2, 5], "col3": [3, 6]})
        mock_load_text_file.return_value = mock_df

        df = load_dataset(Path("dummy.csv.gz"), "csv--gz")

        # Check that load_text_file was called with the right compression argument
        mock_load_text_file.assert_called_once()
        args, kwargs = mock_load_text_file.call_args
        assert kwargs["compression"] == "gzip"
        assert df.equals(mock_df)
