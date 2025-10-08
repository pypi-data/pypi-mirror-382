import unittest

from sapiopylib.rest.DataMgmtService import DataMgmtServer
from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.eln.ElnExperiment import InitializeNotebookExperimentPojo
from sapiopylib.rest.pojo.eln.ExperimentEntryCriteria import ElnEntryCriteria
from sapiopylib.rest.pojo.eln.SapioELNEnums import ElnEntryType

user = SapioUser(url="https://linux-vm:8443/webservice/api", verify_ssl_cert=False,
                 guid="66c2bea5-7cb2-4bfc-a413-304a3f4c3f33",
                 username="yqiao_api", password="Password1!")
eln_man = DataMgmtServer.get_eln_manager(user)

class FR52881Test(unittest.TestCase):
    def test_delete_entries(self):
        exp = eln_man.create_notebook_experiment(InitializeNotebookExperimentPojo("Delete Entries Test"))
        e1 = eln_man.add_experiment_entry(exp.notebook_experiment_id, ElnEntryCriteria(
            ElnEntryType.Table, "E1", "Sample", 2))
        e2 = eln_man.add_experiment_entry(exp.notebook_experiment_id, ElnEntryCriteria(
            ElnEntryType.Table, "E2", "Sample", 3))
        e3 = eln_man.add_experiment_entry(exp.notebook_experiment_id, ElnEntryCriteria(
            ElnEntryType.Table, "E3", "Sample", 4))
        eln_man.delete_experiment_entry_list(exp.notebook_experiment_id, [e1.entry_id, e2.entry_id])
        exp = eln_man.get_eln_experiment_by_id(exp.notebook_experiment_id)
        entry_list = eln_man.get_experiment_entry_list(exp.notebook_experiment_id)
        entry_id_list = [entry.entry_id for entry in entry_list]
        self.assertTrue(e1.entry_id not in entry_id_list)
        self.assertTrue(e2.entry_id not in entry_id_list)
        self.assertTrue(e3.entry_id in entry_id_list)