import logging
import sys
import unittest
from datetime import datetime
from typing import cast

from data_type_models import SampleModel
from sapiopylib.rest.DataMgmtService import DataMgmtServer
from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.datatype.DataTypeComponent import DataFormComponent, FieldDefinitionPosition
from sapiopylib.rest.pojo.datatype.FieldDefinition import VeloxDateFieldDefinition, VeloxStringFieldDefinition
from sapiopylib.rest.pojo.eln.ElnExperiment import InitializeNotebookExperimentPojo
from sapiopylib.rest.pojo.eln.ExperimentEntry import ExperimentTableEntry
from sapiopylib.rest.pojo.eln.ExperimentEntryCriteria import ElnEntryCriteria, ElnTableEntryUpdateCriteria
from sapiopylib.rest.pojo.eln.SapioELNEnums import ElnBaseDataType, ElnEntryType
from sapiopylib.rest.pojo.eln.eln_headings import ElnExperimentTabAddCriteria, ElnExperimentBanner
from sapiopylib.rest.utils.SapioDateUtils import date_time_to_java_millis
from sapiopylib.rest.utils.recordmodel.RecordModelManager import RecordModelManager

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logging.getLogger().setLevel(logging.INFO)

user = SapioUser(url="https://linux-vm:8443/webservice/api", verify_ssl_cert=False,
                 guid="66c2bea5-7cb2-4bfc-a413-304a3f4c3f33",
                 username="yqiao_api", password="Password1!")
additional_data = user.session_additional_data
data_record_manager = DataMgmtServer.get_data_record_manager(user)
eln_manager = DataMgmtServer.get_eln_manager(user)

class TestBannerTab(unittest.TestCase):

    def test_banner(self):
        # Create a banner, get the banner text, see it all works!
        exp = eln_manager.create_notebook_experiment(InitializeNotebookExperimentPojo("Banner Test"))
        exp_id = exp.notebook_experiment_id
        test_html = "Hi! This is a test"
        banner = ElnExperimentBanner(test_html, {"a test": "fun"})
        eln_manager.set_banner(exp_id, banner)
        banner = eln_manager.get_banner(exp_id)
        self.assertEqual(test_html, banner.html)

    def test_tab_data(self):
        """
        Get, create, and delete a tab.
        """
        exp = eln_manager.create_notebook_experiment(InitializeNotebookExperimentPojo("Tab Data Test"))
        exp_id = exp.notebook_experiment_id
        tabs = eln_manager.get_tabs_for_experiment(exp_id)
        self.assertIsNotNone(tabs)
        new_tab_name = "My New Tab"
        entry = eln_manager.add_experiment_entry(exp_id, ElnEntryCriteria(
            ElnEntryType.Table, "MyTable", ElnBaseDataType.EXPERIMENT_DETAIL.data_type_name, 2))
        new_tab = eln_manager.add_tab_for_experiment(exp_id, ElnExperimentTabAddCriteria(
            new_tab_name, [entry.entry_id]))
        self.assertTrue(new_tab is not None and new_tab.tab_id is not None and new_tab.tab_name == new_tab_name)
        tabs = eln_manager.get_tabs_for_experiment(exp_id)
        self.assertTrue(new_tab.tab_id in [tab.tab_id for tab in tabs])
        eln_manager.delete_tab_for_experiment(exp_id, new_tab.tab_id)
        tabs = eln_manager.get_tabs_for_experiment(exp_id)
        self.assertFalse(new_tab.tab_id in [tab.tab_id for tab in tabs])

    def test_add_empty_tab(self):
        """
        Get, create, and delete a tab.
        """
        exp = eln_manager.create_notebook_experiment(InitializeNotebookExperimentPojo("Tab Data Test"))
        exp_id = exp.notebook_experiment_id
        tabs = eln_manager.get_tabs_for_experiment(exp_id)
        self.assertIsNotNone(tabs)
        new_tab_name = "My New Tab"
        new_tab = eln_manager.add_tab_for_experiment(exp_id, ElnExperimentTabAddCriteria(
            new_tab_name, []))
        self.assertTrue(new_tab is not None and new_tab.tab_id is not None and new_tab.tab_name == new_tab_name)
        tabs = eln_manager.get_tabs_for_experiment(exp_id)
        self.assertTrue(new_tab.tab_id in [tab.tab_id for tab in tabs])
        eln_manager.delete_tab_for_experiment(exp_id, new_tab.tab_id)
        tabs = eln_manager.get_tabs_for_experiment(exp_id)
        self.assertFalse(new_tab.tab_id in [tab.tab_id for tab in tabs])

    def test_entry_properties(self):
        """
        Test the entry properties fixes.
        """
        exp = eln_manager.create_notebook_experiment(InitializeNotebookExperimentPojo("Entry Properties Fix Test"))
        exp_id = exp.notebook_experiment_id
        entry: ExperimentTableEntry = cast(ExperimentTableEntry, eln_manager.add_experiment_entry(exp_id, ElnEntryCriteria(
            ElnEntryType.Table, "MyTable", ElnBaseDataType.EXPERIMENT_DETAIL.data_type_name, 2)))
        updater = ElnTableEntryUpdateCriteria()
        updater.is_field_addable = True
        updater.is_existing_field_removable = True
        updater.is_removable = True
        updater.is_renamable = True
        updater.is_hidden = True
        updater.is_static_View = True
        eln_manager.update_experiment_entry(exp_id, entry.entry_id, updater)
        entry: ExperimentTableEntry = cast(ExperimentTableEntry, eln_manager.get_experiment_entry(exp_id, entry.entry_id))
        self.assertTrue(entry.is_field_addable)
        self.assertTrue(entry.is_existing_field_removable)
        self.assertTrue(entry.is_removable)
        self.assertTrue(entry.is_renamable)
        self.assertTrue(entry.is_hidden)
        self.assertTrue(entry.is_static_view)

    def tests_macro_fields(self):
        exp = eln_manager.create_notebook_experiment(InitializeNotebookExperimentPojo("Macro Test"))
        exp_id = exp.notebook_experiment_id
        entry: ExperimentTableEntry = cast(ExperimentTableEntry, eln_manager.add_experiment_entry(exp_id, ElnEntryCriteria(
            ElnEntryType.Table, "MyTable", ElnBaseDataType.EXPERIMENT_DETAIL.data_type_name, 2)))

        today_date_field_def = VeloxDateFieldDefinition(
            entry.data_type_name,"TodayDateTest", "Today Date", default_value="@today")
        current_user_field_def = VeloxStringFieldDefinition(
            entry.data_type_name, "CurrentUserTest", "Current User", default_value="@CurrentUser")
        current_group_field_def = VeloxStringFieldDefinition(
            entry.data_type_name, "CurrentGroupTest", "Current Group", default_value="@CurrentUserGroup")

        # Test add field definitions
        field_list = [today_date_field_def, current_user_field_def, current_group_field_def]
        eln_manager.add_eln_field_definitions(exp_id, entry.entry_id, field_list)

        # Test layout add
        dt_man = DataMgmtServer.get_data_type_manager(user)
        layout = dt_man.get_default_layout(entry.data_type_name)
        first_tab = layout.get_data_type_tab_definition_list()[0]
        first_form: DataFormComponent = cast(DataFormComponent, [x for x in first_tab.get_layout_component_list() if isinstance(x, DataFormComponent)][0])
        max_idx_previous: int = 0
        highest_pos = first_form.max_position
        if highest_pos is not None:
            max_idx_previous = highest_pos.order + 1
        for i, field in enumerate(field_list):
            position = FieldDefinitionPosition(field.data_field_name, first_form.component_name,
                                               order=max_idx_previous + i, form_column=0, form_column_span=4)
            first_form.set_field_definition_position(position)
        first_tab.set_layout_component(first_form)
        layout.set_data_type_tab_definition(first_tab)
        eln_manager.edit_eln_entry_layout(exp_id, entry.entry_id, layout)

        # Finalize tests for definition and layouts
        entry_fields_in_server = dt_man.get_field_definition_list(entry.data_type_name)
        field_names_in_server = set([field.data_field_name for field in entry_fields_in_server])
        for field in field_list:
            self.assertTrue(field.data_field_name in field_names_in_server)
        layout_in_server = dt_man.get_default_layout(entry.data_type_name)
        form_in_server: DataFormComponent = cast(DataFormComponent, layout_in_server.get_data_type_tab_definition(first_tab.tab_name).find_component(first_form.component_name))
        for field in field_list:
            self.assertTrue([pos for pos in form_in_server.positions if pos.data_field_name.upper() == field.data_field_name.upper()])

        # Finally, test the default value macros.
        rec_man = RecordModelManager(user)
        inst_man = rec_man.instance_manager
        now_millis = date_time_to_java_millis(datetime.now())
        model = inst_man.add_new_record(entry.data_type_name)
        self.assertTrue(model.get_field_value(current_user_field_def.data_field_name) == user.username)
        self.assertTrue(model.get_field_value(current_group_field_def.data_field_name) == user.group_name)
        self.assertTrue(model.get_field_value(today_date_field_def.data_field_name) >= now_millis)
        rec_man.store_and_commit()
        self.assertTrue(model.get_field_value(current_user_field_def.data_field_name) == user.username)
        model_group_name: str | None = model.get_field_value(current_group_field_def.data_field_name)
        group_name: str | None = user.group_name
        self.assertTrue( (not model_group_name and not group_name) or model_group_name == group_name)
        self.assertTrue(model.get_field_value(today_date_field_def.data_field_name) >= now_millis)

    def test_missing_values(self):
        rec_man = RecordModelManager(user)
        inst_man = rec_man.instance_manager
        sample = inst_man.add_new_record_of_type(SampleModel)
        self.assertTrue(SampleModel.SAMPLEID__FIELD_NAME.field_name not in sample.fields._model_fields.keys())
        self.assertIsNone(sample.get_SampleId_field())

