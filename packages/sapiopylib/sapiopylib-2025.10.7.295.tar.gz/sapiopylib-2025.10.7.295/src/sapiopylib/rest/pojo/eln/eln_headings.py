from __future__ import annotations

from functools import total_ordering
from typing import Any


class ElnExperimentBanner:
    """
    An ELN Experiment Banner shows at the top of the experiment page.

    Attributes:
        html: The HTML text that may include also placeholders for parameters.
        parameters: The key will be a placeholder in the HTML and the value can be replaced by a plugin that updates banner.
    """
    html: str
    parameters: dict[str, str]

    def __init__(self, html: str, parameters: dict[str, str]):
        self.html = html
        self.parameters = parameters

    def to_json(self) -> dict[str, Any]:
        return {
            "htmlString": self.html,
            "htmlParameters": self.parameters
        }

    def __repr__(self):
        return str(self.to_json())

    def __str__(self):
        return str(self.to_json())

    @staticmethod
    def from_json(data: dict[str, Any]) -> ElnExperimentBanner:
        return ElnExperimentBanner(
            html=data.get("htmlString"),
            parameters=data.get("htmlParameters")
        )


@total_ordering
class ElnExperimentTab:
    tab_name: str
    tab_order: int | None
    max_number_of_columns: int | None
    tab_id: int

    def __init__(self, tab_name: str, tab_order: int | None, max_number_of_columns: int | None, tab_id: int):
        self.tab_name = tab_name
        self.tab_order = tab_order
        self.max_number_of_columns = max_number_of_columns
        self.tab_id = tab_id

    def to_json(self) -> dict[str, Any]:
        return {
            "tabName": self.tab_name,
            "tabOrder": self.tab_order,
            "maxNumberOfColumns": self.max_number_of_columns,
            "tabId": self.tab_id
        }

    @staticmethod
    def from_json(data: dict[str, Any]) -> ElnExperimentTab:
        return ElnExperimentTab(tab_name=data.get("tabName"),
                                tab_order=data.get("tabOrder"),
                                max_number_of_columns=data.get("maxNumberOfColumns"),
                                tab_id=data.get("tabId"))

    def __repr__(self):
        return str(self.to_json())

    def __str__(self):
        return str(self.to_json())

    def __eq__(self, other):
        if not isinstance(other, ElnExperimentTab):
            return False
        return self.tab_id == other.tab_id

    def __lt__(self, other):
        if not isinstance(other, ElnExperimentTab):
            return False
        return self.tab_order < other.tab_order

class ElnExperimentTabAddCriteria:
    """
    A request object containing necessary data to create a new experiment tab.
    """
    tab_name: str
    experiment_entry_id_list: list[int]

    def __init__(self, tab_name: str, experiment_entry_id_list: list[int]):
        self.tab_name = tab_name
        self.experiment_entry_id_list = experiment_entry_id_list

    def to_json(self) -> dict[str, Any]:
        return {
            "tabName": self.tab_name,
            "experimentEntryIdList": self.experiment_entry_id_list
        }
