from .. import PreparationScript

import pandas as pd


COLUMNS_TO_BINARIZE = [
    "agePct12t21",
    "agePct12t29",
    "agePct16t24",
    "racepctblack",
    "racePctWhite",
    "racePctAsian",
    "racePctHisp",
    "FemalePctDiv",
    "MalePctDivorce",
]


class Script(PreparationScript):
    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        # Binarize into >= median (or not)
        for col in COLUMNS_TO_BINARIZE:
            df[col] = df[col] >= df[col].median()
        return df
