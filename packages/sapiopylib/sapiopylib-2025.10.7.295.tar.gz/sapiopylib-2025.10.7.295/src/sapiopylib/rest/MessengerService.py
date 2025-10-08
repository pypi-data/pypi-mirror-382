from __future__ import annotations

from weakref import WeakValueDictionary

from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.Message import VeloxEmail, VeloxMessage, VeloxLogMessage


class SapioMessenger:
    """
    Send messages to users in Sapio. The message can be read later by user if offline.
    """
    user: SapioUser

    __instances: WeakValueDictionary[SapioUser, SapioMessenger] = WeakValueDictionary()
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
        Obtain a Sapio messenger to send emails and messages through the system.

        :param user: The user that will make the webservice request to the application.
        """
        if self.__initialized:
            return
        self.user = user
        self.__initialized = True

    def send_email(self, email: VeloxEmail) -> None:
        """
        Send an email using the SMTP server configured in the Sapio Platform.

        :param email: The details of the email to be sent by the platform.
        """
        sub_path = '/email/send/'
        response = self.user.post(sub_path, payload=email.to_json())
        self.user.raise_for_status(response)

    def send_message(self, message: VeloxMessage) -> None:
        """
        Send a message to users in the app based on username or group.

        :param message: The details of the message to be sent in the platform.
        """
        sub_path = '/message'
        response = self.user.post(sub_path, payload=message.to_json())
        self.user.raise_for_status(response)

    def log_message(self, log_message: VeloxLogMessage):
        """
        Logs a message into the log for this specific app.
        When logged it will include the timestamp and the username of the user who authorized the request.

        This should be functional even without client callback handles.
        :param log_message: The message to add to log of the app.
        """
        sub_path = '/system/log'
        response = self.user.post(sub_path, payload=log_message.to_json())
        self.user.raise_for_status(response)
