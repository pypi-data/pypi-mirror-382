import unittest
from typing import cast

from sapiopylib.rest.DataMgmtService import DataMgmtServer

from sapiopylib.rest.pojo.datatype.FieldDefinition import VeloxSelectionFieldDefinition, ListMode

from sapiopylib.rest.utils.FormBuilder import FormBuilder

from sapiopylib.rest.User import SapioUser

user = SapioUser(url="https://linux-vm:8443/webservice/api", verify_ssl_cert=False,
                 guid="66c2bea5-7cb2-4bfc-a413-304a3f4c3f33",
                 username="yqiao_api", password="Password1!")

class CR52789Test(unittest.TestCase):

    def test_static_list_values(self):
        fb = FormBuilder()
        field_with_list = VeloxSelectionFieldDefinition(fb.data_type_name, "FieldWithList", "Field With List", ListMode.PLUGIN)
        field_with_list.static_list_values = ['a', 'b']
        fb.add_field(field_with_list)
        field_without_list = VeloxSelectionFieldDefinition(fb.data_type_name, "FieldWithoutList", "Field Without List", ListMode.PLUGIN)
        fb.add_field(field_without_list)

        dt_man = DataMgmtServer.get_data_type_manager(user)
        test_dt = dt_man.test_temporary_data_type_translation(fb.get_temporary_data_type())
        without_field_test: VeloxSelectionFieldDefinition = cast(VeloxSelectionFieldDefinition, test_dt.get_field(field_without_list.data_field_name))
        with_field_test: VeloxSelectionFieldDefinition = cast(VeloxSelectionFieldDefinition, test_dt.get_field(field_with_list.data_field_name))
        self.assertIsNone(without_field_test.static_list_values)
        self.assertEqual(with_field_test.static_list_values, field_with_list.static_list_values)