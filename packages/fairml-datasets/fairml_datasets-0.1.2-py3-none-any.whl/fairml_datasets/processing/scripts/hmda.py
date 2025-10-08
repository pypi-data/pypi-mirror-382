from typing import List

from fairml_datasets.file_handling import (
    extract_result,
    make_temp_directory,
    search_zip_archive,
)
from .. import LoadingScript, PreparationScript
from pathlib import Path

import pandas as pd

csv_names = [
    "hmda_2011_nationwide_all-records_labels.csv",
    "hmda_2012_nationwide_all-records_labels.csv",
]

# Inspired by, but not exactly matching
# https://github.com/CausalML/FairnessUnderUnawareness/blob/master/data_cleaning.Rmd

filter_columns = [
    "applicant_ethnicity",
    "applicant_race_1",
    "action_taken",
    "as_of_year",
]

# "including" columns
selected_columns = [
    "action_taken",  # alternative: "action_taken_name",
    "applicant_ethnicity_name",
    "applicant_income_000s",
    "applicant_race_name_1",
    "applicant_race_name_2",
    "applicant_sex_name",
    "as_of_year",
    "census_tract_number",
    "co_applicant_ethnicity_name",
    "co_applicant_race_name_1",
    "co_applicant_race_name_2",
    "co_applicant_sex",
    # Deviation due to one-hot encoding increasing dataset size too much
    # the original value would be "county_name"
    "county_code",
    "loan_amount_000s",
    "population",
    "rate_spread",
    "state_code",
]

# Load only a subset of columns to save memory
columns_to_load = list(set(filter_columns + selected_columns))


class Script(LoadingScript, PreparationScript):
    default_options = {
        "apply_default_filter": True,
        # Subsample only a subset of the data per year, set this to None to use the full ~ 21M rows
        # Defaults to 1M per year => 2M total
        "max_n_per_year": 1000000,
        "subsample_seed": 80539,
    }

    def load(self, locations: List[Path]) -> pd.DataFrame:
        # Automatic handling of multiple zip files is not yet supported.

        # Find CSV files in ZIPs
        result_2011 = search_zip_archive(locations[0], csv_names[0])
        result_2012 = search_zip_archive(locations[1], csv_names[1])

        with make_temp_directory() as temp_dir:
            target_dir = temp_dir

            # Extract CSV files
            target_file_2011 = target_dir / csv_names[0]
            extract_result(result_2011[0], target_dir, target_file_2011)
            target_file_2012 = target_dir / csv_names[1]
            extract_result(result_2012[0], target_dir, target_file_2012)

            # Load CSV files
            df_2011 = pd.read_csv(target_file_2011, usecols=columns_to_load)
            df_2012 = pd.read_csv(target_file_2012, usecols=columns_to_load)

        df = pd.concat([df_2011, df_2012])

        return df

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        # Inspired by https://arxiv.org/pdf/1811.11154 and https://dl.acm.org/doi/10.1145/3351095.3373154
        if self.options["apply_default_filter"]:
            df = df[
                df["applicant_ethnicity"].isin([1, 2])
                & df["applicant_race_1"].isin([1, 2, 3, 4, 5])
                & df["action_taken"].isin([1, 2, 3])
                & df["as_of_year"].isin([2011, 2012])
            ]

        # Subsample
        if self.options["max_n_per_year"] is not None:
            df = (
                df.groupby("as_of_year", group_keys=False)
                .apply(
                    lambda x: x.sample(
                        n=min(len(x), self.options["max_n_per_year"]),
                        random_state=self.options["subsample_seed"],
                    )
                )
                .reset_index(drop=True)
            )

        return df
