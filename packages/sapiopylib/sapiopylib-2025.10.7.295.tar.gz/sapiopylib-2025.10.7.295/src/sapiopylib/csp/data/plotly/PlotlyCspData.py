from __future__ import annotations

import re
from re import Pattern, Match
from typing import List, Dict

from sapiopylib.csp.data.PyCspFieldMap import PyCspObject, CspDataException
from sapiopylib.csp.data.plotly.PlotlyCspEnums import *


class PlotlyColor:
    """
    Construct a plotly color object to produce color strings used by plotly attribute in a UI color property.
    """
    red: int
    green: int
    blue: int
    alpha: float
    html_color: str

    RGB_PATTERN: Pattern = re.compile("rgb\\(\\s*(\\d+),\\s*(\\d+),\\s*(\\d+)\\s*\\)")
    RGBA_PATTERN: Pattern = re.compile("rgba\\(\\s*(\\d+),\\s*(\\d+),\\s*(\\d+),\\s*([0-9.]+)\\s*\\)")

    def set_color_by_plotly_str(self, plotly_color_str: str):
        if not plotly_color_str:
            self.html_color = "#000000"
            return
        match: Match[str] = self.RGB_PATTERN.fullmatch(plotly_color_str)
        if match is not None:
            self.red = int(match.group(1))
            self.green = int(match.group(2))
            self.blue = int(match.group(3))
            return
        match = self.RGBA_PATTERN.fullmatch(plotly_color_str)
        if match is not None:
            self.red = int(match.group(1))
            self.green = int(match.group(2))
            self.blue = int(match.group(3))
            self.alpha = float(match.group(4))
            return
        self.html_color = plotly_color_str

    def set_rgba(self, red: int, green: int, blue: int, alpha: float = None):
        """
        Set the color by red, green, blue, transparency directly.
        """
        self.red = red
        self.green = green
        self.blue = blue
        self.alpha = alpha

    def __init__(self, red: Optional[int] = None, green: Optional[int] = None, blue: Optional[int] = None,
                 alpha: Optional[float] = None, plotly_color_str: Optional[str] = None):
        if plotly_color_str is not None:
            self.set_color_by_plotly_str(plotly_color_str)
        else:
            self.set_rgba(red, green, blue, alpha)

    def __str__(self):
        if self.html_color:
            return self.html_color
        if self.alpha is None:
            return "rgb(" + str(self.red) + ", " + str(self.green) + ", " + str(self.blue) + ")"
        return "rgba(" + str(self.red) + ", " + str(self.green) + ", " + str(self.blue) + ", " + str(self.alpha) + ")"


class PlotlyCspSurface(PyCspObject):
    """
    Describes a surface rendering option in 3D plot data.
    """
    SERIES_NAME__FIELD_NAME = "SeriesName"
    SHOW_SURFACE__FIELD_NAME = "IsShowSurface"
    NUM_SURFACES__FIELD_NAME = "NumSurfaces"
    FILL__FIELD_NAME = "Fill"
    PATTERN__FIELD_NAME = "FillPattern"

    @staticmethod
    def create(series_name: str, show_surface: bool, num_surfaces: int,
               fill: float, pattern: Optional[str]) -> PlotlyCspSurface:
        ret: PlotlyCspSurface = PlotlyCspSurface()
        ret.set_series_name(series_name)
        ret.set_show_surface(show_surface)
        ret.set_num_surfaces(num_surfaces)
        ret.set_fill(fill)
        ret.set_pattern(pattern)
        return ret

    def get_pattern(self) -> Optional[str]:
        return self.get_string_value(self.PATTERN__FIELD_NAME)

    def set_pattern(self, pattern: Optional[str]):
        self[self.PATTERN__FIELD_NAME] = pattern

    def get_fill(self) -> Optional[float]:
        return self.get_float_value(self.FILL__FIELD_NAME)

    def set_fill(self, fill: Optional[float]):
        self[self.FILL__FIELD_NAME] = fill

    def get_num_surfaces(self) -> Optional[int]:
        return self.get_int_value(self.NUM_SURFACES__FIELD_NAME)

    def set_num_surfaces(self, num_surfaces: Optional[int]):
        self[self.NUM_SURFACES__FIELD_NAME] = num_surfaces

    def is_show_surface(self) -> Optional[bool]:
        return self.get_boolean_value(self.SHOW_SURFACE__FIELD_NAME)

    def set_show_surface(self, show_surface: Optional[bool]):
        self[self.SHOW_SURFACE__FIELD_NAME] = show_surface

    def get_series_name(self) -> Optional[str]:
        return self.get_string_value(self.SERIES_NAME__FIELD_NAME)

    def set_series_name(self, series_name: Optional[str]) -> None:
        self[self.SERIES_NAME__FIELD_NAME] = series_name

    def get_model_key(self) -> str:
        return self.get_series_name()


class PlotlyCspMarker(PyCspObject):
    """
    Represents a marker format for a series in a plotly chart.
    """

    SERIES_NAME__FIELD_NAME = "SeriesName"
    SYMBOL__FIELD_NAME = "Symbol"
    COLOR__FIELD_NAME = "MarkerColor"
    COLOR_ARRAY__FIELD_NAME = "ColorArray"
    MARKER_SIZE__FIELD_NAME = "MarkerSize"
    OPACITY__FIELD_NAME = "Opacity"

    @staticmethod
    def create(series_name: str, symbol: Optional[PlotlyMarkerSymbol] = None,
               size: Optional[int] = None, opacity: Optional[float] = None) -> PlotlyCspMarker:
        ret: PlotlyCspMarker = PlotlyCspMarker()
        ret.set_series_name(series_name)
        ret.set_symbol(symbol)
        ret.set_size(size)
        ret.set_opacity(opacity)
        return ret

    def get_symbol(self) -> Optional[str]:
        return self.get_string_value(self.SYMBOL__FIELD_NAME)

    def set_symbol(self, symbol: PlotlyMarkerSymbol) -> None:
        self[self.SYMBOL__FIELD_NAME] = symbol.plotly_id

    def get_series_name(self) -> Optional[str]:
        return self.get_string_value(self.SERIES_NAME__FIELD_NAME)

    def set_series_name(self, series_name: Optional[str]) -> None:
        self[self.SERIES_NAME__FIELD_NAME] = series_name

    def get_color(self) -> Optional[str]:
        return self.get_string_value(self.COLOR__FIELD_NAME)

    def set_color(self, color: PlotlyColor) -> None:
        if not color:
            self[self.COLOR__FIELD_NAME] = None
        else:
            self[self.COLOR__FIELD_NAME] = str(color)

    def get_color_array(self) -> Optional[List[str]]:
        return self[self.COLOR_ARRAY__FIELD_NAME]

    def set_color_array(self, color_array: Optional[List[str]]) -> None:
        self[self.COLOR_ARRAY__FIELD_NAME] = color_array

    def get_size(self) -> Optional[int]:
        return self.get_int_value(self.MARKER_SIZE__FIELD_NAME)

    def set_size(self, size: Optional[int]) -> None:
        self[self.MARKER_SIZE__FIELD_NAME] = size

    def get_opacity(self) -> Optional[float]:
        return self.get_float_value(self.OPACITY__FIELD_NAME)

    def set_opacity(self, opacity: Optional[float]) -> None:
        self[self.OPACITY__FIELD_NAME] = opacity

    def get_model_key(self) -> str:
        return self.get_series_name()


class PlotlyCspMargins(PyCspObject):
    """
    Represents a Plotly Margins Config that goes on the Layout.
    """

    def get_model_key(self) -> str:
        return self.KEYLESS_MODEL_KEY

    @staticmethod
    def create(left: float, right: float, top: float, bottom: float) -> PlotlyCspMargins:
        ret: PlotlyCspMargins = PlotlyCspMargins()
        ret.set_left(left)
        ret.set_right(right)
        ret.set_top(top)
        ret.set_bottom(bottom)
        return ret

    LEFT = "Left"
    RIGHT = "Right"
    TOP = "Top"
    BOTTOM = "Bottom"
    AUTO_EXPAND = "AutoExpand"

    def get_left(self) -> Optional[float]:
        return self.get_float_value(self.LEFT)

    def set_left(self, value: Optional[float]) -> None:
        self[self.LEFT] = value

    def get_right(self) -> Optional[float]:
        return self.get_float_value(self.RIGHT)

    def set_right(self, value: Optional[float]) -> None:
        self[self.RIGHT] = value

    def get_top(self) -> Optional[float]:
        return self.get_float_value(self.TOP)

    def set_top(self, value: Optional[float]):
        self[self.TOP] = value

    def get_bottom(self) -> Optional[float]:
        return self.get_float_value(self.BOTTOM)

    def set_bottom(self, bottom: Optional[float]) -> None:
        self[self.BOTTOM] = bottom

    def is_auto_expand(self) -> Optional[bool]:
        return self.get_boolean_value(self.AUTO_EXPAND)

    def set_auto_expand(self, value: Optional[bool]):
        self[self.AUTO_EXPAND] = value


class PlotlyCspLine(PyCspObject):
    """
    Represents styling of a plotly line.
    """
    SERIES_NAME__FIELD_NAME = "SeriesName"
    DASH__FIELD_NAME = "Dash"
    LINE_COLOR__FIELD_NAME = "Color"
    LINE_WIDTH__FIELD_NAME = "Width"

    def get_series_name(self) -> Optional[str]:
        return self.get_string_value(self.SERIES_NAME__FIELD_NAME)

    def set_series_name(self, value: Optional[str]) -> None:
        self[self.SERIES_NAME__FIELD_NAME] = value

    def get_dash_style(self) -> Optional[str]:
        return self.get_string_value(self.DASH__FIELD_NAME)

    def set_dash_style(self, value: Optional[PlotlyDashStyle]) -> None:
        if value is None:
            self[self.DASH__FIELD_NAME] = None
        else:
            self[self.DASH__FIELD_NAME] = value.plotly_id

    def get_line_color(self) -> Optional[str]:
        return self.get_string_value(self.LINE_COLOR__FIELD_NAME)

    def set_line_color(self, value: Optional[PlotlyColor]) -> None:
        if value is None:
            self[self.LINE_COLOR__FIELD_NAME] = None
        else:
            self[self.LINE_COLOR__FIELD_NAME] = str(value)

    def get_line_width(self) -> Optional[int]:
        return self.get_int_value(self.LINE_WIDTH__FIELD_NAME)

    def set_line_width(self, value: Optional[int]) -> None:
        self[self.LINE_WIDTH__FIELD_NAME] = value

    def get_model_key(self) -> str:
        return self.get_series_name()

    @staticmethod
    def create(series_name: str, dash_style: Optional[PlotlyDashStyle],
               color: Optional[PlotlyColor], width_px: int) -> PlotlyCspLine:
        ret: PlotlyCspLine = PlotlyCspLine()
        ret.set_series_name(series_name)
        ret.set_dash_style(dash_style)
        ret.set_line_color(color)
        ret.set_line_width(width_px)
        return ret


class PlotlyCspHoverLabel(PyCspObject):
    """
    Represents a Plotly HoverLabel Config that goes on annotation and others.
    """
    BG_COLOR__FIELD_NAME = "bgcolor"
    BORDER_COLOR__FIELD_NAME = "bordercolor"
    FONT__FIELD_NAME = "Font"

    def get_model_key(self) -> str:
        return self.KEYLESS_MODEL_KEY

    def get_bg_color(self) -> Optional[str]:
        return self.get_string_value(self.BG_COLOR__FIELD_NAME)

    def set_bg_color(self, value: Optional[str]) -> None:
        self[self.BG_COLOR__FIELD_NAME] = value

    def get_border_color(self) -> Optional[str]:
        return self.get_string_value(self.BORDER_COLOR__FIELD_NAME)

    def set_border_color(self, value: Optional[str]) -> None:
        self[self.BORDER_COLOR__FIELD_NAME] = value


class PlotlyCspGrid(PyCspObject):
    """
    Represents a Plotly Grid Config that goes on the Layout.
    """

    def get_model_key(self) -> str:
        return self.KEYLESS_MODEL_KEY

    ROWS = "Rows"
    COLS = "Columns"
    PATTERN = "Pattern"
    X_GAP = "XGap"
    Y_GAP = "YGap"

    @staticmethod
    def create(num_rows: int, num_cols: int, pattern: Optional[str] = None) -> PlotlyCspGrid:
        ret: PlotlyCspGrid = PlotlyCspGrid()
        ret.set_num_of_rows(num_rows)
        ret.set_num_of_cols(num_cols)
        ret.set_pattern(pattern)
        return ret

    def get_num_of_rows(self) -> int:
        return self.get_int_value(self.ROWS)

    def set_num_of_rows(self, value: int) -> None:
        self[self.ROWS] = value

    def get_num_of_cols(self) -> int:
        return self.get_int_value(self.COLS)

    def set_num_of_cols(self, value: int) -> None:
        self[self.COLS] = value

    def get_pattern(self) -> Optional[str]:
        return self.get_string_value(self.PATTERN)

    def set_pattern(self, value: Optional[str]) -> None:
        self[self.PATTERN] = value

    def get_x_gap(self) -> Optional[float]:
        return self.get_float_value(self.X_GAP)

    def set_x_gap(self, value: Optional[float]) -> None:
        self[self.X_GAP] = value

    def get_y_gap(self) -> Optional[float]:
        return self.get_float_value(self.Y_GAP)

    def set_y_gap(self, value: Optional[float]) -> None:
        self[self.Y_GAP] = value


class PlotlyCspErrorBarData(PyCspObject):

    def get_model_key(self) -> str:
        return self.KEYLESS_MODEL_KEY

    VISIBLE__FIELD_NAME = "IsVisible"
    TYPE__FIELD_NAME = "ErrorBarType"
    SYMMETRIC__FIELD_NAME = "IsSymmetric"
    ARRAY_PLUS__FIELD_NAME = "UpperArray"
    ARRAY_MINUS__FIELD_NAME = "LowerArray"
    VALUE_PLUS__FIELD_NAME = "ValuePlus"
    VALUE_MINUS__FIELD_NAME = "ValueMinus"
    TRACE_REF_PLUS__FIELD_NAME = "TraceRef"
    TRACE_REF_MINUS__FIELD_NAME = "TraceRefMinus"
    STROKE_COLOR__FIELD_NAME = "StrokeColor"
    THICKNESS__FIELD_NAME = "Thickness"
    WIDTH__FIELD_NAME = "Width"

    @staticmethod
    def create_with_symmetric_array(error_array: List[float]) -> PlotlyCspErrorBarData:
        ret: PlotlyCspErrorBarData = PlotlyCspErrorBarData()
        ret.set_visible(True)
        ret.set_error_bar_type(PlotlyErrorBarType.DATA)
        ret.set_symmetric(True)
        ret.set_array_plus(error_array)
        return ret

    @staticmethod
    def create_with_error_arrays(plus_array: List[float], minus_array: List[float]) -> PlotlyCspErrorBarData:
        ret: PlotlyCspErrorBarData = PlotlyCspErrorBarData()
        ret.set_visible(True)
        ret.set_symmetric(True)
        ret.set_error_bar_type(PlotlyErrorBarType.DATA)
        ret.set_array_plus(plus_array)
        ret.set_array_minus(minus_array)
        return ret

    @staticmethod
    def create_with_static_symmetric_error(error_type: PlotlyErrorBarType, value: float):
        ret: PlotlyCspErrorBarData = PlotlyCspErrorBarData()
        ret.set_visible(True)
        ret.set_symmetric(True)
        if error_type == PlotlyErrorBarType.DATA:
            raise CspDataException("When creating symmetric static error, DATA is not a valid mode.")
        ret.set_error_bar_type(error_type)
        ret.set_value_plus(value)

    @staticmethod
    def create_with_static_errors(error_type: PlotlyErrorBarType, value_plus: float, value_minus: float):
        ret: PlotlyCspErrorBarData = PlotlyCspErrorBarData()
        ret.set_visible(True)
        ret.set_symmetric(True)
        if error_type == PlotlyErrorBarType.DATA:
            raise CspDataException("When creating symmetric static error, DATA is not a valid mode.")
        ret.set_error_bar_type(error_type)
        ret.set_value_plus(value_plus)
        ret.set_value_minus(value_minus)
        return ret

    def is_visible(self) -> bool:
        return self.get_boolean_value(self.VISIBLE__FIELD_NAME)

    def set_visible(self, value: bool) -> None:
        self[self.VISIBLE__FIELD_NAME] = value

    def get_error_bar_type(self) -> str:
        return self.get_string_value(self.TYPE__FIELD_NAME)

    def set_error_bar_type(self, value: PlotlyErrorBarType) -> None:
        self[self.TYPE__FIELD_NAME] = value.plotly_id

    def is_symmetric(self) -> Optional[bool]:
        return self.get_boolean_value(self.SYMMETRIC__FIELD_NAME)

    def set_symmetric(self, value: Optional[bool]) -> None:
        self[self.SYMMETRIC__FIELD_NAME] = value

    def get_array_plus(self) -> List[float]:
        return self[self.ARRAY_PLUS__FIELD_NAME]

    def set_array_plus(self, value: List[float]):
        self[self.ARRAY_PLUS__FIELD_NAME] = value

    def get_array_minus(self) -> List[float]:
        return self[self.ARRAY_MINUS__FIELD_NAME]

    def set_array_minus(self, value: List[float]):
        self[self.ARRAY_MINUS__FIELD_NAME] = value

    def get_value_plus(self) -> Optional[float]:
        return self.get_float_value(self.VALUE_PLUS__FIELD_NAME)

    def set_value_plus(self, value: Optional[float]) -> None:
        self[self.VALUE_PLUS__FIELD_NAME] = value

    def get_value_minus(self) -> Optional[float]:
        return self.get_float_value(self.VALUE_MINUS__FIELD_NAME)

    def set_value_minus(self, value: Optional[float]) -> None:
        self[self.VALUE_MINUS__FIELD_NAME] = value

    def get_trace_ref_plus(self) -> Optional[float]:
        return self.get_float_value(self.TRACE_REF_PLUS__FIELD_NAME)

    def set_trace_ref_plus(self, value: Optional[float]) -> None:
        self[self.TRACE_REF_PLUS__FIELD_NAME] = value

    def get_trace_ref_minus(self) -> Optional[float]:
        return self.get_float_value(self.TRACE_REF_MINUS__FIELD_NAME)

    def set_trace_ref_minus(self, value: Optional[float]) -> None:
        self[self.TRACE_REF_MINUS__FIELD_NAME] = value

    def get_stroke_color(self) -> Optional[str]:
        return self.get_string_value(self.STROKE_COLOR__FIELD_NAME)

    def set_stroke_color(self, color: Optional[PlotlyColor]) -> None:
        if color is None:
            self[self.STROKE_COLOR__FIELD_NAME] = None
        else:
            self[self.STROKE_COLOR__FIELD_NAME] = str(color)

    def get_thickness(self) -> Optional[int]:
        return self.get_int_value(self.THICKNESS__FIELD_NAME)

    def set_thickness(self, value: Optional[int]) -> None:
        self[self.THICKNESS__FIELD_NAME] = value

    def get_width(self) -> Optional[int]:
        return self.get_int_value(self.WIDTH__FIELD_NAME)

    def set_width(self, value: Optional[int]) -> None:
        self[self.WIDTH__FIELD_NAME] = value


class PlotlyCspFont(PyCspObject):

    def get_model_key(self) -> str:
        return self.KEYLESS_MODEL_KEY

    FONT_FAMILY__FIELD_NAME = 'FontFamilyStyling'
    FONT_SIZE__FIELD_NAME = "FontSizeStyling"
    FONT_COLOR__FIELD_NAME = "FontColorStyling"

    def get_font_family_type(self) -> Optional[str]:
        return self.get_string_value(self.FONT_FAMILY__FIELD_NAME)

    def set_font_family_type(self, font_family_type: Optional[str]):
        self[self.FONT_FAMILY__FIELD_NAME] = font_family_type

    def set_font_size(self, font_size: Optional[int]):
        self[self.FONT_SIZE__FIELD_NAME] = font_size

    def get_font_size(self) -> Optional[int]:
        return self.get_int_value(self.FONT_SIZE__FIELD_NAME)

    def set_font_color(self, value: Optional[PlotlyColor]):
        if value is None:
            self[self.FONT_COLOR__FIELD_NAME] = None
        else:
            self[self.FONT_COLOR__FIELD_NAME] = str(value)

    def get_font_color(self) -> Optional[str]:
        return self.get_string_value(self.FONT_COLOR__FIELD_NAME)


class PlotlyCspAxis(PyCspObject):
    def get_model_key(self) -> str:
        orientation = self.get_orientation()
        if orientation is None:
            return ""
        return orientation.name

    ORIENTATION__FIELD_NAME = "Orientation"
    TITLE__FIELD_NAME = "Title"
    AUTO_RANGE__FIELD_NAME = "IsAutoRange"
    AXIS_RANGE_MODE__FIELD_NAME = "AxisRangeMode"
    RANGE_MIN__FIELD_NAME = "RangeMin"
    RANGE_MAX__FIELD_NAME = "RangeMax"
    AXIS_TYPE__FIELD_NAME = "AxisType"
    ZERO_LINE__FIELD_NAME = "ZeroLine"
    SHOW_GRID__FIELD_NAME = "ShowGrid"
    SHOW_LINE__FIELD_NAME = "ShowLine"
    CATEGORY_ORDER = "CategoryOrder"
    CATEGORY_ARRAY = "CategoryArray"
    SUBPLOT_AXIS_PROPERTY_NAME = "SubplotAxisPropertyName"
    DOMAIN_CONFIG = "DomainConfig"
    ANCHOR = "Anchor"
    TICK_FONT__FIELD_NAME = "TickFont"
    TITLE_FONT__FIELD_NAME = "TitleFont"
    ZEROLINE_COLOR__FIELD_NAME = "ZeroLineColor"
    LINE_COLOR__FIELD_NAME = "LineColor"
    GRID_COLOR__FIELD_NAME = "GridColor"

    def is_show_line(self) -> Optional[bool]:
        return self.get_boolean_value(self.SHOW_LINE__FIELD_NAME)

    def set_show_line(self, value: Optional[bool]) -> None:
        self[self.SHOW_LINE__FIELD_NAME] = value

    def is_zero_line(self) -> Optional[bool]:
        return self.get_boolean_value(self.ZERO_LINE__FIELD_NAME)

    def set_zero_line(self, value: Optional[bool]) -> None:
        self[self.ZERO_LINE__FIELD_NAME] = value

    def get_zero_line_color(self) -> Optional[str]:
        return self.get_string_value(self.ZEROLINE_COLOR__FIELD_NAME)

    def set_zero_line_color(self, value: Optional[str]) -> None:
        self[self.ZEROLINE_COLOR__FIELD_NAME] = value

    def get_grid_color(self) -> Optional[str]:
        return self.get_string_value(self.GRID_COLOR__FIELD_NAME)

    def set_grid_color(self, grid_color: Optional[str]) -> None:
        self[self.GRID_COLOR__FIELD_NAME] = grid_color

    def get_line_color(self) -> Optional[str]:
        return self.get_string_value(self.LINE_COLOR__FIELD_NAME)

    def set_line_color(self, value: Optional[str]) -> None:
        self[self.LINE_COLOR__FIELD_NAME] = value

    def is_show_grid(self) -> Optional[bool]:
        return self.get_boolean_value(self.SHOW_GRID__FIELD_NAME)

    def set_show_grid(self, value: Optional[bool]) -> None:
        self[self.SHOW_GRID__FIELD_NAME] = value

    def get_category_array(self) -> Optional[List[str]]:
        return self[self.CATEGORY_ARRAY]

    def set_category_array(self, value: Optional[List[str]]) -> None:
        self[self.CATEGORY_ARRAY] = value

    def get_category_order(self) -> str:
        return self.get_string_value(self.CATEGORY_ORDER)

    def set_category_order(self, category_order: PlotlyAxisCategoryOrder):
        self[self.CATEGORY_ORDER] = category_order

    def get_range_max(self) -> Optional[float]:
        return self.get_float_value(self.RANGE_MAX__FIELD_NAME)

    def get_range_min(self) -> Optional[float]:
        return self.get_float_value(self.RANGE_MIN__FIELD_NAME)

    def set_axis_range(self, manual_min: Optional[float], manual_max: Optional[float]):
        if manual_min is None or manual_max is None:
            self.set_auto_range(True)
            self[self.RANGE_MIN__FIELD_NAME] = None
            self[self.RANGE_MAX__FIELD_NAME] = None
        else:
            self.set_auto_range(False)
            self[self.RANGE_MIN__FIELD_NAME] = manual_min
            self[self.RANGE_MAX__FIELD_NAME] = manual_max

    def get_range_mode(self) -> Optional[PlotlyAxisRangeMode]:
        name: Optional[str] = self.get_string_value(self.AXIS_RANGE_MODE__FIELD_NAME)
        if name is None:
            return None
        return PlotlyAxisRangeMode[name]

    def set_range_mode(self, range_mode: PlotlyAxisRangeMode):
        self[self.AXIS_RANGE_MODE__FIELD_NAME] = range_mode.name

    def is_auto_range(self) -> Optional[bool]:
        return self.get_boolean_value(self.AUTO_RANGE__FIELD_NAME)

    def set_auto_range(self, value: Optional[bool]):
        self[self.AUTO_RANGE__FIELD_NAME] = value

    def get_title(self) -> Optional[str]:
        return self.get_string_value(self.TITLE__FIELD_NAME)

    def set_title(self, value: Optional[str]):
        self[self.TITLE__FIELD_NAME] = value

    def get_axis_type(self) -> Optional[PlotlyAxisType]:
        name = self.get_string_value(self.AXIS_TYPE__FIELD_NAME)
        if name is None:
            return None
        return PlotlyAxisType[name]

    def set_axis_type(self, value: PlotlyAxisType):
        self[self.AXIS_TYPE__FIELD_NAME] = value.name

    def get_orientation(self) -> Optional[PlotlyAxisOrientation]:
        name: str = self[self.ORIENTATION__FIELD_NAME]
        if not name:
            return None
        return PlotlyAxisOrientation[name]

    def set_orientation(self, orientation: PlotlyAxisOrientation) -> None:
        self[self.ORIENTATION__FIELD_NAME] = orientation.name

    def get_subplot_axis_property_name(self) -> Optional[str]:
        return self.get_string_value(self.SUBPLOT_AXIS_PROPERTY_NAME)

    def set_subplot_axis_property_name(self, property_name: Optional[str]) -> None:
        self[self.SUBPLOT_AXIS_PROPERTY_NAME] = property_name

    def get_anchor(self) -> Optional[str]:
        return self.get_string_value(self.ANCHOR)

    def set_anchor(self, value: Optional[str]) -> None:
        self[self.ANCHOR] = value


class PlotlyCspData(PyCspObject):
    SERIES_NAME__FIELD_NAME = "SeriesName"
    X_VALUE_LIST__FIELD_NAME = "XValueList"
    Y_VALUE_LIST__FIELD_NAME = "YValueList"
    Z_VALUE_LIST__FIELD_NAME = "ZValueList"
    DATA_TYPE__FIELD_NAME = "DataType"
    MARKER__FIELD_NAME = "Marker"
    LINE__FIELD_NAME = "Line"
    VALUE_LIST__FIELD_NAME = "ValueList"
    ISO_MIN__FIELD_NAME = "IsoMin"
    ISO_MAX__FIELD_NAME = "IsoMax"
    COLOR_SCALE__FIELD_NAME = "ColorScale"
    SURFACE__FIELD_NAME = "Surface"
    CONTOUR__FIELD_NAME = "Contour"
    X_ERROR_BAR__FIELD_NAME = "XErrorBar"
    Y_ERROR_BAR__FIELD_NAME = "YErrorBar"
    Z_ERROR_BAR__FIELD_NAME = "ZErrorBar"
    MODE__FIELD_NAME = "Mode"
    BOX_POINTS__FIELD_NAME = "BoxPoints"
    JITTER__FIELD_NAME = "Jitter"
    POINT_POS__FIELD_NAME = "PointsPosition"
    FILL_COLOR__FIELD_NAME = "FillColor"
    CUSTOM_DATA__FIELD_NAME = "CustomData"
    HOVER_TEMPLATE__FIELD_NAME = "HoverTemplate"
    IS_REVERSE_SCALE__FIELD_NAME = "IsReverseScale"
    IS_SHOW_SCALE__FIELD_NAME = "IsShowScale"
    NUM_CONTOURS__FIELD_NAME = "NumContours"
    HIST_NORM__FIELD_NAME = "HistNorm"
    NUM_DESIRED_BINS_X__FIELD_NAME = "nbinsx"
    NUM_DESIRED_BINS_Y__FIELD_NAME = "nbinsy"
    Z_MIN__FIELD_NAME = "zmin"
    Z_MAX__FIELD_NAME = "zmax"
    X_AXIS = "XAxis"
    Y_AXIS = "YAxis"
    FILL__FIELD_NAME = "Fill"

    def get_hist_norm_func(self) -> Optional[PlotlyHistNorm]:
        name = self.get_string_value(self.HIST_NORM__FIELD_NAME)
        if name is None:
            return None
        return PlotlyHistNorm[name]

    def set_hist_norm_func(self, value: Optional[PlotlyHistNorm]) -> None:
        if value is None:
            self[self.HIST_NORM__FIELD_NAME] = None
        else:
            self[self.HIST_NORM__FIELD_NAME] = value.name

    def get_fill_method(self) -> Optional[str]:
        return self.get_string_value(self.FILL__FIELD_NAME)

    def set_fill_method(self, value: Optional[PlotlyFill]) -> None:
        if value is None:
            self[self.FILL__FIELD_NAME] = None
        else:
            self[self.FILL__FIELD_NAME] = value.plotly_id

    def get_z_min(self) -> Optional[float]:
        return self.get_float_value(self.Z_MIN__FIELD_NAME)

    def get_z_max(self) -> Optional[float]:
        return self.get_float_value(self.Z_MAX__FIELD_NAME)

    def set_z_value_range(self, z_min: float, z_max: float):
        self[self.Z_MIN__FIELD_NAME] = z_min
        self[self.Z_MAX__FIELD_NAME] = z_max

    def clear_z_value_range(self):
        self[self.Z_MAX__FIELD_NAME] = None
        self[self.Z_MIN__FIELD_NAME] = None

    def get_num_contours(self) -> Optional[int]:
        return self.get_int_value(self.NUM_CONTOURS__FIELD_NAME)

    def set_num_contours(self, value: Optional[int]) -> None:
        self[self.NUM_CONTOURS__FIELD_NAME] = value

    def is_show_scale(self) -> Optional[bool]:
        return self.get_boolean_value(self.IS_SHOW_SCALE__FIELD_NAME)

    def set_show_scale(self, value: Optional[bool]):
        self[self.IS_SHOW_SCALE__FIELD_NAME] = value

    def is_reverse_scale(self) -> Optional[bool]:
        return self.get_boolean_value(self.IS_REVERSE_SCALE__FIELD_NAME)

    def set_reverse_scale(self, value: Optional[bool]):
        self[self.IS_REVERSE_SCALE__FIELD_NAME] = value

    def get_hover_template(self):
        return self.get_string_value(self.HOVER_TEMPLATE__FIELD_NAME)

    def set_hover_template(self, hover_template: Optional[str]):
        self[self.HOVER_TEMPLATE__FIELD_NAME] = hover_template

    def get_custom_data_list(self) -> Optional[List[Dict[str, str]]]:
        return self[self.CUSTOM_DATA__FIELD_NAME]

    def set_custom_data_list(self, value: Optional[List[Dict[str, str]]]):
        self[self.CUSTOM_DATA__FIELD_NAME] = value

    def get_fill_color(self) -> Optional[str]:
        return self.get_string_value(self.FILL_COLOR__FIELD_NAME)

    def set_fill_color(self, value: Optional[PlotlyColor]):
        if value is None:
            self[self.FILL_COLOR__FIELD_NAME] = None
        else:
            self[self.FILL_COLOR__FIELD_NAME] = str(value)

    def get_points_position(self) -> Optional[float]:
        return self.get_float_value(self.POINT_POS__FIELD_NAME)

    def set_points_position(self, value: Optional[float]):
        self[self.POINT_POS__FIELD_NAME] = value

    def get_jitter(self) -> Optional[float]:
        return self.get_float_value(self.JITTER__FIELD_NAME)

    def set_jitter(self, value: Optional[float]):
        self[self.JITTER__FIELD_NAME] = value

    def get_box_points(self):
        return self.get_string_value(self.BOX_POINTS__FIELD_NAME)

    def set_box_points(self, value: Optional[PlotlyDataBoxPoints]):
        if value is None:
            self[self.BOX_POINTS__FIELD_NAME] = None
        else:
            self[self.BOX_POINTS__FIELD_NAME] = value.plotly_id

    def get_data_mode(self) -> Optional[str]:
        mode_list: List[str] = self[self.MODE__FIELD_NAME]
        if not mode_list:
            return None
        return "+".join(mode_list)

    def set_data_mode(self, value: Optional[List[PlotlyDataMode]]):
        if value is None:
            self[self.MODE__FIELD_NAME] = None
        else:
            self[self.MODE__FIELD_NAME] = [x.plotly_id for x in value]

    def get_z_error_bar(self) -> Optional[PlotlyCspErrorBarData]:
        return self.get_csp_data(self.Z_ERROR_BAR__FIELD_NAME, PlotlyCspErrorBarData)

    def set_z_error_bar(self, value: Optional[PlotlyCspErrorBarData]):
        self.set_csp_data(self.Z_ERROR_BAR__FIELD_NAME, value)

    def get_y_error_bar(self) -> Optional[PlotlyCspErrorBarData]:
        return self.get_csp_data(self.Y_ERROR_BAR__FIELD_NAME, PlotlyCspErrorBarData)

    def set_y_error_bar(self, value: Optional[PlotlyCspErrorBarData]):
        self.set_csp_data(self.Y_ERROR_BAR__FIELD_NAME, value)

    def get_x_error_bar(self) -> Optional[PlotlyCspErrorBarData]:
        return self.get_csp_data(self.X_ERROR_BAR__FIELD_NAME, PlotlyCspErrorBarData)

    def set_x_error_bar(self, value: Optional[PlotlyCspErrorBarData]):
        self.set_csp_data(self.X_ERROR_BAR__FIELD_NAME, value)

    def get_color_scale(self) -> Optional[str]:
        return self.get_string_value(self.COLOR_SCALE__FIELD_NAME)

    def set_color_scale(self, value: Optional[str]):
        self[self.COLOR_SCALE__FIELD_NAME] = value

    def get_iso_max(self) -> Optional[float]:
        return self.get_float_value(self.ISO_MAX__FIELD_NAME)

    def set_iso_max(self, value: Optional[float]):
        self[self.ISO_MAX__FIELD_NAME] = value

    def get_iso_min(self) -> Optional[float]:
        return self.get_float_value(self.ISO_MIN__FIELD_NAME)

    def set_iso_min(self, value: Optional[float]):
        self[self.ISO_MIN__FIELD_NAME] = value

    def get_value_list(self):
        return self[self.VALUE_LIST__FIELD_NAME]

    def set_value_list(self, value) -> None:
        self[self.VALUE_LIST__FIELD_NAME] = value

    def get_series_name(self) -> Optional[str]:
        return self.get_string_value(self.SERIES_NAME__FIELD_NAME)

    def set_series_name(self, value: Optional[str]) -> None:
        self[self.SERIES_NAME__FIELD_NAME] = value

    def get_data_type(self) -> str:
        return self.get_string_value(self.DATA_TYPE__FIELD_NAME)

    def get_line(self) -> Optional[PlotlyCspLine]:
        return self.get_csp_data(self.LINE__FIELD_NAME, PlotlyCspLine)

    def get_marker(self) -> Optional[PlotlyCspMarker]:
        return self.get_csp_data(self.MARKER__FIELD_NAME, PlotlyCspMarker)

    def get_z_value_list(self):
        return self[self.Z_VALUE_LIST__FIELD_NAME]

    def get_y_value_list(self):
        return self[self.Y_VALUE_LIST__FIELD_NAME]

    def get_x_value_list(self):
        return self[self.X_VALUE_LIST__FIELD_NAME]

    def set_line(self, line: Optional[PlotlyCspLine]) -> None:
        self.set_csp_data(self.LINE__FIELD_NAME, line)

    def set_marker(self, value: Optional[PlotlyCspMarker]) -> None:
        self.set_csp_data(self.MARKER__FIELD_NAME, value)

    def set_data_type(self, value: PlotlyDataType) -> None:
        self[self.DATA_TYPE__FIELD_NAME] = value.plotly_id

    def set_z_value_list(self, value):
        self[self.Z_VALUE_LIST__FIELD_NAME] = value

    def set_y_value_list(self, value):
        self[self.Y_VALUE_LIST__FIELD_NAME] = value

    def set_x_value_list(self, value):
        self[self.X_VALUE_LIST__FIELD_NAME] = value

    def get_surface(self) -> Optional[PlotlyCspSurface]:
        return self.get_csp_data(self.SURFACE__FIELD_NAME, PlotlyCspSurface)

    def set_surface(self, value: Optional[PlotlyCspSurface]):
        self.set_csp_data(self.SURFACE__FIELD_NAME, value)

    def get_num_bins_x(self) -> Optional[int]:
        return self.get_int_value(self.NUM_DESIRED_BINS_X__FIELD_NAME)

    def set_num_bins_x(self, value: Optional[int]):
        self[self.NUM_DESIRED_BINS_X__FIELD_NAME] = value

    def get_num_bins_y(self) -> Optional[int]:
        return self.get_int_value(self.NUM_DESIRED_BINS_Y__FIELD_NAME)

    def set_num_bins_y(self, value: Optional[int]):
        self[self.NUM_DESIRED_BINS_Y__FIELD_NAME] = value

    def get_x_axis(self) -> Optional[str]:
        return self.get_string_value(self.X_AXIS)

    def set_x_axis(self, value: Optional[str]) -> None:
        self[self.X_AXIS] = value

    def get_y_axis(self) -> Optional[str]:
        return self.get_string_value(self.Y_AXIS)

    def set_y_axis(self, value: Optional[str]):
        self[self.Y_AXIS] = value

    def get_model_key(self) -> str:
        return self.get_series_name()


class PlotlyCspChart(PyCspObject):
    ID__FIELD_NAME = "ChartId"
    TITLE__FIELD_NAME = "ChartTitle"
    SERIES_DATA_LIST__FIELD_NAME = "SeriesDataList"
    AXIS_CONFIG_LIST__FIELD_NAME = "AxisConfigurationList"
    IS_3D_MODE__FIELD_NAME = "Is3D"
    HIDE_DISPLAY_MODE_BAR__FIELD_NAME = "HideDisplayModeBar"
    BAR_MODE__FIELD_NAME = "BarMode"
    BAR_NORM__FIELD_NAME = "BarNorm"
    IS_SHOW_LEGENDS__FIELD_NAME = "IsShowLegends"
    HOVER_MODE__FIELD_NAME = "HoverMode"
    IS_SHOW_HEATMAP_ANNOTATIONS = "IsShowHeatmapAnnotations"
    HEATMAP_ANNOTATION_STYLES = "HeatmapAnnotationStyles"
    ANNOTATION = "Annotations"
    SHAPES = "Shapes"
    DRAG_MODE = "DragMode"
    GRID_CONFIG = "GridConfig"
    MARGINS = "Margins"
    DIRECT_JSON_DATA = "DirectJsonData"

    def get_direct_json_data(self) -> Optional[str]:
        return self.get_string_value(self.DIRECT_JSON_DATA)

    def set_direct_json_data(self, json: str | None):
        self[self.DIRECT_JSON_DATA] = json

    def is_show_heatmap_annotations(self) -> bool:
        return self.get_boolean_value(self.IS_SHOW_HEATMAP_ANNOTATIONS, False)

    def is_show_legends(self) -> bool:
        return self.get_boolean_value(self.IS_SHOW_LEGENDS__FIELD_NAME, True)

    def set_show_legends(self, value: bool):
        self[self.IS_SHOW_LEGENDS__FIELD_NAME] = value

    def get_hover_mode_plotly_id(self) -> Optional[str]:
        return self.get_string_value(self.HOVER_MODE__FIELD_NAME)

    def set_hover_mode(self, value: Optional[PlotlyHoverMode]):
        if value is None:
            self[self.HOVER_MODE__FIELD_NAME] = None
        else:
            self[self.HOVER_MODE__FIELD_NAME] = value.plotly_id

    def is_hide_display_mode_bar(self) -> bool:
        return self.get_boolean_value(self.HIDE_DISPLAY_MODE_BAR__FIELD_NAME, False)

    def set_hide_display_mode_bar(self, value: bool) -> None:
        self[self.HIDE_DISPLAY_MODE_BAR__FIELD_NAME] = value

    def get_axis_config_list(self) -> List[PlotlyCspAxis]:
        return self.get_csp_data_list(self.AXIS_CONFIG_LIST__FIELD_NAME, PlotlyCspAxis)

    def set_axis_config_list(self, value: List[PlotlyCspAxis]):
        self.set_csp_data_list(self.AXIS_CONFIG_LIST__FIELD_NAME, value)

    def get_series_data_list(self) -> Optional[List[PlotlyCspData]]:
        return self.get_csp_data_list(self.SERIES_DATA_LIST__FIELD_NAME, PlotlyCspData)

    def set_series_data_list(self, value: Optional[List[PlotlyCspData]]):
        self.set_csp_data_list(self.SERIES_DATA_LIST__FIELD_NAME, value)

    def get_title(self) -> Optional[str]:
        return self.get_string_value(self.TITLE__FIELD_NAME)

    def set_title(self, value: Optional[str]) -> None:
        self[self.TITLE__FIELD_NAME] = value

    def get_id(self) -> Optional[str]:
        return self.get_string_value(self.ID__FIELD_NAME)

    def set_id(self, value: Optional[str]) -> None:
        self[self.ID__FIELD_NAME] = value

    def get_model_key(self) -> str:
        return self.get_id()

    def get_bar_norm(self) -> Optional[str]:
        return self.get_string_value(self.BAR_NORM__FIELD_NAME)

    def set_bar_norm(self, bar_norm: PlotlyBarNorm):
        if bar_norm is None:
            self[self.BAR_NORM__FIELD_NAME] = None
        else:
            self[self.BAR_NORM__FIELD_NAME] = bar_norm.plotly_id

    def get_bar_mode(self) -> str:
        return self.get_string_value(self.BAR_NORM__FIELD_NAME)

    def get_grid(self) -> Optional[PlotlyCspGrid]:
        return self.get_csp_data(self.GRID_CONFIG, PlotlyCspGrid)

    def set_grid(self, grid: PlotlyCspGrid) -> None:
        self.set_csp_data(self.GRID_CONFIG, grid)

    def get_margins(self) -> Optional[PlotlyCspMargins]:
        return self.get_csp_data(self.MARGINS, PlotlyCspMargins)

    def set_margins(self, value: Optional[PlotlyCspMargins]) -> None:
        self.set_csp_data(self.MARGINS, value)