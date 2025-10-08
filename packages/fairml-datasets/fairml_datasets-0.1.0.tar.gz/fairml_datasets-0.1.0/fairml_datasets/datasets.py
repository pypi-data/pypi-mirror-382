import pandas as pd
from typing import List, Optional, Union, Generator
from rich.progress import track

from .processing import (
    annotations,
)
from .dataset import Dataset


class Datasets:
    """
    Helper class to easily work with multiple datasets.

    This class provides interfaces for accessing and working with collections of Dataset objects,
    allowing for batch operations like metadata generation across multiple datasets.
    """

    # DataFrame containing information about Datasets
    df_info: pd.DataFrame

    def __init__(
        self,
        ids: Optional[List[str]] = None,
        inclue_large_datasets: bool = False,
        df_info: Optional[pd.DataFrame] = None,
    ) -> None:
        """
        Initialize a Datasets collection.

        Args:
            ids: Optional list of dataset IDs to include
            inclue_large_datasets: Whether to include datasets marked as 'large'
            df_info: Optional DataFrame containing dataset annotations (will be loaded if None)
        """
        # Load annotations (these can optionally be provided, but it's not such a common usecase)
        if df_info is None:
            df_info = annotations.load()
        else:
            # Copy to avoid changes by reference
            df_info = df_info.copy()

        # Filter out datasets that are not in the list of ids
        if ids is not None:
            df_info = df_info.loc[ids]

        # Filter out large datasets if needed
        if ids is None and not inclue_large_datasets:
            df_info = df_info[~df_info["is_large"]]

        self.df_info = df_info

    def __len__(self) -> int:
        """
        Get the number of datasets in the collection.

        Returns:
            int: The number of datasets
        """
        return len(self.df_info.index)

    # Allow getting datasets by index
    def __getitem__(self, index: Union[int, str]) -> Dataset:
        """
        Get a dataset by index or ID.

        Args:
            index: Integer index or string ID of the dataset

        Returns:
            Dataset: The requested dataset object

        Raises:
            AssertionError: If index is not an integer or string
        """
        if isinstance(index, int):
            # Retrieve via integer row index
            return Dataset(info=self.df_info.iloc[index])
        else:
            # Retrieve via id index
            assert isinstance(index, str), "index must be a string or integer"
            return Dataset(info=self.df_info.loc[index])

    # Make the class iterable
    def __iter__(self) -> Generator[Dataset, None, None]:
        """
        Make the Datasets collection iterable, yielding Dataset objects.

        Yields:
            Dataset: The next dataset in the collection
        """
        for _, row in self.df_info.iterrows():
            yield Dataset(info=row)

    def get_ids(self) -> List[str]:
        """
        Get a list of all dataset IDs in the collection.

        Returns:
            List[str]: List of dataset IDs
        """
        return self.df_info.index.tolist()

    def generate_metadata(self, progress_bar: bool = True) -> pd.DataFrame:
        """
        Generate a dataframe of metadata for all datasets in the collection.

        Args:
            progress_bar: Whether to display a progress bar during generation

        Returns:
            pd.DataFrame: DataFrame containing metadata for all datasets
        """
        metadata_dicts = [
            dataset.generate_metadata()
            for dataset in (track(self) if progress_bar else self)
        ]
        return pd.DataFrame.from_records(data=metadata_dicts)
