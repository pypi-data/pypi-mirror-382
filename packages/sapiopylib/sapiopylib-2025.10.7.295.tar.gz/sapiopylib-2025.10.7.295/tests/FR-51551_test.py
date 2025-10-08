import unittest

from sapiopylib.rest.pojo.eln.ElnExperiment import InitializeNotebookExperimentPojo

from sapiopylib.rest.ELNService import ElnManager

from sapiopylib.rest.DataMgmtService import DataMgmtServer

from sapiopylib.rest.User import SapioUser

user = SapioUser(url="https://linux-vm:8443/webservice/api", verify_ssl_cert=False,
                 guid="3c232543-f407-4828-aae5-b33d4cd31fa7",
                 username="yqiao_api", password="Password1!")
data_record_manager = DataMgmtServer.get_data_record_manager(user)

class FR51551Test(unittest.TestCase):

    def test_transfer_ownership(self):
        eln_man: ElnManager = DataMgmtServer.get_eln_manager(user)
        exp = eln_man.create_notebook_experiment(InitializeNotebookExperimentPojo("Blah"))
        eln_man.transfer_ownership(exp.notebook_experiment_id, "admin")
        exp = eln_man.get_eln_experiment_by_id(exp.notebook_experiment_id)
        self.assertTrue("admin" == exp.owner)
