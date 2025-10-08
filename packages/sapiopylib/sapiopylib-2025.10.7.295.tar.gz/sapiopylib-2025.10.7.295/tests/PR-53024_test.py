import unittest

from sapiopylib.rest.pojo.eln.ElnExperiment import InitializeNotebookExperimentPojo, ElnExperiment

from sapiopylib.rest.DataMgmtService import DataMgmtServer

from sapiopylib.rest.User import SapioUser

user = SapioUser(url="https://linux-vm:8443/webservice/api", verify_ssl_cert=False,
                 guid="66c2bea5-7cb2-4bfc-a413-304a3f4c3f33",
                 username="yqiao_api", password="Password1!")
eln_man = DataMgmtServer.get_eln_manager(user)

class PR52914Test(unittest.TestCase):
    def test_hash_wrapper_field(self):
        exp: ElnExperiment = eln_man.create_notebook_experiment(InitializeNotebookExperimentPojo("Test"))

        exp_list: list[ElnExperiment] = eln_man.get_eln_experiment_list(
            user.username, [exp.notebook_experiment_status])
        self.assertTrue(exp in exp_list)