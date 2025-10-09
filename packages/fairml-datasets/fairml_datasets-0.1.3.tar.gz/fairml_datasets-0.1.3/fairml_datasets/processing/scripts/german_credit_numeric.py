from typing import List
from .. import LoadingScript
from pathlib import Path

import pandas as pd


class Script(LoadingScript):
    def load(self, locations: List[Path]) -> pd.DataFrame:
        column_names = [
            "feat_1",
            "feat_2",
            "feat_3",
            "feat_4",
            "feat_5",
            "feat_6",
            "feat_7",
            "feat_8",
            "feat_9",
            "age",
            "feat_11",
            "feat_12",
            "feat_13",
            "feat_14",
            "feat_15",
            "feat_16",
            "feat_17",
            "feat_18",
            "feat_19",
            "feat_20",
            "feat_21",
            "feat_22",
            "feat_23",
            "feat_24",
            "credit",
        ]

        return pd.read_fwf(locations[0], names=column_names)
