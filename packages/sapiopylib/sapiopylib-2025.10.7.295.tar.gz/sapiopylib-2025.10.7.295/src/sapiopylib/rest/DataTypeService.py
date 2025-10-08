from __future__ import annotations

from typing import Any, Dict, List
from weakref import WeakValueDictionary

from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.datatype.DataType import DataTypeDefinition, DataTypeParser
from sapiopylib.rest.pojo.datatype.DataTypeLayout import DataTypeLayoutParser, DataTypeLayout
from sapiopylib.rest.pojo.datatype.FieldDefinition import FieldDefinitionParser, AbstractVeloxFieldDefinition
from sapiopylib.rest.pojo.datatype.TemporaryDataType import TemporaryDataType
from sapiopylib.rest.pojo.datatype.veloxindex import VeloxIndexDefinitionBuilder, VeloxIndexDefinition


class DataTypeManager:
    """
    Obtain information about data types in the system.
    """
    user: SapioUser

    __instances: WeakValueDictionary[SapioUser, DataTypeManager] = WeakValueDictionary()
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
        Obtains a data type manager to query data type definitions.

        :param user: The user that will make the webservice request to the application.
        """
        if self.__initialized:
            return
        self.user = user
        self.__initialized = True

    def get_field_definition_list(self, data_type_name: str) -> List[AbstractVeloxFieldDefinition] | None:
        """
        Get the field definitions for every field on the provided data type. These fields can be
        used to know what fields will be returned when getting records of this type.

        :param data_type_name: The data type name of a data type in the system.
        :return: A list of the field definitions for every field on the provided data type, or None if data type does not exist.
        """
        sub_path: str = self.user.build_url(['datatypemanager', 'veloxfieldlist', data_type_name])
        response = self.user.get(sub_path)
        self.user.raise_for_status(response)
        if response.status_code == 204:
            return None
        json_list: List[Dict[str, Any]] = response.json()
        return [FieldDefinitionParser.to_field_definition(x) for x in json_list]

    def get_data_type_name_list(self) -> List[str]:
        """
        Get all data type names that exist in the system. These data type names can be used to determine which
        data record can be queried or created in the system and to query information about specific data types.

        :return: A list of all data type names from the system.
        """
        sub_path: str = '/datatypemanager/datatypenamelist'
        response = self.user.get(sub_path)
        self.user.raise_for_status(response)
        json_list: List[str] = response.json()
        return json_list

    def get_data_type_definition(self, data_type_name: str) -> DataTypeDefinition | None:
        """
        Get the data type definition for the given data type. The data type definition can be used to determine a data
        type's display name, plural name, allowable record relationships, and more.

        :param data_type_name: The data type name of a data type in the system.
        :return: The data type definition of the given data type. Return None if data type does not exist.
        """
        sub_path: str = self.user.build_url(['datatypemanager', 'datatypedefinition', data_type_name])
        response = self.user.get(sub_path)
        self.user.raise_for_status(response)
        if response.status_code == 204:
            return None
        json_dct = response.json()
        return DataTypeParser.parse_data_type_definition(json_dct)

    def get_data_type_layout_list(self, data_type_name: str) -> List[DataTypeLayout] | None:
        """
        Get all available layouts for the provided data type name. Layouts are how records are displayed to users in the
        system. They can be used by TemporaryDataTypes and DataRecordDialogRequests to control how client callbacks are
        displayed to the user.

        :param data_type_name: The data type name of a data type in the system.
        :return: A list of all data type layouts for the provided data type. Return None if data type does not exist.
        """
        sub_path: str = self.user.build_url(['datatypemanager', 'layout', data_type_name])
        response = self.user.get(sub_path)
        self.user.raise_for_status(response)
        if response.status_code == 204:
            return None
        json_list: List[Dict[str, Any]] = response.json()
        return [DataTypeLayoutParser.parse_layout(x) for x in json_list]

    def get_default_layout(self, data_type_name: str) -> DataTypeLayout | None:
        """
        Get the default layout for the provided data type name.
        :param data_type_name: The data type name of a data type in the system we are retrieving default layout for.
        """
        sub_path: str = self.user.build_url(['datatypemanager', 'defaultlayout', data_type_name])
        response = self.user.get(sub_path)
        self.user.raise_for_status(response)
        if response.status_code == 204:
            return None
        return DataTypeLayoutParser.parse_layout(response.json())

    def get_temporary_data_type(self, data_type_name: str, layout_name: str | None = None) -> TemporaryDataType | None:
        """
        Get temporary data type for an existing data type in Sapio.
        This object can be used in interactions in client callback methods.
        :param data_type_name: The data type name to obtain the temporary data type object.
        :param layout_name: If not specified, we will return the default layout for current user.
        Otherwise, we will return the temporary type filled with the specified layout.
        :return The temporary data type of the default or provided layout for the data type. Return None if data type does not exist.
        """
        sub_path: str = self.user.build_url(['datatypemanager', 'temporarydatatype', data_type_name])
        if not layout_name:
            layout_name = ""
        response = self.user.get(sub_path, params={"layoutName": layout_name})
        self.user.raise_for_status(response)
        if response.status_code == 204:
            return None
        json_dict: Dict[str, Any] = response.json()
        return TemporaryDataType.from_json(json_dict)

    def insert_or_update_data_type_definition(self, data_type_definition: DataTypeDefinition) -> None:
        """
        Insert or Update Data Type Definition Properties. Requires Data Type Administration system level privilege.
        If the data type definition does not exist yet, create the new data type definition. Otherwise, replace the properties in definition.
        Note: for the parent and child hierarchy, this operation will only insert new parent
        or child relations. It will not remove any existing relations. Use separate calls for removals.
        """
        sub_path: str = self.user.build_url(['datatypemanager', 'datatype'])
        response = self.user.post(sub_path, payload=data_type_definition.to_json())
        self.user.raise_for_status(response)

    def delete_data_type_definition(self, data_type_name: str) -> None:
        """
        Delete Data Type Definition. Requires Data Type Administration system level privilege.
        Delete the data type definition for the provided data type name. This will remove the data type definition and all data stored in this data type will be permanently deleted from database.
        """
        sub_path: str = self.user.build_url(['datatypemanager', 'datatype', data_type_name])
        response = self.user.delete(sub_path)
        self.user.raise_for_status(response)

    def insert_or_update_field_definition_list(self, data_type_name: str,
                                               field_definition_list: List[AbstractVeloxFieldDefinition]) -> None:
        """
        Insert or Update Field Definition List. Requires Data Type Administration system level privilege.
        Add additional fields to the data type definition. If any fields already exists, an error will be thrown.
        """
        sub_path: str = self.user.build_url(['datatypemanager', 'fields', data_type_name])
        response = self.user.post(sub_path, payload=[x.to_json() for x in field_definition_list])
        self.user.raise_for_status(response)

    def delete_field_definition_list(self, data_type_name: str, field_name_list: List[str]) -> None:
        """
        Delete Field Definition List. Requires Data Type Administration system level privilege.
        Delete the provided list of fields from the data type definition. All data in the provided fields will be permanently deleted from database.
        If any of provided field names do not exist in the provided data type, an error will be thrown.
        """
        sub_path: str = self.user.build_url(['datatypemanager', 'fields', data_type_name])
        response = self.user.delete(sub_path, payload=field_name_list)
        self.user.raise_for_status(response)

    def insert_or_update_data_type_layout(self, layout: DataTypeLayout) -> None:
        """
        Insert or Update Data Type Layout. Requires Data Type Administration system level privilege.
        If the layout name already exists, this will replace the existing layout.
        """
        if not layout.data_type_name:
            raise ValueError("Data type name must be set in the layout before being used to update a data type definition.")
        sub_path: str = self.user.build_url(['datatypemanager', 'layout'])
        response = self.user.post(sub_path, payload=layout.to_pojo())
        self.user.raise_for_status(response)

    def delete_data_type_layout(self, data_type_name: str, layout_name: str) -> None:
        """
        Delete Data Type Layout. Requires Data Type Administration system level privilege.
        Delete the layout from the provided data type name. If the layout does not exist, an error will be thrown.
        """
        sub_path: str = self.user.build_url(['datatypemanager', 'layout', data_type_name, layout_name])
        response = self.user.delete(sub_path)
        self.user.raise_for_status(response)

    def get_index_definition_list(self, data_type_name: str) -> List[VeloxIndexDefinition] | None:
        """
        Get Index Definition List. Requires Data Type Administration system level privilege.
        Get index definition list for the provided data type name. This will not include system-defined indexes such as those created for record ID and side link fields.
        """
        sub_path: str = self.user.build_url(['datatypemanager', 'index', data_type_name])
        response = self.user.get(sub_path)
        self.user.raise_for_status(response)
        if response.status_code == 204:
            return None
        json_list: List[Dict[str, Any]] = response.json()
        return [VeloxIndexDefinition.from_json(x) for x in json_list]

    def insert_or_update_index_definition_list(self, data_type_name: str,
                                               index_definition_list: List[VeloxIndexDefinitionBuilder]) -> None:
        """
        Insert or Update Index Definition List. Requires Data Type Administration system level privilege.
        Insert or update the index definition list for the provided data type name. If the index name already exists, this will replace the existing index.
        """
        sub_path: str = self.user.build_url(['datatypemanager', 'index', data_type_name])
        response = self.user.post(sub_path, payload=[x.to_json() for x in index_definition_list])
        self.user.raise_for_status(response)


    def delete_index_definition_list(self, data_type_name: str, index_name_list: List[str]) -> None:
        """
        Delete Index Definition List. Requires Data Type Administration system level privilege.
        Delete the provided list of index definitions from the data type definition. If any of the provided index names do not exist in the provided data type, an error will be thrown.
        """
        sub_path: str = self.user.build_url(['datatypemanager', 'index', data_type_name])
        response = self.user.delete(sub_path, payload=index_name_list)
        self.user.raise_for_status(response)


    def test_temporary_data_type_translation(self, temp_dt_to_test: TemporaryDataType):
        """
        Translate the temporary data type fully into java temporary data type and translate back into JSON again. Nothing else will run in this operation.
        This is created to help unit testing of client POJO structures.
        :param temp_dt_to_test: The temporary data type to test translations for.
        :return: The returned temporary data type that hopefully matches the original one.
        """
        sub_path: str = self.user.build_url(['datatypemanager', 'test', 'temporarydatatype'])
        response = self.user.post(sub_path, payload=temp_dt_to_test.to_json())
        self.user.raise_for_status(response)
        return TemporaryDataType.from_json(response.json())
