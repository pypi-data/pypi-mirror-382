
import unittest
from io import StringIO

from sapiopylib.rest.utils.Protocols import ElnExperimentProtocol, ElnEntryStep

from sapiopylib.rest.pojo.eln.SapioELNEnums import ElnEntryType

from sapiopylib.rest.pojo.eln.ExperimentEntryCriteria import ElnEntryCriteria, ElnAttachmentEntryUpdateCriteria

from sapiopylib.rest.pojo.eln.ElnExperiment import InitializeNotebookExperimentPojo, NotebookExperiment

from sapiopylib.rest.DataMgmtService import DataMgmtServer

from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.utils.autopaging import QueryDataRecordByIdListAutoPager

user = SapioUser(url="https://linux-vm:8443/webservice/api", verify_ssl_cert=False,
                 guid="3c232543-f407-4828-aae5-b33d4cd31fa7",
                 username="yqiao_api", password="Password1!")
notebook_man = DataMgmtServer.get_eln_manager(user)
data_record_manager = DataMgmtServer.get_data_record_manager(user)
class FR51847Test(unittest.TestCase):

    def test_multi_entry_attachments(self):
        exp: NotebookExperiment = notebook_man.create_notebook_experiment(InitializeNotebookExperimentPojo("API Test"))
        att_entry = notebook_man.add_experiment_entry(exp.notebook_experiment_id, ElnEntryCriteria(
            ElnEntryType.Attachment, "Att Test", "Attachment", 2))
        records = data_record_manager.add_data_records("Attachment", 2)
        for i, record in enumerate(records):
            with StringIO("test") as io:
                data_record_manager.set_attachment_data(record, "test" + str(i) + ".txt", io)
        records = QueryDataRecordByIdListAutoPager("Attachment", [x.record_id for x in records], user).get_all_at_once()

        protocol = ElnExperimentProtocol(exp, user)
        att_step = ElnEntryStep(protocol, att_entry)
        att_step.set_records(records)

        att_entry = notebook_man.get_experiment_entry(exp.notebook_experiment_id, att_entry.entry_id)
        att_step = ElnEntryStep(protocol, att_entry)
        test_records = att_step.get_records()
        self.assertEquals(set(records), set(test_records))

    def test_single_entry_attachment(self):
        exp: NotebookExperiment = notebook_man.create_notebook_experiment(InitializeNotebookExperimentPojo("API Test"))
        att_entry = notebook_man.add_experiment_entry(exp.notebook_experiment_id, ElnEntryCriteria(
            ElnEntryType.Attachment, "Att Test", "Attachment", 2))
        records = data_record_manager.add_data_records("Attachment", 1)
        for i, record in enumerate(records):
            with StringIO("test") as io:
                data_record_manager.set_attachment_data(record, "test" + str(i) + ".txt", io)
        records = QueryDataRecordByIdListAutoPager("Attachment", [x.record_id for x in records], user).get_all_at_once()

        update_criteria = ElnAttachmentEntryUpdateCriteria()
        update_criteria.record_id = records[0].record_id
        update_criteria.attachment_name = "test1.txt"
        notebook_man.update_experiment_entry(exp.notebook_experiment_id, att_entry.entry_id, update_criteria)

        protocol = ElnExperimentProtocol(exp, user)

        att_entry = notebook_man.get_experiment_entry(exp.notebook_experiment_id, att_entry.entry_id)
        att_step = ElnEntryStep(protocol, att_entry)
        test_records = att_step.get_records()
        self.assertEquals(set(records), set(test_records))
