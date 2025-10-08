from __future__ import annotations

from functools import total_ordering
from typing import Any, Dict, List, Optional


@total_ordering
class DataRecord:
    """
    A "Data Record" that can be passed as a parameter or result of
    a webservice endpoint to provide info about a record.
    """
    __data_type_name: str
    __record_id: int
    __fields: Dict[str, Any]
    __original_fields: Dict[str, Any]
    __changed_fields: Dict[str, Any]
    __is_new: bool
    __is_deleted: bool

    @property
    def is_deleted(self) -> bool:
        """
        Flag indicating if this record has been deleted during the current transaction.
        Changing this value will not affect the record in the database.  This will only be relevant in web hooks.
        """
        return self.__is_deleted

    @property
    def is_new(self) -> bool:
        """
        Flag indicating if this record is new and has not been saved to the database.  Changing this
        value will not affect the record being saved.  This will only be relevant in web hooks.

        Note: sapiopylib may change this to true on record model for new records.
        This will have no effect to webserver and is simply a syntax sugar.
        """
        return self.__is_new

    @property
    def fields(self) -> Dict[str, Any]:
        """
        The field cache of the data record.
        """
        return self.__fields

    @property
    def data_type_name(self) -> str:
        """
        The data type name of the record.
        """
        return self.__data_type_name

    @property
    def record_id(self) -> int:
        """
        The Record ID that uniquely identifies this record.
        """
        return self.__record_id

    @property
    def data_record_name(self) -> str:
        """
        Get the record name from the fields.
        """
        return self.get_field_value("DataRecordName")

    @record_id.setter
    def record_id(self, record_id: int) -> None:
        if self.__record_id >= 0:
            raise ValueError("Cannot reset data record ID when current ID is non-negative")
        self.__record_id = record_id

    def __le__(self, other):
        if not isinstance(other, DataRecord):
            return False
        other_pojo: DataRecord = other
        return self.__record_id <= other_pojo.__record_id

    def __eq__(self, other):
        if not isinstance(other, DataRecord):
            return False
        other_pojo: DataRecord = other
        if not self.get_record_id() == other_pojo.get_record_id():
            return False
        return True

    def __hash__(self):
        return hash((self.__data_type_name, self.__record_id))

    def __init__(self, data_type_name: str, record_id: int, fields: Dict[str, Any],
                 is_new: bool = False, is_deleted: bool = False):
        """
        A "Data Record" that can be passed as a parameter or result of
        a webservice endpoint to provide info about a record.
        :param data_type_name The name of the data type that this record instance represents.
        :param record_id The global identifier in the system for this record instance.
        :param fields The data fields for this data record.
        """
        self.__data_type_name = data_type_name
        self.__record_id = record_id
        if fields is None:
            fields = dict()
        self.__fields = fields
        self.__original_fields = dict(self.__fields)
        self.__changed_fields = dict()
        self.__is_new = is_new
        self.__is_deleted = is_deleted

    def get_map_key_reference(self):
        """
        Get the String representation of this DataRecordPojo that can be used as a key in a map like those used in the
        addChildren methods.
        """
        return self.get_data_type_name() + ":" + str(self.get_record_id())

    def get_data_type_name(self) -> str:
        """
        Get the data type name of the data record.
        """
        return self.__data_type_name

    def get_record_id(self) -> int:
        """
        Get the record ID of the data record.
        """
        return self.__record_id

    def get_fields(self) -> Dict[str, object]:
        """
        Get COPY of all data fields of the data record in a dictionary.
        """
        return dict(self.__fields)

    def set_fields(self, fields: Dict[str, object]):
        """
        For each key in the dictionary, set its value on this data record.
        Record ID or any other system fields might not be set.
        """
        for key, val in fields.items():
            if key is None:
                continue
            if "RecordId".lower() == key.lower():
                continue
            self.__fields[key] = val
            self.__changed_fields[key] = val

    def set_field_value(self, field_name: str, field_value):
        """
        Set a single field value on the record
        :param field_name: The field name to set for
        :param field_value: The value to set to at the field name.
        """
        self.set_fields({field_name: field_value})

    def get_field_value(self, field_name: str):
        """
        Get a field value by field name
        :param field_name: The field name to get for.
        :return: None if the field does not contain the field name. Otherwise, the object value.
        """
        return self.__fields.get(field_name)

    def commit_changes(self):
        """
        Commit record changes to clear all changed caches.
        """
        self.__changed_fields.clear()
        self.__original_fields = dict(self.__fields)

    def rollback(self):
        """
        Rolls back changes for this data record.
        """
        self.__fields = dict(self.__original_fields)
        self.__changed_fields.clear()

    def get_changed_fields_clone(self) -> Dict[str, Any]:
        """
        Get a copy of changed fields in records. Only fields changed since the last save will be keyed.
        Note: do not call this in a loop. Get the dictionary and store it as a local variable.
        """
        return dict(self.__changed_fields)

    def get_changed_value(self, field_name: str):
        """
        Get the changed value for a single field.
        Note: This will return blank even if the value exists, if the value hasn't been changed after last save.
        """
        return self.__changed_fields.get(field_name)

    def get_last_saved_value(self, field_name: str):
        """
        Get the last saved value for a single field.
        """
        return self.__original_fields.get(field_name)

    def __str__(self):
        if self.__fields is not None and 'DataRecordName' in self.__fields:
            return self.__fields.get("DataRecordName")
        return self.__data_type_name + " " + str(self.__record_id)

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def from_json(json_dct: Dict[str, Any]) -> Optional[DataRecord]:
        if json_dct is None:
            return None
        data_type_name = json_dct.get('dataTypeName')
        record_id = json_dct.get('recordId')
        fields = json_dct.get('fields')
        is_new: bool = bool(json_dct.get('new'))
        is_deleted: bool = bool(json_dct.get('deleted'))
        return DataRecord(data_type_name, record_id, fields, is_new, is_deleted)

    def to_json(self) -> Dict[str, Any]:
        return {
            'dataTypeName': self.__data_type_name,
            'recordId': self.__record_id,
            'fields': self.__fields,
            'new': self.__is_new,
            'deleted': self.__is_deleted
        }


def from_json_record_list(pojo_list: List[dict]) -> List[DataRecord]:
    return [DataRecord.from_json(x) for x in pojo_list]


def to_record_json_list(record_list: List[DataRecord]) -> List[Dict[str, Any]]:
    return [x.to_json() for x in record_list]


@total_ordering
class DataRecordDescriptor:
    """
    Provides a pointer into a remote DataRecord object for a record in Sapio.
    """
    data_type_name: str
    record_id: int

    def __hash__(self):
        return hash(self.record_id)

    def __init__(self, data_type_name: str, record_id: int):
        self.data_type_name = data_type_name
        self.record_id = record_id

    def __le__(self, other):
        if not isinstance(other, DataRecordDescriptor):
            return False
        return self.record_id <= other.record_id

    def __eq__(self, other):
        if not isinstance(other, DataRecordDescriptor):
            return False
        return self.record_id == other.record_id

    def __str__(self):
        return self.data_type_name + ":" + str(self.record_id)

    def to_json(self) -> Dict[str, Any]:
        return {
            'dataTypeName': self.data_type_name,
            'recordId': self.record_id
        }

    @staticmethod
    def from_json(json_dct: Dict[str, Any]) -> Optional[DataRecordDescriptor]:
        if json_dct is None:
            return None
        data_type_name = json_dct.get('dataTypeName')
        record_id = int(json_dct.get('recordId'))
        return DataRecordDescriptor(data_type_name, record_id)

    @staticmethod
    def from_str(raw_text: Optional[str]) -> Optional[DataRecordDescriptor]:
        if not raw_text:
            return None
        split = raw_text.split(':')
        dt_name = split[0]
        record_id = int(split[1])
        return DataRecordDescriptor(dt_name, record_id)

