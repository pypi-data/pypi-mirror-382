"""
Abstract base classes for dataset processing.

This module defines interfaces for custom scripts that handle dataset loading
and preparation, providing a standardized way to process different data formats
and sources.
"""

from abc import ABC, abstractmethod
from hashlib import md5
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import warnings
import pandas as pd


class ProcessingScript(ABC):
    """
    Abstract base class for all dataset processing scripts.

    This class serves as the foundation for specialized processing scripts
    that handle dataset-specific loading or preparation logic.
    """

    # Default options dictionary for the script
    default_options: Optional[Dict[str, Any]] = None

    def __init__(self, processing_options: Optional[Dict[str, Any]] = None):
        """
        Initialize the processing script with options.

        Args:
            options: Dictionary of options to override defaults
        """
        # Create a copy of default options
        self.options = self.default_options.copy() if self.default_options else None

        # Update with provided options
        if processing_options is not None:
            if self.options is None:
                warnings.warn(
                    "Processing options provided but no default options defined. "
                    "This probably means this Dataset is not designed to accept processing options."
                )
                self.options = processing_options
            else:
                self.options.update(processing_options)

    @property
    def has_options(self) -> bool:
        """
        Check if the script has options.

        Returns:
            bool: True if options are defined, False otherwise
        """
        return self.options is not None

    def get_options_hash(self, length: int = 8) -> str:
        """
        Generate a hash of the options for caching purposes.

        Args:
            length: The maximum length of the hash to return (max 32)

        Returns:
            str: A string representation of the options hash
        """
        assert self.has_options, "No options defined for this script."
        # Borrowing code here from the multiversum package, but shortening hashes
        # Note: Getting stable hashes seems to be easier said than done in Python
        # See https://stackoverflow.com/questions/5884066/hashing-a-dictionary/22003440#2200344
        return md5(
            json.dumps(self.options, sort_keys=True).encode("utf-8")
        ).hexdigest()[:length]


# Customise how data is loaded from a file
class LoadingScript(ProcessingScript):
    """
    Abstract class for scripts that handle custom dataset loading.

    This class is used when a dataset requires specialized logic to load
    data from files, such as handling non-standard formats or extracting
    from complex structures.
    """

    @abstractmethod
    def load(self, locations: List[Path]) -> pd.DataFrame:
        """
        Load a dataset from file locations.

        Args:
            locations: List of paths to the dataset files

        Returns:
            pd.DataFrame: The loaded dataset
        """
        pass


# Customise how data is processed / cleaned after loading
class PreparationScript(ProcessingScript):
    """
    Abstract class for scripts that handle custom dataset preparation.

    This class is used when a dataset requires specialized cleaning,
    transformations, or other preparation steps after loading.
    """

    @abstractmethod
    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare/clean a loaded dataset.

        Args:
            df: The raw loaded DataFrame

        Returns:
            pd.DataFrame: The prepared/cleaned DataFrame
        """
        pass
