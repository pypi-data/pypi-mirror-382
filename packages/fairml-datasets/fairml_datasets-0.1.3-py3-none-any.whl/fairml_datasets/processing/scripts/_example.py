from typing import List
from .. import LoadingScript, PreparationScript
from pathlib import Path

import pandas as pd


class Script(LoadingScript, PreparationScript):
    def load(self, locations: List[Path]) -> pd.DataFrame:
        pass

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        pass

    available_options = {}

    def postprocess(self, df: pd.DataFrame, options: dict) -> pd.DataFrame:
        pass
