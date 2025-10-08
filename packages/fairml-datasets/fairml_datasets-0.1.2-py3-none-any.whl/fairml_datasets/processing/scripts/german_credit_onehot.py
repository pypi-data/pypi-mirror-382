from pathlib import Path
from typing import List
from .. import LoadingScript

import pandas as pd


# COMPAS Variant
# Source: https://github.com/alangee/FaiR-N/
class Script(LoadingScript):
    def load(self, locations: List[Path]) -> pd.DataFrame:
        # Stitch together all dataframes
        df_data = pd.read_csv(locations[0])
        df_labels = pd.read_csv(locations[1])

        # Concat data and labels
        df = pd.concat([df_data, df_labels], axis=1)

        return df
