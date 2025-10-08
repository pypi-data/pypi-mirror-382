import unittest
from io import StringIO
from typing import cast

from sapiopylib.rest.pojo.eln.ExperimentEntry import ExperimentDashboardEntry

from sapiopylib.rest.pojo.chartdata.DashboardEnums import DashboardScope

from sapiopylib.rest.pojo.chartdata.DashboardDefinition import DashboardDefinition, BarLineChartDefinition, \
    PieChartDefinition

from sapiopylib.rest.utils.Protocols import ElnExperimentProtocol, ElnEntryStep

from sapiopylib.rest.pojo.eln.SapioELNEnums import ElnEntryType

from sapiopylib.rest.pojo.eln.ExperimentEntryCriteria import ElnEntryCriteria, ElnAttachmentEntryUpdateCriteria, \
    ElnDashboardEntryUpdateCriteria

from sapiopylib.rest.pojo.eln.ElnExperiment import InitializeNotebookExperimentPojo, NotebookExperiment

from sapiopylib.rest.DataMgmtService import DataMgmtServer

from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.utils.autopaging import QueryDataRecordByIdListAutoPager

user = SapioUser(url="https://linux-vm:8443/webservice/api", verify_ssl_cert=False,
                 guid="3c232543-f407-4828-aae5-b33d4cd31fa7",
                 username="yqiao_api", password="Password1!")
notebook_man = DataMgmtServer.get_eln_manager(user)
dashboard_man = DataMgmtServer.get_dashboard_manager(user)

class FR51849Test(unittest.TestCase):
    def test_dashboard_guids(self):
        chart1 = BarLineChartDefinition()
        def1 = DashboardDefinition(DashboardScope.PRIVATE_ELN, [chart1])
        dashboard_man.store_dashboard_definition(def1)
        chart2 = PieChartDefinition()
        def2 = DashboardDefinition(DashboardScope.PRIVATE, [chart2])
        dashboard_man.store_dashboard_definition(def2)
        guid_list: list[str] = [def1.dashboard_guid, def2.dashboard_guid]

        exp: NotebookExperiment = notebook_man.create_notebook_experiment(InitializeNotebookExperimentPojo("API Test"))
        table_entry = notebook_man.add_experiment_entry(exp.notebook_experiment_id, ElnEntryCriteria(
            ElnEntryType.Table, "Table Entry", "Directory", 2))
        dashboard_entry: ExperimentDashboardEntry = cast(ExperimentDashboardEntry, notebook_man.add_experiment_entry(exp.notebook_experiment_id, ElnEntryCriteria(
            ElnEntryType.Dashboard, "Dashboard Entry", "Directory", 3, source_entry_id=table_entry.entry_id)))
        update_criteria = ElnDashboardEntryUpdateCriteria()
        update_criteria.dashboard_guid_list = guid_list
        notebook_man.update_experiment_entry(exp.notebook_experiment_id, dashboard_entry.entry_id, update_criteria)

        dashboard_entry = cast(ExperimentDashboardEntry, notebook_man.get_experiment_entry(exp.notebook_experiment_id, dashboard_entry.entry_id))
        test_update_criteria = dashboard_entry.dashboard_guid_list
        self.assertEqual(test_update_criteria, guid_list)
