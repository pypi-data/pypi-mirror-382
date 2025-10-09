import logging
from pathlib import Path

import pandas as pd
import numpy as np
from folktables import ACSDataSource

from copy import deepcopy
from typing import Literal, Tuple
from functools import reduce
from operator import or_

import folktables
from sklearn.model_selection import train_test_split

from folktables.load_acs import state_list

from fairml_datasets.file_handling import DOWNLOAD_CACHE_DIR

# Important constants!
TRAIN_SIZE = 0.7
TEST_SIZE = 0.3
VALIDATION_SIZE = None
"""
TRAIN_SIZE = 0.6
TEST_SIZE = 0.2
VALIDATION_SIZE = 0.2
"""

SEED = 42

root_dir = DOWNLOAD_CACHE_DIR / "folktables"

data_dir = root_dir / "data" / "folktables"
data_dir.mkdir(parents=True, exist_ok=True)

data_source = ACSDataSource(
    survey_year="2018",
    horizon="1-Year",
    survey="person",
    root_dir=str(data_dir),
)

STATE_COL = "ST"

ACS_CATEGORICAL_COLS = {
    "COW",  # class of worker
    "MAR",  # marital status
    "OCCP",  # occupation code
    "POBP",  # place of birth code
    "RELP",  # relationship status
    "SEX",
    "RAC1P",  # race code
    "DIS",  # disability
    "ESP",  # employment status of parents
    "CIT",  # citizenship status
    "MIG",  # mobility status
    "MIL",  # military service
    "ANC",  # ancestry
    "NATIVITY",
    "DEAR",
    "DEYE",
    "DREM",
    "ESR",
    "ST",
    "FER",
    "GCL",
    "JWTR",
    #     'PUMA',
    #     'POWPUMA',
}


# Both load_folktables_task and split_folktables task are adapted from
# https://github.com/socialfoundations/error-parity/blob/supp-materials/notebooks/data.folktables-datasets-preprocessing-1hot.ipynb
def load_folktables_task(
    acs_data: pd.DataFrame,
    acs_task_name: str,
    train_size: float,
    test_size: float,
    validation_size: float = None,
    max_sensitive_groups: int = None,
    stratify_by_state: bool = True,
) -> Tuple[pd.DataFrame, pd.Series]:
    """Train/test split a given folktables task (or train/test/validation).

    According to the dataset's datasheet, (at least) the ACSIncome
    task should be stratified by state.

    Returns
    -------
    (train_data, test_data, validation_data) : Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]
    """
    # Sanity check
    assert train_size + test_size + (validation_size or 0.0) == 1
    assert all(
        val is None or 0 <= val <= 1 for val in (train_size, test_size, validation_size)
    )

    # Dynamically import/load task object
    acs_task = getattr(folktables, acs_task_name)

    # Add State to the feature columns so we can do stratified splits (will be removed later)
    remove_state_col_later = (
        False  # only remove the state column later if we were the ones adding it
    )
    if stratify_by_state:
        if STATE_COL not in acs_task.features:
            acs_task = deepcopy(acs_task)  # we're gonna need to change this task object
            acs_task.features.append(STATE_COL)
            remove_state_col_later = True
        else:
            remove_state_col_later = False

    # Pre-process data + select task-specific features
    features, label, group = acs_task.df_to_numpy(acs_data)

    # Make a DataFrame with all processed data
    df = pd.DataFrame(data=features, columns=acs_task.features)
    df[acs_task.target] = label

    # Correct column ordering (1st: label, 2nd: group, 3rd and onwards: features)
    cols_order = [acs_task.target, acs_task.group] + list(
        set(acs_task.features) - {acs_task.group}
    )
    if remove_state_col_later:
        cols_order = [col for col in cols_order if col != STATE_COL]

    # Save state_col for stratified split
    if stratify_by_state:
        state_col_data = df[STATE_COL]

    # Enforce correct ordering in df
    df = df[cols_order]

    # Drop samples from sensitive groups with low relative size
    # (e.g., original paper has only White and Black races)
    if max_sensitive_groups is not None and max_sensitive_groups > 0:
        group_sizes = df.value_counts(acs_task.group, sort=True, ascending=False)
        big_groups = group_sizes.index.to_list()[:max_sensitive_groups]

        big_groups_filter = reduce(
            or_,
            [(df[acs_task.group].to_numpy() == g) for g in big_groups],
        )

        # Keep only big groups
        df = df[big_groups_filter]
        state_col_data = state_col_data[big_groups_filter]

        # Group values must be sorted, and start at 0
        # (e.g., if we deleted group=2 but kept group=3, the later should now have value 2)
        if df[acs_task.group].max() > df[acs_task.group].nunique():
            map_to_sequential = {
                g: idx for g, idx in zip(big_groups, range(len(big_groups)))
            }
            df[acs_task.group] = [map_to_sequential[g] for g in df[acs_task.group]]

            logging.warning(
                f"Using the following group value mapping: {map_to_sequential}"
            )
            assert df[acs_task.group].max() == df[acs_task.group].nunique() - 1

    ## Try to enforce correct types
    # All columns should be encoded as integers, dtype=int
    types_dict = {col: int for col in df.columns if df.dtypes[col] != "object"}

    df = df.astype(types_dict)
    # ^ set int types right-away so that categories don't have floating points

    # Set categorical columns to start at value=0! (necessary for sensitive attributes)
    for col in ACS_CATEGORICAL_COLS & set(df.columns):
        df[col] = df[col] - df[col].min()

    # Set categorical columns to the correct dtype "category"
    types_dict.update(
        {
            col: "category"
            for col in (ACS_CATEGORICAL_COLS & set(df.columns))
            # if df[col].nunique() < 10
        }
    )

    # Plus the group is definitely categorical
    types_dict.update({acs_task.group: "category"})

    # And the target is definitely integer
    types_dict.update({acs_task.target: int})

    # Set df to correct types
    df = df.astype(types_dict)

    return df, state_col_data


def split_folktables_task(
    df: pd.DataFrame,
    state_col_data: pd.Series,
    acs_task_name: str,
    train_size: float,
    test_size: float,
    validation_size: float = None,
    stratify_by_state: bool = True,
    save_to_dir: Path = None,
    seed: int = 42,
) -> Tuple[pd.DataFrame, ...]:
    # ** Split data in train/test/validation **
    train_idx, other_idx = train_test_split(
        df.index,
        train_size=train_size,
        stratify=state_col_data if stratify_by_state else None,
        random_state=seed,
        shuffle=True,
    )

    train_df, other_df = df.loc[train_idx], df.loc[other_idx]
    assert len(set(train_idx) & set(other_idx)) == 0

    # Split validation
    if validation_size is not None and validation_size > 0:
        new_test_size = test_size / (test_size + validation_size)

        val_idx, test_idx = train_test_split(
            other_df.index,
            test_size=new_test_size,
            stratify=state_col_data.loc[other_idx] if stratify_by_state else None,
            random_state=seed,
            shuffle=True,
        )

        val_df, test_df = other_df.loc[val_idx], other_df.loc[test_idx]
        assert len(train_idx) + len(val_idx) + len(test_idx) == len(df)
        assert np.isclose(len(val_df) / len(df), validation_size)

    else:
        test_idx = other_idx
        test_df = other_df

    assert np.isclose(len(train_df) / len(df), train_size)
    assert np.isclose(len(test_df) / len(df), test_size)

    # Optionally, save data to disk
    if save_to_dir:
        print(
            f"Saving data to folder '{str(save_to_dir)}' with prefix '{acs_task_name}'."
        )
        train_df.to_csv(
            save_to_dir / f"{acs_task_name}.train.csv", header=True, index_label="index"
        )
        test_df.to_csv(
            save_to_dir / f"{acs_task_name}.test.csv", header=True, index_label="index"
        )

        if validation_size:
            val_df.to_csv(
                save_to_dir / f"{acs_task_name}.validation.csv",
                header=True,
                index_label="index",
            )

    return (train_df, test_df, val_df) if validation_size else (train_df, test_df)


def load_folktables_dataset(
    task_name: Literal[
        "ACSIncome",
        "ACSPublicCoverage",
        "ACSMobility",
        "ACSEmployment",
        "ACSTravelTime",
    ],
    max_sensitive_groups: int | None = None,
    states=state_list,
) -> pd.DataFrame:
    """Load a folktables dataset as used in https://doi.org/10.48550/arXiv.2306.07261.

    Args:
        task_name (str): One of 'ACSIncome', 'ACSPublicCoverage', 'ACSMobility', 'ACSEmployment', 'ACSTravelTime'.
        max_sensitive_groups (int | None): If not None, keep only the biggest n sensitive groups. In the original paper they use 4 and 2 for this.
        states (List[str]): List of states to include in the dataset.
    """
    acs_data = data_source.get_data(states=states, download=True)

    df, state_col_data = load_folktables_task(
        acs_data,
        acs_task_name=task_name,
        train_size=TRAIN_SIZE,
        test_size=TEST_SIZE,
        validation_size=VALIDATION_SIZE,
        max_sensitive_groups=max_sensitive_groups,
        stratify_by_state=True,
    )

    return df
