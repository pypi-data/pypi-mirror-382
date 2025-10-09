from typing import List
from .. import LoadingScript
from pathlib import Path

import pandas as pd

from .helpers.folktables import load_folktables_dataset


class Script(LoadingScript):
    def load(self, locations: List[Path]) -> pd.DataFrame:
        return load_folktables_dataset("ACSIncome")
