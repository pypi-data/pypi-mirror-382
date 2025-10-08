from enum import Enum
from typing import Optional


class SortDirection(Enum):
    """
    Column Sort Direction
    """
    NONE = 0, "None"
    ASCENDING = 1, "Ascending"
    DESCENDING = 2, "Descending"

    custom_report_dir_code: int
    field_def_enum_name: str

    def __init__(self, dir_code: int, field_def_enum_name: str):
        self.custom_report_dir_code = dir_code
        self.field_def_enum_name = field_def_enum_name


class SortDirectionParser:
    """
    Internal JSON parser for SortDirection pojo.
    """
    @staticmethod
    def parse_sort_direction(dir_name: Optional[str]):
        if dir_name is None:
            return None
        return SortDirection[dir_name.upper()]

    @staticmethod
    def direction_to_json(sort_direction: Optional[SortDirection], is_custom_report: bool):
        if sort_direction is None:
            sort_direction = SortDirection.NONE
        # This is due to our dumb translation with different casing for custom report.
        if is_custom_report:
            return sort_direction.name
        else:
            return sort_direction.field_def_enum_name
