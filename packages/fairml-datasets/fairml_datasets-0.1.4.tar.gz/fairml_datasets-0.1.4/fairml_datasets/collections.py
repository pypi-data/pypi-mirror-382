"""
Predefined collections of fairness scenarios.

This module provides specific implementations of the Collection classes
defined in collection.py. It includes utilities to generate scenarios and
predefined collections for common fairness analysis use cases.
"""

# The actual collections we include
from typing import List

from .scenario import Scenario
from .datasets import Datasets
from .dataset import Dataset
from .collection import Collection, PrespecifiedCollection


def generate_dataset_scenarios(
    dataset: Dataset, max_cols_intersection=3
) -> List[Scenario]:
    """
    Generate all Scenarios for a given dataset.

    Args:
        dataset: The dataset to generate scenarios for
        max_cols_intersection: The maximum number of sensitive columns to generate intersections for.
            If there are more sensitive columns, they will be used in isolation.

    Returns:
        List[Scenario]: A list of scenarios
    """
    cols_sensitive = dataset.get_all_sensitive_columns()
    if len(cols_sensitive) > max_cols_intersection:
        # Use only the separate columns, ignoring combinations
        col_combinations = [[col] for col in cols_sensitive]
    else:
        # Use all combinations of sensitive columns (incl. intersections)
        col_combinations = dataset.generate_sensitive_intersections()

    # Convert column combinations to scenarios
    scenarios = [
        Scenario(dataset=dataset, sensitive_columns=sens) for sens in col_combinations
    ]
    return scenarios


class Corpus(Collection):
    """
    The full corpus including all scenarios and datasets.

    This collection contains all available datasets and their associated scenarios,
    providing a comprehensive set for fairness analysis across the entire corpus.
    """

    def __init__(self, inclue_large_datasets=True):
        """
        Initialize the Corpus with all available datasets and scenarios.

        Args:
            inclue_large_datasets: Whether to include datasets marked as 'large'
        """
        all_scenarios = []
        all_datasets = Datasets(inclue_large_datasets=inclue_large_datasets)
        for dataset in all_datasets:
            all_scenarios += generate_dataset_scenarios(dataset=dataset)

        super().__init__(scenarios=all_scenarios)


class DecorrelatedSmall(PrespecifiedCollection):
    """
    Collection of De-Correlated Datasets with k = 5.

    This corresponds to Scenarios described in Table 3 identified with a k.
    """

    scenario_ids = [
        "folktables_acspubliccoverage:RAC1P",
        "heart_disease:sex",
        "hmda:applicant_sex_name;applicant_race_name_1",
        "stop_question_and_frisk_data:SUSPECT_SEX;SUSPECT_RACE_DESCRIPTION; SUSPECT_REPORTED_AGE",
        "folktables_acsemployment_small:RAC1P",
    ]


class DecorrelatedLarge(PrespecifiedCollection):
    """
    Collection of De-Correlated Datasets with tau = 0.

    This corresponds to Scenarios described in Table 3 identified with a tau.
    """

    scenario_ids = [
        "folktables_acspubliccoverage:RAC1P",
        "heart_disease:sex",
        "hmda:applicant_sex_name;applicant_race_name_1",
        "stop_question_and_frisk_data:SUSPECT_SEX;SUSPECT_RACE_DESCRIPTION; SUSPECT_REPORTED_AGE",
        "folktables_acsemployment_small:RAC1P",
        "folktables_acstraveltime:RAC1P",
        "compas:sex;age",
        "folktables_acsincome_small:RAC1P",
        "compas_2_years:age",
        "communities_unnormalized:pct12-21",
        "arrhythmia:sex",
        "folktables_acspubliccoverage_small:RAC1P",
        "compas_2_years_violent:age",
        "south_german_credit:age;foreign_worker",
        "dutch:age",
        "folktables_acsmobility_small:RAC1P",
        "law_school_tensorflow:gender",
        "german_credit_onehot:<= 25 years",
        "communities:racePctAsian",
        "nursery:finance",
        "german_credit_numeric:age",
        "chicago_strategic_subject_list:RACE CODE CD",
    ]


class PermissivelyLicensedSmall(PrespecifiedCollection):
    """
    Collection of Permissively Licensed Datasets with k = 5.

    This corresponds to Scenarios described in Table 4 identified with a k.
    """

    scenario_ids = [
        "folktables_acspubliccoverage:RAC1P",
        "heart_disease:sex",
        "communities_unnormalized:pct12-21",
        "lipton_synthetic_hiring_dataset:sex",
        "bank:age;marital",
    ]


class PermissivelyLicensedLarge(PrespecifiedCollection):
    """
    Collection of Permissively Licensed Datasets with tau = 0.

    This corresponds to Scenarios described in Table 4 identified with a tau.
    """

    scenario_ids = [
        "folktables_acspubliccoverage:RAC1P",
        "heart_disease:sex",
        "communities_unnormalized:pct12-21",
        "lipton_synthetic_hiring_dataset:sex",
        "bank:age;marital",
        "german_credit_onehot:> 25 years",
        "folktables_acsincome:RAC1P",
        "south_german_credit:age",
        "folktables_acsemployment_small:RAC1P",
        "german_credit_numeric:age",
        "student:sex;age",
        "folktables_acstraveltime_small:RAC1P",
        "folktables_acspubliccoverage_small:RAC1P",
        "communities:agePct16t24",
        "folktables_acsmobility:RAC1P",
        "law_school_tensorflow:gender",
    ]


class PermissivelyLicensedFull(PrespecifiedCollection):
    """
    Full collection of Permissively Licensed Datasets.

    This corresponds to all Scenarios described in Table 4.
    """

    scenario_ids = [
        "folktables_acspubliccoverage:RAC1P",
        "heart_disease:sex",
        "communities_unnormalized:pct12-21",
        "lipton_synthetic_hiring_dataset:sex",
        "bank:age;marital",
        "german_credit_onehot:> 25 years",
        "folktables_acsincome:RAC1P",
        "south_german_credit:age",
        "folktables_acsemployment_small:RAC1P",
        "german_credit_numeric:age",
        "student:sex;age",
        "folktables_acstraveltime_small:RAC1P",
        "folktables_acspubliccoverage_small:RAC1P",
        "communities:agePct16t24",
        "folktables_acsmobility:RAC1P",
        "law_school_tensorflow:gender",
        "arrhythmia:sex",
        "adult:race",
        "nursery:finance;parents",
        "folktables_acsincome_small:RAC1P",
        "creditcard:SEX",
        "folktables_acsmobility_small:RAC1P",
        "student_language:age",
        "drug:ethnicity",
        "law_school_lequy:racetxt;male",
        "folktables_acstraveltime:RAC1P",
        "bank_additional_full:age;marital",
        "german_credit:foreign_worker",
        "generate_synthetic_data:s1",
        "bank_additional:age",
        "folktables_acsemployment:RAC1P",
        "bank_full:age",
    ]


class GeographicSmall(PrespecifiedCollection):
    """
    Collection of Geographically Diverse Datasets with k = 5.

    This corresponds to Scenarios described in Table 5 identified with a k.
    """

    scenario_ids = [
        "folktables_acspubliccoverage:RAC1P",
        "heart_disease:sex",
        "dutch:age;citizenship",
        "creditcard:SEX",
        "german_credit_onehot:> 25 years",
    ]


class GeographicLarge(PrespecifiedCollection):
    """
    Collection of Geographically Diverse Datasets with tau = 0.

    This corresponds to Scenarios described in Table 5 identified with a tau.
    """

    scenario_ids = [
        "folktables_acspubliccoverage:RAC1P",
        "heart_disease:sex",
        "dutch:age;citizenship",
        "creditcard:SEX",
        "german_credit_onehot:> 25 years",
        "student:sex",
    ]


class GeographicFull(PrespecifiedCollection):
    """
    Full collection of Geographically Diverse Datasets.

    This corresponds to all Scenarios described in Table 5.
    """

    scenario_ids = [
        "folktables_acspubliccoverage:RAC1P",
        "heart_disease:sex",
        "dutch:age;citizenship",
        "creditcard:SEX",
        "german_credit_onehot:> 25 years",
        "student:sex",
        "arrhythmia:sex",
        "nursery:finance;parents",
        "synth:sensible_feature",
        "drug:ethnicity",
    ]
