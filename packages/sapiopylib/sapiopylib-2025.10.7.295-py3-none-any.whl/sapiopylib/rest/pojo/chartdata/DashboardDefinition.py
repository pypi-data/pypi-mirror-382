from typing import List

from sapiopylib.rest.pojo.chartdata.DashboardSeries import *


class ChartDefinition(ABC):
    chart_guid: Optional[str]
    dashboard_guid: Optional[str]
    display_name: Optional[str]
    description: Optional[str]
    series_list: list[ChartSeries]
    main_data_type_name: Optional[str]
    grouping_type: Optional[ChartGroupingType]
    grouping_type_data_type_name: Optional[str]
    grouping_type_data_field_name: Optional[str]
    created_by: Optional[str]
    date_created: Optional[int]

    def __init__(self):
        self.chart_guid = None
        self.dashboard_guid = None
        self.display_name = None
        self.description = None
        # this series list crashes in server code if it is null.
        self.series_list = []
        self.main_data_type_name = None
        self.grouping_type = ChartGroupingType.NO_GROUPING
        self.grouping_type_data_type_name = None
        self.grouping_type_data_field_name = None
        self.created_by = None
        self.date_created = None

    @abstractmethod
    def get_chart_type(self) -> ChartType:
        pass

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, ChartDefinition):
            return False
        return self.chart_guid == other.chart_guid and self.dashboard_guid == other.dashboard_guid

    def __hash__(self):
        return hash((self.chart_guid, self.dashboard_guid))

    def __str__(self):
        return self.display_name

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = {'chartType': self.get_chart_type().name, 'chartGuid': self.chart_guid,
                               'dashboardGuid': self.dashboard_guid, 'displayName': self.display_name,
                               'description': self.description, 'mainDataTypeName': self.main_data_type_name,
                               'groupingTypeDataTypeName': self.grouping_type_data_type_name,
                               'groupingTypeDataFieldName': self.grouping_type_data_field_name,
                               'createdBy': self.created_by, 'dateCreated': self.date_created,
                               'seriesList': [x.to_json() for x in self.series_list]}
        if self.grouping_type:
            ret['groupingType'] = self.grouping_type.name
        return ret


class BarLineChartDefinition(ChartDefinition):
    horizontal: bool
    show_axis_titles: bool
    series_stacked: bool
    date_grouping_interval_type: Optional[ChartDateGroupingIntervalType]
    date_grouping_data_type_name: Optional[str]
    date_grouping_data_field_name: Optional[str]
    max_axis_ticks: Optional[int]
    max_axis_ticks_priority_pref: Optional[MaxAxisTicksPriorityPref]
    scroll_bars_enabled: bool
    legend_enabled: bool

    def __init__(self):
        super().__init__()
        self.horizontal: bool = False
        self.show_axis_titles: bool = False
        self.series_stacked: bool = False
        self.date_grouping_interval_type: Optional[ChartDateGroupingIntervalType] = None
        self.date_grouping_data_type_name: Optional[str] = None
        self.date_grouping_data_field_name: Optional[str] = None
        self.max_axis_ticks: Optional[int] = None
        self.max_axis_ticks_priority_pref: Optional[MaxAxisTicksPriorityPref] = None
        self.scroll_bars_enabled: bool = False
        self.legend_enabled: bool = False

    def get_chart_type(self) -> ChartType:
        return ChartType.BAR_LINE_CHART

    def to_json(self) -> Dict[str, Any]:
        ret = super().to_json()
        ret['chartType'] = self.get_chart_type().name
        ret['horizontal'] = self.horizontal
        ret['showAxisTitles'] = self.show_axis_titles
        ret['seriesStacked'] = self.series_stacked
        if self.date_grouping_interval_type:
            ret['dateGroupingIntervalType'] = self.date_grouping_interval_type.name
        ret['dateGroupingDataTypeName'] = self.date_grouping_data_type_name
        ret['dateGroupingDataFieldName'] = self.date_grouping_data_field_name
        ret['maxAxisTicks'] = self.max_axis_ticks
        ret['maxAxisTicksPriorityPref'] = self.max_axis_ticks_priority_pref
        ret['scrollbarsEnabled'] = self.scroll_bars_enabled
        ret['legendEnabled'] = self.legend_enabled
        return ret


class FunnelChartDefinition(ChartDefinition):
    funnel_type: FunnelType
    max_axis_ticks: Optional[int]
    max_axis_ticks_priority_pref: Optional[MaxAxisTicksPriorityPref]
    legend_enabled: bool

    def __init__(self):
        super().__init__()
        self.funnel_type: FunnelType = FunnelType.FUNNEL
        self.max_axis_ticks: Optional[int] = None
        self.max_axis_ticks_priority_pref: Optional[MaxAxisTicksPriorityPref] = None
        self.legend_enabled: bool = False

    def get_chart_type(self) -> ChartType:
        return ChartType.FUNNEL_CHART

    def to_json(self) -> Dict[str, Any]:
        ret = super().to_json()
        ret['funnelType'] = self.funnel_type
        ret['maxAxisTicks'] = self.max_axis_ticks
        if self.max_axis_ticks_priority_pref:
            ret['maxAxisTicksPriorityPref'] = self.max_axis_ticks_priority_pref
        ret['legendEnabled'] = self.legend_enabled
        return ret


class GanttChartDefinition(ChartDefinition):
    scroll_bars_enabled: bool = False

    def get_chart_type(self) -> ChartType:
        return ChartType.GANTT_CHART

    def to_json(self) -> Dict[str, Any]:
        ret = super().to_json()
        ret['scrollbarsEnabled'] = self.scroll_bars_enabled
        return ret


class GaugeChartDefinition(ChartDefinition):
    is_cylinder: bool
    minimum_value: Optional[float]
    maximum_value: Optional[float]
    minimum_value_field_data_type_name: Optional[str]
    minimum_value_field_data_field_name: Optional[str]
    minimum_value_field_operation_type: Optional[ChartOperationType]
    maximum_value_field_data_type_name: Optional[str]
    maximum_value_field_data_field_name: Optional[str]
    maximum_value_field_operation_type: Optional[ChartOperationType]
    default_value: Optional[float]
    percentage_color_range: bool
    legend_enabled: bool

    def __init__(self):
        super().__init__()
        self.is_cylinder: bool = False
        self.minimum_value: Optional[float] = None
        self.maximum_value: Optional[float] = None
        self.minimum_value_field_data_type_name: Optional[str] = None
        self.minimum_value_field_data_field_name: Optional[str] = None
        self.minimum_value_field_operation_type: Optional[ChartOperationType] = None
        self.maximum_value_field_data_type_name: Optional[str] = None
        self.maximum_value_field_data_field_name: Optional[str] = None
        self.maximum_value_field_operation_type: Optional[ChartOperationType] = None
        self.default_value: Optional[float] = None
        self.percentage_color_range: bool = False
        self.legend_enabled: bool = False

    def get_chart_type(self) -> ChartType:
        return ChartType.GAUGE_CHART

    def to_json(self) -> Dict[str, Any]:
        ret = super().to_json()
        ret['cylinder'] = self.is_cylinder
        ret['minimumValue'] = self.minimum_value
        ret['maximumValue'] = self.maximum_value
        ret['minimumValueFieldDataTypeName'] = self.minimum_value_field_data_type_name
        ret['minimumValueFieldDataFieldName'] = self.minimum_value_field_data_field_name
        if self.minimum_value_field_operation_type:
            ret['minimumValueFieldOperationType'] = self.minimum_value_field_operation_type.name
        ret['maximumValueFieldDataTypeName'] = self.maximum_value_field_data_type_name
        ret['maximumValueFieldDataFieldName'] = self.maximum_value_field_data_field_name
        if self.maximum_value_field_operation_type:
            ret['maximumValueFieldOperationType'] = self.maximum_value_field_operation_type.name
        ret['defaultValue'] = self.default_value
        ret['percentageColorRange'] = self.percentage_color_range
        ret['legendEnabled'] = self.legend_enabled
        return ret


class HeatMapChartDefinition(ChartDefinition):
    show_axis_titles: bool
    min_number_of_rows: Optional[int]
    min_number_of_cols: Optional[int]
    scrollbar_enabled: bool

    def __init__(self):
        super().__init__()
        self.show_axis_titles: bool = False
        self.min_number_of_rows: Optional[int] = None
        self.min_number_of_cols: Optional[int] = None
        self.scrollbar_enabled: bool = False

    def get_chart_type(self) -> ChartType:
        return ChartType.HEAT_MAP_CHART

    def to_json(self) -> Dict[str, Any]:
        ret = super().to_json()
        ret['showAxisTitles'] = self.show_axis_titles
        ret['minNumberOfRows'] = self.min_number_of_rows
        ret['minNumberOfColumns'] = self.min_number_of_cols
        ret['scrollbarsEnabled'] = self.scrollbar_enabled
        return ret


class MetricChartDefinition(ChartDefinition):
    default_value: Optional[float] = None

    def get_chart_type(self) -> ChartType:
        return ChartType.METRIC_CHART

    def to_json(self) -> Dict[str, Any]:
        ret = super().to_json()
        ret['defaultValue'] = self.default_value
        return ret


class PieChartDefinition(ChartDefinition):
    is_semi_circle: bool
    is_3d: bool
    is_donut: bool
    max_axis_ticks: Optional[int]
    max_axis_ticks_priority_pref: Optional[MaxAxisTicksPriorityPref]
    legend_enabled: bool

    def __init__(self):
        super().__init__()
        self.is_semi_circle: bool = False
        self.is_3d: bool = False
        self.is_donut: bool = False
        self.max_axis_ticks: Optional[int] = None
        self.max_axis_ticks_priority_pref: Optional[MaxAxisTicksPriorityPref] = None
        self.legend_enabled: bool = False

    def get_chart_type(self) -> ChartType:
        return ChartType.PIE_CHART

    def to_json(self) -> Dict[str, Any]:
        ret = super().to_json()
        ret['semiCircle'] = self.is_semi_circle
        ret['threeD'] = self.is_3d
        ret['donut'] = self.is_donut
        ret['maxAxisTicks'] = self.max_axis_ticks
        if self.max_axis_ticks_priority_pref:
            ret['maxAxisTicksPriorityPref'] = self.max_axis_ticks_priority_pref.name
        ret['legendEnabled'] = self.legend_enabled
        return ret


class RadarChartDefinition(ChartDefinition):
    max_axis_ticks: Optional[int]
    max_axis_ticks_priority_pref: Optional[MaxAxisTicksPriorityPref]
    scrollbars_enabled: bool
    legend_enabled: bool

    def __init__(self):
        super().__init__()
        self.max_axis_ticks: Optional[int] = None
        self.max_axis_ticks_priority_pref: Optional[MaxAxisTicksPriorityPref] = None
        self.scrollbars_enabled: bool = False
        self.legend_enabled: bool = False

    def get_chart_type(self) -> ChartType:
        return ChartType.RADAR_CHART

    def to_json(self) -> Dict[str, Any]:
        ret = super().to_json()
        ret['maxAxisTicks'] = self.max_axis_ticks
        if self.max_axis_ticks_priority_pref:
            ret['maxAxisTicksPriorityPref'] = self.max_axis_ticks_priority_pref.name
        ret['scrollbarsEnabled'] = self.scrollbars_enabled
        ret['legendEnabled'] = self.legend_enabled
        return ret


class XyChartDefinition(ChartDefinition):
    show_axis_titles: bool
    series_stacked: bool
    scrollbars_enabled: bool
    legend_enabled: bool

    def __init__(self):
        super().__init__()
        self.show_axis_titles: bool = False
        self.series_stacked: bool = False
        self.scrollbars_enabled: bool = False
        self.legend_enabled: bool = False

    def get_chart_type(self) -> ChartType:
        return ChartType.XY_CHART

    def to_json(self) -> Dict[str, Any]:
        ret = super().to_json()
        ret['showAxisTitles'] = self.show_axis_titles
        ret['seriesStacked'] = self.series_stacked
        ret['scrollbarsEnabled'] = self.scrollbars_enabled
        ret['legendEnabled'] = self.legend_enabled
        return ret


class DashboardDefinition:
    dashboard_guid: Optional[str]
    display_name: Optional[str]
    description: Optional[str]
    linked_report_ids: Optional[List[int]]
    chart_definition_list: Optional[List[ChartDefinition]]
    dashboard_scope: DashboardScope
    group_ids: Optional[List[int]]
    created_by: Optional[str]
    date_created: Optional[int]
    is_active: bool

    def __init__(self, dashboard_scope: DashboardScope = DashboardScope.PRIVATE,
                 chart_definition_list=None):
        super().__init__()
        self.dashboard_guid: Optional[str] = None
        self.display_name: Optional[str] = None
        self.description: Optional[str] = None
        self.linked_report_ids: Optional[List[int]] = None
        self.group_ids: Optional[List[int]] = None
        self.created_by: Optional[str] = None
        self.date_created: Optional[int] = None
        self.is_active: bool = True
        if chart_definition_list is None:
            chart_definition_list = []
        self.chart_definition_list = chart_definition_list
        self.dashboard_scope = dashboard_scope

    def to_json(self) -> Dict[str, Any]:
        ret = {
            'dashboardGuid': self.dashboard_guid,
            'displayName': self.display_name,
            'description': self.description,
            'linkedReportIds': self.linked_report_ids,
            'groupIdsSet': self.group_ids,
            'createdBy': self.created_by,
            'dateCreated': self.date_created,
            'active': self.is_active
        }
        if self.chart_definition_list:
            ret['chartDefinitionList'] = [x.to_json() for x in self.chart_definition_list]
        if self.dashboard_scope:
            ret['dashboardScope'] = self.dashboard_scope.name
        return ret


class DashboardDefinitionParser:
    @staticmethod
    def parse_dashboard_series(json_dct: Dict[str, Any]) -> ChartDefinition:
        ret: ChartDefinition
        chart_type = ChartType[json_dct.get('chartType')]
        if chart_type == ChartType.BAR_LINE_CHART:
            horizontal: bool = json_dct.get('horizontal')
            show_axis_titles: bool = json_dct.get('showAxisTitles')
            series_stacked: bool = json_dct.get('seriesStacked')
            date_grouping_interval_type: Optional[ChartDateGroupingIntervalType] = None
            if json_dct.get('dateGroupingIntervalType'):
                date_grouping_interval_type = ChartDateGroupingIntervalType[json_dct.get('dateGroupingIntervalType')]
            date_grouping_data_type_name: Optional[str] = json_dct.get('dateGroupingDataTypeName')
            date_grouping_data_field_name: Optional[str] = json_dct.get('dateGroupingDataFieldName')
            max_axis_ticks: Optional[int] = json_dct.get('maxAxisTicks')
            max_axis_ticks_priority_pref: Optional[MaxAxisTicksPriorityPref] = None
            if json_dct.get('maxAxisTicksPriorityPref'):
                max_axis_ticks_priority_pref = MaxAxisTicksPriorityPref[json_dct.get('maxAxisTicksPriorityPref')]
            scroll_bars_enabled: bool = json_dct.get('scrollbarsEnabled')
            legend_enabled: bool = json_dct.get('legendEnabled')
            bar_line_chart = BarLineChartDefinition()
            bar_line_chart.horizontal = horizontal
            bar_line_chart.show_axis_titles = show_axis_titles
            bar_line_chart.series_stacked = series_stacked
            bar_line_chart.date_grouping_interval_type = date_grouping_interval_type
            bar_line_chart.date_grouping_data_type_name = date_grouping_data_type_name
            bar_line_chart.date_grouping_data_field_name = date_grouping_data_field_name
            bar_line_chart.max_axis_ticks = max_axis_ticks
            bar_line_chart.max_axis_ticks_priority_pref = max_axis_ticks_priority_pref
            bar_line_chart.scroll_bars_enabled = scroll_bars_enabled
            bar_line_chart.legend_enabled = legend_enabled
            ret = bar_line_chart
        elif chart_type == ChartType.FUNNEL_CHART:
            funnel_type: FunnelType = FunnelType.FUNNEL
            if json_dct.get('funnelType'):
                funnel_type = FunnelType[json_dct.get('funnelType')]
            max_axis_ticks: Optional[int] = json_dct.get('maxAxisTicks')
            max_axis_ticks_priority_pref = Optional[MaxAxisTicksPriorityPref] = None
            if json_dct.get('maxAxisTicksPriorityPref'):
                max_axis_ticks_priority_pref = MaxAxisTicksPriorityPref[json_dct.get('maxAxisTicksPriorityPref')]
            legend_enabled: bool = json_dct.get('legendEnabled')
            funnel_chart = FunnelChartDefinition()
            funnel_chart.funnel_type = funnel_type
            funnel_chart.max_axis_ticks = max_axis_ticks
            funnel_chart.max_axis_ticks_priority_pref = max_axis_ticks_priority_pref
            funnel_chart.legend_enabled = legend_enabled
            ret = funnel_chart
        elif chart_type == ChartType.GANTT_CHART:
            scroll_bars_enabled: bool = json_dct.get('scrollbarsEnabled')
            gantt_chart = GanttChartDefinition()
            gantt_chart.scroll_bars_enabled = scroll_bars_enabled
            ret = gantt_chart
        elif chart_type == ChartType.GAUGE_CHART:
            is_cylinder: bool = json_dct.get('cylinder')
            minimum_value: Optional[float] = json_dct.get('minimumValue')
            maximum_value: Optional[float] = json_dct.get('maximumValue')
            minimum_value_field_data_type_name: Optional[str] = json_dct.get('minimumValueFieldDataTypeName')
            minimum_value_field_data_field_name: Optional[str] = json_dct.get('minimumValueFieldDataFieldName')
            minimum_value_field_operation_type: Optional[ChartOperationType] = None
            if json_dct.get('minimumValueFieldOperationType'):
                minimum_value_field_operation_type = ChartOperationType[json_dct.get('minimumValueFieldOperationType')]
            maximum_value_field_data_type_name: Optional[str] = json_dct.get('maximumValueFieldDataTypeName')
            maximum_value_field_data_field_name: Optional[str] = json_dct.get('maximumValueFieldDataFieldName')
            maximum_value_field_operation_type: Optional[ChartOperationType] = None
            if json_dct.get('maximumValueFieldOperationType'):
                maximum_value_field_operation_type = ChartOperationType[json_dct.get('maximumValueFieldOperationType')]
            default_value: Optional[float] = json_dct.get('defaultValue')
            percentage_color_range: bool = json_dct.get('percentageColorRange')
            legend_enabled: bool = json_dct.get('legendEnabled')
            gauge_chart = GaugeChartDefinition()
            gauge_chart.is_cylinder = is_cylinder
            gauge_chart.minimum_value = minimum_value
            gauge_chart.maximum_value = maximum_value
            gauge_chart.minimum_value_field_data_type_name = minimum_value_field_data_type_name
            gauge_chart.minimum_value_field_data_field_name = minimum_value_field_data_field_name
            gauge_chart.minimum_value_field_operation_type = minimum_value_field_operation_type
            gauge_chart.maximum_value_field_data_type_name = maximum_value_field_data_type_name
            gauge_chart.maximum_value_field_data_field_name = maximum_value_field_data_field_name
            gauge_chart.maximum_value_field_operation_type = maximum_value_field_operation_type
            gauge_chart.default_value = default_value
            gauge_chart.percentage_color_range = percentage_color_range
            gauge_chart.legend_enabled = legend_enabled
            ret = gauge_chart
        elif chart_type == ChartType.HEAT_MAP_CHART:
            show_axis_titles: bool = json_dct.get('showAxisTitles')
            min_number_of_rows: Optional[int] = json_dct.get('minNumberOfRows')
            min_number_of_cols: Optional[int] = json_dct.get('minNumberOfColumns')
            scrollbar_enabled: bool = json_dct.get('scrollbarsEnabled')
            heat_map_chart = HeatMapChartDefinition()
            heat_map_chart.show_axis_titles = show_axis_titles
            heat_map_chart.min_number_of_rows = min_number_of_rows
            heat_map_chart.min_number_of_cols = min_number_of_cols
            heat_map_chart.scrollbar_enabled = scrollbar_enabled
            ret = heat_map_chart
        elif chart_type == ChartType.METRIC_CHART:
            default_value: Optional[float] = json_dct.get('defaultValue')
            metric_chart = MetricChartDefinition()
            metric_chart.default_value = default_value
            ret = metric_chart
        elif chart_type == ChartType.PIE_CHART:
            is_semi_circle: bool = json_dct.get('semiCircle')
            is_3d: bool = json_dct.get('threeD')
            is_donut: bool = json_dct.get('donut')
            max_axis_ticks: Optional[int] = json_dct.get('maxAxisTicks')
            max_axis_ticks_priority_pref: Optional[MaxAxisTicksPriorityPref] = None
            if json_dct.get('maxAxisTicksPriorityPref'):
                max_axis_ticks_priority_pref = MaxAxisTicksPriorityPref[json_dct.get('maxAxisTicksPriorityPref')]
            legend_enabled: bool = json_dct.get('legendEnabled')
            pie_chart = PieChartDefinition()
            pie_chart.is_semi_circle = is_semi_circle
            pie_chart.is_3d = is_3d
            pie_chart.is_donut = is_donut
            pie_chart.max_axis_ticks = max_axis_ticks
            pie_chart.max_axis_ticks_priority_pref = max_axis_ticks_priority_pref
            pie_chart.legend_enabled = legend_enabled
            ret = pie_chart
        elif chart_type == ChartType.RADAR_CHART:
            max_axis_ticks: Optional[int] = json_dct.get('maxAxisTicks')
            max_axis_ticks_priority_pref: Optional[MaxAxisTicksPriorityPref] = None
            if json_dct.get('maxAxisTicksPriorityPref'):
                max_axis_ticks_priority_pref = MaxAxisTicksPriorityPref[json_dct.get('max_axis_ticks_priority_pref')]
            scrollbars_enabled: bool = json_dct.get('scrollbarsEnabled')
            legend_enabled: bool = json_dct.get('legendEnabled')
            radar_chart = RadarChartDefinition()
            radar_chart.max_axis_ticks = max_axis_ticks
            radar_chart.max_axis_ticks_priority_pref = max_axis_ticks_priority_pref
            radar_chart.scrollbars_enabled = scrollbars_enabled
            radar_chart.legend_enabled = legend_enabled
            ret = radar_chart
        elif chart_type == ChartType.XY_CHART:
            show_axis_titles: bool = json_dct.get('showAxisTitles')
            series_stacked: bool = json_dct.get('seriesStacked')
            scrollbars_enabled: bool = json_dct.get('scrollbarsEnabled')
            legend_enabled: bool = json_dct.get('legendEnabled')
            xy_chart = XyChartDefinition()
            xy_chart.show_axis_titles = show_axis_titles
            xy_chart.series_stacked = series_stacked
            xy_chart.scrollbars_enabled = scrollbars_enabled
            xy_chart.legend_enabled = legend_enabled
            ret = xy_chart
        else:
            raise ValueError("Chart Type not supported: " + str(chart_type))
        ret.chart_guid = json_dct.get('chartGuid')
        ret.dashboard_guid = json_dct.get('dashboardGuid')
        ret.display_name = json_dct.get('displayName')
        ret.description = json_dct.get('description')
        series_list: List[ChartSeries] = []
        if json_dct.get('seriesList'):
            series_list = [ChartSeriesParser.parse_dashboard_series(x) for x in json_dct.get('seriesList')]
        ret.series_list = series_list
        return ret

    @staticmethod
    def parse_dashboard_definition(json_dct: Dict[str, Any]) -> DashboardDefinition:
        dashboard_guid: Optional[str] = json_dct.get('dashboardGuid')
        display_name: Optional[str] = json_dct.get('displayName')
        description: Optional[str] = json_dct.get('description')
        linked_report_ids: Optional[List[int]] = json_dct.get('linkedReportIds')
        chart_definition_list: Optional[List[ChartDefinition]] = None
        if json_dct.get('chartDefinitionList'):
            chart_definition_list = [DashboardDefinitionParser.parse_dashboard_series(x)
                                     for x in json_dct.get('chartDefinitionList')]
        dashboard_scope: DashboardScope = DashboardScope.PRIVATE
        if json_dct.get('dashboardScope'):
            dashboard_scope = DashboardScope[json_dct.get('dashboardScope')]
        group_ids: Optional[List[int]] = json_dct.get('groupIdsSet')
        created_by: Optional[str] = json_dct.get('createdBy')
        date_created: Optional[int] = json_dct.get('dateCreated')
        is_active: bool = json_dct.get('active')
        ret = DashboardDefinition()
        ret.dashboard_guid = dashboard_guid
        ret.display_name = display_name
        ret.description = description
        ret.linked_report_ids = linked_report_ids
        ret.chart_definition_list = chart_definition_list
        ret.dashboard_scope = dashboard_scope
        ret.group_ids = group_ids
        ret.created_by = created_by
        ret.date_created = date_created
        ret.is_active = is_active
        return ret
