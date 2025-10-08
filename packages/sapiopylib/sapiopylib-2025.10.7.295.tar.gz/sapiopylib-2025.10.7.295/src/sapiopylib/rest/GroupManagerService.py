from __future__ import annotations

from typing import List, Dict, Any
from weakref import WeakValueDictionary

from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.UserInfo import UserGroupInfo, UserInfo


class VeloxGroupManager:
    """
    Obtains info for groups in Sapio.
    """
    user: SapioUser

    __instances: WeakValueDictionary[SapioUser, VeloxGroupManager] = WeakValueDictionary()
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
        Obtains a group manager to perform queries on group membership and info.

        :param user: The user that will make the webservice request to the application.
        """
        if self.__initialized:
            return
        self.user = user
        self.__initialized = True

    def get_user_group_name_list(self) -> List[str]:
        """
        Get the names of all groups in the system.

        :return: A list of the names for all user groups in the system.
        """
        sub_path = '/usergroup/namelist/'
        response = self.user.get(sub_path)
        self.user.raise_for_status(response)
        return response.json()

    def get_user_group_info_list(self) -> List[UserGroupInfo]:
        """
        Get the user group info for all groups in the system.

        :return: A list of user group info for all user groups in the system.
        """
        sub_path = '/usergroup/infolist/'
        response = self.user.get(sub_path)
        self.user.raise_for_status(response)
        return [UserGroupInfo.parse(x) for x in response.json()]

    def get_user_group_info_by_id(self, group_id: int) -> UserGroupInfo | None:
        """
        Get a user group's info by its group ID.

        :param group_id: The ID of a group in the system.
        :return: The user group info that matches the provided group ID.
        """
        sub_path = self.user.build_url(['usergroup', 'info', 'id', str(group_id)])
        response = self.user.get(sub_path)
        self.user.raise_for_status(response)
        if response.status_code == 204:
            return None
        return UserGroupInfo.parse(response.json())

    def get_user_group_info_by_name(self, group_name: str) -> UserGroupInfo | None:
        """
        Get a user group's info by its group name.

        :param group_name: The name of a group in the system.
        :return: The user group info that matches the provided group name.
        """
        sub_path = self.user.build_url(['usergroup', 'info', 'name', group_name])
        response = self.user.get(sub_path)
        if response.status_code == 204:
            return None
        self.user.raise_for_status(response)
        return UserGroupInfo.parse(response.json())

    def get_user_info_list_for_group(self, group_name: str) -> List[UserInfo]:
        """
        Given the group name, retrieve the user info list of all users who have membership in that group.

        :param group_name: The name of a group in the system.
        :return: A list of user info for every member in the provided group.
        """
        sub_path = self.user.build_url(['usergroup', 'userassignment', group_name])
        response = self.user.get(sub_path)
        self.user.raise_for_status(response)
        return [UserInfo.parse(x) for x in response.json()]

    def get_user_info_map_for_groups(self, group_names: List[str]) -> Dict[str, List[UserInfo]]:
        """
        Given a list of group names, retrieve the user info list of all users who have membership in those groups.

        :param group_names: A list of names of groups in the system.
        :return: A dictionary of user info for every member in the provided groups, mapped by group name.
        """
        sub_path = '/usergroup/userassignment/'
        response = self.user.post(sub_path, payload=group_names)
        self.user.raise_for_status(response)
        raw_json: Dict[str, List[Dict[str, Any]]] = response.json()
        ret: Dict[str, List[UserInfo]] = dict()
        for key, value in raw_json.items():
            user_info_list = [UserInfo.parse(x) for x in value]
            ret[key] = user_info_list
        return ret

    def get_user_group_info_list_for_user(self, username: str) -> List[UserGroupInfo] | None:
        """
        Get a list of user groups the given user has membership of.

        :param username: The username of a user in the system.
        :return: A list of user group info for every group that the given user is a member of. Return None if username does not exist in the system.
        """
        sub_path = self.user.build_url(['usergroup', 'groupassignment', username])
        response = self.user.get(sub_path)
        self.user.raise_for_status(response)
        if response.status_code == 204:
            return None
        return [UserGroupInfo.parse(x) for x in response.json()]
