from typing import List, Optional, Dict, Tuple

from sapiopylib.rest.DataMgmtService import DataMgmtServer
from sapiopylib.rest.ELNService import ElnManager
from sapiopylib.rest.pojo.DataRecord import DataRecord
from sapiopylib.rest.pojo.chartdata.DashboardDefinition import BarLineChartDefinition, DashboardDefinition, \
    XyChartDefinition, HeatMapChartDefinition, GanttChartDefinition, GaugeChartDefinition
from sapiopylib.rest.pojo.chartdata.DashboardEnums import ChartGroupingType, \
    ChartOperationType, DashboardScope, PointShapeType, LineStyleType
from sapiopylib.rest.pojo.chartdata.DashboardSeries import BarChartSeries, XyChartSeries, HeatMapChartSeries, \
    GanttChartSeries, GaugeChartSeries
from sapiopylib.rest.pojo.eln.ElnEntryPosition import ElnEntryPosition
from sapiopylib.rest.pojo.eln.ExperimentEntryCriteria import AbstractElnEntryCriteria, ExperimentEntryCriteriaUtil, \
    ElnDashboardEntryCriteria, ElnFormEntryCriteria, ElnTableEntryCriteria, ElnPluginEntryCriteria
from sapiopylib.rest.pojo.eln.SapioELNEnums import ElnEntryType, ElnBaseDataType
from sapiopylib.rest.utils.Protocols import ElnExperimentProtocol, ElnEntryStep
from sapiopylib.rest.utils.plates.MultiLayerPlating import MultiLayerPlateConfig, MultiLayerPlateLayer
from sapiopylib.rest.utils.plates.MultiLayerPlatingUtils import MultiLayerPlatingManager


def validate_records_is_of_type(data_type_name: str, initial_attached_records: Optional[List[DataRecord]]):
    if initial_attached_records:
        for record in initial_attached_records:
            if record.get_data_type_name().lower() != data_type_name.lower():
                raise ValueError("Not all records passed in are of type " + data_type_name)


# CR-53182: Updated to return a type-specific entry creation criteria object instead of returning the created entry.
# The caller can now do any updates through the creation criteria instead of needing a separate call to make updates.
def _get_entry_creation_criteria(data_type_name: Optional[str], protocol: ElnExperimentProtocol,
                                 step_name: str, entry_type: ElnEntryType, position: Optional[ElnEntryPosition] = None)\
        -> Tuple[ElnManager, AbstractElnEntryCriteria]:
    tab_id: int | None = None
    order: int | None = None
    column_order: int | None = None
    column_span: int | None = None
    if position:
        tab_id = position.tab_id
        order = position.order
        column_order = position.column_order
        column_span = position.column_span
    # noinspection PyTypeChecker
    last_step: ElnEntryStep = protocol.get_sorted_step_list()[-1]
    if tab_id is None:
        tab_id = last_step.eln_entry.notebook_experiment_tab_id
    if order is None:
        order = last_step.eln_entry.order + 1
    eln_manager = DataMgmtServer.get_eln_manager(protocol.user)
    entry_criteria = ExperimentEntryCriteriaUtil.get_entry_creation_criteria(entry_type, step_name, data_type_name, order)
    entry_criteria.notebook_experiment_tab_id = tab_id
    entry_criteria.column_order = column_order
    entry_criteria.column_span = column_span
    return eln_manager, entry_criteria


class ELNStepFactory:
    """
    Factory that provides simple functions to create a new ELN step under an ELN protocol.
    """

    @staticmethod
    def _create_dashboard_step_from_chart(chart, data_source_step, protocol, step_name, position) -> \
            Tuple[DashboardDefinition, ElnEntryStep]:
        dashboard: DashboardDefinition = DashboardDefinition()
        dashboard.chart_definition_list = [chart]
        dashboard.dashboard_scope = DashboardScope.PRIVATE_ELN
        dashboard = DataMgmtServer.get_dashboard_manager(protocol.user).store_dashboard_definition(dashboard)
        eln_manager, new_entry_criteria = _get_entry_creation_criteria("",protocol, step_name, ElnEntryType.Dashboard, position)
        new_entry_criteria: ElnDashboardEntryCriteria
        new_entry_criteria.dashboard_guid_list = [dashboard.dashboard_guid]
        new_entry_criteria.source_entry_id = data_source_step.get_id()
        new_entry_criteria.entry_height = 500
        new_entry = eln_manager.add_experiment_entry(protocol.eln_experiment.notebook_experiment_id, new_entry_criteria)
        step = ElnEntryStep(protocol, new_entry)
        return dashboard, step

    @staticmethod
    def create_form_step(protocol: ElnExperimentProtocol, step_name: str, data_type_name: str,
                         initial_attached_record: Optional[DataRecord] = None,
                         position: Optional[ElnEntryPosition] = None) -> ElnEntryStep:
        """
        Create a new form step at the end of the protocol.
        :param protocol: The protocol to create a new step for.
        :param step_name: The step name for this entry, which is also the entry name.
        :param data_type_name: The data type name of the records that can be attached to the new step.
        :param initial_attached_record: The initially attached record for the new form step.
        Note: if unspecified, a form step will use a new record.
        :param position: The position of the new step. If not specified, the new step will be added at the end.
        :return: The new form step.
        """
        eln_manager, new_entry_criteria = _get_entry_creation_criteria(data_type_name, protocol, step_name, ElnEntryType.Form, position)
        new_entry_criteria: ElnFormEntryCriteria
        if initial_attached_record:
            validate_records_is_of_type(data_type_name, [initial_attached_record])
            new_entry_criteria.record_id = initial_attached_record.get_record_id()
        new_entry = eln_manager.add_experiment_entry(protocol.eln_experiment.notebook_experiment_id, new_entry_criteria)
        ret = ElnEntryStep(protocol, new_entry)
        protocol.invalidate()
        return ret

    @staticmethod
    def create_table_step(protocol: ElnExperimentProtocol, step_name: str, data_type_name: str,
                          initial_attached_records: Optional[List[DataRecord]] = None,
                          position: Optional[ElnEntryPosition] = None) -> ElnEntryStep:
        """
        Create a new table step at the end of the protocol.
        :param protocol: The protocol to create a new step for.
        :param step_name: The step name for this entry, which is also the entry name.
        :param data_type_name: The data type name of the records that can be attached to the new step.
        :param initial_attached_records: The initially attached records for the new form step.
        :param position: The position of the new step. If not specified, the new step will be added at the end.
        :return: The new table step
        """
        eln_manager, new_entry_criteria = _get_entry_creation_criteria(data_type_name, protocol, step_name, ElnEntryType.Table, position)
        new_entry_criteria: ElnTableEntryCriteria
        new_entry = eln_manager.add_experiment_entry(protocol.eln_experiment.notebook_experiment_id, new_entry_criteria)
        if initial_attached_records:
            validate_records_is_of_type(data_type_name, initial_attached_records)
            eln_manager.add_records_to_table_entry(protocol.eln_experiment.notebook_experiment_id,
                                                   new_entry.entry_id, initial_attached_records)
        ret = ElnEntryStep(protocol, new_entry)
        protocol.invalidate()
        return ret

    @staticmethod
    def create_plugin_entry(protocol: ElnExperimentProtocol, step_name: str, plugin_name: str,
                            initial_step_options: Optional[Dict[str, str]],
                            position: Optional[ElnEntryPosition] = None) -> ElnEntryStep:
        """
        Create a new Client-Side Plugin (CSP) entry
        :param protocol: The protocol to create a new step for.
        :param step_name: The step name for this entry, which is also the entry name.
        :param plugin_name: The GWT full class name to embed into this step.
        :param initial_step_options: If specified, add these plugin entry options to the current step.
        :param position: The position of the new step. If not specified, the new step will be added at the end.
        :return: The new CSP entry step.
        """
        eln_manager, new_entry_criteria = _get_entry_creation_criteria('Sample', protocol, step_name, ElnEntryType.Plugin, position)
        new_entry_criteria: ElnPluginEntryCriteria
        new_entry_criteria.csp_plugin_name = plugin_name
        new_entry_criteria.entry_height = 600
        if initial_step_options:
            new_entry_criteria.entry_options_map = initial_step_options
        new_entry = eln_manager.add_experiment_entry(protocol.eln_experiment.notebook_experiment_id, new_entry_criteria)
        ret = ElnEntryStep(protocol, new_entry)
        protocol.invalidate()
        return ret

    @staticmethod
    def create_text_entry(protocol: ElnExperimentProtocol, text_data: str,
                          position: Optional[ElnEntryPosition] = None) -> ElnEntryStep:
        """
        Create a text entry at the end of the protocol, with a initial text specified in the text entry.
        :param protocol: The protocol to create a new step for.
        :param text_data: Must be non-blank. This is what will be displayed. Some HTML format tags can be inserted.
        :param position: The position of the new step. If not specified, the new step will be added at the end.
        :return: The new text entry step.
        """
        eln_manager, new_entry_criteria = _get_entry_creation_criteria(ElnBaseDataType.TEXT_ENTRY_DETAIL.data_type_name,
                                                              protocol, 'Text Entry', ElnEntryType.Text, position)
        new_entry = eln_manager.add_experiment_entry(protocol.eln_experiment.notebook_experiment_id, new_entry_criteria)
        record = eln_manager.get_data_records_for_entry(protocol.eln_experiment.notebook_experiment_id,
                                                        new_entry.entry_id).result_list[0]
        record.set_field_value(ElnBaseDataType.get_text_entry_data_field_name(), text_data)
        DataMgmtServer.get_data_record_manager(protocol.user).commit_data_records([record])
        ret = ElnEntryStep(protocol, new_entry)
        protocol.invalidate()
        return ret

    @staticmethod
    def create_bar_chart_step(protocol: ElnExperimentProtocol, data_source_step: ElnEntryStep, step_name: str,
                              x_field_name: str, y_field_name: str,
                              grouping_type: ChartGroupingType = ChartGroupingType.GROUP_BY_FIELD,
                              operation_type: ChartOperationType = ChartOperationType.TOTAL,
                              position: Optional[ElnEntryPosition] = None) -> \
            Tuple[ElnEntryStep, DashboardDefinition]:
        """
        Create a bar chart where X field name may be of text field and Y field name is of numeric field
        :return: The tuple of (step, dashboard)
        """
        if not data_source_step.get_data_type_names():
            raise ValueError("The data source step did not declare a data type name.")
        data_type_name: str = data_source_step.get_data_type_names()[0]
        series = BarChartSeries(data_type_name, y_field_name)
        chart = BarLineChartDefinition()
        chart.grouping_type = grouping_type
        chart.grouping_type_data_type_name = data_type_name
        chart.grouping_type_data_field_name = x_field_name
        series.operation_type = operation_type
        series.data_type_name = data_type_name
        series.data_field_name = y_field_name
        chart.series_list = [series]

        dashboard, step = ELNStepFactory._create_dashboard_step_from_chart(chart, data_source_step, protocol, step_name, position)
        protocol.invalidate()
        return step, dashboard

    @staticmethod
    def create_gantt_chart_step(protocol: ElnExperimentProtocol, data_source_step: ElnEntryStep, step_name: str,
                                name_field_name: str, start_field_name: str, end_field_name: str,
                                group_by_field_name: str = "DataRecordName",
                                position: Optional[ElnEntryPosition] = None) -> \
            Tuple[ElnEntryStep, DashboardDefinition]:
        """
        Create a gantt chart where start and end are numeric and name is text field.

        In this call, the "group by field" is the label on the left, while the segment name is the one showing on hover
        of the highlighted region.
        """
        if not data_source_step.get_data_type_names():
            raise ValueError("The data source step did not declare a data type name.")
        data_type_name: str = data_source_step.get_data_type_names()[0]
        series: GanttChartSeries = GanttChartSeries(data_type_name, name_field_name,
                                                    data_type_name, start_field_name,
                                                    data_type_name, end_field_name)
        chart = GanttChartDefinition()
        chart.series_list = [series]
        chart.grouping_type = ChartGroupingType.GROUP_BY_FIELD
        chart.grouping_type_data_type_name = data_type_name
        chart.grouping_type_data_field_name = group_by_field_name
        dashboard, step = ELNStepFactory._create_dashboard_step_from_chart(chart, data_source_step, protocol, step_name, position)
        protocol.invalidate()
        return step, dashboard

    @staticmethod
    def create_gauge_chart(protocol: ElnExperimentProtocol, data_source_step: ElnEntryStep,
                           step_name: str, progress_field_name: str,
                           operation_type: ChartOperationType = ChartOperationType.VALUE,
                           position: Optional[ElnEntryPosition] = None) -> \
            Tuple[ElnEntryStep, DashboardDefinition]:
        """
        Create a gauge chart tracking the progress stored in a data record's data field.
        """
        if not data_source_step.get_data_type_names():
            raise ValueError("The data source step did not declare a data type name.")
        data_type_name: str = data_source_step.get_data_type_names()[0]
        series: GaugeChartSeries = GaugeChartSeries(data_type_name, progress_field_name)
        series.operation_type = operation_type
        chart = GaugeChartDefinition()
        chart.series_list = [series]
        dashboard, step = ELNStepFactory._create_dashboard_step_from_chart(chart, data_source_step, protocol, step_name, position)
        protocol.invalidate()
        return step, dashboard


    @staticmethod
    def create_xy_chart_step(protocol: ElnExperimentProtocol, data_source_step: ElnEntryStep, step_name: str,
                             x_field_name: str, y_field_name: str,
                             line_style: LineStyleType = LineStyleType.NORMAL,
                             point_shape: PointShapeType = PointShapeType.CIRCLE,
                             position: Optional[ElnEntryPosition] = None) -> \
            Tuple[ElnEntryStep, DashboardDefinition]:
        """
        Create an X-Y chart where X and Y fields are both numeric.
        """
        if not data_source_step.get_data_type_names():
            raise ValueError("The data source step did not declare a data type name.")
        data_type_name: str = data_source_step.get_data_type_names()[0]
        series: XyChartSeries = XyChartSeries(data_type_name, x_field_name, data_type_name, y_field_name)
        series.line_style_type = line_style
        series.point_shape_type = point_shape
        chart: XyChartDefinition = XyChartDefinition()
        chart.series_list = [series]

        dashboard, step = ELNStepFactory._create_dashboard_step_from_chart(chart, data_source_step, protocol, step_name, position)
        protocol.invalidate()
        return step, dashboard

    @staticmethod
    def create_heatmap_chart_step(protocol: ElnExperimentProtocol, data_source_step: ElnEntryStep, step_name: str,
                                  x_field_name: str, y_field_name: str, size_field_name: Optional[str],
                                  color_field_name: Optional[str], show_data_point_labels: bool = True,
                                  min_num_rows: Optional[int] = None, min_num_cols: Optional[int] = None,
                                  position: Optional[ElnEntryPosition] = None) -> \
            Tuple[ElnEntryStep, DashboardDefinition]:
        """
        Create a heatmap chart where size,color fields are numeric, while X and Y are any fields sorted in alphanumeric.
        """
        if not data_source_step.get_data_type_names():
            raise ValueError("The data source step did not declare a data type name.")
        data_type_name: str = data_source_step.get_data_type_names()[0]
        series: HeatMapChartSeries = HeatMapChartSeries(data_type_name, x_field_name, data_type_name, y_field_name,
                                                        data_type_name, size_field_name,
                                                        data_type_name, color_field_name)
        series.show_data_point_labels = show_data_point_labels
        chart: HeatMapChartDefinition = HeatMapChartDefinition()
        chart.min_number_of_rows = min_num_rows
        chart.min_number_of_cols = min_num_cols

        dashboard, step = ELNStepFactory._create_dashboard_step_from_chart(chart, data_source_step, protocol, step_name, position)
        protocol.invalidate()
        return step, dashboard

    @staticmethod
    def add_3d_plate_step(protocol: ElnExperimentProtocol, layers: List[MultiLayerPlateLayer],
                          config: MultiLayerPlateConfig = MultiLayerPlateConfig(),
                          entry_name: str = "3D Plating") -> Tuple[ElnEntryStep, List[DataRecord], List[DataRecord]]:
        """
        Add a 3D Plating step to the experiment, pre-plating records based on the provided MultiLayerPlateLayers
        :return A tuple of (step, plate records, well element records)
        """
        plate_man: MultiLayerPlatingManager = MultiLayerPlatingManager(protocol)
        plates, well_elements = plate_man.create_well_positions(config, layers)

        # set entry options
        plate_record_ids: List[str] = list(map(lambda p: str(p.get_record_id()), plates))
        initial_step_options = {
            "MultiLayerPlating_Plate_RecordIdList": ",".join(plate_record_ids),
            "MultiLayerPlating_Entry_Prefs": MultiLayerPlatingManager.get_entry_prefs_json(layers),
            "MultiLayerPlating_Entry_PrePlating_Prefs": MultiLayerPlatingManager.get_plate_configs_json(config)}
        plating_step: ElnEntryStep = ELNStepFactory.create_plugin_entry(
            protocol, entry_name,
            "com.velox.gwt.client.plugins.multilayerplating.core.ElnMultiLayerPlatingClientPlugin",
            initial_step_options)

        # commit created records
        DataMgmtServer.get_data_record_manager(protocol.user).commit_data_records(plates + well_elements)
        protocol.invalidate()
        return plating_step, plates, well_elements
