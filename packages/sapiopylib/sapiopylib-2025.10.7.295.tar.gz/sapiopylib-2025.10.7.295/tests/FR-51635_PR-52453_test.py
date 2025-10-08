import unittest

from sapiopylib.rest.pojo.eln.ElnEntryPosition import ElnEntryPosition

from sapiopylib.rest.pojo.eln.ElnExperiment import InitializeNotebookExperimentPojo

from sapiopylib.rest.pojo.eln.SapioELNEnums import TemplateAccessLevel

from sapiopylib.rest.DataMgmtService import DataMgmtServer

from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.eln.protocol_template import ProtocolTemplateQuery

user = SapioUser(url="https://linux-vm:8443/webservice/api", verify_ssl_cert=False,
                 guid="3c232543-f407-4828-aae5-b33d4cd31fa7",
                 username="yqiao_api", password="Password1!")
data_record_manager = DataMgmtServer.get_data_record_manager(user)
eln_manager = DataMgmtServer.get_eln_manager(user)

class TestFR51635(unittest.TestCase):

    def test_field_set_info(self):
        field_set_info_list = eln_manager.get_field_set_info_list()
        print("Field Set Info List:")
        for field_set_info in field_set_info_list:
            print(field_set_info.__dict__)
        field_set_info = field_set_info_list[0]
        print("Fields for " + field_set_info.field_set_name)
        fields = eln_manager.get_predefined_fields_from_field_set_id(field_set_info.field_set_id)
        for field in fields:
            print(field.data_field_name)

    def test_protocol_template(self):
        print("Protocol Template List:")
        protocol_template_list = eln_manager.get_protocol_template_info_list(ProtocolTemplateQuery(
            whitelist_access_levels=[TemplateAccessLevel.PUBLIC, TemplateAccessLevel.PRIVATE], active_templates_only=False))
        for template in protocol_template_list:
            print(template.template_name)
        print("Public Template list:")
        public_template_list = eln_manager.get_protocol_template_info_list(ProtocolTemplateQuery(
            whitelist_access_levels=[TemplateAccessLevel.PUBLIC], active_templates_only=False))
        for template in public_template_list:
            print(template.template_name)
        public_template = public_template_list[0]
        print("Active Template List:")
        active_only_template_list = eln_manager.get_protocol_template_info_list((ProtocolTemplateQuery(active_templates_only=True)))
        for template in active_only_template_list:
            print(template.template_name)

        exp = eln_manager.create_notebook_experiment(InitializeNotebookExperimentPojo(experiment_name="Blah"))
        entry_list = eln_manager.get_experiment_entry_list(exp.notebook_experiment_id, False)
        eln_manager.add_protocol_template(exp.notebook_experiment_id, public_template.template_id, ElnEntryPosition(tab_id=entry_list[0].notebook_experiment_tab_id,
                                                                                                                    order=2))
        entry_list = eln_manager.get_experiment_entry_list(exp.notebook_experiment_id, False)
        print("Result Entries for new Experiment:")
        for entry in entry_list:
            print(entry.entry_name)

