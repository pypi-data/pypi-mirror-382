"""
Utilities for downloading, extracting, and loading dataset files.

This module provides functions to handle file operations related to fairness datasets,
including downloading from URLs, extracting from zip archives, and loading data in
various formats into pandas DataFrames.
"""

import tempfile
import contextlib
import shutil
from pathlib import Path
from urllib.request import urlretrieve
import zipfile
import re
import pandas as pd
import numpy as np
from typing import List, Tuple, Optional, Generator
import logging
from scipy.io.arff import loadarff

ZipSearchResult = Tuple[zipfile.ZipFile, str]

logger = logging.getLogger(__name__)

ROOT_CACHE_DIR = Path("cache")
DATASET_CACHE_DIR = ROOT_CACHE_DIR / "datasets"
DOWNLOAD_CACHE_DIR = ROOT_CACHE_DIR / "downloads"


@contextlib.contextmanager
def make_temp_directory() -> Generator[Path, None, None]:
    """
    Context manager that creates a temporary directory and cleans it up when done.

    Yields:
        Path: Path to the temporary directory
    """
    temp_dir = tempfile.mkdtemp()
    try:
        yield Path(temp_dir)
    finally:
        shutil.rmtree(temp_dir)


def _download_file(url: str, destination: Path):
    """
    Downloads a file from the internet to a destination on the local drive.

    Args:
        url: URL of the file to download
        destination: Local path where the file will be saved
    """
    logger.info(f"Downloading file from internet ({url}).")

    urlretrieve(url, destination)


def download_dataset(
    urls: List[str],
    filenames: List[str],
    target_directory: Path,
    is_zip: bool,
    read_cache: bool = True,
) -> List[Path]:
    """
    Downloads a dataset and optionally places it in cache.

    Args:
        urls: List of URLs to download from
        filenames: List of filenames to save as
        target_directory: Directory to save files to
        is_zip: Whether the download is a zip archive
        read_cache: Whether to use cached files if available

    Returns:
        List[Path]: Paths to the downloaded files

    Raises:
        AssertionError: If parameters are invalid
        ValueError: If matching files cannot be found in zip archives
    """
    logger.debug(f"Retrieving dataset from {urls} (filenames: {filenames}).")

    if isinstance(is_zip, np.bool_) or isinstance(is_zip, np.bool):
        is_zip = bool(is_zip)
    assert isinstance(is_zip, bool), "is_zip must be a boolean"
    assert len(filenames) > 0, "At least one data filename must be specified."
    assert (
        is_zip or len(filenames) == len(urls)
    ), f"The number of filenames has to match the number of URLs for non-zip archives. ({filenames}|{urls})"

    with make_temp_directory() as temp_dir:

        def filename_to_path(filename):
            return target_directory / filename

        filepaths = [filename_to_path(f) for f in filenames]

        # Check whether the file(s) might already be in the cache
        if read_cache and all([f.exists() for f in filepaths]):
            logger.debug("Cache hit, skipping download.")
            return filepaths

        if not is_zip:
            logger.debug("Downloading files directly.")
            # Download files directly from their URLs
            for url, filepath in zip(urls, filepaths):
                _download_file(url, filepath)

        else:
            # Download is a zip-directory, so we'll have to find the correct file(s)
            logger.debug("Extracting files from zip.")

            # Only a single URL is supported for zip files
            assert (not is_zip) or len(
                urls
            ) == 1, "Exactly one URL must be specified for zip archives."
            url = urls[0]

            # Download the zip file
            zip_filename = f"{hash(url)}.zip"
            zip_path = temp_dir / zip_filename
            _download_file(url, zip_path)

            # Extract all files
            for filename in filenames:
                target_file = filename_to_path(filename)

                results = search_zip_archive(zip_path, filename)
                if len(results) == 0:
                    results = search_nested_zip_archives(zip_path, filename)

                if len(results) != 1:
                    raise ValueError(
                        f"There are {len(results)} files matching "
                        f"{filename} in the zip archive (incl. nested) at {url}."
                    )

                # Extract the correct file from the zip archive
                matching_result = results[0]
                extract_result(matching_result, target_directory, target_file)

        assert all(
            [f.exists() for f in filepaths]
        ), "Not all files were downloaded / extracted successfully."

        return filepaths


def load_text_file(
    location: Path,
    delimiter: str,
    compression: Optional[str] = None,
    colnames: Optional[List[str]] = None,
    verify_colnames: bool = False,
) -> pd.DataFrame:
    """
    Loads a text file (CSV, TSV, etc.) with the specified delimiter.

    Args:
        location: Path to the file
        delimiter: Delimiter character used in the file
        compression: Compression type (e.g., 'gzip')
        colnames: List of column names
        verify_colnames: If True, verifies that the number of column names matches the number of columns in the file

    Returns:
        pd.DataFrame: DataFrame containing the loaded data

    Raises:
        AssertionError: If the number of column names does not match the number of columns in the file
    """
    # Determine header setting based on presence of column names
    header = 0 if colnames is not None else "infer"

    na_values = ["?"]

    # If we need to verify column names, check the file structure
    if verify_colnames and colnames is not None:
        # Read a small sample to detect columns
        sample_df = pd.read_table(
            location, delimiter=delimiter, compression=compression, header=None, nrows=5
        )
        num_columns = len(sample_df.columns)

        assert len(colnames) == num_columns, (
            f"Number of column names ({len(colnames)}) doesn't match "
            f"the number of columns in the file ({num_columns})."
        )

    # Read the actual file with specified options
    return pd.read_table(
        location,
        delimiter=delimiter,
        compression=compression,
        names=colnames,
        header=header,
        na_values=na_values,
    )


def load_dataset(
    location: Path,
    data_format: str,
    colnames: Optional[str] = None,
    verify_colnames: bool = True,
) -> pd.DataFrame:
    """
    Loads a dataset from a location on the local drive.

    Args:
        location: Path to the file
        data_format: Format of the data file (e.g., 'csv', 'tsv', 'arff', 'xls', 'xlsx')
        colnames: Semicolon-separated string of column names
        verify_colnames: Whether to verify the column names

    Returns:
        pd.DataFrame: DataFrame containing the loaded data

    Raises:
        NotImplementedError: If the data format or modifier is not supported
    """
    logger.debug(
        f"Loading dataset from {location} (data_format: {data_format}, colnames: {colnames})."
    )

    # Split colnames
    if colnames is not None:
        colnames = colnames.split(";")
    else:
        colnames = None

    # Support format modifiers
    if "--" in data_format:
        data_format, modifier = data_format.split("--")
    else:
        modifier = None

    if modifier == "gz":
        compression = "gzip"
    elif modifier is None:
        compression = None
    else:
        raise NotImplementedError(f"Modifier '{modifier}' is not supported.")

    # Handle text file formats
    text_file_delimiter = None
    if data_format == "csv":
        text_file_delimiter = ","
    if data_format == "space-separated":
        text_file_delimiter = " "
    if data_format == "semicolon-separated":
        text_file_delimiter = ";"
    if data_format == "tsv":
        text_file_delimiter = "\t"

    if text_file_delimiter is not None:
        return load_text_file(
            location,
            delimiter=text_file_delimiter,
            compression=compression,
            colnames=colnames,
            verify_colnames=verify_colnames,
        )

    # Handle other file formats
    if data_format == "arff":
        data, meta = loadarff(location)
        df = pd.DataFrame(data)
        df = df.map(lambda x: x.decode("utf-8") if isinstance(x, bytes) else x)
        return df
    if data_format == "xls" or data_format == "xlsx":
        if compression is not None:
            raise NotImplementedError(
                f"Compression '{compression}' is not supported for Excel files."
            )
        return pd.read_excel(location, sheet_name=0)
    else:
        raise NotImplementedError(
            f"Loading of '{data_format}' files is not yet implemented."
        )


def search_zip_archive(
    zip_path: Path, search_pattern: str, regex: bool = False
) -> List[ZipSearchResult]:
    """
    Traverses a zip directory and returns a list of (zipfile, filename) tuples.

    Args:
        zip_path: Path to the zip archive
        search_pattern: Pattern to search for in filenames
        regex: Whether to treat the search pattern as a regular expression

    Returns:
        List[ZipSearchResult]: List of tuples containing the zipfile and matching filename
    """
    logger.debug(f"Searching through zip archive ({zip_path, search_pattern}).")

    zip_archive = zipfile.ZipFile(zip_path)

    # Use the correct search function
    if regex:

        def check(f):
            return bool(re.search(search_pattern, f))

    else:

        def check(f):
            return search_pattern in f

    files_in_zip = zip_archive.namelist()
    matching_files_in_zip = [f for f in files_in_zip if check(f)]

    return [(zip_archive, f) for f in matching_files_in_zip]


def search_nested_zip_archives(
    zip_path: Path, search_pattern: str
) -> List[ZipSearchResult]:
    """
    Searches for a file in nested zip archives (i.e. zip archives IN a zip archive).

    Args:
        zip_path: Path to the zip archive
        search_pattern: Pattern to search for in filenames

    Returns:
        List[ZipSearchResult]: List of tuples containing the zipfile and matching filename
    """
    logger.debug(f"Searching through NESTED zip archive ({zip_path, search_pattern}).")
    # Find any zip archives in the original archive
    nested_zips = search_zip_archive(zip_path, "\.zip$", regex=True)

    # Extract the nested zips
    with make_temp_directory() as temp_dir:
        results = []
        for nested_zip in nested_zips:
            # Extract the nested zip
            extracted_nested_zip = extract_result(nested_zip, temp_dir)
            # Search the just-now-extracted nested zip
            result = search_zip_archive(extracted_nested_zip, search_pattern)
            results += result
        return results


def extract_result(
    result: ZipSearchResult, target_dir: Path, target_file: Optional[Path] = None
) -> Path:
    """
    Extracts a file from a zip archive.

    Args:
        result: Tuple containing the zipfile and matching filename
        target_dir: Directory to extract the file to
        target_file: Optional path to rename the extracted file to

    Returns:
        Path: Path to the extracted file
    """
    zip_archive, matching_file = result
    file_extracted = zip_archive.extract(matching_file, target_dir)

    if target_file is not None:
        # Ensure the extracted file ends up at "target_file"
        if not target_file == file_extracted:
            Path(file_extracted).rename(target_file)
        return target_file
    else:
        # Return the original location of the extracted file
        return Path(file_extracted)
