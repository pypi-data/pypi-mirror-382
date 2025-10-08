from __future__ import annotations

from typing import List, Dict, Any
from weakref import WeakValueDictionary

from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.Picklist import PickListConfig, PicklistParser


class PicklistManager:
    """
    Manages picklists in Sapio.
    """
    user: SapioUser
    __instances: WeakValueDictionary[SapioUser, PicklistManager] = WeakValueDictionary()
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
        Obtain a pick list manager for reading from and writing to or creating pick lists in the system.

        :param user: The user that will make the webservice request to the application.
        """
        if self.__initialized:
            return
        self.user = user
        self.__initialized = True

    def get_picklist_config_list(self) -> List[PickListConfig]:
        """
        Get every pick list configuration in the system.

        :return: A list of all pick list configurations from the system.
        """
        sub_path: str = '/picklist/getConfigList'
        response = self.user.get(sub_path)
        self.user.raise_for_status(response)
        json_list: List[Dict[str, Any]] = response.json()
        return [PicklistParser.parse_picklist_config(x) for x in json_list]

    def get_picklist(self, picklist_name: str) -> PickListConfig | None:
        """
        Get the picklist by the provided picklist name.
        :param picklist_name The name of the picklist to search for.
        :return Return None object if the picklist is not found in the system. Otherwise, return the picklist values.
        """
        sub_path: str = self.user.build_url(['picklist', 'getConfig', picklist_name])
        response = self.user.get(sub_path)
        self.user.raise_for_status(response)
        if response.status_code == 201 or response.status_code == 204:
            return None
        json: Dict[str, Any] = response.json()
        return PicklistParser.parse_picklist_config(json)


    def update_picklist_value_list(self, pick_list_name: str, pick_list_new_value_list: List[str]) \
            -> PickListConfig:
        """
        Update the specified pick list config in the system.

        :param pick_list_name: The name of the pick list to update. If there is no picklist with this name, then a new
            pick list will be created with this name.
        :param pick_list_new_value_list: The list of values in the pick list.
        :return: The updated or new pick list configuration object.
        """
        sub_path = self.user.build_url(['picklist', 'updateConfigValueList', pick_list_name])
        response = self.user.post(sub_path, payload=pick_list_new_value_list)
        self.user.raise_for_status(response)
        json_dct = response.json()
        return PicklistParser.parse_picklist_config(json_dct)


# Alias classes
PickListManager: type = PicklistManager
