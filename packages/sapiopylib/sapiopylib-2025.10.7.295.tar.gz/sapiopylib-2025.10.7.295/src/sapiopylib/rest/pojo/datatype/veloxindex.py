from __future__ import  annotations

from typing import Any

from sapiopylib.rest.pojo.datatype.FieldDefinition import AbstractVeloxFieldDefinition, FieldDefinitionParser

class VeloxIndexColumn:
    """
    A column within a Velox index definition.
    Attributes:
        data_field_name: The name of the data field that this column is based on.
        column_name: The name of the DB column in the index.
        index_column_length: The length of the column in the index.
    """
    data_field_name: str
    column_name: str
    index_column_length: int

    def __init__(self, data_field_name: str, column_name: str, index_column_length: int):
        self.data_field_name = data_field_name
        self.column_name = column_name
        self.index_column_length = index_column_length

    def __eq__(self, other):
        if not isinstance(other, VeloxIndexColumn):
            return False
        return self.column_name == other.column_name

    def __hash__(self):
        return hash(self.column_name)

    def __str__(self):
        return self.column_name

    def to_json(self) -> dict[str, Any]:
        return {
            "dataFieldName": self.data_field_name,
            "columnName": self.column_name,
            "indexColumnLength": self.index_column_length
        }

    @staticmethod
    def from_json(json_dct: dict[str, Any]) -> VeloxIndexColumn:
        return VeloxIndexColumn(
            data_field_name=json_dct.get('dataFieldName'),
            column_name=json_dct.get('columnName'),
            index_column_length=json_dct.get('indexColumnLength')
        )

class VeloxIndexDefinition:
    """
    A custom index created for a data type definition in Sapio.
    System indexes may not have a record of this index object.
    Attributes:
        index_name: The index name of this index definition, unique within the data type.
        index_column_list: A list of columns that are indexed by this index.
    """
    index_name: str
    index_column_list: list[VeloxIndexColumn]

    def __init__(self, index_name: str, index_column_list: list[VeloxIndexColumn]):
        self.index_name = index_name
        self.index_column_list = index_column_list

    def __eq__(self, other):
        if not isinstance(other, VeloxIndexDefinition):
            return False
        return self.index_name == other.index_name

    def __hash__(self):
        return hash(self.index_name)

    def __str__(self):
        return self.index_name

    def to_json(self) -> dict[str, Any]:
        return {
            "indexName": self.index_name,
            "indexColumnList": [x.to_json() for x in self.index_column_list] if self.index_column_list is not None else None
        }

    @staticmethod
    def from_json(json_dct: dict[str, Any]) -> VeloxIndexDefinition:
        return VeloxIndexDefinition(
            index_name=json_dct.get('indexName'),
            index_column_list=[VeloxIndexColumn.from_json(x) for x in json_dct.get('indexColumnList')]
        )

class VeloxIndexDefinitionBuilder:
    """
    A custom index created for a data type definition in Sapio.
    System indexes may not have a record of this index object.
    For example, RecordId field and all side link fields are always indexed,
    even though they are not explicitly returning as index definitions.
    Attributes:
        index_name: The index name of this index definition, unique within the data type.
        index_field_list: A list of field definitions that are indexed by this index.
    """
    index_name: str
    index_field_list: list[AbstractVeloxFieldDefinition]
    def __init__(self, index_name: str, index_field_list: list[AbstractVeloxFieldDefinition]):
        self.index_name = index_name
        self.index_field_list = index_field_list

    def __eq__(self, other):
        if not isinstance(other, VeloxIndexDefinitionBuilder):
            return False
        return self.index_name == other.index_name

    def __hash__(self):
        return hash(self.index_name)

    def __str__(self):
        return self.index_name

    def to_json(self) -> dict[str, Any]:
        return {
            "indexName": self.index_name,
            "indexFieldList": [x.to_json() for x in self.index_field_list] if self.index_field_list is not None else None
        }

    @staticmethod
    def from_json(json_dct: dict[str, Any]) -> VeloxIndexDefinitionBuilder:
        return VeloxIndexDefinitionBuilder(
            index_name=json_dct.get('indexName'),
            index_field_list=[FieldDefinitionParser.to_field_definition(x) for x in json_dct.get('indexColumnList')]
        )