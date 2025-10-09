from typing import List
from .. import PreparationScript, LoadingScript
from pathlib import Path

import pandas as pd
import numpy as np


class Script(PreparationScript, LoadingScript):
    default_options = {
        "personal_status_to_sex": False,  # Opts: True, False (This is generally a bad idea, since the information is not truly available)
        "age_to_binary": True,  # Opts: True, False
    }

    def load(self, locations: List[Path]) -> pd.DataFrame:
        column_names = [
            "status",
            "month",
            "credit_history",
            "purpose",
            "credit_amount",
            "savings",
            "employment",
            "investment_as_income_percentage",
            "personal_status",
            "other_debtors",
            "residence_since",
            "property",
            "age",
            "installment_plans",
            "housing",
            "number_of_credits",
            "skill_level",
            "people_liable_for",
            "telephone",
            "foreign_worker",
            "credit",
        ]

        return pd.read_csv(locations[0], sep=" ", names=column_names)

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.options["personal_status_to_sex"]:
            # Convert personal_status to sex
            replacement_map = {
                "personal_status": {
                    "A91": "male",
                    "A93": "male",
                    "A94": "male",
                    "A92": "female",
                    "A95": "female",
                }
            }
            df.replace(replacement_map, inplace=True)
            df.rename(columns={"personal_status": "sex"}, inplace=True)

        if self.options["age_to_binary"]:
            # Convert age to binary
            df["age"] = np.where(df["age"] > 25, "old", "young")

        return df
