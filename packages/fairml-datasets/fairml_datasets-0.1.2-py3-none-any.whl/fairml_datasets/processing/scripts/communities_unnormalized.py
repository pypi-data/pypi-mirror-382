from .. import PreparationScript

import pandas as pd


COLUMNS_TO_BINARIZE = [
    "pct12-21",
    "pct12-29",
    "pct16-24",
    "pctBlack",
    "pctWhite",
    "pctAsian",
    "pctHisp",
    "pctFemDivorc",
    "pctMaleDivorc",
]


class Script(PreparationScript):
    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        # Binarize into >= median (or not)
        for col in COLUMNS_TO_BINARIZE:
            df[col] = df[col] >= df[col].median()
        return df
