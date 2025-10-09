from typing import List
from .. import PreparationScript, LoadingScript
from pathlib import Path

import pandas as pd


class Script(PreparationScript, LoadingScript):
    def load(self, locations: List[Path]) -> pd.DataFrame:
        column_names = [
            "id",  # 1
            "age",  # 2
            "gender",  # 3
            "education",  # 4
            "country",  # 5
            "ethnicity",  # 6
            "nscore",  # 7
            "escore",  # 8
            "oscore",  # 9
            "ascore",  # 10
            "cscore",  # 11
            "impulsive",  # 12
            "ss",  # 13
            "alcohol",  # 14
            "amphet",  # 15
            "amyl",  # 16
            "benzos",  # 17
            "caff",  # 18
            "cannabis",  # 19
            "choc",  # 20
            "coke",  # 21
            "crack",  # 22
            "ecstasy",  # 23
            "heroin",  # 24
            "ketamine",  # 25
            "legalh",  # 26
            "lsd",  # 27
            "meth",  # 28
            "mushrooms",  # 29
            "semer",  # 30
            "nicotine",  # 31
            "vsa",  # 32
        ]

        return pd.read_csv(
            locations[0],
            names=column_names,
            dtype={
                "age": "str",
                "gender": "str",
                "education": "str",
                "country": "str",
                "ethnicity": "str",
            },
        )

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        replacement_map = {
            "age": {
                "-0.95197": "18-24",
                "-0.07854": "25-34",
                "0.49788": "35-44",
                "1.09449": "45-54",
                "1.82213": "55-64",
                "2.59171": "65+",
            },
            "gender": {"0.48246": "Female", "-0.48246": "Male"},
            "education": {
                "-2.43591": "Left school before 16 years",
                "-1.73790": "Left school at 16 years",
                "-1.43719": "Left school at 17 years",
                "-1.22751": "Left school at 18 years",
                "-0.61113": "Some college or university, no certificate or degree",
                "-0.05921": "Professional certificate/ diploma",
                "0.45468": "University degree",
                "1.16365": "Masters degree",
                "1.98437": "Doctorate degree",
            },
            "country": {
                "-0.09765": "Australia",
                "0.24923": "Canada",
                "-0.46841": "New Zealand",
                "-0.28519": "Other",
                "0.21128": "Republic of Ireland",
                "0.96082": "UK",
                "-0.57009": "USA",
            },
            "ethnicity": {
                "-0.50212": "Asian",
                "-1.10702": "Black",
                "1.90725": "Mixed-Black/Asian",
                "0.12600": "Mixed-White/Asian",
                "-0.22166": "Mixed-White/Black",
                "0.11440": "Other",
                "-0.31685": "White",
            },
        }
        df.replace(replacement_map, inplace=True)

        return df
