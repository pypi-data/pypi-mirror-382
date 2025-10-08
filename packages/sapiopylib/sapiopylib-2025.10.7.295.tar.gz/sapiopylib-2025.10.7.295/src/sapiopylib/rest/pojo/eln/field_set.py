from __future__ import annotations

from datetime import datetime
from typing import Any

from sapiopylib.rest.utils.SapioDateUtils import java_millis_to_datetime


class ElnFieldSetInfo:
    """
    Details about an ELN Field Set that represents a collection of predefined fields in the system.

    Attributes:
        field_set_id: The identifier of the ELN Field Set this info object represents
        field_set_name: The system name of the field set
        field_set_display_name: The display name of the field set4
        eln_data_type_name: The base Notebook Experiment Data Type associated with this field set
        description: The description of the EnbFieldSet
        created_by: The username that created the EnbFieldSet
        field_set_category: The plugin category to set on this EnbFieldSet.  This is used to organized the EnbFieldSets in the Notebook Experiment UI.
        date_created: The date the EnbFieldSet was created
        auto_plugin: Indicates if this EnbFieldSet is an auto plugin.  AutoRunPlugin field sets will run the set of field set plugins when they are added to a Notebook Experiment.
        file_load_plugin: Indicates if this EnbFieldSet is associated with a plugin to load a file.
        eln_admin_only: Indicates if this EnbFieldSet should only be visible to ELN Admin users.
        last_modified_by: The username that last modified the EnbFieldSet
        last_modified_date: The date the EnbFieldSet was last modified
    """
    field_set_id: int
    field_set_name: str
    field_set_display_name: str
    eln_data_type_name: str
    description: str | None
    created_by: str
    field_set_category: str | None
    date_created: datetime
    auto_plugin: bool
    file_load_plugin: bool
    eln_admin_only: bool
    last_modified_by: str
    last_modified_date: datetime

    def __init__(self, field_set_id: int, field_set_name: str, field_set_display_name: str, eln_data_type_name: str,
                 description: str | None, created_by: str, field_set_category: str | None, date_created: datetime,
                 auto_plugin: bool, file_load_plugin: bool, eln_admin_only: bool, last_modified_by: str,
                 last_modified_date: datetime):
        self.field_set_id = field_set_id
        self.field_set_name = field_set_name
        self.field_set_display_name = field_set_display_name
        self.eln_data_type_name = eln_data_type_name
        self.description = description
        self.created_by = created_by
        self.field_set_category = field_set_category
        self.date_created = date_created
        self.auto_plugin = auto_plugin
        self.file_load_plugin = file_load_plugin
        self.eln_admin_only = eln_admin_only
        self.last_modified_by = last_modified_by
        self.last_modified_date = last_modified_date

    @staticmethod
    def from_json(json_dct: dict[str, Any]) -> ElnFieldSetInfo:
        field_set_id: int = json_dct.get('fieldSetId')
        field_set_name: str = json_dct.get('fieldSetName')
        field_set_display_name: str = json_dct.get('fieldSetDisplayName')
        eln_data_type_name: str = json_dct.get('enbDataTypeName')
        description: str | None = json_dct.get('description')
        created_by: str = json_dct.get('createdBy')
        field_set_category: str | None = json_dct.get('fieldSetCategory')
        date_created: datetime = java_millis_to_datetime(json_dct.get('dateCreated'))
        auto_plugin: bool = json_dct.get('autoPlugin')
        file_load_plugin: bool = json_dct.get('fileLoadPlugin')
        eln_admin_only: bool = json_dct.get('elnAdminOnly')
        last_modified_by: str = json_dct.get('lastModifiedBy')
        last_modified_date: datetime = java_millis_to_datetime(json_dct.get('lastModifiedDate'))
        return ElnFieldSetInfo(field_set_id, field_set_name, field_set_display_name, eln_data_type_name,
                               description, created_by, field_set_category, date_created, auto_plugin,
                               file_load_plugin, eln_admin_only, last_modified_by, last_modified_date)