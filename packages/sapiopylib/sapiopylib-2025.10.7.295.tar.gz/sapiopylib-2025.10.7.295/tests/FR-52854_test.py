import logging
import sys
import unittest
from time import sleep

from sapiopylib.rest.utils.DataTypeCacheManager import DataTypeCacheManager

from sapiopylib.rest.utils.recorddatasinks import InMemoryRecordDataSink

from sapiopylib.rest.utils.recordmodel.properties import Child

from data_type_models import *
from sapiopylib.rest.utils.recordmodel.RecordModelManager import RecordModelManager

from sapiopylib.rest.pojo.eln.SapioELNEnums import ElnEntryType

from sapiopylib.rest.pojo.eln.ExperimentEntryCriteria import ElnEntryCriteria, ElnTableEntryUpdateCriteria

from sapiopylib.rest.DataMgmtService import DataMgmtServer
from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.eln.ElnExperiment import InitializeNotebookExperimentPojo
from sapiopylib.rest.pojo.eln.ElnExperimentRole import ElnRoleAssignment, ElnUserExperimentRole, ElnGroupExperimentRole

user = SapioUser(url="https://linux-vm:8443/webservice/api", verify_ssl_cert=False,
                 guid="66c2bea5-7cb2-4bfc-a413-304a3f4c3f33",
                 username="yqiao_api", password="Password1!")
data_record_manager = DataMgmtServer.get_data_record_manager(user)
eln_man = DataMgmtServer.get_eln_manager(user)
rec_man = RecordModelManager(user)
inst_man = rec_man.instance_manager
report_man = DataMgmtServer.get_report_manager(user)
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logging.getLogger().setLevel(logging.DEBUG)

class FR52854Test(unittest.TestCase):
    def test_batch_entry_update(self):
        exp = eln_man.create_notebook_experiment(InitializeNotebookExperimentPojo("T1"))
        e1 = eln_man.add_experiment_entry(exp.notebook_experiment_id, ElnEntryCriteria(
            ElnEntryType.Table, "E1", "Sample", 2))
        e2 = eln_man.add_experiment_entry(exp.notebook_experiment_id, ElnEntryCriteria(
            ElnEntryType.Table, "E2", "Sample", 3))
        update_request = {
            e1.entry_id: ElnTableEntryUpdateCriteria(),
            e2.entry_id: ElnTableEntryUpdateCriteria()
        }
        update_request[e1.entry_id].entry_name = "T1"
        update_request[e2.entry_id].entry_name = "T2"
        eln_man.update_experiment_entries(exp.notebook_experiment_id, update_request)
        exp = eln_man.get_eln_experiment_by_id(exp.notebook_experiment_id)
        entries = eln_man.get_experiment_entry_list(exp.notebook_experiment_id)
        e1 = [e for e in entries if e.entry_id == e1.entry_id][0]
        e2 = [e for e in entries if e.entry_id == e2.entry_id][0]
        self.assertTrue(e1.entry_name == "T1")
        self.assertTrue(e2.entry_name == "T2")

    def test_report_builder_with_existing_attachment_id(self):
        existing_att_rec = data_record_manager.add_data_record(AttachmentModel.DATA_TYPE_NAME)
        existing_att_rec.set_field_value(AttachmentModel.ATTACHMENTID__FIELD_NAME.field_name, "Bad Data")

        all_samples = []
        children_samples = []
        master_sample = inst_man.add_new_record_of_type(SampleModel)
        master_sample.set_Volume_field(500)
        all_samples.append(master_sample)
        for i in range(5):
            child_sample: SampleModel = master_sample.add(Child.create(SampleModel))
            child_sample.set_Volume_field(i)
            all_samples.append(child_sample)
            children_samples.append(child_sample)
        rec_man.store_and_commit()
        data_context = report_man.initialize_report_data_context(all_samples, 'Test Template')
        self.assertTrue(data_context.field_map_by_record_id_by_type)
        self.assertTrue(data_context.entry_data_context_map)
        data_context.entry_data_context_map['Form1'].set_records([master_sample])
        data_context.entry_data_context_map['Table1'].set_records(children_samples)
        data_context.existing_attachment_record_id = existing_att_rec.record_id
        data_context.attachment_additional_fields = {
            AttachmentModel.ATTACHMENTID__FIELD_NAME.field_name: "Good Data"
        }
        report_man.generate_report_pdf('Test Template', 'Attachment', data_context)
        sleep(10)
        existing_att_rec = data_record_manager.query_data_records_by_id(existing_att_rec.get_data_type_name(), [existing_att_rec.record_id]).result_list[0]
        self.assertTrue(existing_att_rec.get_field_value(AttachmentModel.ATTACHMENTID__FIELD_NAME.field_name) == "Good Data")
        # Also manually verify the PDF content.
        sink = InMemoryRecordDataSink(user)
        sink.get_attachment_data(existing_att_rec)
        self.assertTrue(len(sink.data) > 0)

    def test_record_model_wrappers(self):
        dt_helper = DataTypeCacheManager(user)
        self.assertEquals(SampleModel.DISPLAY_NAME, dt_helper.get_display_name(SampleModel.DATA_TYPE_NAME))
        self.assertEquals(SampleModel.PLURAL_DISPLAY_NAME, dt_helper.get_plural_display_name(SampleModel.DATA_TYPE_NAME))
        self.assertEquals(SampleModel.SAMPLEID__FIELD_NAME.display_name,
                          dt_helper.get_fields_for_type(SampleModel.DATA_TYPE_NAME).get(SampleModel.SAMPLEID__FIELD_NAME.field_name).display_name)
        self.assertEquals(SampleModel.CHEMICALREAGENT_EXT_TOTALHBONDACCEPTORS__FIELD_NAME.field_name,
                          ChemicalReagentModel.DATA_TYPE_NAME + "." + ChemicalReagentModel.TOTALHBONDACCEPTORS__FIELD_NAME.field_name)

