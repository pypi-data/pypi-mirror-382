from __future__ import annotations

from enum import Enum
from typing import Optional


class PlotlyAxisOrientation(Enum):
    X = 0
    Y = 1
    Z = 2


class PlotlyMarkerSymbol(Enum):
    CIRCLE = "circle"
    CIRCLE_OPEN = "circle-open"
    CIRCLE_DOT = "circle-dot",
    CIRCLE_OPEN_DOT = "circle-open-dot"
    SQUARE = "square"
    SQUARE_OPEN = "square-open"
    SQUARE_DOT = "square-dot"
    SQUARE_OPEN_DOT = "square-open-dot"
    DIAMOND = "diamond",
    DIAMOND_OPEN = "diamond-open"
    DIAMOND_DOT = "diamond-dot"
    DIAMOND_OPEN_DOT = "diamond-open-dot"
    CROSS = "cross"
    CROSS_OPEN = "cross-open"
    CROSS_DOT = "cross-dot"
    CROSS_OPEN_DOT = "cross-open-dot",
    STAR = "star"
    STAR_SQUARE = "star-square"
    STAR_DIAMOND = "star-diamond",
    HOURGLASS = "hourglass"
    BOWTIE = "bowtie"

    plotly_id: str

    def __init__(self, plotly_id: str):
        self.plotly_id = plotly_id

    @staticmethod
    def from_plotly_id(plotly_id: Optional[str]) -> Optional[PlotlyMarkerSymbol]:
        for v in PlotlyMarkerSymbol:
            if v.plotly_id == plotly_id:
                return v
        return None


class PlotlyHoverMode(Enum):
    X = "x"
    Y = "y"
    CLOSEST = "closest"
    X_UNIFIED = "x unified"
    Y_UNIFIED = "y unified"

    plotly_id: str

    def __init__(self, plotly_id: str):
        self.plotly_id = plotly_id

    @staticmethod
    def from_plotly_id(plotly_id: Optional[str]) -> Optional[PlotlyHoverMode]:
        for v in PlotlyHoverMode:
            if v.plotly_id == plotly_id:
                return v
        return None


class PlotlyHistNorm(Enum):
    NONE = None, "No Normalization"
    PERCENT = "percent", "Percentage"
    PROBABILITY = "probability", "Probability"
    DENSITY = "density", "Density"
    PROBABILITY_DENSITY = "probability density", "Probability-Density"

    plotly_id: str
    display_name: str

    def __init__(self, plotly_id: str, display_name: str):
        self.plotly_id = plotly_id
        self.display_name = display_name

    @staticmethod
    def from_plotly_id(plotly_id: Optional[str]) -> Optional[PlotlyHistNorm]:
        for v in PlotlyHistNorm:
            if v.plotly_id == plotly_id:
                return v
        return None


class PlotlyErrorBarType(Enum):
    CONSTANT = "constant", "Constant"
    PERCENT = "percent", "Percent"
    SQUARE_ROOT = "sqrt", "Square Root"
    DATA = "data", "Data Array"

    plotly_id: str
    display_name: str

    def __init__(self, plotly_id: str, display_name: str):
        self.plotly_id = plotly_id
        self.display_name = display_name

    @staticmethod
    def from_plotly_id(plotly_id: Optional[str]) -> Optional[PlotlyErrorBarType]:
        for v in PlotlyErrorBarType:
            if v.plotly_id == plotly_id:
                return v
        return None


class PlotlyDataType(Enum):
    SCATTER = "scatter", "Scatter (Vector Graphics)"
    SCATTER_GL = "scattergl", "Scatter (WebGL)"
    SCATTER_3D = "scatter3d", "3D Scatter"
    SURFACE = "surface", "Surface"
    MESH_3D = "mesh3d", "3D Mesh"
    CONE = "cone", "Cone"
    STREAM_TUBE = "streamtube", "Tube"
    ISO_SURFACE = "isosurface", "Isosurfance"
    BAR = "bar", "Bar"
    BOX = "box", "Box"
    HEAT_MAP = "heatmap", "Heatmap"
    DENSITY_MAP = "histogram2dcontour", "Density"
    HISTOGRAM = "histogram", "Histogram"

    plotly_id: str
    display_name: str

    def __init__(self, plotly_id: str, display_name: str):
        self.plotly_id = plotly_id
        self.display_name = display_name

    @staticmethod
    def from_plotly_id(plotly_id: Optional[str]) -> Optional[PlotlyDataType]:
        for v in PlotlyDataType:
            if v.plotly_id == plotly_id:
                return v
        return None


class PlotlyDataMode(Enum):
    LINES = "lines", "Lines"
    MARKERS = "markers", "Markers"
    TEXT = "text", "Text"

    plotly_id: str
    display_name: str

    def __init__(self, plotly_id: str, display_name: str):
        self.plotly_id = plotly_id
        self.display_name = display_name

    @staticmethod
    def from_plotly_id(plotly_id: Optional[str]) -> Optional[PlotlyDataMode]:
        for v in PlotlyDataMode:
            if v.plotly_id == plotly_id:
                return v
        return None


class PlotlyDataBoxPoints(Enum):
    ALL = "all", "All"
    OUTLIERS = "outliers", "Outliers"
    SUSPECTED_OUTLIERS = "suspectedoutliers", "Suspected Outliers"
    NONE = "false", "None"

    plotly_id: str
    display_name: str

    def __init__(self, plotly_id: str, display_name: str):
        self.plotly_id = plotly_id
        self.display_name = display_name

    @staticmethod
    def from_plotly_id(plotly_id: Optional[str]) -> Optional[PlotlyDataMode]:
        for v in PlotlyDataMode:
            if v.plotly_id == plotly_id:
                return v
        return None


class PlotlyDashStyle(Enum):
    SOLID = "solid", "Solid"
    DOT = "dot", "Dots"
    DASH = "dash", "Dashes"
    LONG_DASH = "longdash", "Long Dashes"
    DASH_DOT = "dashdot", "Dashes and Dots"
    LONG_DASH_DOT = "longdashdot", "Long Dashes and Dots"

    plotly_id: str
    display_name: str

    def __init__(self, plotly_id: str, display_name: str):
        self.plotly_id = plotly_id
        self.display_name = display_name

    @staticmethod
    def from_plotly_id(plotly_id: Optional[str]) -> Optional[PlotlyDashStyle]:
        for v in PlotlyDashStyle:
            if v.plotly_id == plotly_id:
                return v
        return None


class PlotlyColorScale(Enum):
    Greys = "Greys", "Greys"
    YELLOW_GREEN_BLUE = "YlGnBu", "Yellow-Green-Blue"
    Greens = "Greens", "Greens"
    YELLOW_ORANGE_RED = "YlOrRd", "Yellow-Orange-Red"
    BLUE_RED = "Bluered", "Blue-Red"
    RED_BLUE = "RdBu", "Red-Blue"
    Reds = "Reds", "Reds"
    Blues = "Blues", "Blues"
    Picnic = "Picnic", "Picnic"
    Rainbow = "Rainbow", "Rainbow"
    Portland = "Portland", "Portland"
    Jet = "Jet", "Jet"
    Hot = "Hot", "Hot"
    Blackbody = "Blackbody", "Blackbody"
    Earth = "Earth", "Earth"
    Electric = "Electric", "Electric"
    Viridis = "Viridis", "Viridis"
    Cividis = "Cividis", "Cividis"

    plotly_id: str
    display_name: str

    def __init__(self, plotly_id: str, display_name: str):
        self.plotly_id = plotly_id
        self.display_name = display_name

    @staticmethod
    def from_plotly_id(plotly_id: Optional[str]) -> Optional[PlotlyColorScale]:
        for v in PlotlyColorScale:
            if v.plotly_id == plotly_id:
                return v
        return None


class PlotlyBarNorm(Enum):
    DEFAULT = "", "None (As Is)"
    FRACTION = "fraction", "Fraction"
    PERCENT = "percent", "Percent"

    plotly_id: str
    display_name: str

    def __init__(self, plotly_id: str, display_name: str):
        self.plotly_id = plotly_id
        self.display_name = display_name

    @staticmethod
    def from_plotly_id(plotly_id: Optional[str]) -> Optional[PlotlyBarNorm]:
        for v in PlotlyBarNorm:
            if v.plotly_id == plotly_id:
                return v
        return None


class PlotlyAxisCategoryOrder(Enum):
    TRACE = "trace", "Trace of Data"
    CATEGORY_ASC = "category ascending", "Category Ascending"
    CATEGORY_DESC = "category descending", "Category Descending"
    ARRAY = "array", "Custom Order Array (Requires setting category array)"
    TOTAL_ASC = "total ascending", "Total Ascending"
    TOTAL_DESC = "total descending", "Total Descending"
    MIN_ASC = "min ascending", "Minimum Ascending"
    MIN_DESC = "min descending", "Minimum Descending"
    MAX_ASC = "max ascending", "Maximum Ascending"
    MAX_DESC = "max descending", "Maximum Descending"
    SUM_ASC = "sum ascending", "Sum Ascending"
    SUM_DESC = "sum descending", "Sum Descending"
    MEAN_ASC = "mean ascending", "Mean Ascending"
    MEAN_DESC = "mean descending", "Mean Descending"
    MEDIAN_ASC = "median ascending", "Median Ascending"
    MEDIAN_DESC = "median descending", "Median Descending"

    plotly_id: str
    display_name: str

    def __init__(self, plotly_id: str, display_name: str):
        self.plotly_id = plotly_id
        self.display_name = display_name

    @staticmethod
    def from_plotly_id(plotly_id: Optional[str]) -> Optional[PlotlyAxisCategoryOrder]:
        for v in PlotlyAxisCategoryOrder:
            if v.plotly_id == plotly_id:
                return v
        return None


class PlotlyAxisRangeMode(Enum):
    NORMAL = "normal", "Normal"
    INCLUDE_ZERO = "tozero", "Includes 0"
    NON_NEGATIVE = "nonnegative", "Non-Negative"

    plotly_id: str
    display_name: str

    def __init__(self, plotly_id: str, display_name: str):
        self.plotly_id = plotly_id
        self.display_name = display_name

    @staticmethod
    def from_plotly_id(plotly_id: Optional[str]) -> Optional[PlotlyAxisRangeMode]:
        for v in PlotlyAxisRangeMode:
            if v.plotly_id == plotly_id:
                return v
        return None


class PlotlyAxisType(Enum):
    AUTO = "-", "Automatic"
    LINEAR = "linear", "Linear"
    LOG = "log", "Logarithmic"
    DATE = "date", "Date"
    CATEGORY = "category", "Category"
    MULTI_CATEGORY = "multicategory", "Multi-Category"

    plotly_id: str
    display_name: str

    def __init__(self, plotly_id: str, display_name: str):
        self.plotly_id = plotly_id
        self.display_name = display_name

    @staticmethod
    def from_plotly_id(plotly_id: Optional[str]) -> Optional[PlotlyAxisType]:
        for v in PlotlyAxisType:
            if v.plotly_id == plotly_id:
                return v
        return None


class PlotlyFill(Enum):
    NONE = "none"
    TO_NEXT_Y = "tonexty"
    TO_NEXT_X = "tonextx"
    TO_ZERO_Y = "tozeroy"
    TO_ZERO_X = "tozerox"
    TO_NEXT = "tonext"
    TO_SELF = "toself"

    plotly_id: str

    def __init__(self, plotly_id: str):
        self.plotly_id = plotly_id

    @staticmethod
    def from_plotly_id(plotly_id: Optional[str]) -> Optional[PlotlyFill]:
        for v in PlotlyFill:
            if v.plotly_id == plotly_id:
                return v
        return None
