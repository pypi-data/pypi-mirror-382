from __future__ import annotations

import logging
from typing import Dict, Any, Optional

from sapiopylib.rest.DataTypeService import DataTypeManager
from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.datatype.DataType import DataTypeDefinition
from sapiopylib.rest.pojo.datatype.FieldDefinition import AbstractVeloxFieldDefinition, FieldType, \
    VeloxSideLinkFieldDefinition
from sapiopylib.rest.utils.singletons import SapioContextManager


class DataTypeCacheManager(SapioContextManager):
    """
    Manages a data type cache for the purpose retrieving data type and data field definitions efficiently.
    """
    user: SapioUser
    __data_type_cache: Dict[str, DataTypeDefinition]
    __data_field_cache: Dict[str, Dict[str, AbstractVeloxFieldDefinition]]

    def __init__(self, user: SapioUser):
        super().__init__(user)
        self.__data_type_cache = dict()
        self.__data_field_cache = dict()

    def get_display_name(self, dt_name: str) -> str:
        """
        Retrieve the display name of a data type.
        """
        return self.get_data_type(dt_name).display_name

    def get_plural_display_name(self, dt_name: str) -> str:
        """
        Retrieve the plural display name of a data type.
        """
        return self.get_data_type(dt_name).plural_display_name

    def get_default_field_map(self, dt_name: str) -> Dict[str, Any]:
        """
        Obtain the default value field map for a data type.
        This will not include any field names whose default value is blank.
        """
        field_by_name: Dict[str, AbstractVeloxFieldDefinition] = self.get_fields_for_type(dt_name)
        ret: Dict[str, Any] = dict()
        for field_name, field in field_by_name.items():
            if hasattr(field, 'default_value'):
                default_value: Any = getattr(field, 'default_value')
                if default_value:
                    ret[field_name] = default_value
        return ret

    def get_data_type(self, dt_name: str) -> DataTypeDefinition:
        """
        Retrieve the data type definition object from cache.
        If this cache is not loaded, load it right now.
        """
        if dt_name in self.__data_type_cache:
            return self.__data_type_cache[dt_name]
        dt_man: DataTypeManager = DataTypeManager(self.user)
        dt_def: DataTypeDefinition = dt_man.get_data_type_definition(dt_name)
        self.__data_type_cache[dt_name] = dt_def
        return dt_def

    def get_fields_for_type(self, dt_name: str) -> Dict[str, AbstractVeloxFieldDefinition]:
        """
        Retrieve the data field definitions for a data type from cache.
        If this is not loaded, load it right now.
        """
        if dt_name in self.__data_field_cache:
            return self.__data_field_cache[dt_name]
        dt_man: DataTypeManager = DataTypeManager(self.user)
        field_list = dt_man.get_field_definition_list(dt_name)
        ret: Dict[str, AbstractVeloxFieldDefinition] = dict()
        for field in field_list:
            ret[field.data_field_name] = field
        self.__data_field_cache[dt_name] = ret
        return ret

    def is_side_link_field(self, dt_name: str, field_name: str) -> bool:
        """
        Tests whether a data field is of side link field type.
        """
        field_def_map = self.get_fields_for_type(dt_name)
        field_def: AbstractVeloxFieldDefinition = field_def_map.get(field_name)
        if field_def is None:
            return False
        return field_def.data_field_type == FieldType.SIDE_LINK

    def get_side_link_to_data_type_name(self, dt_name: str, field_name: str) -> Optional[str]:
        """
        Get the data type name defined in a field definition which tells us the data type name of the target record.
        :param dt_name: The data type name of the side link field definition.
        :param field_name: The data field name of the side link field definition.
        :return: If this is not a side link field definition, return None. Otherwise, return the data type name.
        """
        field_def_map = self.get_fields_for_type(dt_name)
        field_def: AbstractVeloxFieldDefinition = field_def_map.get(field_name)
        if isinstance(field_def, VeloxSideLinkFieldDefinition):
            return field_def.linked_data_type_name
        else:
            return None
