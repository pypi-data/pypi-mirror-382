import unittest

from sapiopylib.rest.pojo.eln.SapioELNEnums import ElnEntryType

from sapiopylib.rest.pojo.eln.ExperimentEntryCriteria import ElnEntryCriteria, ElnTableEntryUpdateCriteria

from sapiopylib.rest.pojo.eln.ElnExperiment import InitializeNotebookExperimentPojo

from sapiopylib.rest.DataMgmtService import DataMgmtServer
from sapiopylib.rest.User import SapioUser

user = SapioUser(url="https://linux-vm:8443/webservice/api", verify_ssl_cert=False,
                 guid="66c2bea5-7cb2-4bfc-a413-304a3f4c3f33",
                 username="yqiao_api", password="Password1!")
eln_man = DataMgmtServer.get_eln_manager(user)

class FR52644Test(unittest.TestCase):

    def test_collapse_entry(self):
        exp = eln_man.create_notebook_experiment(InitializeNotebookExperimentPojo("Blah"))
        sample_table_entry = eln_man.add_experiment_entry(exp.notebook_experiment_id, ElnEntryCriteria(
            ElnEntryType.Table, "Sample", "Sample", 2
        ))
        update_criteria = ElnTableEntryUpdateCriteria()
        update_criteria.collapse_entry = True
        eln_man.update_experiment_entry(exp.notebook_experiment_id, sample_table_entry.entry_id, update_criteria)
        sample_table_entry = eln_man.get_experiment_entry(exp.notebook_experiment_id, sample_table_entry.entry_id)
        self.assertTrue(sample_table_entry.is_collapsed)

