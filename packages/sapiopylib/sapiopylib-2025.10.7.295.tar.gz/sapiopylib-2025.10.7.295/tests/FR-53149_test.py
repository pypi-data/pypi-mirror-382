import unittest

from sapiopylib.rest.pojo.eln.SapioELNEnums import ElnEntryType, ElnBaseDataType
from sapiopylib.rest.pojo.eln.ExperimentEntryCriteria import ElnEntryCriteria
from sapiopylib.rest.pojo.eln.ElnExperiment import InitializeNotebookExperimentPojo
from sapiopylib.rest.pojo.datatype.DataTypeLayout import DataTypeLayout, TableLayout
from sapiopylib.rest.pojo.datatype.FieldDefinition import VeloxStringFieldDefinition
from sapiopylib.rest.pojo.datatype.DataType import DataTypeDefinition
from sapiopylib.rest.User import SapioUser

from sapiopylib.rest.DataMgmtService import DataMgmtServer
from sapiopylib.rest.pojo.datatype.veloxindex import VeloxIndexDefinitionBuilder

user = SapioUser(url="https://linux-vm:8443/webservice/api", verify_ssl_cert=False,
                 guid="66c2bea5-7cb2-4bfc-a413-304a3f4c3f33",
                 username="yqiao_api", password="Password1!")
eln_man = DataMgmtServer.get_eln_manager(user)
dt_man = DataMgmtServer.get_data_type_manager(user)

class FR_53149_test(unittest.TestCase):
    def test_create_and_delete_data_type(self):
        dt_name = "TestDataType"
        display_name = "Test Data Type"
        dt_def: DataTypeDefinition = dt_man.get_data_type_definition(dt_name)
        if dt_def:
            dt_man.delete_data_type_definition(dt_name)
        dt_def = DataTypeDefinition(dt_name, display_name=display_name, is_high_volume=True, is_extension_type=False, is_attachment=True, attachment_type=".png")
        dt_man.insert_or_update_data_type_definition(dt_def)
        dt_def = dt_man.get_data_type_definition(dt_name)

        # Test data type attributes.
        self.assertIsNotNone(dt_def)
        self.assertEqual(dt_def.data_type_name, dt_name)
        self.assertEqual(dt_def.display_name, display_name)
        self.assertEqual(dt_def.plural_display_name, display_name + "s")
        self.assertTrue(dt_def.is_high_volume)
        self.assertFalse(dt_def.is_extension_type)
        self.assertTrue(dt_def.is_attachment)
        self.assertEqual(dt_def.attachment_type, ".png")

        # Test adding of a data field on data type.
        field_name: str = "TestField"
        field_display_name = "Test Field"
        field_def: VeloxStringFieldDefinition = VeloxStringFieldDefinition(dt_name, field_name, field_display_name, max_length=4000, num_lines=5)
        dt_man.insert_or_update_field_definition_list(dt_name, [field_def])
        field_def_list = dt_man.get_field_definition_list(dt_name)
        # Get field def by field name
        field_def = next((f for f in field_def_list if f.data_field_name == field_name), None)
        self.assertIsNotNone(field_def)
        self.assertEqual(field_def.data_field_name, field_name)
        self.assertEqual(field_def.display_name, field_display_name)
        self.assertEqual(field_def.data_type_name, dt_name)
        self.assertEqual(field_def.max_length, 4000)
        self.assertEqual(field_def.num_lines, 5)

        # Test Index Assignment
        index_name = "TestIndex"
        index_def = VeloxIndexDefinitionBuilder(index_name, [field_def])
        dt_man.insert_or_update_index_definition_list(dt_name, [index_def])
        index_list = dt_man.get_index_definition_list(dt_name)
        index_def = next((i for i in index_list if i.index_name == index_name), None)
        self.assertIsNotNone(index_def)
        self.assertEqual(index_def.index_name, index_name)
        self.assertEqual(len(index_def.index_column_list), 1)
        self.assertEqual(index_def.index_column_list[0].data_field_name, field_name)

        # Test layout creation and deletion.
        layout_name = "TestLayout"
        layout = DataTypeLayout(layout_name, layout_name, description="This is a test layout", number_of_columns=5, fill_view=True)
        layout.data_type_name = dt_name
        table_layout = TableLayout(cell_size=128, record_image_width=64)
        layout.table_layout = table_layout
        dt_man.insert_or_update_data_type_layout(layout)
        layout_list = dt_man.get_data_type_layout_list(dt_name)
        layout = next((l for l in layout_list if l.layout_name == layout_name), None)
        self.assertIsNotNone(layout)
        self.assertEqual(layout.layout_name, layout_name)
        self.assertEqual(layout.display_name, layout_name)
        self.assertEqual(layout.description, "This is a test layout")
        self.assertEqual(layout.number_of_columns, 5)
        self.assertTrue(layout.fill_view)
        self.assertIsNotNone(layout.table_layout)
        self.assertEqual(layout.table_layout.cell_size, 128)
        self.assertEqual(layout.table_layout.record_image_width, 64)

        # Finally test delete data type.
        dt_man.delete_data_type_definition(dt_name)
        dt_def = dt_man.get_data_type_definition(dt_name)
        self.assertIsNone(dt_def)

    def test_edit_notebook_experiment_type(self):
        exp = eln_man.create_notebook_experiment(InitializeNotebookExperimentPojo("Edit Notebook Experiment Type Test"))
        self.assertIsNotNone(exp)
        # Create table of experiment details entry.
        entry = eln_man.add_experiment_entry(exp.notebook_experiment_id, ElnEntryCriteria(ElnEntryType.Table, "Record Image Table", ElnBaseDataType.EXPERIMENT_DETAIL.data_type_name, 2))
        self.assertIsNotNone(entry)
        # Set the data type to have data record image and have a custom image width in table column
        dt_name = entry.data_type_name
        dt_def: DataTypeDefinition = dt_man.get_data_type_definition(dt_name)
        self.assertIsNotNone(dt_def)
        dt_def.is_record_image_assignable = True
        eln_man.update_eln_data_type_definition(exp.notebook_experiment_id, entry.entry_id, dt_def)

        # Update layout to have a wider image cell.
        layout = dt_man.get_default_layout(dt_name)
        self.assertIsNotNone(layout)
        layout.table_layout = TableLayout(cell_size=128, record_image_width=64)
        eln_man.update_eln_data_type_layout(exp.notebook_experiment_id, entry.entry_id, layout)

        # Check resulting type def
        dt_def = dt_man.get_data_type_definition(dt_name)
        self.assertEqual(dt_def.data_type_name, dt_name)
        self.assertTrue(dt_def.is_record_image_assignable)
        layout = dt_man.get_default_layout(dt_name)
        self.assertIsNotNone(layout)
        self.assertEqual(layout.table_layout.cell_size, 128)
        self.assertEqual(layout.table_layout.record_image_width, 64)
