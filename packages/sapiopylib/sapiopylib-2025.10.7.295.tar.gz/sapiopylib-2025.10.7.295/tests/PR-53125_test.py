import unittest

from sapiopylib.rest.pojo.eln.ExperimentEntryCriteria import AbstractElnEntryUpdateCriteria, ElnTextEntryUpdateCriteria

from sapiopylib.rest.pojo.eln.ElnEntryPosition import ElnEntryPosition

from sapiopylib.rest.pojo.chartdata.DashboardEnums import ChartType
from sapiopylib.rest.pojo.eln.eln_headings import ElnExperimentTabAddCriteria

from sapiopylib.rest.utils.Protocols import ElnExperimentProtocol

from sapiopylib.rest.utils.ProtocolUtils import ELNStepFactory

from sapiopylib.rest.pojo.eln.ElnExperiment import InitializeNotebookExperimentPojo, ElnExperiment

from sapiopylib.rest.DataMgmtService import DataMgmtServer

from sapiopylib.rest.User import SapioUser

user = SapioUser(url="https://linux-vm:8443/webservice/api", verify_ssl_cert=False,
                 guid="66c2bea5-7cb2-4bfc-a413-304a3f4c3f33",
                 username="yqiao_api", password="Password1!")
eln_man = DataMgmtServer.get_eln_manager(user)
data_record_manager = DataMgmtServer.get_data_record_manager(user)

class PR53125Test(unittest.TestCase):
    def test_gauge_chart(self):
        exp: ElnExperiment = eln_man.create_notebook_experiment(InitializeNotebookExperimentPojo("Test Gauge Chart Exp"))
        sample_record = data_record_manager.add_data_record("Sample")
        sample_record.set_field_value("Volume", 50)
        data_record_manager.commit_data_records([sample_record])

        # Add gauge chart
        protocol = ElnExperimentProtocol(exp, user)
        form_step = ELNStepFactory.create_form_step(protocol, "Sample", "Sample", sample_record)
        chart_step, dashboard = ELNStepFactory.create_gauge_chart(protocol, form_step, "Gauge Test", "Volume")
        self.assertTrue(dashboard.chart_definition_list[0].get_chart_type() == ChartType.GAUGE_CHART)

        # Check the gauge chart manually in the ELN and ensure it has right rendered value of "50" in the gauge chart.
        # Note: at this point the release version seem to have gauge chart max as 50 instead of 100 even though that's the fallback max value by default.
        # Jimmy said just assume this works and it will work in next version.

    def test_update_text_entry(self):
        exp: ElnExperiment = eln_man.create_notebook_experiment(InitializeNotebookExperimentPojo("Test Text and Tab Exp"))
        new_tab = eln_man.add_tab_for_experiment(exp.notebook_experiment_id, ElnExperimentTabAddCriteria("Test Tab", []))
        protocol = ElnExperimentProtocol(exp, user)

        # First, test the creation of a text entry with a specified tab id.
        text_step = ELNStepFactory.create_text_entry(protocol, "Test Second Tab Text Entry", position=ElnEntryPosition(new_tab.tab_id, None))
        text_entry = text_step.eln_entry
        self.assertTrue(text_entry.notebook_experiment_tab_id == new_tab.tab_id)

        entry_list = eln_man.get_experiment_entry_list(exp.notebook_experiment_id)
        title_entry = entry_list[0]

        # Move to first tab using the update method
        text_entry_update = ElnTextEntryUpdateCriteria()
        text_entry_update.entry_name = "New Name"
        text_entry_update.notebook_experiment_tab_id = title_entry.notebook_experiment_tab_id
        eln_man.update_experiment_entry(exp.notebook_experiment_id, text_entry.entry_id, text_entry_update)
        text_entry = eln_man.get_experiment_entry(exp.notebook_experiment_id, text_entry.entry_id)
        self.assertEquals("New Name", text_entry.entry_name)
        self.assertTrue(text_entry.notebook_experiment_tab_id == title_entry.notebook_experiment_tab_id)

        # Create text entry in the first tab and check it is in the first tab.
        table_step = ELNStepFactory.create_table_step(protocol, "Sample", "Sample", [],
                                                      position=ElnEntryPosition(title_entry.notebook_experiment_tab_id, title_entry.order + 1))
        table_entry = table_step.eln_entry
        self.assertTrue(text_entry.notebook_experiment_tab_id == table_entry.notebook_experiment_tab_id)


