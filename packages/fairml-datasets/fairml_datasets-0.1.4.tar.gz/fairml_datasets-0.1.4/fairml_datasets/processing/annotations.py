"""
Module for loading and processing dataset annotations.

This module provides functions to load, clean, and process the raw annotations file
that contains metadata about fairness datasets, including their sources, formats,
and other properties needed for proper handling.
"""

# This module contains the code to load, process & clean the raw annotation file

import logging
import pandas as pd

from ..data import RAW, FINAL

RAW_ANNOTATION_FILE = RAW / "annotations.csv"
CLEAN_ANNOTATION_FILE = FINAL / "annotations.csv"

logger = logging.getLogger(__name__)


def load_cleaned():
    """
    Load the cleaned annotations from the processed CSV file.

    This is the only function useful in production, as raw annotations are not
    intended to be publicly released as they provide little additional value.

    Returns:
        pd.DataFrame: DataFrame containing the cleaned dataset annotations.
    """
    datasets = pd.read_csv(CLEAN_ANNOTATION_FILE)

    # Remove "ann_" prefix from column names
    datasets.columns = datasets.columns.str.replace("ann_", "", regex=False)

    datasets.set_index("new_dataset_id", inplace=True)

    return datasets


def load_raw():
    """
    Load the raw annotations from the data directory.

    Returns:
        pd.DataFrame: DataFrame containing the raw dataset annotations
    """
    # Load from csv (tracked in git)
    datasets = pd.read_csv(RAW_ANNOTATION_FILE, skiprows=1)

    return datasets


def load_online():
    """
    Load the raw annotations directly from Google Sheets.

    Returns:
        pd.DataFrame: DataFrame containing the raw dataset annotations
    """
    sheet_id = "1TFzwZLxas4wDBrVMbwUhstDIzaulIHgauHRYpDHEVWk"
    datasets_gid = "2080081335"

    datasets = pd.read_csv(
        f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={datasets_gid}",
        skiprows=1,
    )

    return datasets


def filter_rows(df: pd.DataFrame, binary_mask: pd.Series, reason: str):
    """
    Filter the rows of a dataframe based on a binary mask.

    Args:
        df: DataFrame to filter
        binary_mask: Boolean mask to apply to the DataFrame
        reason: Reason for filtering (used in log messages)

    Returns:
        pd.DataFrame: Filtered DataFrame

    Raises:
        ValueError: If no rows remain after filtering
    """
    n_drop = sum(~binary_mask)
    if n_drop > 0:
        logger.warning(
            (
                f"Dropping n = {n_drop}, reason: {reason}. "
                f"n = {sum(binary_mask)} rows left."
            )
        )
    if sum(binary_mask) == 0:
        raise ValueError(f"No rows left after filtering for {reason}.")

    # Do actual filtering
    df = df[binary_mask]
    return df


def clean(datasets: pd.DataFrame):
    """
    Clean and process the raw annotations DataFrame.

    This function filters datasets based on various criteria, transforms values,
    and prepares the annotations for use in the fairml_datasets package.

    Args:
        datasets: Raw annotations DataFrame

    Returns:
        pd.DataFrame: Cleaned and processed annotations DataFrame with dataset_id as index
    """
    # - Clean datasets -
    # Filter the list of datasets
    datasets = filter_rows(
        datasets,
        datasets["STATUS"].isin(
            ["DONE", "PROCESSING NEEDED", "COPIED PARTIALLY", "COPIED OVER"]
        ),
        "status not ready",
    )
    datasets = filter_rows(
        datasets, datasets["is_accessible"] == "Publicly", "is_accessible != Publicly"
    )
    datasets = filter_rows(
        datasets,
        datasets["data_type"].isin(["tabular data"]),
        "data_type != tabular data (only tabular data is supported for now)",
    )
    datasets = filter_rows(
        datasets,
        datasets["used_for_classification"],
        "used_for_classification is False",
    )

    # datasets = filter_rows(
    #     datasets,
    #     ~(datasets["format"].isna() & datasets["custom_download"] == "No"),
    #     "format is missing",
    # )

    datasets["format"] = datasets["format"].str.lower()
    # Generate new columns
    datasets["is_zip"] = datasets["custom_download"].str.contains("unzip")
    with pd.option_context("future.no_silent_downcasting", True):
        datasets["custom_download"] = (
            datasets["custom_download"]
            .replace(
                {
                    "Yes": True,
                    # Unzip is handled by default
                    "Yes (unzip)": False,
                    "No": False,
                }
            )
            .infer_objects(copy=False)
        )
    datasets["colnames"] = datasets["colnames"].replace("-", pd.NA)
    # Drop unnecessary columns
    columns_to_drop = [
        "STATUS",
        "full_dataset_id",
        "dataset_base_id",
        "ANNOTATOR",
        "NOTES",
        "description",
        "loading_status",
        "error_message",
        "high_priority",
        "used_for_classification",
    ]
    datasets = datasets.drop(columns=columns_to_drop)

    assert datasets["new_dataset_id"].is_unique
    datasets.set_index("new_dataset_id", inplace=True)

    # True if dataset_size contains "Yes", else False
    datasets["is_large"] = datasets["dataset_size"].str.contains("Yes")

    return datasets


def load(raw: bool = False, online: bool = False):
    """
    Load and clean interim datasets from raw annotations.

    Args:
        online: Whether to load annotations from online source or local file

    Returns:
        pd.DataFrame: Cleaned DataFrame containing dataset annotations
    """
    if raw:
        # Load and clean annotations
        if online:
            datasets = load_online()
        else:
            datasets = load_raw()

        datasets = clean(datasets)
    else:
        # Load pre-cleaned annotations
        assert not online

        datasets = load_cleaned()

    return datasets
