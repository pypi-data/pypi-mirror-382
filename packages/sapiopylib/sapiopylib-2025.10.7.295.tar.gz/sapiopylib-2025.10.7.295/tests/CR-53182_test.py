import base64
import io
import unittest
from typing import cast, Any

from sapiopylib.rest.DataMgmtService import DataMgmtServer
from sapiopylib.rest.DataRecordManagerService import DataRecordManager
from sapiopylib.rest.ELNService import ElnManager
from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.DataRecord import DataRecord
from sapiopylib.rest.pojo.chartdata.DashboardDefinition import BarLineChartDefinition, DashboardDefinition
from sapiopylib.rest.pojo.chartdata.DashboardEnums import ChartGroupingType, ChartOperationType, DashboardScope
from sapiopylib.rest.pojo.chartdata.DashboardSeries import BarChartSeries
from sapiopylib.rest.pojo.datatype.FieldDefinition import AbstractVeloxFieldDefinition, VeloxStringFieldDefinition, \
    VeloxIntegerFieldDefinition
from sapiopylib.rest.pojo.eln.ElnExperiment import InitializeNotebookExperimentPojo
from sapiopylib.rest.pojo.eln.ExperimentEntry import ExperimentAttachmentEntry, EntryRecordAttachment, ExperimentEntry, \
    ExperimentDashboardEntry, ExperimentPluginEntry, ExperimentTextEntry, ExperimentFormEntry
from sapiopylib.rest.pojo.eln.ExperimentEntryCriteria import ElnEntryCriteria, ElnAttachmentEntryCriteria, \
    AbstractElnEntryCriteria, ElnTableEntryCriteria, ElnDashboardEntryCriteria, ElnDashboardEntryUpdateCriteria, \
    ElnPluginEntryCriteria, ElnPluginEntryUpdateCriteria, ElnTextEntryCriteria, ElnFormEntryCriteria, \
    ElnFormEntryUpdateCriteria
from sapiopylib.rest.pojo.eln.SapioELNEnums import ElnEntryType, ElnBaseDataType
from sapiopylib.rest.utils.plates.MultiLayerPlating import MultiLayerPlateLayer, MultiLayerPlateConfig, \
    MultiLayerDataTypeConfig, MultiLayerReplicateConfig, MultiLayerDilutionConfig
from sapiopylib.rest.utils.plates.MultiLayerPlatingUtils import MultiLayerPlatingManager
from sapiopylib.rest.utils.plates.PlatingUtils import PlatingOrder

user = SapioUser(url="https://linux-vm:8443/webservice/api", verify_ssl_cert=False,
                 guid="3c232543-f407-4828-aae5-b33d4cd31fa7",
                 username="yqiao_api", password="Password1!")

class CR53182Test(unittest.TestCase):
    dr_man: DataRecordManager
    eln_man: ElnManager
    exp_id: int
    entry_order: int

    def test_entry_creation(self):
        """
        Test that the various entry types can be created using both the old ElnEntryCriteria, for reverse compatibility,
        and the new type-specific creation criteria.
        """
        self.dr_man = DataMgmtServer.get_data_record_manager(user)
        self.eln_man = DataMgmtServer.get_eln_manager(user)
        self.entry_order = 1

        exp = self.eln_man.create_notebook_experiment(InitializeNotebookExperimentPojo("Test"))
        self.exp_id: int = exp.notebook_experiment_id

        self.attachment_entry_creation()
        self.dashboard_entry_creation()
        self.global_dt_form_entry_creation()
        self.eln_dt_form_entry_creation()
        self.plugin_entry_creation()
        self.global_dt_table_entry_creation()
        self.eln_dt_table_entry_creation()
        self.temp_data_entry_creation()
        self.text_entry_creation()

    def add_entry(self, criteria: AbstractElnEntryCriteria) -> ExperimentEntry:
        return self.eln_man.add_experiment_entry(self.exp_id, criteria)

    def next_order(self) -> int:
        self.entry_order += 1
        return self.entry_order

    def attachment_entry_creation(self):
        file_name: str = "test.csv"
        file_data: bytes = b'Column 1,Column 2\nValue 1,Value 2\nValue 3,Value 4\n'
        attachment: DataRecord = self.create_attachment(file_name, file_data)
        rec_id: int = attachment.record_id

        old_criteria = ElnEntryCriteria(ElnEntryType.Attachment, "Old Attachment Entry", "Attachment", self.next_order(),
                                        attachment_data_base64=base64.b64encode(file_data).decode('utf-8'),
                                        attachment_file_name=file_name)
        old_entry = cast(ExperimentAttachmentEntry, self.add_entry(old_criteria))
        # Using the old method creates a new attachment record, so the record ID will be different,
        # but the file data should be the same.
        self.assertFalse(old_entry.record_id == rec_id, f"{old_entry.record_id} == {rec_id}")
        old_entry_data: bytes = self.read_attachment(self.get_attachment_by_id(old_entry.record_id))
        self.assertTrue(file_data == old_entry_data, f"{file_data} != {old_entry_data}")

        new_criteria = ElnAttachmentEntryCriteria("New Attachment Entry", "Attachment", self.next_order())
        new_criteria.entry_attachment_list = [EntryRecordAttachment(file_name, rec_id)]
        new_entry = cast(ExperimentAttachmentEntry, self.add_entry(new_criteria))
        # Using the new method uses the provided record, so the record ID should be the same.
        self.assertTrue(new_entry.record_id == rec_id, f"{new_entry.record_id} != {rec_id}")

    def get_attachment_by_id(self, record_id: int) -> DataRecord:
        return self.dr_man.query_data_records_by_id("Attachment", [record_id]).result_list[0]

    def create_attachment(self, file_name: str, file_data: bytes) -> DataRecord:
        attachment: DataRecord = self.dr_man.add_data_record("Attachment")
        with io.BytesIO(file_data) as stream:
            self.dr_man.set_attachment_data(attachment, file_name, stream)
        return attachment

    def read_attachment(self, attachment: DataRecord) -> bytes:
        with io.BytesIO() as data_sink:
            def consume_data(chunk: bytes):
                data_sink.write(chunk)
            self.dr_man.get_attachment_data(attachment, consume_data)
            data_sink.flush()
            data_sink.seek(0)
            file_bytes = data_sink.read()
        return file_bytes

    def dashboard_entry_creation(self):
        # Create a table entry for the dashboard to source their data from.
        source: int = self.add_entry(ElnTableEntryCriteria("Dashboard Source", "Sample", self.next_order())).entry_id
        fields: list[dict[str, Any]] = [
            {
                "Volume": 10 * (i + 1),
            }
            for i in range(5)
        ]
        records: list[DataRecord] = self.dr_man.add_data_records_with_data("Sample", fields)
        self.eln_man.add_records_to_table_entry(self.exp_id, source, records)

        # Create a bar chart dashboard to use the GUID of.
        dashboard_guid: str = self.create_dashboard()

        # Create a dashboard entry using the old method. This must be done in two steps, the first to create the
        # entry and the second to update it with the dashboard GUID.
        old_criteria = ElnEntryCriteria(ElnEntryType.Dashboard, "Old Dashboard Entry", "", self.next_order(),
                                        source_entry_id=source)
        old_entry = cast(ExperimentDashboardEntry, self.add_entry(old_criteria))
        self.assertTrue(old_entry.data_source_entry_id == source, f"{old_entry.data_source_entry_id} != {source}")

        update = ElnDashboardEntryUpdateCriteria()
        update.entry_height = 500
        update.dashboard_guid_list = [dashboard_guid]
        self.eln_man.update_experiment_entry(self.exp_id, old_entry.entry_id, update)
        # Get the updated entry.
        old_entry = cast(ExperimentDashboardEntry, self.eln_man.get_experiment_entry(self.exp_id, old_entry.entry_id))
        self.assertListEqual(old_entry.dashboard_guid_list, [dashboard_guid], f"{old_entry.dashboard_guid_list} != {[dashboard_guid]}")

        # Create a dashboard entry using the new method. This can be done in one step.
        new_criteria = ElnDashboardEntryCriteria("New Dashboard Entry", "", self.next_order())
        new_criteria.source_entry_id = source
        new_criteria.dashboard_guid_list = [dashboard_guid]
        new_criteria.entry_height = 500
        new_entry = cast(ExperimentDashboardEntry, self.add_entry(new_criteria))
        self.assertTrue(new_entry.data_source_entry_id == source, f"{new_entry.data_source_entry_id} != {source}")
        self.assertListEqual(new_entry.dashboard_guid_list, [dashboard_guid], f"{new_entry.dashboard_guid_list} != {[dashboard_guid]}")

    def create_dashboard(self) -> str:
        data_type_name: str = "Sample"
        x_field_name: str = "SampleId"
        y_field_name: str = "Volume"

        series = BarChartSeries(data_type_name, y_field_name)
        chart = BarLineChartDefinition()
        chart.grouping_type = ChartGroupingType.GROUP_BY_FIELD
        chart.grouping_type_data_type_name = data_type_name
        chart.grouping_type_data_field_name = x_field_name
        series.operation_type = ChartOperationType.TOTAL
        series.data_type_name = data_type_name
        series.data_field_name = y_field_name
        chart.series_list = [series]

        dashboard: DashboardDefinition = DashboardDefinition()
        dashboard.chart_definition_list = [chart]
        dashboard.dashboard_scope = DashboardScope.PRIVATE_ELN
        dashboard = DataMgmtServer.get_dashboard_manager(self.user).store_dashboard_definition(dashboard)
        return dashboard.dashboard_guid

    def global_dt_form_entry_creation(self):
        record: DataRecord = self.dr_man.add_data_record("Sample")
        layout: str = "Default Layout"
        forms: list[str] = ["Sample Details"]

        # Create a form entry using the old method. This must be done in two steps, the first to create the
        # entry and the second to update it with the record ID.
        old_criteria = ElnEntryCriteria(ElnEntryType.Form, "Old Global Form Entry", "Sample", self.next_order())
        old_entry = cast(ExperimentFormEntry, self.add_entry(old_criteria))

        update = ElnFormEntryUpdateCriteria()
        update.record_id = record.record_id
        update.data_type_layout_name = layout
        update.form_name_list = forms
        self.eln_man.update_experiment_entry(self.exp_id, old_entry.entry_id, update)
        old_entry = cast(ExperimentFormEntry, self.eln_man.get_experiment_entry(self.exp_id, old_entry.entry_id))
        self.assertTrue(old_entry.record_id == record.record_id, f"{old_entry.record_id} != {record.record_id}")
        self.assertTrue(old_entry.data_type_layout_name == layout, f"{old_entry.data_type_layout_name} != {layout}")
        self.assertTrue(old_entry.form_name_list == forms, f"{old_entry.form_name_list} != {forms}")

        # Create a form entry using the new method. This can be done in one step.
        new_criteria = ElnFormEntryCriteria("New Global Form Entry", "Sample", self.next_order())
        new_criteria.record_id = record.record_id
        new_criteria.data_type_layout_name = layout
        new_criteria.form_name_list = forms
        new_entry = cast(ExperimentFormEntry, self.add_entry(new_criteria))
        self.assertTrue(new_entry.record_id == record.record_id, f"{new_entry.record_id} != {record.record_id}")
        self.assertTrue(new_entry.data_type_layout_name == layout, f"{new_entry.data_type_layout_name} != {layout}")
        self.assertTrue(new_entry.form_name_list == forms, f"{new_entry.form_name_list} != {forms}")

    def eln_dt_form_entry_creation(self):
        dt: str = ElnBaseDataType.EXPERIMENT_DETAIL.data_type_name
        fields: list[AbstractVeloxFieldDefinition] = [
            VeloxStringFieldDefinition(dt, "Column1", "Column 1", editable=True),
            VeloxIntegerFieldDefinition(dt, "Column2", "Column 2", editable=True)
        ]
        field_map: dict[str, Any] = {
            "Column1": "Testing",
            "Column2": 123
        }

        # Create a form entry using the old method. This must be done in two steps, the first to create the
        # entry and the second to update it with the record ID.
        old_criteria = ElnEntryCriteria(ElnEntryType.Form, "Old ELN Form Entry", dt, self.next_order())
        old_criteria.field_definition_list = fields
        old_criteria.field_map_list = [field_map]
        old_entry = cast(ExperimentFormEntry, self.add_entry(old_criteria))

        update = ElnFormEntryUpdateCriteria()
        update.is_field_addable = False
        update.is_existing_field_removable = True
        self.eln_man.update_experiment_entry(self.exp_id, old_entry.entry_id, update)
        old_entry = cast(ExperimentFormEntry, self.eln_man.get_experiment_entry(self.exp_id, old_entry.entry_id))
        self.assertTrue(old_entry.is_field_addable == False, f"{old_entry.is_field_addable} != False")
        self.assertTrue(old_entry.is_existing_field_removable == True, f"{old_entry.is_existing_field_removable} != True")
        record: DataRecord = self.get_form_record(old_entry)
        for field, value in field_map.items():
            self.assertTrue(record.get_fields()[field] == value, f"[{field}]: {record.get_fields()[field]} != {value}")

        # Create a form entry using the new method. This can be done in one step.
        new_criteria = ElnFormEntryCriteria("New ELN Form Entry", dt, self.next_order())
        new_criteria.field_definition_list = fields
        new_criteria.field_map = field_map
        new_criteria.is_field_addable = False
        new_criteria.is_existing_field_removable = True
        new_entry = cast(ExperimentFormEntry, self.add_entry(new_criteria))
        self.assertTrue(new_entry.is_field_addable == False, f"{new_entry.is_field_addable} != False")
        self.assertTrue(new_entry.is_existing_field_removable == True, f"{new_entry.is_existing_field_removable} != True")
        record: DataRecord = self.get_form_record(new_entry)
        for field, value in field_map.items():
            self.assertTrue(record.get_fields()[field] == value, f"[{field}]: {record.get_fields()[field]} != {value}")

    def get_form_record(self, entry: ExperimentFormEntry) -> DataRecord:
        return self.eln_man.get_data_records_for_entry(self.exp_id, entry.entry_id).result_list[0]

    def plugin_entry_creation(self):
        # Get the configs for the plugin entry. Using a 3D plater entry.
        plate: DataRecord = self.dr_man.add_data_record("Plate")
        plugin_name: str = "com.velox.gwt.client.plugins.multilayerplating.core.ElnMultiLayerPlatingClientPlugin"
        layer = MultiLayerPlateLayer(
            MultiLayerDataTypeConfig("Sample"),
            PlatingOrder.FillBy.BY_COLUMN,
            MultiLayerReplicateConfig(),
            MultiLayerDilutionConfig()
        )
        entry_options: dict[str, str] = {
            "MultiLayerPlating_Plate_RecordIdList": ",".join([str(plate.record_id)]),
            "MultiLayerPlating_Entry_Prefs": MultiLayerPlatingManager.get_entry_prefs_json([layer]),
            "MultiLayerPlating_Entry_PrePlating_Prefs": MultiLayerPlatingManager.get_plate_configs_json(MultiLayerPlateConfig())
        }

        # Create a plugin entry using the old method. This must be done in two steps, the first to create the
        # entry and the second to update it with the entry options.
        old_criteria = ElnEntryCriteria(ElnEntryType.Plugin, "Old Plugin Entry", "Sample", self.next_order(),
                                        csp_plugin_name=plugin_name)
        old_entry = cast(ExperimentPluginEntry, self.add_entry(old_criteria))
        self.assertTrue(old_entry.plugin_name == plugin_name, f"{old_entry.plugin_name} != {plugin_name}")

        # Update the entry with the entry options.
        update = ElnPluginEntryUpdateCriteria()
        update.entry_height = 500
        update.entry_options_map = entry_options
        self.eln_man.update_experiment_entry(self.exp_id, old_entry.entry_id, update)

        # Create a plugin entry using the new method. This can be done in one step.
        new_criteria = ElnPluginEntryCriteria("New Plugin Entry", "Sample", self.next_order())
        new_criteria.csp_plugin_name = plugin_name
        new_criteria.entry_options_map = entry_options
        new_criteria.entry_height = 500
        new_entry = cast(ExperimentPluginEntry, self.add_entry(new_criteria))
        self.assertTrue(new_entry.plugin_name == plugin_name, f"{new_entry.plugin_name} != {plugin_name}")

        # We can't assert that the option maps were set, as trying to request the options right after creating the
        # entry will just return an empty dictionary.

    def global_dt_table_entry_creation(self):
        records: list[DataRecord] = self.dr_man.add_data_records("Sample", 3)
        columns: list[TableColumn] = [
            TableColumn("Sample", "SampleId"),
            TableColumn("Sample", "Volume"),
            TableColumn("Sample", "Concentration")
        ]
        fields: list[str] = ["SampleId", "Volume", "Concentration"]

        # Create a table entry using the old method. This must be done in two steps, the first to create the
        # entry and the second to update it with the record ID.
        old_criteria = ElnEntryCriteria(ElnEntryType.Table, "Old Global Table Entry", "Sample", self.next_order())
        old_entry = cast(ExperimentTableEntry, self.add_entry(old_criteria))

        update = ElnTableEntryUpdateCriteria()
        update.table_column_list = columns
        self.eln_man.update_experiment_entry(self.exp_id, old_entry.entry_id, update)
        old_entry = cast(ExperimentTableEntry, self.eln_man.get_experiment_entry(self.exp_id, old_entry.entry_id))
        self.eln_man.add_records_to_table_entry(self.exp_id, old_entry.entry_id, records)
        old_entry_fields: list[str] = [field.data_field_name for field in old_entry.table_column_list]
        for field in fields:
            self.assertTrue(field in old_entry_fields, f"{field} not in {old_entry_fields}")

        # Create a table entry using the new method. This can be done in one step.
        new_criteria = ElnTableEntryCriteria("New Global Table Entry", "Sample", self.next_order())
        new_criteria.table_column_list = columns
        new_entry = cast(ExperimentTableEntry, self.add_entry(new_criteria))
        self.eln_man.add_records_to_table_entry(self.exp_id, new_entry.entry_id, records)
        new_entry_fields: list[str] = [field.data_field_name for field in new_entry.table_column_list]
        for field in fields:
            self.assertTrue(field in new_entry_fields, f"{field} not in {new_entry_fields}")

    def eln_dt_table_entry_creation(self):
        dt: str = ElnBaseDataType.EXPERIMENT_DETAIL.data_type_name
        fields: list[AbstractVeloxFieldDefinition] = [
            VeloxStringFieldDefinition(dt, "Column1", "Column 1", editable=True),
            VeloxIntegerFieldDefinition(dt, "Column2", "Column 2", editable=True)
        ]
        field_maps: list[dict[str, Any]] = [
            {
                "Column1": "Testing",
                "Column2": 123
            },
            {
                "Column1": "Testing 2",
                "Column2": 456
            }
        ]

        # Create a table entry using the old method. This must be done in two steps, the first to create the
        # entry and the second to update it with the record ID.
        old_criteria = ElnEntryCriteria(ElnEntryType.Table, "Old ELN Table Entry", dt, self.next_order())
        old_criteria.field_definition_list = fields
        old_criteria.field_map_list = field_maps
        old_entry = cast(ExperimentTableEntry, self.add_entry(old_criteria))

        update = ElnTableEntryUpdateCriteria()
        update.is_field_addable = False
        update.is_existing_field_removable = True
        self.eln_man.update_experiment_entry(self.exp_id, old_entry.entry_id, update)
        old_entry = cast(ExperimentTableEntry, self.eln_man.get_experiment_entry(self.exp_id, old_entry.entry_id))
        self.assertTrue(old_entry.is_field_addable == False, f"{old_entry.is_field_addable} != False")
        self.assertTrue(old_entry.is_existing_field_removable == True, f"{old_entry.is_existing_field_removable} != True")
        records: list[DataRecord] = self.get_table_records(old_entry)
        for record, field_map in zip(records, field_maps):
            for field, value in field_map.items():
                self.assertTrue(record.get_fields()[field] == value, f"[{field}]: {record.get_fields()[field]} != {value}")

        # Create a table entry using the new method. This can be done in one step.
        new_criteria = ElnTableEntryCriteria("New ELN Table Entry", dt, self.next_order())
        new_criteria.field_definition_list = fields
        new_criteria.field_map_list = field_maps
        new_criteria.is_field_addable = False
        new_criteria.is_existing_field_removable = True
        new_entry = cast(ExperimentTableEntry, self.add_entry(new_criteria))
        self.assertTrue(new_entry.is_field_addable == False, f"{new_entry.is_field_addable} != False")
        self.assertTrue(new_entry.is_existing_field_removable == True, f"{new_entry.is_existing_field_removable} != True")
        records: list[DataRecord] = self.get_table_records(new_entry)
        for record, field_map in zip(records, field_maps):
            for field, value in field_map.items():
                self.assertTrue(record.get_fields()[field] == value, f"[{field}]: {record.get_fields()[field]} != {value}")

    def get_table_records(self, entry: ExperimentTableEntry) -> list[DataRecord]:
        return self.eln_man.get_data_records_for_entry(self.exp_id, entry.entry_id).result_list

    def temp_data_entry_creation(self):
        # TODO: I don't know of any temp data plugins to test.
        pass

    def text_entry_creation(self):
        # Text entries don't have any special update criteria, so both the old and the new method are essentially the
        # same.
        dt: str = ElnBaseDataType.TEXT_ENTRY_DETAIL.data_type_name
        field: str = ElnBaseDataType.get_text_entry_data_field_name()
        old_criteria = ElnEntryCriteria(ElnEntryType.Text, "Old Text Entry", dt, self.next_order())
        old_entry = cast(ExperimentTextEntry, self.add_entry(old_criteria))
        old_text: DataRecord = self.eln_man.get_data_records_for_entry(self.exp_id, old_entry.entry_id).result_list[0]
        old_text.set_field_value(field, "This entry was created with the old method.")

        new_criteria = ElnTextEntryCriteria("New Text Entry", dt, self.next_order())
        new_entry = cast(ExperimentTextEntry, self.add_entry(new_criteria))
        new_text: DataRecord = self.eln_man.get_data_records_for_entry(self.exp_id, new_entry.entry_id).result_list[0]
        new_text.set_field_value(field, "This entry was created with the new method.")

        self.dr_man.commit_data_records([old_text, new_text])
