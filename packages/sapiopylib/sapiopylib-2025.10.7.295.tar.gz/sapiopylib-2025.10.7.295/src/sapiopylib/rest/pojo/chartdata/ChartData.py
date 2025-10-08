from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Optional, List


class ChartDataSeriesValueType(Enum):
    CATEGORY = "CategoryChartDataSeriesValuePojo"
    GANTT = "GanttChartDataSeriesValuePojo"
    XY = "XyChartDataSeriesValuePojo"
    BUBBLE = "BubbleChartDataSeriesValuePojo"
    GAUGE = "GaugeChartDataSeriesValuePojo"
    HEAT_MAP = "HeatMapChartDataSeriesValuePojo"

    class_name: str

    def __init__(self, class_name: str):
        self.class_name = class_name


class AbstractChartDataSeriesValue(ABC):

    @abstractmethod
    def get_value_type(self) -> ChartDataSeriesValueType:
        pass

    def to_json(self) -> Dict[str, Any]:
        return {
            '@type': self.get_value_type().class_name,
            'type': self.get_value_type().name
        }


class CategoryChartDataSeriesValue(AbstractChartDataSeriesValue):
    value: Optional[float]
    record_ids_of_matching_rows: Optional[List[Dict[str, int]]]

    def __init__(self, value: Optional[float] = None,
                 record_ids_of_matching_rows: Optional[List[Dict[str, int]]] = None):
        self.value = value
        self.record_ids_of_matching_rows = record_ids_of_matching_rows

    def get_value_type(self) -> ChartDataSeriesValueType:
        return ChartDataSeriesValueType.CATEGORY

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_json()
        ret['value'] = self.value
        ret['recIdsOfMatchingRows'] = self.record_ids_of_matching_rows
        return ret


class BubbleChartDataSeriesValue(AbstractChartDataSeriesValue):
    size: Optional[float]

    def __init__(self, size: Optional[float]):
        self.size = size

    def get_value_type(self) -> ChartDataSeriesValueType:
        return ChartDataSeriesValueType.BUBBLE

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_json()
        ret['size'] = self.size
        return ret


class GanttChartDataSeriesValue(AbstractChartDataSeriesValue):
    segment_start: Optional[float]
    segment_end: Optional[float]
    segment_name: Optional[str]
    record_ids_of_matching_rows: Optional[List[Dict[str, int]]]

    def get_value_type(self) -> ChartDataSeriesValueType:
        return ChartDataSeriesValueType.GANTT

    def __init__(self, segment_start: Optional[float] = None, segment_end: Optional[float] = None,
                 segment_name: Optional[str] = None,
                 record_ids_of_matching_rows: Optional[List[Dict[str, int]]] = None):
        self.segment_start = segment_start
        self.segment_end = segment_end
        self.segment_name = segment_name
        self.record_ids_of_matching_rows = record_ids_of_matching_rows

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_json()
        ret['segmentStart'] = self.segment_start
        ret['segmentEnd'] = self.segment_end
        ret['segmentName'] = self.segment_name
        ret['recIdsOfMatchingRows'] = self.record_ids_of_matching_rows
        return ret


class GaugeChartDataSeriesValue(AbstractChartDataSeriesValue):
    min_value: Optional[float]
    max_value: Optional[float]

    def get_value_type(self) -> ChartDataSeriesValueType:
        return ChartDataSeriesValueType.GAUGE

    def __init__(self, min_value: Optional[float] = None, max_value: Optional[float] = None):
        self.min_value = min_value
        self.max_value = max_value

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_json()
        ret['minValue'] = self.min_value
        ret['maxValue'] = self.max_value
        return ret


class HeatMapChartDataSeriesValue(AbstractChartDataSeriesValue):
    x: str
    y: str
    size: Optional[float]
    color: Optional[float]
    record_ids_of_matching_rows: Optional[List[Dict[str, int]]]

    def get_value_type(self) -> ChartDataSeriesValueType:
        return ChartDataSeriesValueType.HEAT_MAP

    def __init__(self, x: str, y: str, size: Optional[float] = None, color: Optional[float] = None,
                 record_ids_of_matching_rows: Optional[List[Dict[str, int]]] = None):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.record_ids_of_matching_rows = record_ids_of_matching_rows

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_json()
        ret['x'] = self.x
        ret['y'] = self.y
        ret['size'] = self.size
        ret['color'] = self.color
        ret['recIdsOfMatchingRows'] = self.record_ids_of_matching_rows
        return ret


class XyChartDataSeriesValue(AbstractChartDataSeriesValue):
    x: float
    y: float
    record_ids_of_matching_rows: Optional[List[Dict[str, int]]]

    def __init__(self, x: float, y: float, record_ids_of_matching_rows: Optional[List[Dict[str, int]]] = None):
        self.x = x
        self.y = y
        self.record_ids_of_matching_rows = record_ids_of_matching_rows

    def get_value_type(self) -> ChartDataSeriesValueType:
        return ChartDataSeriesValueType.XY

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_json()
        ret['x'] = self.x
        ret['y'] = self.y
        ret['recIdsOfMatchingRows'] = self.record_ids_of_matching_rows
        return ret


class ChartDataSeriesKey:
    series_key_value: str
    series_name: str
    field_group_value: str
    series_def_index: int

    def __init__(self, series_key_value: str, series_name: str, field_group_value: str, series_def_index: int):
        self.series_key_value = series_key_value
        self.series_name = series_name
        self.field_group_value = field_group_value
        self.series_def_index = series_def_index

    def to_json(self) -> Dict[str, Any]:
        return {
            'seriesKeyValue': self.series_key_value,
            'seriesName': self.series_name,
            'fieldGroupValue': self.field_group_value,
            'seriesDefIndex': self.series_def_index
        }


class ChartDataAxisSeriesTick:
    axis_tick_key_value: str
    series_values: Optional[Dict[ChartDataSeriesKey, AbstractChartDataSeriesValue]]

    def __init__(self, axis_tick_key_value: str,
                 series_values: Optional[Dict[ChartDataSeriesKey, AbstractChartDataSeriesValue]]):
        self.axis_tick_key_value = axis_tick_key_value
        self.series_values = series_values

    def to_json(self) -> Dict[str, Any]:
        series_value_pojo: Optional[Dict[Dict[str, Any], Dict[str, Any]]] = None
        if self.series_values is not None:
            series_value_pojo = dict()
            for key, value in self.series_values.items():
                key_pojo = key.to_json()
                value_pojo = value.to_json()
                series_value_pojo[key_pojo] = value_pojo
        return {
            'axisTickKeyValue': self.axis_tick_key_value,
            'seriesValues': series_value_pojo
        }


class ChartDataSource:
    axis_ticks: Optional[List[ChartDataAxisSeriesTick]]
    series_keys: Optional[List[ChartDataSeriesKey]]

    def __init__(self, axis_ticks: Optional[List[ChartDataAxisSeriesTick]] = None,
                 series_keys: Optional[List[ChartDataSeriesKey]] = None):
        self.axis_ticks = axis_ticks
        self.series_keys = series_keys

    def to_json(self) -> Dict[str, Any]:
        axis_tick_pojo_list = None
        if self.axis_ticks is not None:
            axis_tick_pojo_list = [x.to_json() for x in self.axis_ticks]
        series_key_pojo_list = None
        if self.series_keys is not None:
            series_key_pojo_list = [x.to_json() for x in self.series_keys]
        return {
            'axisTicks': axis_tick_pojo_list,
            'seriesKeys': series_key_pojo_list
        }


class ChartDataParser:
    @staticmethod
    def parse_chart_type_by_class_name(chart_type_class_name: str) -> Optional[ChartDataSeriesValueType]:
        for chart_type in ChartDataSeriesValueType:
            if chart_type.class_name == chart_type_class_name:
                return chart_type
        return None

    @staticmethod
    def parse_chart_data_series_key(json_dct: Dict[str, Any]) -> ChartDataSeriesKey:
        series_key_value: str = json_dct.get('seriesKeyValue')
        series_name: str = json_dct.get('seriesName')
        field_group_value: str = json_dct.get('fieldGroupValue')
        series_def_index: int = json_dct.get('seriesDefIndex')
        return ChartDataSeriesKey(series_key_value, series_name, field_group_value, series_def_index)

    @staticmethod
    def parse_chart_data_series_value(json_dct: Dict[str, Any]) -> AbstractChartDataSeriesValue:
        class_name: str = json_dct.get('@type')
        chart_type = ChartDataParser.parse_chart_type_by_class_name(class_name)
        if chart_type == ChartDataSeriesValueType.CATEGORY:
            value: Optional[float] = json_dct.get('value')
            record_ids_of_matching_rows: Optional[List[Dict[str, int]]] = json_dct.get('recIdsOfMatchingRows')
            return CategoryChartDataSeriesValue(value, record_ids_of_matching_rows)
        elif chart_type == ChartDataSeriesValueType.BUBBLE:
            size: Optional[float] = json_dct.get('size')
            return BubbleChartDataSeriesValue(size)
        elif chart_type == ChartDataSeriesValueType.GANTT:
            segment_start: Optional[float] = json_dct.get('segmentStart')
            segment_end: Optional[float] = json_dct.get('segmentEnd')
            segment_name: Optional[str] = json_dct.get('segmentName')
            record_ids_of_matching_rows: Optional[List[Dict[str, int]]] = json_dct.get('recIdsOfMatchingRows')
            return GanttChartDataSeriesValue(segment_start, segment_end, segment_name, record_ids_of_matching_rows)
        elif chart_type == ChartDataSeriesValueType.GAUGE:
            min_value: Optional[float] = json_dct.get('minValue')
            max_value: Optional[float] = json_dct.get('maxValue')
            return GaugeChartDataSeriesValue(min_value, max_value)
        elif chart_type == ChartDataSeriesValueType.HEAT_MAP:
            x: str = json_dct.get('x')
            y: str = json_dct.get('y')
            size: Optional[float] = json_dct.get('size')
            color: Optional[float] = json_dct.get('color')
            record_ids_of_matching_rows: Optional[List[Dict[str, int]]] = json_dct.get('recIdsOfMatchingRows')
            return HeatMapChartDataSeriesValue(x, y, size, color, record_ids_of_matching_rows)
        elif chart_type == ChartDataSeriesValueType.XY:
            x: float = json_dct.get('x')
            y: float = json_dct.get('y')
            record_ids_of_matching_rows: Optional[List[Dict[str, int]]] = json_dct.get('recIdsOfMatchingRows')
            return XyChartDataSeriesValue(x, y, record_ids_of_matching_rows)
        else:
            raise NotImplemented("Unexpected chart type class name: " + class_name)

    @staticmethod
    def parse_data_axis_tick(json_dct: Dict[str, Any]) -> ChartDataAxisSeriesTick:
        axis_tick_key_value: str = json_dct.get('axisTickKeyValue')
        series_values: Optional[Dict[ChartDataSeriesKey, AbstractChartDataSeriesValue]] = None
        if json_dct.get('seriesValues') is not None:
            series_value_pojo: Optional[Dict[Dict[str, Any], Dict[str, Any]]] = json_dct.get('seriesValues')
            for key_pojo, value_pojo in series_value_pojo.items():
                key = ChartDataParser.parse_chart_data_series_key(key_pojo)
                value = ChartDataParser.parse_chart_data_series_value(value_pojo)
                series_values[key] = value
        return ChartDataAxisSeriesTick(axis_tick_key_value, series_values)

    @staticmethod
    def parse_chart_data_source(json_dct: Dict[str, Any]) -> ChartDataSource:
        axis_ticks: Optional[List[ChartDataAxisSeriesTick]] = None
        series_keys: Optional[List[ChartDataSeriesKey]] = None
        if json_dct.get('axisTicks') is not None:
            axis_ticks = [ChartDataParser.parse_data_axis_tick(x) for x in json_dct.get('axisTicks')]
        if json_dct.get('seriesKeys') is not None:
            series_keys = [ChartDataParser.parse_chart_data_series_key(x) for x in json_dct.get('seriesKeys')]
        return ChartDataSource(axis_ticks, series_keys)
