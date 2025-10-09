from .. import PreparationScript

import pandas as pd


class Script(PreparationScript):
    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        # Converted version of the original processing script:
        # read_SouthGermanCredit.R

        # Rename columns to match the specified names
        nam_evtree = [
            "status",
            "duration",
            "credit_history",
            "purpose",
            "amount",
            "savings",
            "employment_duration",
            "installment_rate",
            "personal_status_sex",
            "other_debtors",
            "present_residence",
            "property",
            "age",
            "other_installment_plans",
            "housing",
            "number_credits",
            "job",
            "people_liable",
            "telephone",
            "foreign_worker",
            "credit_risk",
        ]
        df.columns = nam_evtree

        # Specify numeric columns
        numeric_cols = [1, 4, 5, 12]

        # Make all non-numeric columns categorical
        for i in set(range(21)) - set(numeric_cols):
            df.iloc[:, i] = pd.Categorical(df.iloc[:, i])

        # Assign levels to categorical variables

        # `credit_risk`
        df["credit_risk"] = pd.Categorical(
            df["credit_risk"], categories=[0, 1], ordered=True
        )
        df["credit_risk"] = df["credit_risk"].cat.rename_categories(["bad", "good"])

        # `status`
        df["status"] = pd.Categorical(
            df["status"], categories=[1, 2, 3, 4], ordered=True
        ).rename_categories(
            [
                "no checking account",
                "... < 0 DM",
                "0<= ... < 200 DM",
                "... >= 200 DM / salary for at least 1 year",
            ]
        )

        # `credit_history`
        df["credit_history"] = pd.Categorical(
            df["credit_history"], categories=[0, 1, 2, 3, 4], ordered=True
        ).rename_categories(
            [
                "delay in paying off in the past",
                "critical account/other credits elsewhere",
                "no credits taken/all credits paid back duly",
                "existing credits paid back duly till now",
                "all credits at this bank paid back duly",
            ]
        )

        # `purpose`
        df["purpose"] = pd.Categorical(
            df["purpose"], categories=[0, 1, 2, 3, 4, 5, 6, 8, 9, 10], ordered=True
        ).rename_categories(
            [
                "others",
                "car (new)",
                "car (used)",
                "furniture/equipment",
                "radio/television",
                "domestic appliances",
                "repairs",
                "education",
                "retraining",
                "business",
            ]
        )

        # `savings`
        df["savings"] = pd.Categorical(
            df["savings"], categories=[1, 2, 3, 4, 5], ordered=True
        ).rename_categories(
            [
                "unknown/no savings account",
                "... < 100 DM",
                "100 <= ... < 500 DM",
                "500 <= ... < 1000 DM",
                "... >= 1000 DM",
            ]
        )

        # `other_debtors`
        df["other_debtors"] = pd.Categorical(
            df["other_debtors"], categories=[1, 2, 3], ordered=True
        ).rename_categories(["none", "co-applicant", "guarantor"])

        # `employment_duration`
        df["employment_duration"] = pd.Categorical(
            df["employment_duration"], categories=[1, 2, 3, 4, 5], ordered=True
        ).rename_categories(
            ["unemployed", "< 1 yr", "1 <= ... < 4 yrs", "4 <= ... < 7 yrs", ">= 7 yrs"]
        )

        # `installment_rate`
        df["installment_rate"] = pd.Categorical(
            df["installment_rate"], categories=[1, 2, 3, 4], ordered=True
        ).rename_categories([">= 35", "25 <= ... < 35", "20 <= ... < 25", "< 20"])

        # `personal_status_sex`
        df["personal_status_sex"] = pd.Categorical(
            df["personal_status_sex"], categories=[1, 2, 3, 4], ordered=True
        ).rename_categories(
            [
                "male : divorced/separated",
                "female : non-single or male : single",
                "male : married/widowed",
                "female : single",
            ]
        )

        # `present_residence`
        df["present_residence"] = pd.Categorical(
            df["present_residence"], categories=[1, 2, 3, 4], ordered=True
        ).rename_categories(
            ["< 1 yr", "1 <= ... < 4 yrs", "4 <= ... < 7 yrs", ">= 7 yrs"]
        )

        # `property`
        df["property"] = pd.Categorical(
            df["property"], categories=[1, 2, 3, 4], ordered=True
        ).rename_categories(
            [
                "unknown / no property",
                "car or other",
                "building soc. savings agr./life insurance",
                "real estate",
            ]
        )

        # `other_installment_plans`
        df["other_installment_plans"] = pd.Categorical(
            df["other_installment_plans"], categories=[1, 2, 3], ordered=True
        ).rename_categories(["bank", "stores", "none"])

        # `housing`
        df["housing"] = pd.Categorical(
            df["housing"], categories=[1, 2, 3], ordered=True
        ).rename_categories(["for free", "rent", "own"])

        # `number_credits`
        df["number_credits"] = pd.Categorical(
            df["number_credits"], categories=[1, 2, 3, 4], ordered=True
        ).rename_categories(["1", "2-3", "4-5", ">= 6"])

        # `job`
        df["job"] = pd.Categorical(
            df["job"], categories=[1, 2, 3, 4], ordered=True
        ).rename_categories(
            [
                "unemployed/unskilled - non-resident",
                "unskilled - resident",
                "skilled employee/official",
                "manager/self-empl./highly qualif. employee",
            ]
        )

        # `people_liable`
        df["people_liable"] = pd.Categorical(
            df["people_liable"], categories=[1, 2], ordered=True
        ).rename_categories(["3 or more", "0 to 2"])

        # `telephone`
        df["telephone"] = pd.Categorical(
            df["telephone"], categories=[1, 2], ordered=True
        ).rename_categories(["no", "yes (under customer name)"])

        # `foreign_worker`
        df["foreign_worker"] = pd.Categorical(
            df["foreign_worker"], categories=[1, 2], ordered=True
        ).rename_categories(["yes", "no"])

        return df
