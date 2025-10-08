import json
from typing import Dict, Any, List

from sapiopylib.csp.data.plotly.PlotlyCspData import PlotlyCspChart
from sapiopylib.rest.pojo.webhook.WebhookContext import SapioWebhookContext


class JarvisDashboardWebhookContext:
    op_name: str
    data_frame_field_name_list: List[str]
    data_frame_field_map_list: List[str]
    param_map: Dict[str, Any]
    variable_to_column_map: Dict[str, str]
    chart_data_list: List[PlotlyCspChart]
    summary_table_by_dt_name: Dict[str, List[Dict[str, Any]]]

    def __init__(self, webhook_context: SapioWebhookContext):
        context_data = webhook_context.context_data
        if not context_data:
            raise ValueError("Jarvis dashboard context is missing.")
        raw: Dict[str, Any] = json.loads(context_data)
        self.op_name = raw['opName']
        self.data_frame_field_name_list = raw['dataFrameFieldNameList']
        self.data_frame_field_map_list = raw['dataFrameFieldMapList']
        self.param_map = raw['paramMap']
        self.variable_to_column_map = raw['variableToColumnMap']
        self.summary_table_by_dt_name = raw['summaryTableByDTName']
        chart_data_map_list: List[Dict[str, Any]] = raw['chartDataList']
        self.chart_data_list = list()
        if chart_data_map_list:
            for data_map in chart_data_map_list:
                chart: PlotlyCspChart = PlotlyCspChart(data_map)
                self.chart_data_list.append(chart)

