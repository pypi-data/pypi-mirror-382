"""
Scenario module for fairness datasets.

A scenario represents a specific fairness analysis configuration for a dataset,
typically focusing on specific sensitive attributes or fairness concerns.
"""

from typing import List

from .dataset import Dataset


class Scenario(Dataset):
    """
    A specialized version of Dataset with specific sensitive columns.

    The Scenario class extends Dataset to focus analysis on particular
    sensitive attributes, enabling targeted fairness evaluations.
    """

    def __init__(self, dataset: Dataset | str, sensitive_columns: List[str]):
        """
        Initialize a Scenario with a dataset and specific sensitive columns.

        Args:
            dataset: Either a Dataset object or a dataset id (string)
            sensitive_columns: List of column names to use as sensitive attributes
        """
        if not isinstance(dataset, Dataset):
            dataset = Dataset.from_id(dataset)

        # create same dataset, but overwrite sensitive attributes
        super().__init__(dataset.info)

        self._sensitive_columns = sensitive_columns

    @staticmethod
    def from_id(scenario_id: str) -> "Scenario":
        """
        Create a Scenario object using a scenario id.

        Scenario ids follow a strict format, represented as a f-string, it would
        look as follows: "{dataset_id}:{';'.join(sensitive_columns)}". Sensitive
        columns can contain any special characters except semicolons and colons,
        but they must match column names *exactly*.

        Args:
            id: The scenario's id

        Returns:
            Scenario: A Scenario object
        """
        dataset_id, sensitive_columns_str = scenario_id.split(":")
        sensitive_columns = sensitive_columns_str.split(";")

        return Scenario(dataset_id, sensitive_columns)
