from __future__ import annotations

from weakref import WeakValueDictionary

from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.session import SessionInfo, AuditLogEntry


class SessionManager:
    """
    Obtains and manages the current list of user sessions in the system.
    This is typically administrative function.
    """
    user: SapioUser

    __instances: WeakValueDictionary[SapioUser, SessionManager] = WeakValueDictionary()
    __initialized: bool

    def __new__(cls, user: SapioUser):
        """
        Observes singleton pattern per record model manager object.

        :param user: The user that will make the webservice request to the application.
        """
        obj = cls.__instances.get(user)
        if not obj:
            obj = object.__new__(cls)
            obj.__initialized = False
            cls.__instances[user] = obj
        return obj

    def __init__(self, user: SapioUser):
        """
        Obtain a user manager for retrieving information about users in the system.

        :param user: The user that will make the webservice request to the application.
        """
        if self.__initialized:
            return
        self.user = user
        self.__initialized = True

    def get_session_info_list(self) -> list[SessionInfo]:
        """
        Obtains all currently online sessions info to see who and how many users are online.
        """
        sub_path = '/system/session_info'
        response = self.user.get(sub_path)
        self.user.raise_for_status(response)
        return [SessionInfo.from_json(x) for x in response.json()]

    def kill_session(self, session_id: str):
        """
        Kills the given user session ID. It will pass without incident even if the ID is not valid.
        However, an exception code 403 status will be thrown if user does not have sufficient access.
        """
        sub_path = '/system/kill_session'
        response = self.user.post(sub_path, payload=session_id, is_payload_plain_text=True)
        self.user.raise_for_status(response)

    def insert_audit_log(self, audit_log_list: list[AuditLogEntry]) -> None:
        """
        Insert the list of provided audit log entries into the audit log.  These entries will be inserted as "INFO" rows
         in the audit log table with the current user as the session who made the change at the current timestamp.
        """
        sub_path = '/system/audit_log/insert_events'
        payload = [x.to_json() for x in audit_log_list]
        response = self.user.post(sub_path, payload=payload)
        self.user.raise_for_status(response)
