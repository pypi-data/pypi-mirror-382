import json
from pathlib import Path
import warnings
import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Literal, Optional, Union, Tuple, Any
from aif360.datasets import BinaryLabelDataset
from rich.logging import RichHandler
from itertools import combinations, chain
from sklearn.model_selection import train_test_split as sk_train_test_split

from fairml_datasets.metadata import (
    generate_binarized_descriptives,
    generate_general_descriptives,
)

from .transform import PreprocessingInfo, filter_columns, transform
from .processing import ProcessingScript, annotations
from .file_handling import (
    DOWNLOAD_CACHE_DIR,
    download_dataset,
    load_dataset,
    DATASET_CACHE_DIR,
    make_temp_directory,
)
from .processing.datasets import (
    get_processing_script,
    parse_feature_column_filter,
)
from .processing import (
    LoadingScript,
    PreparationScript,
)


DEFAULT_SEED = 80539

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)


class Dataset:
    """
    Main class representing a fairness dataset with methods to download, load, transform and split data.

    Provides interfaces to common fairness-related operations like identifying sensitive columns,
    preparing data for analysis, and generating metadata.
    """

    info: pd.Series

    def __init__(self, info: pd.Series):
        """
        Initialize a Dataset, one will usually use Dataset.from_id() instead,
        unless you have a custom collection of dataset annotations.

        Args:
            info: A pandas Series containing annotations for the dataset
        """
        assert isinstance(info, pd.Series), "info must be a pandas.Series"
        self.info = info.replace({np.nan: None})
        self._sensitive_columns = None

    @staticmethod
    def from_id(id: str) -> "Dataset":
        """
        Create a Dataset object using the dataset identifier.

        Args:
            id: String identifier of the dataset

        Returns:
            Dataset: A Dataset object
        """
        df_info = annotations.load()
        return Dataset(df_info.loc[id])

    def __repr__(self) -> str:
        """
        Returns a string representation of the Dataset object (for printing)

        Returns:
            str: A string representation of the Dataset object
        """
        return f"fairml_datasets.Dataset(id={self.dataset_id})"

    @property
    def dataset_id(self) -> str:
        """
        Get the dataset identifier.

        Returns:
            str: The dataset identifier
        """
        return self.info.name

    @property
    def name(self) -> str:
        """
        Get the human-readable name of the dataset.

        Returns:
            str: The name of the dataset
        """
        return self.info["dataset_name"]

    def get_processing_script(
        self, processing_options: Dict[str, Any] = None
    ) -> ProcessingScript:
        """
        Get the ProcessingScript for this dataset with optional configuration.

        Args:
            processing_options: Dictionary of options to pass to the processing script

        Returns:
            ProcessingScript: The processing script for this dataset, or None if not available
        """
        ScriptClass = get_processing_script(self.dataset_id)
        if ScriptClass is not None:
            return ScriptClass(processing_options=processing_options)
        else:
            if processing_options is not None:
                warnings.warn(
                    "Processing_options provided, but no processing script available. Ignoring processing_options."
                )
            return None

    def get_urls(self) -> List[str]:
        """
        Get the download URLs for this dataset.

        Returns:
            List[str]: List of download URLs, empty if none available
        """
        if self.info["download_url"] is not None:
            return self.info["download_url"].split(";")
        else:
            return []

    def get_filenames(self) -> List[str]:
        """
        Get the expected filenames for the raw dataset files.

        Returns:
            List[str]: List of expected filenames
        """
        urls = self.get_urls()
        if self.info["filename_raw"] is not None:
            return self.info["filename_raw"].split(";")
        elif urls:
            return [url.rsplit("/", 1)[-1] for url in urls]
        else:
            return [self.dataset_id]

    def _download(self, directory: Path, read_cache: bool = True) -> List[Path]:
        """
        Download the dataset files to a specified directory.

        Args:
            directory: Directory to store downloaded files
            read_cache: Whether to use cached files if available

        Returns:
            List[Path]: Paths to downloaded files
        """
        target_dir = directory / str(self.dataset_id)
        target_dir.mkdir(parents=True, exist_ok=True)

        return download_dataset(
            urls=self.get_urls(),
            filenames=self.get_filenames(),
            target_directory=target_dir,
            is_zip=self.info["is_zip"],
            read_cache=read_cache,
        )

    def load(
        self,
        stage: Literal[
            "downloaded", "loaded", "prepared", "binarized", "transformed", "split"
        ] = "prepared",
        cache_at: Literal["downloaded", "prepared"] = "prepared",
        check_cache: bool = True,
        processing_options: Optional[Dict[str, Any]] = None,
    ) -> pd.DataFrame:
        """
        Load the dataset at a specific processing stage.

        Args:
            stage: Processing stage at which to return the dataset
            cache_at: Stage at which to cache the dataset (downloaded or prepared)
            check_cache: Whether to check for cached data
            processing_options: Options to pass to the dataset's processing script (if available; optional)

        Returns:
            pd.DataFrame: The pandas dataframe with data at the specified stage of processing
        """
        if stage == "split":
            logger.info(
                "Please use .split_dataset(), .train_test_split() or .train_test_val_split to split the dataset. 'Binarized' data will be returned from this function."
            )
            stage = "binarized"

        # Load the custom processing script (if it exists)
        script = self.get_processing_script(processing_options=processing_options)
        has_script = script is not None

        # Check the "prepared" cache
        # Add a hash to the cache name if necessary, as the script might have options
        opt_hash_postfix = (
            ("-" + script.get_options_hash())
            if has_script and script.has_options
            else ""
        )
        cached_filename = f"{self.dataset_id}{opt_hash_postfix}.parquet"
        cached_filepath = DATASET_CACHE_DIR / cached_filename
        if check_cache and cached_filepath.exists():
            logger.info(f"Loading cached dataset from {cached_filepath}")
            return pd.read_parquet(cached_filepath, engine="fastparquet")

        if not self.info["custom_download"]:
            assert (
                self.info["download_url"] is not None
            ), "Dataset is missing download URL."

            with make_temp_directory() as temp_dir:
                cache_download = cache_at == "downloaded"
                download_dir = temp_dir if not cache_download else DOWNLOAD_CACHE_DIR

                # Step 1: Download the dataset
                locations = self._download(
                    directory=download_dir, read_cache=cache_download
                )
                if stage == "downloaded":
                    # Cast to DataFrame so we can stick to one return type
                    return pd.DataFrame({"file_paths": [str(loc) for loc in locations]})

                # Step 2: Load the dataset
                if has_script and isinstance(script, LoadingScript):
                    dataset = script.load(locations)
                    assert (
                        dataset is not None
                    ), "LoadingScript returned None, maybe a return was missing?"
                else:
                    assert (
                        len(locations) == 1
                    ), "Multiple files, but no custom script to handle them."

                    dataset = load_dataset(
                        location=locations[0],
                        data_format=self.info["format"],
                        colnames=self.info["colnames"],
                    )
        else:
            if stage == "downloaded":
                warnings.warn(
                    "Use stage == downloaded for a dataset that uses a custom download (most likely synthetic data). Returning an empty Dataframe."
                )
                return pd.DataFrame()

            # Alternative Step 1 & 2: Using a custom download & loading script
            if has_script and isinstance(script, LoadingScript):
                logger.debug(f"Detected LoadingScript for {self.dataset_id}.")
                dataset = script.load(locations=[])
            else:
                raise ValueError(
                    f"Dataset {self.dataset_id} flagged as custom download, "
                    "but is missing a loading script."
                )
        if stage == "loaded":
            return dataset

        # Step 3: Prepare the dataset (if applicable)
        if has_script and isinstance(script, PreparationScript):
            logger.debug(f"Detected PreparationScript for {self.dataset_id}.")
            dataset = script.prepare(dataset)
        # Cache the dataset (optional)
        if cache_at == "prepared":
            DATASET_CACHE_DIR.mkdir(exist_ok=True, parents=True)
            dataset.to_parquet(cached_filepath, index=False, engine="fastparquet")

        if stage == "prepared":
            return dataset
        if stage == "transformed":
            df, _ = self.transform(dataset)
            return df
        elif stage == "binarized":
            df, _ = self.binarize(
                dataset,
                transform_sensitive_columns="intersection_binary",
                transform_sensitive_values="majority_minority",
            )
            return df
        else:
            raise ValueError(f"Unsupported stage: {stage}")

    def to_pandas(self) -> pd.DataFrame:
        """
        Load the dataset as a pandas DataFrame.

        Use .load() if you want more control.

        Returns:
            pd.DataFrame: The dataset as a pandas DataFrame
        """
        return self.load()

    def to_numpy(self) -> np.ndarray:
        """
        Load the dataset as a numpy array.

        Use .load() if you want more control.

        Returns:
            np.ndarray: The dataset as a numpy array
        """
        return self.load().to_numpy()

    def binarize(
        self,
        df: Optional[pd.DataFrame] = None,
        sensitive_columns: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> tuple[pd.DataFrame, PreprocessingInfo]:
        """
        Apply binarization transformations to the dataset for fairness analysis.

        This is a convenience method that calls transform() with specific parameters
        to convert categorical sensitive attributes to binary format using
        'intersection_binary' and 'majority_minority' strategies.

        Args:
            df: Optional DataFrame to transform, if None the dataset is loaded
            sensitive_columns: List of sensitive attribute column names
            **kwargs: Additional arguments for transformation, passed to transform()

        Returns:
            tuple[pd.DataFrame, PreprocessingInfo]: Binarized DataFrame and preprocessing information
        """
        return self.transform(
            df=df,
            sensitive_columns=sensitive_columns,
            transform_sensitive_columns="intersection_binary",
            transform_sensitive_values="majority_minority",
            **kwargs,
        )

    def transform(
        self,
        df: Optional[pd.DataFrame] = None,
        sensitive_columns: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> tuple[pd.DataFrame, PreprocessingInfo]:
        """
        Apply default transformations to the dataset.

        Args:
            df: Optional DataFrame to transform, if None the dataset is loaded
            sensitive_columns: List of sensitive attribute column names
            **kwargs: Additional arguments for transformation, passed to transform()

        Returns:
            tuple[pd.DataFrame, PreprocessingInfo]: Transformed DataFrame and preprocessing information
        """
        logger.debug(f"Transforming: {self.dataset_id}")

        if df is None:
            df = self.load()
        target_column = self.get_target_column()
        if sensitive_columns is None:
            sensitive_columns = self.sensitive_columns

        feature_columns = self.get_feature_columns(df=df)
        target_lvl_good_bad = self.get_target_lvl_good_value()

        return transform(
            df=df,
            sensitive_columns=sensitive_columns,
            feature_columns=feature_columns,
            target_column=target_column,
            target_lvl_good_bad=target_lvl_good_bad,
            **kwargs,
        )

    def get_feature_columns(self, df: pd.DataFrame) -> List[str]:
        """
        Get the feature columns for the dataset.

        Args:
            df: DataFrame containing the dataset

        Returns:
            List[str]: List of feature column names
        """
        target_column = set([self.get_target_column()])
        sensitive_columns = set(self.sensitive_columns)
        typical_col_features = self.get_typical_col_features()
        colnames = set(df.columns)
        feature_columns = parse_feature_column_filter(
            colnames, target_column, sensitive_columns, typical_col_features
        )
        return feature_columns

    def filter_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter the dataset to include only the required columns.

        Args:
            df: DataFrame to filter

        Returns:
            pd.DataFrame: Filtered DataFrame
        """
        sensitive_columns = set(self.sensitive_columns)
        feature_columns = self.get_feature_columns()
        target_column = set([self.get_target_column()])

        return filter_columns(
            sensitive_columns=sensitive_columns,
            feature_columns=feature_columns,
            target_column=target_column,
        )

    def to_aif360_BinaryLabelDataset(
        self,
        sensitive_columns: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> "BinaryLabelDataset":  # noqa: F821
        """
        Convert the dataset to AIF360 BinaryLabelDataset format.

        Args:
            sensitive_columns: List of sensitive attribute column names
            **kwargs: Additional arguments for transformation passed to .binarize() and then .transform()

        Returns:
            BinaryLabelDataset: The dataset in AIF360 format
        """
        df = self.load()

        # Preprocessing (this can affect columns / column names)
        df, info = self.binarize(df=df, sensitive_columns=sensitive_columns, **kwargs)
        sensitive_columns = info.sensitive_columns

        # Create the AIF360 dataset
        from aif360.datasets import BinaryLabelDataset

        dataset = BinaryLabelDataset(
            favorable_label=1,
            unfavorable_label=0,
            df=df,
            label_names=[self.get_target_column()],
            protected_attribute_names=sensitive_columns,
        )

        return dataset

    def generate_metadata(self) -> Dict[str, Union[str, int, float]]:
        """
        Generate metadata about the dataset for fairness analysis.

        Returns:
            Dict[str, Union[str, int, float]]: Dictionary of metadata
        """
        try:
            df_raw = self.load()
        except Exception as e:
            logger.exception(
                f"Data loading / preparation error in {self.dataset_id}: {e}"
            )
            return {
                "id": self.dataset_id,
                "debug_meta_status": "LOAD_ERROR",
                "debug_meta_error_message": str(e),
            }

        try:
            sensitive_columns = self.sensitive_columns
            target_column = self.get_target_column()
            target_lvl_good_value = self.get_target_lvl_good_value()
            feature_columns = self.get_feature_columns(df=df_raw)

            general_descriptives = generate_general_descriptives(
                df_raw=df_raw,
                sensitive_columns=sensitive_columns,
                target_column=target_column,
                target_lvl_good_value=target_lvl_good_value,
                feature_columns=list(feature_columns),
            )

            try:
                df, info = self.binarize(df=df_raw, sensitive_columns=sensitive_columns)
                sensitive_columns = info.sensitive_columns
                col_na_indicator = info.col_na_indicator
            except Exception as e:
                logger.exception(f"Transformation Error in {self.dataset_id}: {e}")

            binarized_descriptives = generate_binarized_descriptives(
                df=df,
                sensitive_columns=sensitive_columns,
                target_column=target_column,
                col_na_indicator=col_na_indicator,
            )

            meta = {
                "id": self.dataset_id,
                # Metadata used for debugging / development
                "debug_meta_status": "OK",
                "debug_meta_colnames": ";".join(df.columns.tolist()),
                "debug_meta_coltypes": ";".join(
                    [str(df[col].dtype) for col in df.columns]
                ),
            }
            meta.update(general_descriptives)
            meta.update(binarized_descriptives)

            return meta
        except Exception as e:
            logger.exception(f"Metadata error in {self.dataset_id}: {e}")
            return {
                "id": self.dataset_id,
                "debug_meta_status": "METADATA_ERROR",
                "debug_meta_error_message": str(e),
            }

    def _get_sensitive_parsed(self) -> Optional[Dict[str, str]]:
        """
        Get the parsed sensitive columns information.

        Returns:
            Optional[Dict[str, str]]: Dictionary mapping sensitive column names to descriptions
        """
        return (
            json.loads(self.info["typical_col_sensitive"])
            if self.info["typical_col_sensitive"] is not None
            else None
        )

    def get_all_sensitive_columns(self) -> List[str]:
        """
        Get all available (typically used) sensitive columns for this dataset.

        Returns:
            List[str]: List of all sensitive column names
        """
        sensitive_parsed = self._get_sensitive_parsed()
        return list(sensitive_parsed.keys()) if sensitive_parsed is not None else []

    def _get_default_scenario_sensitive_columns(self) -> List[str]:
        """
        Get the default sensitive columns for the standard Scenario.

        Returns:
            List[str]: List of sensitive column names
        """
        sensitive_cols = self.info["default_scenario_sensitive_cols"].split(";")
        if len(sensitive_cols) > 0:
            return sensitive_cols
        else:
            raise ValueError

    @property
    def sensitive_columns(self) -> List[str]:
        """
        Get the sensitive columns for this dataset.

        Returns:
            List[str]: List of sensitive column names
        """
        if self._sensitive_columns is not None:
            return self._sensitive_columns
        return self._get_default_scenario_sensitive_columns()

    def generate_sensitive_intersections(self) -> List[List[str]]:
        """
        Generate all possible intersections of sensitive attributes.

        Returns:
            List[List[str]]: List of all possible combinations of sensitive attributes
        """
        if self._sensitive_columns is not None:
            warnings.warn(
                "Generating sensitive intersections on a scenario. You will usually want to do this on the dataset itself, as they will be generated for ALL available sensitive attributes, not the ones in the scenario."
            )
        sensitive_columns = self.get_all_sensitive_columns()
        all_combinations = list(
            chain.from_iterable(
                combinations(sensitive_columns, r)
                for r in range(1, len(sensitive_columns) + 1)
            )
        )
        return [list(combo) for combo in all_combinations]

    def get_target_column(self) -> str:
        """
        Get the name of the target column for this dataset.

        Returns:
            str: Name of the target column
        """
        target_col = self.info["typical_col_target"]
        # Strip leading question mark
        if target_col.startswith("?"):
            target_col = target_col[1:]
        # Separate multiple columns by semicolon
        if ";" in target_col:
            target_cols = target_col.split(";")
            # The first column is the "most" typical, so use this one for now
            # This is currently only an issue for the Drug dataset
            target_col = target_cols[0]
        return target_col

    def get_target_lvl_good_value(self) -> Optional[str]:
        """
        Get the value in the target column that represents a favorable outcome.

        Returns:
            Optional[str]: The value representing a favorable outcome
        """
        target_lvl_good = str(self.info["target_lvl_good"])
        # Strip leading question mark
        if target_lvl_good.startswith("?"):
            target_lvl_good = target_lvl_good[1:]
        # Encode empty string as None
        if target_lvl_good == "":
            return None
        return target_lvl_good

    def citation(self) -> Optional[str]:
        """
        Get the citation for this dataset in BibTeX format.

        Returns:
            Optional[str]: The citation in BibTeX format, or None if not available
        """
        citation_text = self.info.get("citation")
        if citation_text and isinstance(citation_text, str):
            return citation_text.strip()
        return None

    def get_typical_col_features(self) -> str | None:
        """
        Get information about typical feature columns.

        Returns:
            str | None: Information about typical feature columns
        """
        typical_col_features = self.info["typical_col_features"]
        if typical_col_features.startswith("?"):
            typical_col_features = typical_col_features[1:]
        if typical_col_features == "":
            return None
        return typical_col_features

    def split_dataset(
        self,
        df: Union[pd.DataFrame, BinaryLabelDataset],
        splits: Tuple[float, ...],
        seed: int = DEFAULT_SEED,
        stratify: bool = True,
        stratify_manual: Optional[str] = None,
        sensitive_columns: Optional[List[str]] = None,
    ) -> Tuple[Union[pd.DataFrame, BinaryLabelDataset], ...]:
        """
        Split a dataset into multiple partitions based on specified ratios.

        Args:
            df: DataFrame or AIF360 BinaryLabelDataset to split
            splits: Tuple of fractions that sum to 1.0. For example, (0.6, 0.2, 0.2) for train/val/test
            seed: Random seed for reproducibility
            stratify: Whether to stratify the split by target column and sensitive attributes
            stratify_manual: Column to stratify by (defaults to combined target+sensitive if None and stratify=True)
            sensitive_columns: List of sensitive attribute column names

        Returns:
            Tuple of datasets with the same type as df
        """
        # Validate splits
        if not isinstance(splits, tuple) or len(splits) < 2:
            raise ValueError("splits must be a tuple with at least 2 elements")
        if round(sum(splits), 10) != 1.0:
            raise ValueError(f"Split values must sum to 1.0, got {sum(splits)}")

        if stratify_manual is not None and not stratify:
            logger.error(
                "stratify_manual is set but stratify is False. Setting stratify to True."
            )
            stratify = True

        # If AIF360 dataset, convert to pandas for splitting
        is_aif360 = isinstance(df, BinaryLabelDataset)
        pandas_df = df if not is_aif360 else df.convert_to_dataframe()[0]

        # Determine column to use for stratification
        stratify_col = None
        if stratify:
            # Manual column provided
            if stratify_manual is not None:
                if stratify_manual in pandas_df.columns:
                    stratify_col = pandas_df[stratify_manual]
                else:
                    raise ValueError(
                        f"Stratify column {stratify_manual} not found in dataframe."
                    )
            else:
                # Get target and sensitive columns for combined stratification
                target_column = self.get_target_column()
                if sensitive_columns is None:
                    sensitive_columns = self.sensitive_columns

                # Handle the case where sensitive columns were transformed
                # Check if original sensitive columns exist, if not try sensitive_intersection
                available_sensitive_columns = []
                for col in sensitive_columns:
                    if col in pandas_df.columns:
                        available_sensitive_columns.append(col)

                # If no original sensitive columns found, check for sensitive_intersection
                if (
                    not available_sensitive_columns
                    and "sensitive_intersection" in pandas_df.columns
                ):
                    sensitive_columns = ["sensitive_intersection"]

                strat_columns = [target_column] + sensitive_columns

                # Check if columns exist in the dataframe
                if not set(strat_columns).issubset(set(pandas_df.columns)):
                    missing_columns = set(strat_columns) - set(pandas_df.columns)
                    raise ValueError(
                        f"Target or sensitive columns not found in dataframe: {missing_columns}"
                    )

                logger.info(
                    f"Stratifying split by columns: {strat_columns}"
                )

                # Combine target and sensitive columns for stratification
                if len(strat_columns) == 1:
                    stratify_col = pandas_df[strat_columns[0]]
                else:
                    stratify_col = (
                        pandas_df[strat_columns]
                        .astype(str)
                        .apply(lambda x: "_".join(x.values), axis=1)
                    )

        result = []
        remaining_df = pandas_df.copy()
        remaining_prob = 1.0

        # Iteratively split dataset
        for i, split_ratio in enumerate(splits[:-1]):
            if len(remaining_df) == 0:
                # Handle edge case of empty dataframe
                result.append(remaining_df.copy())
                continue

            # Calculate the proportion for this split from the remaining data
            proportion = split_ratio / remaining_prob

            # Get stratification data for current split
            current_stratify = (
                stratify_col.loc[remaining_df.index]
                if stratify_col is not None
                else None
            )

            # If there's only one class in the stratification column, don't stratify
            if current_stratify is not None and len(current_stratify.unique()) < 2:
                logger.warning(
                    f"Only one class present in stratification column for split {i}. Not stratifying this split."
                )
                current_stratify = None

            # Split the data
            new_split, remaining_df = sk_train_test_split(
                remaining_df,
                test_size=1 - proportion,
                random_state=seed,
                stratify=current_stratify,
            )

            result.append(new_split)
            remaining_prob -= split_ratio

        # Add the final piece
        result.append(remaining_df)

        # Convert back to AIF360 if needed
        if is_aif360:
            return tuple(
                BinaryLabelDataset(
                    df=split_df,
                    label_names=df.label_names,
                    protected_attribute_names=df.protected_attribute_names,
                    favorable_label=df.favorable_label,
                    unfavorable_label=df.unfavorable_label,
                )
                for split_df in result
            )

        return tuple(result)

    def train_test_split(
        self,
        df: Union[pd.DataFrame, BinaryLabelDataset],
        test_size: float = 0.3,
        **kwargs: Any,
    ) -> Tuple[
        Union[pd.DataFrame, BinaryLabelDataset], Union[pd.DataFrame, BinaryLabelDataset]
    ]:
        """
        Split a dataset into train and test sets.

        Args:
            df: DataFrame or BinaryLabelDataset to split (if None, dataset is loaded)
            test_size: Fraction of data to use for testing
            **kwargs: Additional arguments to pass to split_dataset

        Returns:
            Tuple of (train_data, test_data)
        """
        train_size = 1.0 - test_size
        return self.split_dataset(df, splits=(train_size, test_size), **kwargs)

    def train_test_val_split(
        self,
        df: Union[pd.DataFrame, BinaryLabelDataset],
        test_size: float = 0.2,
        val_size: float = 0.2,
        **kwargs: Any,
    ) -> Tuple[
        Union[pd.DataFrame, BinaryLabelDataset],
        Union[pd.DataFrame, BinaryLabelDataset],
        Union[pd.DataFrame, BinaryLabelDataset],
    ]:
        """
        Split a dataset into train, validation, and test sets.

        Args:
            df: DataFrame or BinaryLabelDataset to split
            test_size: Fraction of data to use for testing
            val_size: Fraction of data to use for validation
            **kwargs: Additional arguments to pass to split_dataset

        Returns:
            Tuple of (train_data, val_data, test_data)
        """
        # Calculate train size based on test and validation sizes
        train_size = 1.0 - test_size - val_size

        if train_size <= 0:
            raise ValueError(
                f"Invalid split sizes: test_size ({test_size}) + val_size ({val_size}) must be less than 1.0"
            )

        return self.split_dataset(
            df, splits=(train_size, val_size, test_size), **kwargs
        )
