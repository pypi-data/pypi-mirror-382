import unittest

from sapiopylib.rest.DataMgmtService import DataMgmtServer
from sapiopylib.rest.User import SapioUser

user = SapioUser(url="https://linux-vm:8443/webservice/api", verify_ssl_cert=False,
                 guid="3c232543-f407-4828-aae5-b33d4cd31fa7",
                 username="yqiao_api", password="Password1!")


class FR52428Test(unittest.TestCase):

    def test_picklist_by_name(self):
        picklist_man = DataMgmtServer.get_picklist_manager(user)
        pick_list = picklist_man.get_picklist("BlahBlahBlahBlahNotExist")
        self.assertIsNone(pick_list)

    def test_user_group_info(self):
        group_man = DataMgmtServer.get_group_manager(user)
        admin_group_info = group_man.get_user_group_info_by_name("Admin")
        self.assertIsNotNone(admin_group_info)
        self.assertTrue(admin_group_info.data_type_layout_map)
