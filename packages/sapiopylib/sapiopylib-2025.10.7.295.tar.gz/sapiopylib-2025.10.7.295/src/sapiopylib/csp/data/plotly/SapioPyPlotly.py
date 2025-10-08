from typing import Union, Any

import plotly
import plotly.graph_objects as go
from plotly.basedatatypes import BaseTraceType
from plotly.graph_objs import Figure, Layout, Scatter, Bar, Box, Heatmap, Histogram, Histogram2dContour, Isosurface, \
    Scatter3d
from plotly.graph_objs.layout import Margin, XAxis, YAxis

from sapiopylib.csp.data.plotly.PlotlyCspData import *


def _get_plotly_marker(csp_marker: Optional[PlotlyCspMarker]):
    if csp_marker is None:
        return None
    symbol: Optional[str] = csp_marker.get_symbol()
    color: Optional[str] = csp_marker.get_color()
    color_array: Optional[List[str]] = csp_marker.get_color_array()
    size: Optional[int] = csp_marker.get_size()
    opacity: Optional[float] = csp_marker.get_opacity()
    ret = {
        'opacity': opacity,
        'symbol': symbol,
        'color': color,
        'size': size
    }
    if color_array:
        # PR-51574 Fixed wrong variable name.
        ret['color'] = color_array
    return ret


def _get_plotly_line(csp_line: Optional[PlotlyCspLine]):
    if csp_line is None:
        return None
    color: Optional[str] = csp_line.get_line_color()
    dash: Optional[str] = csp_line.get_dash_style()
    width: Optional[int] = csp_line.get_line_width()
    return {
        'color': color,
        'dash': dash,
        'width': width
    }


def to_error_bar_dict(error_csp: PlotlyCspErrorBarData) -> dict[str, Any] | None:
    if error_csp is None:
        return None
    ret: dict[str, Any] = dict()
    ret['type'] = error_csp.get_error_bar_type()
    ret['symmetric'] = error_csp.is_symmetric()
    ret['array'] = error_csp.get_array_plus()
    ret['arrayminus'] = error_csp.get_array_minus()
    ret['traceref'] = error_csp.get_trace_ref_plus()
    ret['tracerefminus'] = error_csp.get_trace_ref_minus()
    ret['color'] = error_csp.get_stroke_color()
    ret['thickness'] = error_csp.get_thickness()
    ret['value'] = error_csp.get_value_plus()
    ret['valueminus'] = error_csp.get_value_minus()
    ret['visible'] = error_csp.is_visible()
    ret['width'] = error_csp.get_width()

def _get_data_list(csp_data_list: Optional[List[PlotlyCspData]]) -> list[BaseTraceType]:
    if csp_data_list is None:
        return list()
    ret = list()
    for csp_series in csp_data_list:
        series_name = csp_series.get_series_name()
        x = csp_series.get_x_value_list()
        y = csp_series.get_y_value_list()
        z = csp_series.get_z_value_list()
        csp_marker = csp_series.get_marker()
        marker = _get_plotly_marker(csp_marker)
        csp_line = csp_series.get_line()
        line = _get_plotly_line(csp_line)
        error_x = to_error_bar_dict(csp_series.get_x_error_bar())
        error_y = to_error_bar_dict(csp_series.get_y_error_bar())
        box_points = csp_series.get_box_points()
        jitter = csp_series.get_jitter()
        point_pos = csp_series.get_points_position()
        fill_method = csp_series.get_fill_method()
        fill_color = csp_series.get_fill_color()
        mode = csp_series.get_data_mode()
        color_scale = csp_series.get_color_scale()
        is_reverse_scale = csp_series.is_reverse_scale()
        is_show_scale = csp_series.is_show_scale()
        n_contours = csp_series.get_num_contours()

        hist_norm: Optional[str] = None
        hist_norm_func = csp_series.get_hist_norm_func()
        if hist_norm_func is not None:
            hist_norm = hist_norm_func.plotly_id

        n_bin_x = csp_series.get_num_bins_x()
        n_bin_y = csp_series.get_num_bins_y()
        custom_data_list = csp_series.get_custom_data_list()
        dt: PlotlyDataType = PlotlyDataType.from_plotly_id(csp_series.get_data_type())
        chart: Optional[BaseTraceType]
        if dt == PlotlyDataType.HEAT_MAP:
            chart = Heatmap(x=x, y=y, z=z, customdata=custom_data_list, name=series_name,
                            colorscale=color_scale, reversescale=is_reverse_scale, showscale=is_show_scale)
        elif dt == PlotlyDataType.SCATTER or dt == PlotlyDataType.SCATTER_GL:
            chart = Scatter(x=x, y=y, error_x=error_x, error_y=error_y, customdata=custom_data_list, mode=mode,
                            fillcolor=fill_color, fill=fill_method, line=line, marker=marker, name=series_name)
        elif dt == PlotlyDataType.BAR:
            chart = Bar(x=x, y=y, error_x=error_x, error_y=error_y, customdata=custom_data_list,
                        marker=marker, name=series_name)
        elif dt == PlotlyDataType.BOX:
            chart = Box(x=x, y=y, customdata=custom_data_list, jitter=jitter, boxpoints=box_points, pointpos=point_pos,
                        fillcolor=fill_color, line=line, marker=marker, name=series_name)
        elif dt == PlotlyDataType.DENSITY_MAP:
            chart = Histogram2dContour(x=x, y=y, z=z, customdata=custom_data_list, line=line, marker=marker,
                                       name=series_name,
                                       ncontours=n_contours, showscale=is_show_scale, reversescale=is_reverse_scale,
                                       colorscale=color_scale)
        elif dt == PlotlyDataType.SURFACE:
            chart = plotly.graph_objs.Surface(x=x, y=y, z=z, customdata=custom_data_list, colorscale=color_scale,
                            reversescale=is_reverse_scale, showscale=is_show_scale, name=series_name)
        elif dt == PlotlyDataType.ISO_SURFACE:
            chart = Isosurface(x=x, y=y, z=z, customdata=custom_data_list, colorscale=color_scale,
                               reversescale=is_reverse_scale, showscale=is_show_scale, name=series_name)
        elif dt == PlotlyDataType.HISTOGRAM:
            chart = Histogram(x=x, y=y, error_x=error_x, error_y=error_y, nbinsx=n_bin_x, nbinsy=n_bin_y,
                              histnorm=hist_norm, customdata=custom_data_list, marker=marker, name=series_name)
        elif dt == PlotlyDataType.SCATTER_3D:
            chart = Scatter3d(x=x, y=y, z=z, error_x=error_x, error_y=error_y, customdata=custom_data_list, mode=mode,
                              line=line, marker=marker, name=series_name)
        else:
            raise CspDataException("Unsupported series data type: " + dt.name)
        if chart is not None:
            ret.append(chart)
    return ret


def _get_layout(csp_chart: PlotlyCspChart) -> Layout:
    x_axis: Optional[XAxis] = None
    y_axis: Optional[YAxis] = None
    if csp_chart.get_axis_config_list():
        for csp_axis in csp_chart.get_axis_config_list():
            orientation = csp_axis.get_orientation()
            axis_range: Optional[List[float]] = None
            auto_range = csp_axis.is_auto_range()
            if not auto_range:
                axis_range = [csp_axis.get_range_min(), csp_axis.get_range_max()]
            range_mode = csp_axis.get_range_mode().plotly_id
            category_order = csp_axis.get_category_order()
            category_array = csp_axis.get_category_array()
            is_show_grid = csp_axis.is_show_grid()
            is_zero_line = csp_axis.is_zero_line()
            zero_line_color = csp_axis.get_zero_line_color()
            grid_color = csp_axis.get_grid_color()
            line_color = csp_axis.get_line_color()
            show_line = csp_axis.is_show_line()
            anchor = csp_axis.get_anchor()

            if orientation == PlotlyAxisOrientation.X:
                x_axis = XAxis(range=axis_range, rangemode=range_mode, autorange=auto_range,
                               categoryorder=category_order, categoryarray=category_array,
                               showgrid=is_show_grid, zeroline=is_zero_line, zerolinecolor=zero_line_color,
                               gridcolor=grid_color, linecolor=line_color, showline=show_line,
                               anchor=anchor)
            elif orientation == PlotlyAxisOrientation.Y:
                y_axis = YAxis(range=axis_range, rangemode=range_mode, autorange=auto_range,
                               categoryorder=category_order, categoryarray=category_array,
                               showgrid=is_show_grid, zeroline=is_zero_line, zerolinecolor=zero_line_color,
                               gridcolor=grid_color, linecolor=line_color, showline=show_line,
                               anchor=anchor)
    title = csp_chart.get_title()
    bar_mode = csp_chart.get_bar_mode()
    bar_norm = csp_chart.get_bar_norm()
    csp_margin = csp_chart.get_margins()

    margin: Optional[Margin] = None
    if csp_margin is not None:
        margin = Margin(autoexpand=csp_margin.is_auto_expand(), b=csp_margin.get_bottom(),
                        l=csp_margin.get_left(), r=csp_margin.get_right(), t=csp_margin.get_top())

    return Layout(xaxis=x_axis, yaxis=y_axis, title=title, barmode=bar_mode, barnorm=bar_norm, margin=margin)


class SapioPyPlotlyUtil:
    @staticmethod
    def get_chart(csp_chart: PlotlyCspChart) -> Figure:
        """
        Get the chart from Sapio CSP Data.
        """
        if csp_chart.get_direct_json_data():
            return plotly.io.from_json(csp_chart.get_direct_json_data())
        data = _get_data_list(csp_chart.get_series_data_list())
        layout = _get_layout(csp_chart)
        return go.Figure(data=data, layout=layout)

    @staticmethod
    def export_image_data(fig: Figure, destination, format: Optional[str] = None,
                          width: Optional[int] = None, height: Optional[int] = None,
                          scale: Union[int, float, None] = None):
        """
        Write an image to a destination.
        :param fig: The source figure.
        :param destination:
        :param format:
        :param width:
        :param height:
        :param scale:
        :return:
        """
        fig.write_image(destination, format=format, width=width, height=height, scale=scale)
