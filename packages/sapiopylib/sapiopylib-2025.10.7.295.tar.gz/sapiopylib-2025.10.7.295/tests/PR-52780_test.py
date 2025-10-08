import unittest

from sapiopylib.rest.pojo.datatype.FieldDefinition import VeloxDateRangeFieldDefinition

from sapiopylib.rest.utils.FormBuilder import FormBuilder

from sapiopylib.rest.DataMgmtService import DataMgmtServer

from sapiopylib.rest.User import SapioUser

user = SapioUser(url="https://linux-vm:8443/webservice/api", verify_ssl_cert=False,
                 guid="66c2bea5-7cb2-4bfc-a413-304a3f4c3f33",
                 username="yqiao_api", password="Password1!")

class TestPR52780(unittest.TestCase):

    def test_static_date_range_fields(self):
        dt_man = DataMgmtServer.get_data_type_manager(user)
        fb = FormBuilder()
        static_date_range_field = VeloxDateRangeFieldDefinition(fb.get_data_type_name(), "StaticDateRange", "Static")
        static_date_range_field.static_date = True
        zoned_date_range_field = VeloxDateRangeFieldDefinition(fb.get_data_type_name(), "DateRange", "Zoned")
        zoned_date_range_field.static_date = False
        fb.add_field(static_date_range_field)
        fb.add_field(zoned_date_range_field)
        source_dt = fb.get_temporary_data_type()
        dt = dt_man.test_temporary_data_type_translation(source_dt)
        static_test_field: VeloxDateRangeFieldDefinition = dt.get_field(static_date_range_field.data_field_name)
        self.assertIsNotNone(static_test_field)
        self.assertTrue(static_test_field.static_date)

        zoned_test_field: VeloxDateRangeFieldDefinition = dt.get_field(zoned_date_range_field.data_field_name)
        self.assertIsNotNone(zoned_test_field)
        self.assertFalse(zoned_test_field.static_date)