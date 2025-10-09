from pathlib import Path
from typing import List
from .. import LoadingScript

import pandas as pd


# COMPAS Variant
# Source: https://github.com/samuel-deng/Ensuring-Fairness-Beyond-the-Training-Data
class Script(LoadingScript):
    def load(self, locations: List[Path]) -> pd.DataFrame:
        # Stitch together all dataframes
        df = pd.concat(
            [pd.read_csv(location, index_col=0) for location in locations],
        ).reset_index(drop=True)
        return df
