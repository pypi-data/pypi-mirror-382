import abc
from typing import Type, Any
from weakref import WeakKeyDictionary

from sapiopylib.rest.User import SapioUser

class _SapioAbstractMeta(abc.ABCMeta):
    _instances: WeakKeyDictionary[SapioUser, dict[Type, Any]] = WeakKeyDictionary()

    def __call__(cls, *args, **kwargs):
        # Assume the user is passed as the first argument or as a 'user' keyword arg
        user: SapioUser
        if args:
            user = args[0]
        elif 'user' in kwargs:
            user = kwargs['user']
        else:
            raise ValueError("User identifier must be provided as the first argument or 'user' keyword.")
        if not isinstance(user, SapioUser):
            raise TypeError("The first argument or 'user' keyword must be an instance of SapioUser.")

        if user not in cls._instances:
            cls._instances[user] = {}
        class_impl_dict = cls._instances[user]
        if cls not in class_impl_dict:
            class_impl_dict[cls] = super(_SapioAbstractMeta, cls).__call__(*args, **kwargs)
        return class_impl_dict[cls]

class SapioContextManager(abc.ABC, metaclass=_SapioAbstractMeta):
    """
    This singleton class includes both the user context along with commonly used managers in Sapio.
    """
    _user: SapioUser

    @property
    def user(self) -> SapioUser:
        """
        Return the user context object.
        """
        return self._user

    def __init__(self, user: SapioUser):
        if not isinstance(user, SapioUser):
            raise TypeError("The user must be an instance of SapioUser.")
        self._user = user

