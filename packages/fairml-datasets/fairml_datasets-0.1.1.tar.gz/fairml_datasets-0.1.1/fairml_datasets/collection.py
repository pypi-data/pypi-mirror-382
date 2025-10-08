"""
Classes for managing collections of fairness scenarios.

This module provides classes to organize and iterate through groups of related
fairness scenarios, making it easier to run batch analyses across multiple datasets
with different sensitive attribute configurations.
"""

# Collection contains a list with scenarios and allows iterating over them
from typing import List

from .scenario import Scenario


class Collection:
    """
    A collection of fairness scenarios that can be iterated through.

    This class provides a way to group multiple related scenarios
    and perform batch operations or analyses across them.
    """

    scenarios: List[Scenario]

    def __init__(self, scenarios: List[Scenario]):
        """
        Initialize a Collection with a list of scenarios.

        Args:
            scenarios: List of Scenario objects
        """
        self.scenarios = scenarios

    def __iter__(self):
        """
        Make the Collection iterable, yielding each scenario in turn.

        Returns:
            Iterator over scenarios in the collection
        """
        return iter(self.scenarios)


class PrespecifiedCollection(Collection):
    """
    A collection of scenarios with predefined dataset and sensitive column configurations.

    This class derives from Collection and is designed to be subclassed with
    a specific 'info' attribute that defines which datasets and sensitive columns to use.
    """

    scenario_ids: List[str]

    def __init__(self):
        """
        Initialize a PrespecifiedCollection based on the predefined scenario ids.
        """
        # Generate scenarios based on info
        scenarios = [Scenario.from_id(scenario_id) for scenario_id in self.scenario_ids]
        super().__init__(scenarios)
