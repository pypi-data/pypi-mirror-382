# The tiny descriptors about data type and data field pairs.
from typing import Any, Dict


class DataFieldDescriptor:
    data_type_name: str
    data_field_name: str

    def __init__(self, data_type_name: str, data_field_name: str):
        self.data_type_name = data_type_name
        self.data_field_name = data_field_name

    def to_pojo(self) -> Dict[str, Any]:
        return {
            'dataTypeName': self.data_type_name,
            'dataFieldName': self.data_field_name
        }


class DataFieldDescriptorParser:
    @staticmethod
    def parse_data_field_descriptor(json_dct: Dict[str, Any]) -> DataFieldDescriptor:
        data_type_name: str = json_dct.get('dataTypeName')
        data_field_name: str = json_dct.get('dataFieldName')
        return DataFieldDescriptor(data_type_name, data_field_name)
