from __future__ import annotations

from functools import total_ordering
from typing import Optional, Dict, Any


@total_ordering
class ElnEntryPosition:
    """
    Describes the position of an entry to be added to the Experiment.
    """
    tab_id: Optional[int]
    order: Optional[int]
    column_span: Optional[int]
    column_order: Optional[int]

    def __init__(self, tab_id: Optional[int], order: Optional[int],
                 column_span: Optional[int] = None, column_order: Optional[int] = None):
        self.tab_id = tab_id
        self.order = order
        self.column_span = column_span
        self.column_order = column_order

    def to_json(self) -> Dict[str, Any]:
        return {
            'notebookExperimentTabId': self.tab_id,
            'order': self.order,
            'columnSpan': self.column_span,
            'columnOrder': self.column_order
        }

    @staticmethod
    def from_json(json_dct: Dict[str, Any]) -> ElnEntryPosition:
        tab_id: Optional[int] = json_dct.get('notebookExperimentTabId')
        order: Optional[int] = json_dct.get('order')
        column_span: Optional[int] = json_dct.get('columnSpan')
        column_order: Optional[int] = json_dct.get('columnOrder')
        return ElnEntryPosition(tab_id, order,
                                column_span=column_span, column_order=column_order)

    def __eq__(self, other):
        if not isinstance(other, ElnEntryPosition):
            return False
        return self.tab_id == other.tab_id and \
               self.order == other.order and \
               self.column_span == other.column_span and \
               self.column_order == other.column_order

    def __lt__(self, other):
        if not isinstance(other, ElnEntryPosition):
            return False
        # Note that tab ID doesn't equate to tab order.
        if self.tab_id != other.tab_id:
            return self.tab_id < other.tab_id
        if self.order != other.order:
            return self.order < other.order
        return self.column_span < other.column_span


ExperimentEntryPosition = ElnEntryPosition

