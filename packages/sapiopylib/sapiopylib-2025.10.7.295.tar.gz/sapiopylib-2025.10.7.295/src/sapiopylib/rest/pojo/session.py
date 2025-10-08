from __future__ import annotations

from typing import Any


class SessionInfo:
    """
    Session Info data for a single session.
    """
    session_id: str
    username: str

    def __init__(self, session_id: str, username: str):
        self.session_id = session_id
        self.username = username

    @staticmethod
    def from_json(json_dct: dict[str, Any]):
        session_id = json_dct.get('sessionId')
        username = json_dct.get('userName')
        return SessionInfo(session_id, username)

    def __str__(self):
        return self.session_id + " (" + self.username + ")"

    def __repr__(self):
        return self.session_id

    def __eq__(self, other):
        if not isinstance(other, SessionInfo):
            return False
        return self.session_id == other.session_id and self.username == other.username

    def __hash__(self):
        return hash((self.session_id, self.username))


class AuditLogEntry:
    """
    The audit log entry POJO of a single row of audit log.
    """
    data_type_name: str
    record_id: int
    data_record_name: str
    description: str

    def __init__(self, data_type_name: str, record_id: int, data_record_name: str, description: str):
        self.data_type_name = data_type_name
        self.record_id = record_id
        self.data_record_name = data_record_name
        self.description = description

    def __str__(self):
        data_record_name: str | None = self.data_record_name
        if not data_record_name:
            data_record_name = self.data_type_name + " " + str(self.record_id)
        return data_record_name + ": " + self.description

    def __repr__(self):
        return self.__str__()

    def to_json(self) -> dict[str, Any]:
        return {
            'dataTypeName': self.data_type_name,
            'recordId': self.record_id,
            'dataRecordName': self.data_record_name,
            'description': self.description
        }
