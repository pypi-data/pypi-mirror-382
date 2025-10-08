from .. import PreparationScript

import pandas as pd


# COMPAS
class Script(PreparationScript):
    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        # Default filtering
        # Code from https://github.com/Trusted-AI/AIF360/blob/main/aif360/datasets/compas_dataset.py
        # based on https://github.com/propublica/compas-analysis/blob/master/Compas%20Analysis.ipynb
        return df[
            (df.days_b_screening_arrest <= 30)
            & (df.days_b_screening_arrest >= -30)
            & (df.is_recid != -1)
            & (df.c_charge_degree != "O")
            & (df.score_text != "N/A")
        ]
