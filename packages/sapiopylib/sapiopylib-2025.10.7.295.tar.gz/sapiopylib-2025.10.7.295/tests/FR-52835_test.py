import logging
import sys
import unittest

from sapiopylib.rest.DataMgmtService import DataMgmtServer
from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.eln.ElnExperiment import InitializeNotebookExperimentPojo
from sapiopylib.rest.pojo.eln.ElnExperimentRole import ElnRoleAssignment, ElnUserExperimentRole, ElnGroupExperimentRole

user = SapioUser(url="https://linux-vm:8443/webservice/api", verify_ssl_cert=False,
                 guid="66c2bea5-7cb2-4bfc-a413-304a3f4c3f33",
                 username="yqiao_api", password="Password1!")
eln_man = DataMgmtServer.get_eln_manager(user)
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logging.getLogger().setLevel(logging.DEBUG)

#Note: this test assumes user isn't "admin" user.
#Also: you need ELN admin priv as the context user (for batch call test)
class FR52835Test(unittest.TestCase):
    def test_batch_assignment(self):
        exp_1 = eln_man.create_notebook_experiment(InitializeNotebookExperimentPojo("T1"))
        exp_2 = eln_man.create_notebook_experiment(InitializeNotebookExperimentPojo("T2"))
        assignment_map: dict[int, ElnRoleAssignment] = {
            exp_1.notebook_experiment_id: ElnRoleAssignment([
                ElnUserExperimentRole(True, False, False, False, "admin")
            ], []),
            exp_2.notebook_experiment_id: ElnRoleAssignment([
                ElnUserExperimentRole(False, True, False, False, "admin")
            ], [])
        }
        eln_man.update_role_assignments(assignment_map)
        exp_1 = eln_man.get_eln_experiment_by_id(exp_1.notebook_experiment_id)
        exp_2 = eln_man.get_eln_experiment_by_id(exp_2.notebook_experiment_id)
        self.assertTrue(ElnUserExperimentRole(True, False, False, False, "admin") in exp_1.user_roles.values())
        self.assertTrue(ElnUserExperimentRole(False, True, False, False, "admin") in exp_2.user_roles.values())

    def test_exp_assignment(self):
        exp = eln_man.create_notebook_experiment(InitializeNotebookExperimentPojo("TR"))
        role = ElnUserExperimentRole(True, False, False, False, "admin")
        eln_man.update_role_assignment(exp.notebook_experiment_id, ElnRoleAssignment([role], []))
        exp = eln_man.get_eln_experiment_by_id(exp.notebook_experiment_id)
        self.assertTrue(role in exp.user_roles.values())
        groups = DataMgmtServer.get_group_manager(user).get_user_group_info_list()
        if groups:
            group = groups[0]
            g_role = ElnGroupExperimentRole(False, True, False, False, group.group_id)
            eln_man.update_role_assignment(exp.notebook_experiment_id, ElnRoleAssignment([], [g_role]))
            exp = eln_man.get_eln_experiment_by_id(exp.notebook_experiment_id)
            self.assertTrue(g_role in exp.group_roles.values())
