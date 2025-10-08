from __future__ import annotations

from abc import ABC
from datetime import datetime
from typing import Any, cast

from sapiopylib.rest.pojo.eln.SapioELNEnums import ElnExperimentStatus, ExperimentEntryStatus
from sapiopylib.rest.utils.SapioDateUtils import java_millis_to_datetime


class AbstractElnESignature(ABC):
    exp_id: int
    username: str
    timestamp: datetime
    comments: str | None
    approval_due_date: datetime | None

    def __init__(self, exp_id: int, username: str, timestamp: datetime, comments: str, approval_due_date: datetime):
        self.exp_id = exp_id
        self.username = username
        self.timestamp = timestamp
        self.comments = comments
        self.approval_due_date = approval_due_date

    def __str__(self):
        return "Signed by " + self.username + " at " + str(self.timestamp)

class ElnExperimentESignature(AbstractElnESignature):
    status: ElnExperimentStatus

    def __init__(self, status: ElnExperimentStatus,
                 exp_id: int, username: str, timestamp: datetime, comments: str, approval_due_date: datetime):
        super().__init__(exp_id, username, timestamp, comments, approval_due_date)
        self.status = status

    def __str__(self):
        return super().__str__() + " with status " + self.status.name

class ExperimentEntryESignature(AbstractElnESignature):
    status: ExperimentEntryStatus
    entry_id: int

    def __init__(self, status: ExperimentEntryStatus, entry_id: int,
                 exp_id: int, username: str, timestamp: datetime, comments: str, approval_due_date: datetime):
        super().__init__(exp_id, username, timestamp, comments, approval_due_date)
        self.status = status
        self.entry_id = entry_id

    def __str__(self):
        return super().__str__() + " with status " + self.status.name

class ElnESignatureParser:

    @staticmethod
    def parse(json_dct: dict[str, Any]) -> AbstractElnESignature:
        exp_id: int = int(json_dct.get('notebookExperimentId'))
        username: str = json_dct.get('username')
        timestamp: datetime = java_millis_to_datetime(json_dct.get('timestamp'))
        comments: str | None = json_dct.get('comments')
        due_date: datetime = java_millis_to_datetime(json_dct.get('approvalDueDate'))
        discriminator: str = json_dct.get("@type")
        if 'NotebookExperimentESignaturePojo' == discriminator:
            status_str: str = json_dct.get('notebookExperimentStatus')
            status: ElnExperimentStatus = cast(ElnExperimentStatus, ElnExperimentStatus[status_str])
            return ElnExperimentESignature(status,
                                           exp_id, username, timestamp, comments, due_date)
        elif 'ExperimentEntryESignaturePojo' == discriminator:
            status_str: str = json_dct.get('experimentEntryStatus')
            status: ExperimentEntryStatus = cast(ExperimentEntryStatus, ExperimentEntryStatus[status_str])
            entry_id: int = json_dct.get('experimentEntryId')
            return ExperimentEntryESignature(status, entry_id,
                                             exp_id, username, timestamp, comments, due_date)

