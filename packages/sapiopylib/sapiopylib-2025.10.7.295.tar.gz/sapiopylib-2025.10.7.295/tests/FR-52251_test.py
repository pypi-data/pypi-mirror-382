import unittest

from data_type_models import DirectoryModel
from sapiopylib.rest.DataMgmtService import DataMgmtServer
from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.acl import AccessType, SetDataRecordACLCriteria

user = SapioUser(url="https://linux-vm:8443/webservice/api", verify_ssl_cert=False,
                 guid="3c232543-f407-4828-aae5-b33d4cd31fa7",
                 username="yqiao_api", password="Password1!")
data_record_manager = DataMgmtServer.get_data_record_manager(user)

class FR52251Test(unittest.TestCase):

    def test_acl(self):
        record = data_record_manager.add_data_record(DirectoryModel.DATA_TYPE_NAME)
        record.set_field_value(DirectoryModel.DIRECTORYNAME__FIELD_NAME.field_name, "Test ACL Root")

        acl_list = data_record_manager.get_data_record_acl(record.data_type_name, [record.record_id])
        acl = acl_list[0]
        # Initially the record should start with default ACL ID.
        self.assertTrue(acl.base_record_id is None)
        acl.update_user_access('yqiao_api', AccessType.DELETE, True)
        acl.update_user_access('yqiao_api', AccessType.OWNER, True)
        acl.update_user_access('yqiao_api', AccessType.ACLMGMT, True)
        acl.update_user_access('admin', AccessType.WRITE, False)
        acl.update_user_access('admin', AccessType.READ, True)
        data_record_manager.set_data_record_acl(SetDataRecordACLCriteria([record], [acl]))
        acl_list = data_record_manager.get_data_record_acl(record.data_type_name, [record.record_id])
        acl = acl_list[0]
        # Now it will have its own ACL.
        self.assertTrue(acl.base_record_id == record.record_id)
        my_user_access = acl.get_user_access('yqiao_api')
        self.assertTrue(my_user_access is not None)
        self.assertTrue(my_user_access.has_access(AccessType.READ))
        self.assertTrue(my_user_access.has_access(AccessType.WRITE))
        self.assertTrue(my_user_access.has_access(AccessType.DELETE))
        self.assertTrue(my_user_access.has_access(AccessType.OWNER))
        self.assertTrue(my_user_access.has_access(AccessType.ACLMGMT))
        admin_user_access = acl.get_user_access('admin')
        self.assertTrue(admin_user_access.has_access(AccessType.READ))
        self.assertFalse(admin_user_access.has_access(AccessType.WRITE))
        self.assertFalse(admin_user_access.has_access(AccessType.DELETE))
