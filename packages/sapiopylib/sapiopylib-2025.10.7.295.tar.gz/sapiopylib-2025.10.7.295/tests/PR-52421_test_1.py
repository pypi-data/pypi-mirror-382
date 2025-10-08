import unittest
from typing import cast

from data_type_models import SampleModel
from sapiopylib.rest.DataMgmtService import DataMgmtServer
from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.datatype.FieldDefinition import *

user = SapioUser(url="https://linux-vm:8443/webservice/api", verify_ssl_cert=False,
                 guid="3c232543-f407-4828-aae5-b33d4cd31fa7",
                 username="yqiao_api", password="Password1!")
dt_man = DataMgmtServer.get_data_type_manager(user)

class PR52421Test(unittest.TestCase):

    def test_def_transfers(self):
        sample_field_list = dt_man.get_field_definition_list('Sample')
        sample_fields = {field.data_field_name: field for field in sample_field_list}
        sample_type_field: VeloxSelectionFieldDefinition = cast(VeloxSelectionFieldDefinition, sample_fields.get(SampleModel.EXEMPLARSAMPLETYPE__FIELD_NAME.field_name))
        self.assertTrue(sample_type_field.direct_edit)
        container_type_field: VeloxPickListFieldDefinition = cast(VeloxPickListFieldDefinition, sample_fields.get(SampleModel.CONTAINERTYPE__FIELD_NAME.field_name))
        self.assertTrue(container_type_field.direct_edit)
        volume_unit_field: VeloxPickListFieldDefinition = cast(VeloxPickListFieldDefinition, sample_fields.get(SampleModel.VOLUMEUNITS__FIELD_NAME.field_name))
        self.assertFalse(volume_unit_field.direct_edit)

    def test_def_self_picklist_transfers(self):
        field = VeloxPickListFieldDefinition("X", "Y", "Z", "A", direct_edit=True)
        test: VeloxPickListFieldDefinition = cast(VeloxPickListFieldDefinition, FieldDefinitionParser.to_field_definition(field.to_json()))
        self.assertTrue(field.direct_edit == test.direct_edit)
        field.direct_edit = False
        test: VeloxPickListFieldDefinition = cast(VeloxPickListFieldDefinition, FieldDefinitionParser.to_field_definition(field.to_json()))
        self.assertTrue(field.direct_edit == test.direct_edit)

    def test_def_self_selection_list_transfers(self):
        field = VeloxSelectionFieldDefinition("X", "Y", "Z", ListMode.USER, direct_edit=True)
        test: VeloxSelectionFieldDefinition = cast(VeloxSelectionFieldDefinition, FieldDefinitionParser.to_field_definition(field.to_json()))
        self.assertTrue(field.direct_edit == test.direct_edit)
        field.direct_edit = False
        test: VeloxSelectionFieldDefinition = cast(VeloxSelectionFieldDefinition, FieldDefinitionParser.to_field_definition(field.to_json()))
        self.assertTrue(field.direct_edit == test.direct_edit)
