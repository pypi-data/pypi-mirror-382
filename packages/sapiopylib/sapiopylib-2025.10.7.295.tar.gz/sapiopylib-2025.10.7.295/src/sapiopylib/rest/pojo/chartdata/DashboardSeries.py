from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

from sapiopylib.rest.pojo.chartdata.DashboardEnums import *


class ChartSeries(ABC):

    @abstractmethod
    def get_chart_type(self) -> ChartType:
        pass

    @abstractmethod
    def get_chart_series_type(self) -> ChartSeriesType:
        pass

    chart_guid: Optional[str] = None

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, ChartSeries):
            return False
        return self.chart_guid == other.chart_guid

    def __hash__(self):
        return hash(self.chart_guid)

    def to_json(self) -> Dict[str, Any]:
        return {
            'chartType': self.get_chart_type().name,
            'chartSeriesType': self.get_chart_series_type().name,
            'chartGuid': self.chart_guid
        }


class CategoryChartSeries(ChartSeries):
    operation_type: Optional[ChartOperationType]
    data_type_name: str
    data_field_name: str

    def __init__(self, data_type_name: str, data_field_name: str):
        self.operation_type: Optional[ChartOperationType] = None
        self.data_type_name = data_type_name
        self.data_field_name = data_field_name

    @abstractmethod
    def get_chart_type(self) -> ChartType:
        pass

    @abstractmethod
    def get_chart_series_type(self) -> ChartSeriesType:
        pass

    def to_json(self) -> Dict[str, Any]:
        ret = super().to_json()
        if self.operation_type is not None:
            ret['operationType'] = self.operation_type.name
        ret['dataTypeName'] = self.data_type_name
        ret['dataFieldName'] = self.data_field_name
        return ret


class BarLineChartSeries(CategoryChartSeries):
    show_data_point_labels: bool
    show_trend_line: bool
    separate_value_axis: bool

    def __init__(self, data_type_name: str, data_field_name: str):
        super().__init__(data_type_name, data_field_name)
        self.show_data_point_labels: bool = False
        self.show_trend_line: bool = False
        self.separate_value_axis: bool = False

    def get_chart_type(self):
        return ChartType.BAR_LINE_CHART

    @abstractmethod
    def get_chart_series_type(self) -> ChartSeriesType:
        pass

    def to_json(self) -> Dict[str, Any]:
        ret = super().to_json()
        ret['showDataPointLabels'] = self.show_data_point_labels
        ret['showTrendLine'] = self.show_trend_line
        ret['separateValueAxis'] = self.separate_value_axis
        return ret


class BarChartSeries(BarLineChartSeries):
    bar_style_type: Optional[BarStyleType]

    def __init__(self, data_type_name: str, data_field_name: str):
        super().__init__(data_type_name, data_field_name)
        self.bar_style_type = None

    def get_chart_series_type(self) -> ChartSeriesType:
        return ChartSeriesType.BAR_CHART

    def to_json(self) -> Dict[str, Any]:
        ret = super().to_json()
        if self.bar_style_type is not None:
            ret['barStyleType'] = self.bar_style_type.name
        return ret


class LineChartSeries(BarLineChartSeries):
    point_shape_type: Optional[PointShapeType]
    is_show_area: bool
    line_stype_type: Optional[LineStyleType]

    def __init__(self, data_type_name: str, data_field_name: str):
        super().__init__(data_type_name, data_field_name)
        self.point_shape_type: Optional[PointShapeType] = None
        self.is_show_area: bool = False
        self.line_stype_type: Optional[LineStyleType] = None

    def get_chart_series_type(self) -> ChartSeriesType:
        return ChartSeriesType.LINE_CHART

    def to_json(self) -> Dict[str, Any]:
        ret = super().to_json()
        ret['showArea'] = self.is_show_area
        if self.point_shape_type is not None:
            ret['pointShapeType'] = self.point_shape_type.name
        if self.line_stype_type is not None:
            ret['lineStyleType'] = self.line_stype_type.name
        return ret


class FunnelChartSeries(CategoryChartSeries):
    def __init__(self, data_type_name: str, data_field_name: str):
        super().__init__(data_type_name, data_field_name)

    def get_chart_type(self) -> ChartType:
        return ChartType.FUNNEL_CHART

    def get_chart_series_type(self) -> ChartSeriesType:
        return ChartSeriesType.FUNNEL_CHART


class GaugeChartSeries(CategoryChartSeries):

    def __init__(self, data_type_name: str, data_field_name: str):
        super().__init__(data_type_name, data_field_name)

    def get_chart_type(self) -> ChartType:
        return ChartType.GAUGE_CHART

    def get_chart_series_type(self) -> ChartSeriesType:
        return ChartSeriesType.GAUGE_CHART


class MetricChartSeries(CategoryChartSeries):
    def __init__(self, data_type_name: str, data_field_name: str):
        super().__init__(data_type_name, data_field_name)

    def get_chart_type(self) -> ChartType:
        return ChartType.METRIC_CHART

    def get_chart_series_type(self) -> ChartSeriesType:
        return ChartSeriesType.METRIC_CHART


class PieChartSeries(CategoryChartSeries):
    variable_radius_slice: bool

    def __init__(self, data_type_name: str, data_field_name: str):
        super().__init__(data_type_name, data_field_name)
        self.variable_radius_slice = False

    def get_chart_type(self) -> ChartType:
        return ChartType.PIE_CHART

    def get_chart_series_type(self) -> ChartSeriesType:
        return ChartSeriesType.PIE_CHART

    def to_json(self) -> Dict[str, Any]:
        ret = super().to_json()
        ret['variableRadiusSlice'] = self.variable_radius_slice
        return ret


class RadarChartSeries(CategoryChartSeries):
    def __init__(self, data_type_name: str, data_field_name: str):
        super().__init__(data_type_name, data_field_name)

    def get_chart_type(self) -> ChartType:
        return ChartType.RADAR_CHART

    @abstractmethod
    def get_chart_series_type(self) -> ChartSeriesType:
        pass


class RadarBarChartSeries(RadarChartSeries):
    def __init__(self, data_type_name: str, data_field_name: str):
        super().__init__(data_type_name, data_field_name)

    def get_chart_series_type(self) -> ChartSeriesType:
        return ChartSeriesType.RADAR_BAR_CHART


class RadarLineChartSeries(RadarChartSeries):

    def __init__(self, data_type_name: str, data_field_name: str):
        super().__init__(data_type_name, data_field_name)

    def get_chart_series_type(self) -> ChartSeriesType:
        return ChartSeriesType.RADAR_LINE_CHART


class HeatMapChartSeries(ChartSeries):
    x_data_type_name: str
    x_data_field_name: str
    y_data_type_name: str
    y_data_field_name: str
    size_data_type_name: Optional[str]
    size_data_field_name: Optional[str]
    color_data_type_name: Optional[str]
    color_data_field_name: Optional[str]
    point_shape_type: Optional[PointShapeType]
    show_data_point_labels: bool

    def __init__(self, x_data_type_name: str, x_data_field_name: str, y_data_type_name: str, y_data_field_name: str,
                 size_data_type_name: Optional[str], size_data_field_name: Optional[str],
                 color_data_type_name: Optional[str], color_data_field_name: Optional[str]):
        self.x_data_type_name = x_data_type_name
        self.x_data_field_name = x_data_field_name
        self.y_data_type_name = y_data_type_name
        self.y_data_field_name = y_data_field_name
        self.size_data_type_name = size_data_type_name
        self.size_data_field_name = size_data_field_name
        self.color_data_type_name = color_data_type_name
        self.color_data_field_name = color_data_field_name
        self.point_shape_type: Optional[PointShapeType] = None
        self.show_data_point_labels: bool = False

    def get_chart_type(self) -> ChartType:
        return ChartType.HEAT_MAP_CHART

    def get_chart_series_type(self) -> ChartSeriesType:
        return ChartSeriesType.HEAT_MAP_CHART

    def to_json(self) -> Dict[str, Any]:
        ret = super().to_json()
        ret['xDataTypeName'] = self.x_data_type_name
        ret['xDataFieldName'] = self.x_data_field_name
        ret['yDataTypeName'] = self.y_data_type_name
        ret['yDataFieldName'] = self.y_data_field_name
        ret['sizeDataTypeName'] = self.size_data_type_name
        ret['sizeDataFieldName'] = self.size_data_field_name
        ret['colorDataTypeName'] = self.color_data_type_name
        ret['colorDataFieldName'] = self.color_data_field_name
        ret['showDataPointLabels'] = self.show_data_point_labels
        if self.point_shape_type is not None:
            ret['pointShapeType'] = self.point_shape_type.name
        return ret


class XyChartSeries(ChartSeries):
    x_data_type_name: str
    x_data_field_name: str
    y_data_type_name: str
    y_data_field_name: str
    line_style_type: Optional[LineStyleType]
    point_shape_type: Optional[PointShapeType]
    show_data_point_labels: bool
    show_trend_line: bool
    show_area: bool

    def __init__(self, x_data_type_name: str, x_data_field_name: str, y_data_type_name: str, y_data_field_name: str):
        self.x_data_type_name = x_data_type_name
        self.x_data_field_name = x_data_field_name
        self.y_data_type_name = y_data_type_name
        self.y_data_field_name = y_data_field_name
        self.line_style_type: Optional[LineStyleType] = None
        self.point_shape_type: Optional[PointShapeType] = None
        self.show_data_point_labels: bool = False
        self.show_trend_line: bool = False
        self.show_area: bool = False

    def get_chart_type(self) -> ChartType:
        return ChartType.XY_CHART

    def get_chart_series_type(self) -> ChartSeriesType:
        return ChartSeriesType.XY_CHART

    def to_json(self) -> Dict[str, Any]:
        ret = super().to_json()
        ret['xDataTypeName'] = self.x_data_type_name
        ret['xDataFieldName'] = self.x_data_field_name
        ret['yDataTypeName'] = self.y_data_type_name
        ret['yDataFieldName'] = self.y_data_field_name
        ret['showDataPointLabels'] = self.show_data_point_labels
        ret['showTrendLine'] = self.show_trend_line
        ret['showArea'] = self.show_area
        if self.line_style_type is not None:
            ret['lineStyleType'] = self.line_style_type.name
        if self.point_shape_type is not None:
            ret['pointShapeType'] = self.point_shape_type.name
        return ret


class BubbleChartSeries(XyChartSeries):
    size_data_type_name: str
    size_data_field_name: str

    def __init__(self, x_data_type_name: str, x_data_field_name: str, y_data_type_name: str, y_data_field_name: str,
                 size_data_type_name: str, size_data_field_name: str):
        super().__init__(x_data_type_name, x_data_field_name, y_data_type_name, y_data_field_name)
        self.size_data_type_name = size_data_type_name
        self.size_data_field_name = size_data_field_name

    def get_chart_series_type(self) -> ChartSeriesType:
        return ChartSeriesType.BUBBLE_CHART


class GanttChartSeries(ChartSeries):
    segment_name_data_type_name: Optional[str]
    segment_name_data_field_name: Optional[str]
    segment_start_data_type_name: Optional[str]
    segment_start_data_field_name: Optional[str]
    segment_end_data_type_name: Optional[str]
    segment_end_data_field_name: Optional[str]

    def __init__(self, segment_name_data_type_name: Optional[str], segment_name_data_field_name: Optional[str],
                 segment_start_data_type_name: Optional[str], segment_start_data_field_name: Optional[str],
                 segment_end_data_type_name: Optional[str], segment_end_data_field_name: Optional[str]):
        self.segment_name_data_type_name = segment_name_data_type_name
        self.segment_name_data_field_name = segment_name_data_field_name
        self.segment_start_data_type_name = segment_start_data_type_name
        self.segment_start_data_field_name = segment_start_data_field_name
        self.segment_end_data_type_name = segment_end_data_type_name
        self.segment_end_data_field_name = segment_end_data_field_name

    def get_chart_type(self) -> ChartType:
        return ChartType.GANTT_CHART

    def get_chart_series_type(self) -> ChartSeriesType:
        return ChartSeriesType.GANTT_CHART

    def to_json(self) -> Dict[str, Any]:
        ret = super().to_json()
        ret['segmentNameDataTypeName'] = self.segment_name_data_type_name
        ret['segmentNameDataFieldName'] = self.segment_name_data_field_name
        ret['segmentStartDataTypeName'] = self.segment_start_data_type_name
        ret['segmentStartDataFieldName'] = self.segment_start_data_field_name
        ret['segmentEndDataTypeName'] = self.segment_end_data_type_name
        ret['segmentEndDataFieldName'] = self.segment_end_data_field_name
        return ret


class ChartSeriesParser:

    @staticmethod
    def parse_dashboard_series(json_dct: Dict[str, Any]) -> ChartSeries:
        series_type: ChartSeriesType = ChartSeriesType[json_dct.get('chartSeriesType')]
        chart_type: ChartType = ChartType[json_dct.get('chartType')]
        line_style_type: Optional[LineStyleType] = None
        point_style_type: Optional[PointShapeType] = None
        ret: ChartSeries
        if series_type in [ChartSeriesType.XY_CHART, ChartSeriesType.BUBBLE_CHART]:
            x_data_type_name = json_dct.get('xDataTypeName')
            x_data_field_name = json_dct.get('xDataFieldName')
            y_data_type_name = json_dct.get('yDataTypeName')
            y_data_field_name = json_dct.get('yDataFieldName')
            line_style_type_name = json_dct.get('lineStyleType')
            if line_style_type_name:
                line_style_type = LineStyleType[line_style_type_name]
            point_style_type_name = json_dct.get('pointShapeType')
            if point_style_type_name:
                point_style_type = PointShapeType[point_style_type_name]
            show_data_point_labels = json_dct.get('showDataPointLabels')
            show_trend_line = json_dct.get('showTrendLine')
            show_area = json_dct.get('showArea')
            xy_series: XyChartSeries
            if series_type == ChartSeriesType.XY_CHART:
                xy_series = XyChartSeries(x_data_type_name, x_data_field_name, y_data_type_name, y_data_field_name)
            else:
                size_data_type_name = json_dct.get('sizeDataTypeName')
                size_data_field_name = json_dct.get('sizeDataFieldName')
                xy_series = BubbleChartSeries(x_data_type_name, x_data_field_name, y_data_type_name, y_data_field_name,
                                              size_data_type_name, size_data_field_name)
            ret = xy_series
            xy_series.line_style_type = line_style_type
            xy_series.point_shape_type = point_style_type
            xy_series.show_data_point_labels = show_data_point_labels
            xy_series.show_trend_line = show_trend_line
            xy_series.show_area = show_area
        elif series_type == ChartSeriesType.HEAT_MAP_CHART:
            x_data_type_name = json_dct.get('xDataTypeName')
            x_data_field_name = json_dct.get('xDataFieldName')
            y_data_type_name = json_dct.get('yDataTypeName')
            y_data_field_name = json_dct.get('yDataFieldName')
            size_data_type_name = json_dct.get('sizeDataTypeName')
            size_data_field_name = json_dct.get('sizeDataFieldName')
            color_data_type_name = json_dct.get('colorDataTypeName')
            color_data_field_name = json_dct.get('colorDataFieldName')
            show_data_point_labels = json_dct.get('showDataPointLabels')
            point_style_type_name = json_dct.get('pointShapeType')
            if point_style_type_name:
                point_style_type = PointShapeType[point_style_type_name]
            heat_map_series = HeatMapChartSeries(x_data_type_name, x_data_field_name,
                                                 y_data_type_name, y_data_field_name,
                                                 size_data_type_name, size_data_field_name,
                                                 color_data_type_name, color_data_field_name)
            heat_map_series.show_data_point_labels = show_data_point_labels
            heat_map_series.point_shape_type = point_style_type
            ret = heat_map_series
        elif series_type in [ChartSeriesType.BAR_CHART, ChartSeriesType.LINE_CHART, ChartSeriesType.FUNNEL_CHART,
                             ChartSeriesType.GAUGE_CHART, ChartSeriesType.METRIC_CHART, ChartSeriesType.PIE_CHART,
                             ChartSeriesType.RADAR_BAR_CHART, ChartSeriesType.RADAR_LINE_CHART]:
            operation_type_name = json_dct.get('operationType')
            operation_type: Optional[ChartOperationType] = None
            if operation_type_name:
                operation_type = ChartOperationType[operation_type_name]
            data_type_name: str = json_dct.get('dataTypeName')
            data_field_name: str = json_dct.get('dataFieldName')

            category_series: CategoryChartSeries
            if series_type in [ChartSeriesType.BAR_CHART or ChartSeriesType.LINE_CHART]:
                show_data_point_labels: bool = json_dct.get('showDataPointLabels')
                show_trend_line: bool = json_dct.get('showTrendLine')
                separate_value_axis: bool = json_dct.get('separateValueAxis')
                bar_line_series: BarLineChartSeries
                if series_type == ChartSeriesType.BAR_CHART:
                    bar_style_type: Optional[BarStyleType] = None
                    bar_style_type_name = json_dct.get('barStyleType')
                    if bar_style_type_name:
                        bar_style_type = BarStyleType[bar_style_type_name]
                    bar_series = BarChartSeries(data_type_name, data_field_name)
                    bar_series.bar_style_type = bar_style_type
                    bar_line_series = bar_series
                elif series_type == ChartSeriesType.LINE_CHART:
                    is_show_area = json_dct.get('showArea')
                    line_style_type_name = json_dct.get('lineStyleType')
                    if line_style_type_name:
                        line_style_type = LineStyleType[line_style_type_name]
                    point_style_type_name = json_dct.get('pointShapeType')
                    if point_style_type_name:
                        point_style_type = PointShapeType[point_style_type_name]
                    line_series = LineChartSeries(data_type_name, data_field_name)
                    line_series.is_show_area = is_show_area
                    line_series.line_stype_type = line_style_type
                    line_series.point_shape_type = point_style_type
                    bar_line_series = line_series
                else:
                    raise ValueError("Unsupported chart series type " + str(series_type))
                bar_line_series.show_data_point_labels = show_data_point_labels
                bar_line_series.show_trend_line = show_trend_line
                bar_line_series.separate_value_axis = separate_value_axis
                category_series = bar_line_series
            elif series_type == ChartSeriesType.FUNNEL_CHART:
                category_series = FunnelChartSeries(data_type_name, data_field_name)
            elif series_type == ChartSeriesType.GAUGE_CHART:
                category_series = GaugeChartSeries(data_type_name, data_field_name)
            elif series_type == ChartSeriesType.METRIC_CHART:
                category_series = MetricChartSeries(data_type_name, data_field_name)
            elif series_type == ChartSeriesType.PIE_CHART:
                variable_radius_slice = json_dct.get('variableRadiusSlice')
                pie_series = PieChartSeries(data_type_name, data_field_name)
                pie_series.variable_radius_slice = variable_radius_slice
                category_series = pie_series
            elif series_type == ChartSeriesType.RADAR_BAR_CHART:
                category_series = RadarBarChartSeries(data_type_name, data_field_name)
            elif series_type == ChartSeriesType.RADAR_LINE_CHART:
                category_series = RadarLineChartSeries(data_type_name, data_field_name)
            else:
                raise ValueError("Unsupported category series type: " + str(series_type))
            category_series.operation_type = operation_type
            ret = category_series
        elif series_type == ChartSeriesType.GANTT_CHART:
            segment_name_data_type_name: Optional[str] = json_dct.get("segmentNameDataTypeName")
            segment_name_data_field_name: Optional[str] = json_dct.get("segmentNameDataFieldName")
            segment_start_data_type_name: Optional[str] = json_dct.get("segmentStartDataTypeName")
            segment_start_data_field_name: Optional[str] = json_dct.get("segmentStartDataFieldName")
            segment_end_data_type_name: Optional[str] = json_dct.get("segmentEndDataTypeName")
            segment_end_data_field_name: Optional[str] = json_dct.get("segmentEndDataFieldName")
            return GanttChartSeries(segment_name_data_type_name=segment_name_data_type_name,
                                    segment_name_data_field_name=segment_name_data_field_name,
                                    segment_start_data_type_name=segment_start_data_type_name,
                                    segment_start_data_field_name=segment_start_data_field_name,
                                    segment_end_data_type_name=segment_end_data_type_name,
                                    segment_end_data_field_name=segment_end_data_field_name)
        else:
            raise ValueError("Unexpected series type: " + str(series_type))
        guid: Optional[str] = json_dct.get('chartGuid')
        ret.chart_guid = guid
        return ret
