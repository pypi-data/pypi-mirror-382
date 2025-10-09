from typing import List
from .. import LoadingScript, PreparationScript
from pathlib import Path

import pandas as pd


class Script(LoadingScript, PreparationScript):
    def load(self, locations: List[Path]) -> pd.DataFrame:
        return pd.read_excel(locations[0], na_values=["(null)"])

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        # Convert into integer, 4 hour blocks
        df["STOP_FRISK_TIME"] = pd.to_datetime(df["STOP_FRISK_TIME"]).dt.hour // 4
        return df
