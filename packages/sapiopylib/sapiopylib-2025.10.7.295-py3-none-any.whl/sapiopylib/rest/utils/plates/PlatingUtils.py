from __future__ import annotations

from enum import Enum
from typing import List, Optional

from sapiopylib.rest.pojo import DataRecord


class PlateLocation:
    """
    Describes row and column position for a plate.
    """
    row_pos: str
    col_pos: int

    def __init__(self, row_pos: str, col_pos: int):
        self.row_pos = row_pos
        self.col_pos = col_pos

    @staticmethod
    def of_index(row_index: int, col_index: int) -> PlateLocation:
        """
        An alternative constructor, to build plate location by 0-based index of row and column.
        """
        row_pos: str = chr(row_index + ord('A'))
        col_pos = col_index + 1
        return PlateLocation(row_pos, col_pos)

    def get_row_index(self) -> int:
        return ord(self.row_pos) - ord('A')

    def get_col_index(self) -> int:
        return self.col_pos - 1


class PlatingOrder:
    """
    Describes the plating filling directions settings.
    """

    class FillBy(Enum):
        BY_ROW = "Row"
        BY_COLUMN = "Column"

        display_name: str

        def __init__(self, display_name: str):
            self.display_name = display_name

    class DirectionHorizontal(Enum):
        EAST = "East"
        WEST = "West"

        display_name: str

        def __init__(self, display_name: str):
            self.display_name = display_name

    class DirectionVertical(Enum):
        NORTH = "North"
        SOUTH = "South"

        display_name: str

        def __init__(self, display_name: str):
            self.display_name = display_name

    fill_by: FillBy
    horizontal_dir: DirectionHorizontal
    vertical_dir: DirectionVertical

    def __init__(self, order_fill_by: FillBy,
                 order_direction_vertical: DirectionVertical,
                 order_direction_horizontal: DirectionHorizontal):
        self.fill_by = order_fill_by
        self.horizontal_dir = order_direction_horizontal
        self.vertical_dir = order_direction_vertical

    def __str__(self):
        return "Fill by " + self.fill_by.display_name + ", " + self.vertical_dir.display_name \
             + self.horizontal_dir.display_name

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, PlatingOrder):
            return False
        other_plating_order: PlatingOrder = other
        return (self.fill_by, self.horizontal_dir, self.vertical_dir) == \
            (other_plating_order.fill_by, other_plating_order.horizontal_dir, other_plating_order.vertical_dir)

    def __hash__(self):
        return hash((self.fill_by, self.horizontal_dir, self.vertical_dir))


class PlatingUtils:

    @staticmethod
    def get_wells_in_order(plate_record: DataRecord, plating_order: PlatingOrder,
                           start_location: Optional[PlateLocation] = None) -> List[PlateLocation]:
        """
        Given the plate records and the directional settings of the plate fill,
        return an ordered list of plate filling locations.
        :param plate_record: The plate record to perform the filling
        :param plating_order: The plating order settings.
        :param start_location: Optional. If specified, filter down the list to be after this location.
        :return: An order list of how the plate should be filled.
        """

        # identify plate row/col count
        plate_row_count: int = plate_record.get_field_value("PlateRows")
        plate_col_count: int = plate_record.get_field_value("PlateColumns")

        if plate_row_count is None or plate_col_count is None:
            raise Exception("Could not identify Well Order.")

        plate_well_count: int = plate_row_count * plate_col_count

        # create new location arr
        locations: List[PlateLocation] = []

        for x in range(plate_well_count):

            row_pos: str
            col_pos: int

            # default to order by column in the South-East direction.

            if plating_order.fill_by is PlatingOrder.FillBy.BY_ROW:
                if plating_order.vertical_dir is PlatingOrder.DirectionVertical.NORTH:
                    row_pos = chr(((plate_row_count - 1) - (x // plate_col_count)) + ord('A'))
                else:
                    row_pos = chr((x // plate_col_count) + ord('A'))
                if plating_order.horizontal_dir is PlatingOrder.DirectionHorizontal.WEST:
                    col_pos = (plate_col_count - (x % plate_col_count))
                else:
                    col_pos = (x % plate_col_count) + 1
            else:
                if plating_order.vertical_dir is PlatingOrder.DirectionVertical.NORTH:
                    row_pos = chr(((plate_row_count - 1) - (x % plate_row_count)) + ord('A'))
                else:
                    row_pos = chr((x % plate_row_count) + ord('A'))
                if plating_order.horizontal_dir is PlatingOrder.DirectionHorizontal.WEST:
                    col_pos = (plate_col_count - (x // plate_row_count))
                else:
                    col_pos = (x // plate_row_count) + 1

            locations.append(PlateLocation(row_pos, col_pos))

        if start_location is None:
            return locations

        start_index = locations.index(start_location)
        return locations[start_index:]
