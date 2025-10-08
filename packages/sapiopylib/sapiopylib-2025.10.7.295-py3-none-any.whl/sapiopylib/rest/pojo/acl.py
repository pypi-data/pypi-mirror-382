# This module includes basic ACL data structures in Sapio.
from __future__ import annotations

from enum import Enum
from typing import Any

from sapiopylib.rest.pojo.DataRecord import DataRecord


class AccessType(Enum):
    """
    All access types that are visible to webservice.

    This is used both in record ACL and data type access.
    """
    READ = "Read", 0
    WRITE = "Write", 1
    DELETE = "Delete", 2
    OWNER = "Owner", 5
    ACLMGMT = "ACL Management", 6

    display_name: str
    access_type_id: int

    def __init__(self, display_name: str, access_type_id: int):
        self.display_name = display_name
        self.access_type_id = access_type_id


class DataRecordAccess:
    """
    The access control list for a data record.  This object contains the access level for a single user or group to this data record.

    Attributes:
        new_access: Indicates that access to this data record is new, previously did not have access
        access_changed: Indicates that this access has changed
        access_list: The map of access control for this data record.  This is a map from AccessType to a boolean indicating whether the user or group has that access.
    """
    _new_access: bool
    _access_changed: bool
    _access_list: dict[AccessType, bool]

    def __init__(self, is_new: bool = False):
        self._access_list: dict[AccessType, bool] ={
            AccessType.READ: False,
            AccessType.WRITE: False,
            AccessType.DELETE: False,
            AccessType.OWNER: False,
            AccessType.ACLMGMT: False
        }
        self._new_access = is_new
        self._access_changed = False

    def has_access(self, access_type: AccessType) -> bool:
        """
        Get whether a particular access type is allowed.
        """
        access: bool | None = self._access_list.get(access_type)
        return access is not None and access

    def set_access(self, access_type: AccessType, allow_access: bool):
        """
        Set the access level for a particular access type.
        """
        self._access_changed = True
        if allow_access:
            if access_type is AccessType.OWNER:
                self._access_list[AccessType.OWNER] = True
            elif access_type is AccessType.ACLMGMT:
                self._access_list[AccessType.ACLMGMT] = True
            if access_type is AccessType.READ or access_type is AccessType.WRITE or access_type is AccessType.DELETE:
                self._access_list[AccessType.READ] = True
            if access_type is AccessType.WRITE or access_type is AccessType.DELETE:
                self._access_list[AccessType.WRITE] = True
            if access_type is AccessType.DELETE:
                self._access_list[AccessType.DELETE] = True
        else:
            if access_type is AccessType.OWNER:
                self._access_list[AccessType.OWNER] = False
            elif access_type is AccessType.ACLMGMT:
                self._access_list[AccessType.ACLMGMT] = False
            if access_type is AccessType.DELETE or access_type is AccessType.WRITE or AccessType is AccessType.READ:
                self._access_list[AccessType.DELETE] = False
            if access_type is AccessType.WRITE or AccessType is AccessType.READ:
                self._access_list[AccessType.WRITE] = False
            if access_type is AccessType.READ:
                self._access_list[AccessType.READ] = False

    @property
    def access_changed(self) -> bool:
        return self._access_changed

    @property
    def new_access(self) -> bool:
        return self._new_access

    def to_json(self) -> dict[str, Any]:
        access_json_list: dict[str, bool] = dict()
        for key, value in self._access_list.items():
            access_json_list[key.name] = value
        return {
            "newAccess": self._new_access,
            "accessChanged": self._access_changed,
            "accessList": access_json_list
        }

    @staticmethod
    def from_json(json_dct: dict[str, Any]) -> DataRecordAccess:
        access_json_list: dict[str, bool] = json_dct.get('accessList')
        access_list: dict[AccessType, bool] = dict()
        for type_name, is_granted in access_json_list.items():
            access_list[AccessType[type_name]] = is_granted

        ret = DataRecordAccess()
        ret._new_access = json_dct.get('newAccess')
        ret._access_changed = json_dct.get('accessChanged')
        ret._access_list = access_list
        return ret

    def __hash__(self):
        return hash((self._new_access, self._access_changed, self._access_list))

    def __eq__(self, other):
        if not isinstance(other, DataRecordAccess):
            return False
        return (other._new_access == self._new_access and other._access_changed == self._access_changed and
                other._access_list == self._access_list)


class DataRecordACL:
    """
    The access control list for a data record.  This object contains the access control for a single data record
    that can be inherited to its children.  This object contains access for both users and groups in the system.
    """
    _acl_id: int
    _base_record_id: int | None
    _data_record_access_map: dict[str, DataRecordAccess]
    _group_data_record_access_map: dict[int, DataRecordAccess]

    def __init__(self):
        self._acl_id = -1
        self._base_record_id = None
        self._data_record_access_map = dict()
        self._group_data_record_access_map = dict()

    @property
    def acl_id(self) -> int:
        """
        Get the unique ID for this access control list.
        """
        return self._acl_id

    @property
    def base_record_id(self) -> int:
        """
        The record id that this access control list is associated with.  This is the top-level record id that this access control list is associated with.
        """
        return self._base_record_id

    def get_user_access(self, username: str) -> DataRecordAccess:
        """
        Get the access associated with the user. If there is no object mapped to user yet, then one will be created with no access.
        In this case, the newly created object will not be in the map yet so we should set it using set_user_access if we want to make modifications on it.
        :param username: The user to retrieve user access for.
        """
        access = self._data_record_access_map.get(username)
        if access is None:
            access = DataRecordAccess()
        return access

    def set_user_access(self, username: str, access: DataRecordAccess) -> None:
        """
        Set the access for the provided user. This will replace any existing access for the user.
        :param username: The user to overwrite its access.
        :param access: The access permission details.
        """
        self._data_record_access_map[username] = access

    def update_user_access(self, username: str, access_type: AccessType, grant: bool) -> None:
        """
        Set the user's access to a specific access type. Note this will NOT overwrite existing ACL on user that is unrelated to the permission.
        :param username: The username of the user to set the access level for.
        :param access_type: The type of access to set for this user.
        :param grant: Whether to grant or revoke access to the provided access type
        """
        access = self._data_record_access_map.get(username)
        if access is None:
            access = DataRecordAccess()
        access.set_access(access_type, grant)
        self.set_user_access(username, access)

    def get_group_access(self, group_id: int):
        """
        Get the access that is associated with the provided group. If no object is mapped to the group yet, then
        one will be created with no access. The newly created object will not be added to the access map so any changes
        made to the object should be set using the access.

        :param group_id: The ID of the group to get access object for.
        :return: The access details for the provided group in the referenced data record.
        """
        access = self._group_data_record_access_map.get(group_id)
        if access is None:
            access = DataRecordAccess()
        return access

    def set_group_access(self, group_id: int, access: DataRecordAccess) -> None:
        """
        Set the access for the provided group. This will replace any access that was previously set for the provided group ID.
        :param group_id: The group ID to associate the access object with.
        :param access: The access object to be associated with the group.
        """
        self._group_data_record_access_map[group_id] = access

    def update_group_access(self, group_id: int, access_type: AccessType, grant: bool) -> None:
        """
        Set the group's access for a specific access type.
        :param group_id: The ID of the group to set access for.
        :param access_type: THe type of access to be set.
        :param grant: Whether we are granting or revoking.
        """
        access = self._group_data_record_access_map.get(group_id)
        if access is None:
            access = DataRecordAccess()
        access.set_access(access_type, grant)
        self.set_group_access(group_id, access)

    def to_json(self) -> dict[str, Any]:
        return {
            "aclId": self._acl_id,
            "baseRecordId": self._base_record_id,
            "dataRecordAccessMap": {k: v.to_json() for k, v in self._data_record_access_map.items() if k is not None and v is not None},
            "groupDataRecordAccessMap": {k: v.to_json() for k, v in self._group_data_record_access_map.items() if k is not None and v is not None}
        }

    @staticmethod
    def from_json(json_dct: dict[str, Any]) -> DataRecordACL:
        ret: DataRecordACL = DataRecordACL()
        ret._acl_id = int(json_dct.get('aclId'))
        if json_dct.get('baseRecordId'):
            ret._base_record_id = int(json_dct.get('baseRecordId'))
        if json_dct.get('dataRecordAccessMap'):
            ret._data_record_access_map = {k: DataRecordAccess.from_json(v) for k, v in json_dct.get('dataRecordAccessMap').items() if k is not None and v is not None}
        if json_dct.get('groupDataRecordAccessMap'):
            ret._group_data_record_access_map = {k: DataRecordAccess.from_json(v) for k, v in json_dct.get('groupDataRecordAccessMap').items() if k is not None and v is not None}
        return ret

class SetDataRecordACLCriteria:
    """
    Criteria for setting DataRecordACLs.  The two lists must be the same size.
    The first list is the data records to set ACLs for, and the second list is the DataRecordACLs to set.
    The DataRecordACLs must be in the same order as the data records.
    """
    data_record_list: list[DataRecord]
    data_record_acl_list: list[DataRecordACL]

    def __init__(self, data_record_list: list[DataRecord], data_record_acl_list: list[DataRecordACL]):
        self.data_record_list = data_record_list
        self.data_record_acl_list = data_record_acl_list

    def to_json(self) -> dict[str, Any]:
        return {
            'dataRecords': [x.to_json() for x in self.data_record_list],
            'dataRecordACLs': [x.to_json() for x in self.data_record_acl_list]
        }

