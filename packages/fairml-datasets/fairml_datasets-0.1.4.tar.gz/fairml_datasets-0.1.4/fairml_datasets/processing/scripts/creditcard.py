from typing import List
from .. import LoadingScript
from pathlib import Path

import pandas as pd


# CreditCard
class Script(LoadingScript):
    def load(self, locations: List[Path]) -> pd.DataFrame:
        # Skip the first row
        return pd.read_excel(locations[0], header=1)
