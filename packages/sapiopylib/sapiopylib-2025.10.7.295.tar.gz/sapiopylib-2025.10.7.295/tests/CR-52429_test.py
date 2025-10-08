import unittest

from sapiopylib.rest.DataMgmtService import DataMgmtServer
from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.chartdata.DashboardDefinition import PieChartDefinition, DashboardDefinition
from sapiopylib.rest.pojo.chartdata.DashboardEnums import DashboardScope
from sapiopylib.rest.pojo.eln.ElnExperiment import InitializeNotebookExperimentPojo
from sapiopylib.rest.pojo.eln.ExperimentEntryCriteria import ElnEntryCriteria
from sapiopylib.rest.pojo.eln.SapioELNEnums import ElnEntryType, ElnBaseDataType

user = SapioUser(url="https://linux-vm:8443/webservice/api", verify_ssl_cert=False,
                 guid="3c232543-f407-4828-aae5-b33d4cd31fa7",
                 username="yqiao_api", password="Password1!")

# These are tests for changes on status 204 handling for no data.
class CR52429Test(unittest.TestCase):

    def test_custom_report_service(self):
        report_man = DataMgmtServer.get_custom_report_manager(user)
        report = report_man.run_system_report_by_name("BlahBlahNotExist")
        self.assertIsNone(report)
        report = report_man.run_system_report_by_name("All Projects")
        self.assertTrue(report)

    def test_dashboard_service(self):
        dashboard_man = DataMgmtServer.get_dashboard_manager(user)
        chart = PieChartDefinition()
        private_def = DashboardDefinition(DashboardScope.PRIVATE, [chart])
        private_dash = dashboard_man.store_dashboard_definition(private_def)
        private_dash = dashboard_man.get_dashboard(private_dash.dashboard_guid)
        self.assertTrue(private_dash)
        dash = dashboard_man.get_dashboard("BlahBlahBlahNotExist")
        self.assertIsNone(dash)

    def test_data_record_manager(self):
        data_record_manager = DataMgmtServer.get_data_record_manager(user)
        rec = data_record_manager.query_system_for_record("Directory", 1)
        self.assertTrue(rec)
        rec = data_record_manager.query_system_for_record("Directory", -1)
        self.assertIsNone(rec)

    def test_eln_manager(self):
        eln_manager = DataMgmtServer.get_eln_manager(user)
        self.assertIsNone(eln_manager.get_eln_experiment_by_record_id(-1))
        self.assertIsNone(eln_manager.get_experiment_entry_list(-1))
        self.assertIsNone(eln_manager.get_experiment_entry(-1, -1))
        self.assertIsNone(eln_manager.get_predefined_field_by_id(-1))
        self.assertIsNone(eln_manager.get_predefined_fields_from_field_set_id(-1))
        self.assertIsNone(eln_manager.get_experiment_entry_options(-1, -1))
        self.assertIsNone(eln_manager.get_notebook_experiment_options(-1))

        exp = eln_manager.create_notebook_experiment(InitializeNotebookExperimentPojo("Test"))
        entry = eln_manager.add_experiment_entry(
            exp.notebook_experiment_id, ElnEntryCriteria(ElnEntryType.Table, "Samples", "Sample", 2))
        self.assertTrue(eln_manager.get_eln_experiment_by_record_id(exp.experiment_record_id).notebook_experiment_id == exp.notebook_experiment_id)
        self.assertTrue(entry in eln_manager.get_experiment_entry_list(exp.notebook_experiment_id))
        self.assertTrue(entry == eln_manager.get_experiment_entry(exp.notebook_experiment_id, entry.entry_id))

        self.assertIsNotNone(eln_manager.get_notebook_experiment_options(exp.notebook_experiment_id))
        self.assertIsNotNone(eln_manager.get_experiment_entry_options(exp.notebook_experiment_id, entry.entry_id))

    def test_picklist_service(self):
        picklist_man = DataMgmtServer.get_picklist_manager(user)
        self.assertIsNone(picklist_man.get_picklist("BlahBlahBlahNotExist"))
        self.assertTrue("Freezer" in picklist_man.get_picklist('Storage Unit Types').entry_list)

    def test_user_group_service(self):
        group_man = DataMgmtServer.get_group_manager(user)
        self.assertIsNone(group_man.get_user_group_info_by_name("BlahBlahBlahNotExist"))
        self.assertIsNone(group_man.get_user_group_info_by_id(-1))
        self.assertIsNone(group_man.get_user_group_info_list_for_user("BlahBlahBlahNotExist"))
        admin_group = group_man.get_user_group_info_by_name("Admin")
        self.assertIsNotNone(admin_group)
        self.assertIsNotNone(group_man.get_user_group_info_by_id(admin_group.group_id))
        self.assertIsNotNone(group_man.get_user_group_info_list_for_user("admin"))
