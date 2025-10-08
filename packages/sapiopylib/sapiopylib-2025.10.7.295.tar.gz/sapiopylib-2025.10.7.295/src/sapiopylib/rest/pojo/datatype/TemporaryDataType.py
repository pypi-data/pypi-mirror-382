from __future__ import annotations

from typing import Any, List, Dict, Optional

from sapiopylib.rest.pojo.datatype.DataTypeLayout import DataTypeLayout, DataTypeLayoutParser
from sapiopylib.rest.pojo.datatype.FieldDefinition import AbstractVeloxFieldDefinition, FieldDefinitionParser


class TemporaryDataType:
    """
    Represent a temporary data type layout and fields, usually used to ask user for further input.

    Attributes:
        data_type_layout: The layout to be displayed to user.
        data_type_name: The data type name of this temp type. Usually not useful. But required.
        display_name: The display name of this temp type.
        plural_display_name: The display name of this temp type when UI talks about multiple records of this type.
        attachment: Whether this temp type allows attachment data.
        record_image_assignable: Whether images can be assigned to this temp type.
        icon_name: The name of the icon that should be displayed for this temporary data type. The GUID.
        icon_color: The color of the icon that should be displayed for this temporary data type. The HTML hex start with #.
    """
    data_type_layout: Optional[DataTypeLayout]
    _field_definition_map: Dict[str, AbstractVeloxFieldDefinition]
    data_type_name: str
    display_name: str
    plural_display_name: str
    attachment: bool
    record_image_assignable: bool
    icon_name: str | None
    icon_color: str | None

    def get_field(self, field_name: str) -> AbstractVeloxFieldDefinition | None:
        """
        Get the field definition by field name.
        """
        return self._field_definition_map.get(field_name.upper())

    def get_field_def_list(self):
        return list(self._field_definition_map.values())

    def set_field_definition(self, field_def: AbstractVeloxFieldDefinition):
        """
        Replace existing field with the same field name with the new field definition.
        """
        field_def._data_type_name = self.data_type_name
        self._field_definition_map[field_def.get_data_field_name().upper()] = field_def

    def set_field_definition_list(self, field_def_list: List[AbstractVeloxFieldDefinition]):
        """
        Replaces existing field definition list for this temp type with a new list of fields.
        """
        self._field_definition_map.clear()
        for field_def in field_def_list:
            self.set_field_definition(field_def)

    def __init__(self, data_type_name: str, display_name: str, plural_display_name: str,
                 data_type_layout: Optional[DataTypeLayout] = None,
                 field_def_list: Optional[List[AbstractVeloxFieldDefinition]] = None,
                 attachment: bool = False, record_image_assignable: bool = False,
                 icon_name: str | None = None, icon_color: str | None = None):
        self._field_definition_map = dict()
        self.data_type_name = data_type_name
        self.display_name = display_name
        self.plural_display_name = plural_display_name

        if data_type_layout is not None:
            data_type_layout.data_type_name = data_type_name
        self.data_type_layout = data_type_layout

        self.attachment = attachment
        self.record_image_assignable = record_image_assignable
        if field_def_list is not None:
            self.set_field_definition_list(field_def_list)
        self.icon_name = icon_name
        self.icon_color = icon_color

    def __hash__(self):
        return hash(self.data_type_name)

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, TemporaryDataType):
            return False
        return self.data_type_name == other.data_type_name

    def __str__(self):
        return self.display_name

    def to_json(self) -> Dict[str, Any]:
        layout_pojo = None
        if self.data_type_layout is not None:
            layout_pojo = self.data_type_layout.to_pojo()
        field_def_pojo_map = dict()
        for field_name, field_def in self._field_definition_map.items():
            field_def_pojo_map[field_name] = field_def.to_json()
        return {
            'dataTypeLayout': layout_pojo,
            'veloxFieldDefinitionMap': field_def_pojo_map,
            'dataTypeName': self.data_type_name,
            'displayName': self.display_name,
            'attachment': self.attachment,
            'recordImageAssignable': self.record_image_assignable,
            'pluralDisplayName': self.plural_display_name,
            'iconName': self.icon_name,
            'iconColor': self.icon_color
        }

    @staticmethod
    def from_json(json_dct: dict[str, Any]) -> TemporaryDataType:
        data_type_layout = DataTypeLayoutParser.parse_layout(json_dct.get('dataTypeLayout'))

        field_def_pojo_map: dict[str, dict[str, Any]] = json_dct.get('veloxFieldDefinitionMap')
        field_definition_list: list[AbstractVeloxFieldDefinition] = list()
        for field_name, field_value in field_def_pojo_map.items():
            field_definition_list.append(FieldDefinitionParser.to_field_definition(field_value))

        data_type_name: str = json_dct.get('dataTypeName')
        display_name: str = json_dct.get('displayName')
        is_attachment: bool = json_dct.get('attachment')
        is_record_image_assignable: bool = json_dct.get('recordImageAssignable')
        plural_display_name: str = json_dct.get('pluralDisplayName')
        icon_name: str = json_dct.get('iconName')
        icon_color: str = json_dct.get('iconColor')

        return TemporaryDataType(data_type_name, display_name, plural_display_name, data_type_layout,
                                 field_definition_list, is_attachment, is_record_image_assignable,
                                 icon_name, icon_color)