from __future__ import annotations

from typing import List
from weakref import WeakValueDictionary

from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.UserInfo import UserInfoCriteria, UserInfo


class VeloxUserManager:
    """
    Obtains info for users in Sapio.
    """
    user: SapioUser

    __instances: WeakValueDictionary[SapioUser, VeloxUserManager] = WeakValueDictionary()
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

    def get_user_info_list(self, criteria: UserInfoCriteria = UserInfoCriteria()) -> List[UserInfo]:
        """
        Retrieve a list of user info data based on the given criteria.

        :param criteria: Search criteria that can be used to filter the search results.
        :return: A list of user info that matches the search criteria.
        """
        sub_path = '/user/infolist/'
        response = self.user.post(sub_path, payload=criteria.to_json())
        self.user.raise_for_status(response)
        json_dct_list = response.json()
        return [UserInfo.parse(x) for x in json_dct_list]

    def get_user_name_list(self, include_deactivated_users: bool = False) -> List[str]:
        """
        Get a list of all available usernames in the Sapio system.

        :param include_deactivated_users: Whether to include the users that are deactivated.
        :return: A list of all usernames in the system that match the search criteria.
        """
        sub_path = '/user/namelist/'
        params = {
            'includeDeactivatedUsers': include_deactivated_users
        }
        response = self.user.get(sub_path, params=params)
        self.user.raise_for_status(response)
        return response.json()
