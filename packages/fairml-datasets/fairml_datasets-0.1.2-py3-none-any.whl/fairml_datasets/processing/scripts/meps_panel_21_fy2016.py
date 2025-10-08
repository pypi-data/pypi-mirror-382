from typing import List
from .. import LoadingScript, PreparationScript
from pathlib import Path

import pandas as pd


class Script(LoadingScript, PreparationScript):
    def load(self, locations: List[Path]) -> pd.DataFrame:
        return pd.read_sas(locations[0], format="xport", encoding="utf-8")

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        df = self.apply_AIF360_preprocessing_panel21_fy2016(df)

        return df

    # from: https://github.com/Trusted-AI/AIF360/blob/master/aif360/datasets/meps_dataset_panel21_fy2016.py
    def apply_AIF360_preprocessing_panel21_fy2016(self, df):
        """
        1.Create a new column, RACE that is 'White' if RACEV2X = 1 and HISPANX = 2 i.e. non Hispanic White
        and 'Non-White' otherwise
        2. Restrict to Panel 21
        3. RENAME all columns that are PANEL/ROUND SPECIFIC
        4. Drop rows based on certain values of individual features that correspond to missing/unknown - generally < -1
        5. Compute UTILIZATION, binarize it to 0 (< 10) and 1 (>= 10)
        """

        def race(row):
            if (row["HISPANX"] == 2) and (
                row["RACEV2X"] == 1
            ):  # non-Hispanic Whites are marked as WHITE; all others as NON-WHITE
                return "White"
            return "Non-White"

        df["RACEV2X"] = df.apply(lambda row: race(row), axis=1)
        df = df.rename(columns={"RACEV2X": "RACE"})

        df = df[df["PANEL"] == 21]

        # RENAME COLUMNS
        df = df.rename(
            columns={
                "FTSTU53X": "FTSTU",
                "ACTDTY53": "ACTDTY",
                "HONRDC53": "HONRDC",
                "RTHLTH53": "RTHLTH",
                "MNHLTH53": "MNHLTH",
                "CHBRON53": "CHBRON",
                "JTPAIN53": "JTPAIN",
                "PREGNT53": "PREGNT",
                "WLKLIM53": "WLKLIM",
                "ACTLIM53": "ACTLIM",
                "SOCLIM53": "SOCLIM",
                "COGLIM53": "COGLIM",
                "EMPST53": "EMPST",
                "REGION53": "REGION",
                "MARRY53X": "MARRY",
                "AGE53X": "AGE",
                "POVCAT16": "POVCAT",
                "INSCOV16": "INSCOV",
            }
        )

        df = df[df["REGION"] >= 0]  # remove values -1
        df = df[df["AGE"] >= 0]  # remove values -1

        df = df[df["MARRY"] >= 0]  # remove values -1, -7, -8, -9

        df = df[df["ASTHDX"] >= 0]  # remove values -1, -7, -8, -9

        df = df[
            (
                df[
                    [
                        "FTSTU",
                        "ACTDTY",
                        "HONRDC",
                        "RTHLTH",
                        "MNHLTH",
                        "HIBPDX",
                        "CHDDX",
                        "ANGIDX",
                        "EDUCYR",
                        "HIDEG",
                        "MIDX",
                        "OHRTDX",
                        "STRKDX",
                        "EMPHDX",
                        "CHBRON",
                        "CHOLDX",
                        "CANCERDX",
                        "DIABDX",
                        "JTPAIN",
                        "ARTHDX",
                        "ARTHTYPE",
                        "ASTHDX",
                        "ADHDADDX",
                        "PREGNT",
                        "WLKLIM",
                        "ACTLIM",
                        "SOCLIM",
                        "COGLIM",
                        "DFHEAR42",
                        "DFSEE42",
                        "ADSMOK42",
                        "PHQ242",
                        "EMPST",
                        "POVCAT",
                        "INSCOV",
                    ]
                ]
                >= -1
            ).all(1)
        ]  # for all other categorical features, remove values < -1

        def utilization(row):
            return (
                row["OBTOTV16"]
                + row["OPTOTV16"]
                + row["ERTOT16"]
                + row["IPNGTD16"]
                + row["HHTOTD16"]
            )

        df["TOTEXP16"] = df.apply(lambda row: utilization(row), axis=1)
        lessE = df["TOTEXP16"] < 10.0
        df.loc[lessE, "TOTEXP16"] = 0.0
        moreE = df["TOTEXP16"] >= 10.0
        df.loc[moreE, "TOTEXP16"] = 1.0

        df = df.rename(columns={"TOTEXP16": "UTILIZATION"})
        return df
