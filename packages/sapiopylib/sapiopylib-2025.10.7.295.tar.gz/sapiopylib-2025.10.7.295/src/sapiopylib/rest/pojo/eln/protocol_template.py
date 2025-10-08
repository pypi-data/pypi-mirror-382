from __future__ import annotations

from datetime import datetime
from typing import Any

from sapiopylib.rest.pojo.eln.SapioELNEnums import *
from sapiopylib.rest.utils.SapioDateUtils import java_millis_to_datetime


class ProtocolTemplateQuery:
    """
    The search criteria used to look for ProtocolTemplateInfoPojo in the system.

    Attributes:
        protocol_template_id_whitelist: If specified, only retrieve protocol templates that match these IDs.
        protocol_template_id_blacklist: If specified, only retrieve protocol templates that do not match any of these IDs.
        latest_version_only: If the query should only return the latest versions of the templates.  This value defaults to true. If this is true, the query will only public templates.
        access_level_white_list: If specified, only retrieve the template info with these access levels. Note: This is still subject to user context permission implicitly. So the user may not be able to see private templates from other users.
        active_templates_only: If true, this query will only return active templates.  This value defaults to true.
    """
    protocol_template_id_whitelist: list[int] | None
    protocol_template_id_blacklist: list[int] | None
    latest_version_only: bool
    access_level_white_list: list[TemplateAccessLevel] | None
    active_templates_only: bool

    def __init__(self, whitelist_id: list[int] | None = None, blacklist_id: list[int] | None = None,
                 latest_version_only: bool = True, whitelist_access_levels: list[TemplateAccessLevel] | None = None,
                 active_templates_only: bool = True):
        self.protocol_template_id_whitelist = whitelist_id
        self.protocol_template_id_blacklist = blacklist_id
        self.latest_version_only = latest_version_only
        self.access_level_white_list = whitelist_access_levels
        self.active_templates_only = active_templates_only

    def to_json(self) -> dict[str, Any]:
        access_white_list_json_list: list[str] | None = None
        if self.access_level_white_list:
            access_white_list_json_list = [x.name for x in self.access_level_white_list]
        ret: dict[str, Any] = {
            'protocolTemplateIdWhiteList': self.protocol_template_id_whitelist,
            'protocolTemplateIdBlackList': self.protocol_template_id_blacklist,
            'latestVersionOnly': self.latest_version_only,
            'accessLevelWhiteList': access_white_list_json_list,
            'activeTemplatesOnly': self.active_templates_only
        }
        return ret

    @staticmethod
    def from_json(json_dct: dict[str, Any]) -> ProtocolTemplateQuery:
        protocol_template_id_whitelist: list[int] | None = json_dct.get('protocolTemplateIdWhiteList')
        protocol_template_id_blacklist: list[int] | None = json_dct.get('protocolTemplateIdBlackList')
        latest_version_only: bool = json_dct.get('latestVersionOnly')
        access_level_white_list: list[TemplateAccessLevel] | None = None
        if json_dct.get('accessLevelWhiteList'):
            access_level_white_list = [TemplateAccessLevel(x) for x in json_dct.get('accessLevelWhiteList')]
        active_templates_only: bool = json_dct.get('activeTemplatesOnly')
        return ProtocolTemplateQuery(protocol_template_id_whitelist, protocol_template_id_blacklist,
                                     latest_version_only, access_level_white_list, active_templates_only)

class ProtocolTemplateInfo:
    """
    Includes metadata of an ELN Protocol Template.

    Attributes:
        template_id: The identifier of the Protocol Template this info object represents
        template_name: The underlying name of the Protocol Template this info object represents
        display_name: The display name of the Protocol Template this info object represents
        description: The description of the Protocol Template this info object represents
        active: Whether or not this template is active
        created_by: The user that created this Protocol Template
        date_created: The date this Protocol Template was created
        last_modified_by: The user that last modified this Protocol Template
        last_modified_date: The date this Protocol Template was last modified
        access_level: How accessible this Protocol Template is.  If the template is PRIVATE, then only the user that created the template can see it.  If the template is PUBLIC, then all users in the system can see the template.
        template_version: The version of this template.  Template versions are only set on public templates.
    """
    template_id: int
    template_name: str
    display_name: str
    description: str | None
    active: bool
    created_by: str
    date_created: datetime
    last_modified_by: str
    last_modified_date: datetime
    access_level: TemplateAccessLevel
    template_version: int | None

    def __init__(self, template_id: int, template_name: str, display_name: str, description: str | None, active: bool,
                 created_by: str, date_created: datetime, last_modified_by: str, last_modified_date: datetime,
                 access_level: TemplateAccessLevel, template_version: int | None):
        self.template_id = template_id
        self.template_name = template_name
        self.display_name = display_name
        self.description = description
        self.active = active
        self.created_by = created_by
        self.date_created = date_created
        self.last_modified_by = last_modified_by
        self.last_modified_date = last_modified_date
        self.access_level = access_level
        self.template_version = template_version

    @staticmethod
    def from_json(json_dct: dict[str, Any]) -> ProtocolTemplateInfo:
        template_id: int = json_dct.get('templateId')
        template_name: str = json_dct.get('templateName')
        display_name: str = json_dct.get('displayName')
        description: str | None = json_dct.get('description')
        active: bool = json_dct.get('active')
        created_by: str = json_dct.get('createdBy')
        date_created: datetime = java_millis_to_datetime(json_dct.get('dateCreated'))
        last_modified_by: str = json_dct.get('lastModifiedBy')
        last_modified_date: datetime = java_millis_to_datetime(json_dct.get('lastModifiedDate'))
        access_level: TemplateAccessLevel = json_dct.get('accessLevel')
        template_version: int | None = json_dct.get('templateVersion')
        return ProtocolTemplateInfo(template_id, template_name, display_name, description, active,
                                    created_by, date_created, last_modified_by, last_modified_date, access_level,
                                    template_version)
