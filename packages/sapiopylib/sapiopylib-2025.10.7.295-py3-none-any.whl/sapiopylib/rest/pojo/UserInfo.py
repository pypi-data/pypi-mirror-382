from __future__ import annotations

import base64
import json
from typing import List, Optional, Dict, Any


class UserInfoCriteria:
    include_deactivated_users: bool
    load_profile_image: bool
    username_whitelist: Optional[List[str]]

    def __init__(self, include_deactivated_users: bool = False,
                 load_profile_image: bool = False,
                 username_whitelist: Optional[List[str]] = None):
        self.include_deactivated_users = include_deactivated_users
        self.load_profile_image = load_profile_image
        if username_whitelist:
            self.username_whitelist = username_whitelist
        else:
            self.username_whitelist = None

    def to_json(self) -> Dict[str, Any]:
        return {
            'includeDeactivatedUsers': self.include_deactivated_users,
            'loadProfileImage': self.load_profile_image,
            'usernameWhiteList': self.username_whitelist
        }

    def __str__(self):
        return json.dumps(self.to_json())


class UserInfo:
    """
    Contains detailed data about a user in Sapio system.

    For additional info, try querying VeloxUser record for non-api users.
    """
    username: str
    first_name: Optional[str]
    middle_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    group_map: Dict[int, str]
    api_user: bool
    profile_image: Optional[bytes]
    job_title: Optional[str]
    user_record_id: Optional[int]
    active: bool
    locked: bool

    def __init__(self, username: str, first_name: Optional[str], middle_name: Optional[str], last_name: Optional[str],
                 email: Optional[str], group_map: Dict[int, str], api_user: bool, profile_image: Optional[bytes],
                 job_title: Optional[str], user_record_id: Optional[int], active: bool, locked: bool):
        self.username = username
        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name
        self.email = email
        self.group_map = group_map
        self.api_user = api_user
        self.profile_image = profile_image
        self.job_title = job_title
        self.user_record_id = user_record_id
        self.active = active
        self.locked = locked

    @staticmethod
    def parse(json_dct: Dict[str, Any]):
        username: str = json_dct.get('username')
        first_name: Optional[str] = json_dct.get('firstName')
        middle_name: Optional[str] = json_dct.get('middleName')
        last_name: Optional[str] = json_dct.get('lastName')
        email: Optional[str] = json_dct.get('emailAddress')
        group_map: Dict[int, str] = json_dct.get('groupMap')
        api_user: bool = json_dct.get('apiUser')
        profile_image: Optional[bytes] = None
        profile_image_base64 = json_dct.get('profileImage')
        if profile_image_base64:
            profile_image = base64.b64decode(profile_image_base64)
        job_title: Optional[str] = json_dct.get('jobTitle')
        user_record_id: Optional[int] = json_dct.get('userRecordId')
        active: bool = json_dct.get('active')
        locked: bool = json_dct.get('locked')
        return UserInfo(username=username, first_name=first_name,
                        middle_name=middle_name, last_name=last_name,
                        email=email, group_map=group_map, api_user=api_user, profile_image=profile_image,
                        job_title=job_title, user_record_id=user_record_id, active=active, locked=locked)


class UserGroupInfo:
    """
    POJO that represents details about a UserGroup from within the system.
    """
    group_id: int
    group_name: str
    default: bool
    client_plugin_path: Optional[str]
    limited_user_type_name: Optional[str]
    data_type_layout_map: dict[str, str]
    homepage_layout_name: str

    def __init__(self, group_id: int, group_name: str, default: bool, client_plugin_path: Optional[str],
                 limited_user_type_name: Optional[str], data_type_layout_map: dict[str, str],
                 homepage_layout_name: str):
        self.group_id = group_id
        self.group_name = group_name
        self.default = default
        self.client_plugin_path = client_plugin_path
        self.limited_user_type_name = limited_user_type_name
        self.data_type_layout_map = data_type_layout_map
        self.homepage_layout_name = homepage_layout_name

    @staticmethod
    def parse(json_dct: Dict[str, Any]) -> UserGroupInfo:
        group_id: int = json_dct.get('userGroupId')
        group_name: str = json_dct.get('userGroupName')
        default: bool = json_dct.get('default')
        client_plugin_path: Optional[str] = json_dct.get('clientPluginPath')
        limited_user_type_name: Optional[str] = json_dct.get('limitedUserTypeName')
        data_type_layout_map: dict[str, str] = json_dct.get('dataTypeLayoutMap')
        homepage_layout_name: str = json_dct.get('homepageLayoutName')
        return UserGroupInfo(group_id=group_id, group_name=group_name, default=default,
                             client_plugin_path=client_plugin_path, limited_user_type_name=limited_user_type_name,
                             data_type_layout_map=data_type_layout_map, homepage_layout_name=homepage_layout_name)
