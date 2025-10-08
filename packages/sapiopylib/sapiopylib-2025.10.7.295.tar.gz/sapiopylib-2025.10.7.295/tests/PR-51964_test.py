json_str: str = """
[{"Is3D":false,"Margins":{"Left":60.0,"Top":35.0,"Right":10.0,"Bottom":60.0},"AxisConfigurationList":[],"ChartTitle":null,"ChartId":"Bar","SeriesDataList":[{"SeriesName":"Bar Data","YValueList":[81.8,92.6],"DataType":"bar","XValueList":["x: Test Score Before Using Calculator","y: Test Score After Using Calculator"],"YErrorBar":{"UpperArray":[3.8719504129056204,2.0119642143934864],"ErrorBarType":"data","IsVisible":true,"IsSymmetric":true}}]},{"Is3D":false,"Margins":{"Left":60.0,"Top":35.0,"Right":10.0,"Bottom":60.0},"AxisConfigurationList":[{"AxisRangeMode":"NORMAL","IsAutoRange":true,"Title":"Groups","RangeMin":null,"AxisType":"CATEGORY","RangeMax":null,"Orientation":"X"},{"AxisRangeMode":"NORMAL","IsAutoRange":true,"Title":"Value","RangeMin":null,"AxisType":"LINEAR","RangeMax":null,"Orientation":"Y"}],"ChartTitle":null,"ChartId":"Box","SeriesDataList":[{"SeriesName":"x: Test Score Before Using Calculator","YValueList":[71.0,72.0,85.0,90.0,91.0],"Jitter":0.3,"DataType":"box","BoxPoints":"all","PointsPosition":0.0},{"SeriesName":"y: Test Score After Using Calculator","YValueList":[85.0,90.0,95.0,96.0,97.0],"Jitter":0.3,"DataType":"box","BoxPoints":"all","PointsPosition":0.0}]}]
"""

import unittest
import json
import os
import tempfile
from typing import List, Dict, Any

from plotly.graph_objs import Figure
from sapiopylib.csp.data.plotly.PlotlyCspData import PlotlyCspChart
from sapiopylib.csp.data.plotly.SapioPyPlotly import SapioPyPlotlyUtil

class TestPR51964(unittest.TestCase):
    def test_chart_gen_with_and_without_error_bars(self):

        with tempfile.TemporaryDirectory() as temp_dir:
            field_map_list: List[Dict[str, Any]] = json.loads(json_str)
            image_file_path_list: List[str] = list()
            chart_num: int = 1
            for field_map in field_map_list:
                chart: PlotlyCspChart = PlotlyCspChart(field_map)
                file_name = 'chart' + str(chart_num) + ".png"
                file_path = os.path.join(temp_dir, file_name)
                fig: Figure = SapioPyPlotlyUtil.get_chart(chart)
                SapioPyPlotlyUtil.export_image_data(fig, file_path, format="png", scale=1.67)
                chart_num += 1
                image_file_path_list.append(file_path)
