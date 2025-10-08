from typing import Optional, Dict, Any

from sapiopylib.rest.pojo.Sort import SortDirection, SortDirectionParser


class TableColumn:
    """
    Represents a table column in a table of reports.
    """
    data_type_name: str
    data_field_name: str
    sort_direction: Optional[SortDirection]
    sort_order: Optional[int]

    def __init__(self, data_type_name: str, data_field_name: str,
                 sort_direction: SortDirection = None, sort_order: Optional[int] = None):
        """
        Create a new table column config on a tabular report.
        :param data_type_name: The data type name of the table column.
        :param data_field_name: The data field name of the table column.
        :param sort_direction: If sorting is enabled for this field, how should value be sorted.
        :param sort_order: The priority of this field among all fields to be sorted in this table.
        """
        self.data_type_name = data_type_name
        self.data_field_name = data_field_name
        self.sort_direction = sort_direction
        self.sort_order = sort_order

    def to_json(self) -> Dict[str, Any]:
        sort_direction: Optional[str] = SortDirectionParser.direction_to_json(self.sort_direction, False)
        return {
            'dataTypeName': self.data_type_name,
            'dataFieldName': self.data_field_name,
            'sortDirection': sort_direction,
            'sortOrder': self.sort_order
        }


class TableColumnParser:

    @staticmethod
    def to_table_column(json_dct: Dict[str, Any]) -> TableColumn:
        data_type_name: str = json_dct.get('dataTypeName')
        data_field_name: str = json_dct.get('dataFieldName')
        sort_direction_name = json_dct.get('sortDirection')
        sort_direction: Optional[SortDirection] = SortDirectionParser.parse_sort_direction(sort_direction_name)
        sort_order = json_dct.get('sortOrder')
        return TableColumn(data_type_name, data_field_name, sort_direction, sort_order)
