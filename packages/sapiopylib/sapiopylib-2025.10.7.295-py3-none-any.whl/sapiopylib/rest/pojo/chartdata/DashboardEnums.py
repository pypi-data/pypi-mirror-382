# These are dashboard definitions' Enum classes
from enum import Enum


class ChartDateGroupingIntervalType(Enum):
    DAY = "Day"
    WEEK = "Week"
    MONTH = "Month"
    YEAR = "Year"
    EXACT = "Exact"

    text: str

    def __init__(self, text: str):
        self.text = text

    def __str__(self):
        return self.text


class BarStyleType(Enum):
    BAR_2D = "2D Bar"
    CURVED = "2D Curved Bars"
    BAR_3D = "3D Bar"
    CYLINDER = "3D Cylinder Bars"

    text: str

    def __init__(self, text: str):
        self.text = text

    def __str__(self):
        return self.text


class ChartGroupingType(Enum):
    GROUP_ALL_TOGETHER = "Group All Together"
    GROUP_BY_FIELD = "Group By Field"
    NO_GROUPING = "Group By Records of Type"

    text: str

    def __init__(self, text: str):
        self.text = text

    def __str__(self):
        return self.text


class ChartOperationType(Enum):
    VALUE = "Field Value"
    COUNT = "Count"
    AVERAGE = "AVERAGE"
    TOTAL = "Total"
    MEDIAN = "Median"

    text: str

    def __init__(self, text: str):
        self.text = text

    def __str__(self):
        return self.text


class ChartSeriesType(Enum):
    BAR_CHART = "Bar Chart"
    BUBBLE_CHART = "Bubble Chart"
    LINE_CHART = "Line Chart"
    PIE_CHART = "Pie Chart"
    FUNNEL_CHART = "Funnel Chart"
    GANTT_CHART = "Gantt Chart"
    GAUGE_CHART = "Gauge Chart"
    RADAR_LINE_CHART = "Radar Line Chart"
    RADAR_BAR_CHART = "Radar Bar Chart"
    XY_CHART = "XY Chart"
    METRIC_CHART = "Metric Chart"
    HEAT_MAP_CHART = "Heat Map Chart"

    text: str

    def __init__(self, text: str):
        self.text = text

    def __str__(self):
        return self.text


class ChartType(Enum):
    BAR_LINE_CHART = "Bar/Line Chart"
    PIE_CHART = "Pie Chart"
    FUNNEL_CHART = "Funnel Chart"
    GANTT_CHART = "Gantt Chart"
    GAUGE_CHART = "Gauge Chart"
    RADAR_CHART = "Radar Chart"
    XY_CHART = "XY Chart"
    METRIC_CHART = "Metric Chart"
    HEAT_MAP_CHART = "Heat Map Chart"

    text: str

    def __init__(self, text: str):
        self.text = text

    def __str__(self):
        return self.text


class DashboardScope(Enum):
    SYSTEM = 1
    PUBLIC = 2
    PRIVATE = 3
    PRIVATE_ELN = 4
    REPORT_BUILDER_ENTRY = 5


class FunnelType(Enum):
    FUNNEL = "Funnel"
    PYRAMID = "Pyramid"
    STEP_FUNNEL = "Step Funnel"

    text: str

    def __init__(self, text: str):
        self.text = text

    def __str__(self):
        return self.text


class LineStyleType(Enum):
    NONE = "None", "line"
    NORMAL = "Straight Line", "line"
    SMOOTH = "Smoothed Line", "smoothedLine"
    DASHED = "Dashed Line", "dashed"
    STEP = "Step Line", "step"

    text: str
    chart_config_value: str

    def __init__(self, text: str, chart_config_value: str):
        self.text = text
        self.chart_config_value = chart_config_value

    def __str__(self):
        return self.text


class MaxAxisTicksPriorityPref(Enum):
    TICK_AXIS_VALUE = 1
    TICK_NUM_RECORDS = 2


class PointShapeType(Enum):
    NONE = "None", "none"
    CIRCLE = "Round", "round"
    SQUARE = "Square", "square"
    TRIANGLE_UP = "Triangle-Up", "triangleUp"
    TRIANGLE_DOWN = "Triangle-Down", "triangleDown"
    TRIANGLE_LEFT = "Triangle-Left", "triangleLeft"
    TRIANGLE_RIGHT = "Triangle-Right", "triangleRight"
    DIAMOND = "Diamond", "diamond"
    STAR = "Star", "star"
    STARBURST = "Starburst", "starburst"

    text: str
    chart_config_value: str

    def __init__(self, text: str, chart_config_value: str):
        self.text = text
        self.chart_config_value = chart_config_value

    def __str__(self):
        return self.text


