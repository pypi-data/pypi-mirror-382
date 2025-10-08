import unittest
from io import StringIO
from typing import cast

from sapiopylib.rest.utils.recordmodel.PyRecordModel import SapioRecordModelException

from sapiopylib.rest.utils.recordmodel.RecordModelManager import RecordModelManager


from sapiopylib.rest.pojo.eln.SapioELNEnums import ElnEntryType, ElnBaseDataType

from sapiopylib.rest.pojo.eln.ExperimentEntryCriteria import ElnEntryCriteria, ElnAttachmentEntryUpdateCriteria, \
    ElnDashboardEntryUpdateCriteria

from sapiopylib.rest.pojo.eln.ElnExperiment import InitializeNotebookExperimentPojo, NotebookExperiment

from sapiopylib.rest.DataMgmtService import DataMgmtServer

from sapiopylib.rest.User import SapioUser
from data_type_models import *

user = SapioUser(url="https://linux-vm:8443/webservice/api", verify_ssl_cert=False,
                 guid="66c2bea5-7cb2-4bfc-a413-304a3f4c3f33",
                 username="yqiao_api", password="Password1!")
notebook_man = DataMgmtServer.get_eln_manager(user)
rec_man = RecordModelManager(user)
inst_man = rec_man.instance_manager

class FR51849Test(unittest.TestCase):

    def test_eln_wrappers(self):
        exp: NotebookExperiment = notebook_man.create_notebook_experiment(InitializeNotebookExperimentPojo("API Test"))
        table_entry = notebook_man.add_experiment_entry(exp.notebook_experiment_id, ElnEntryCriteria(
            ElnEntryType.Table, "Table Entry", ElnBaseDataType.SAMPLE_DETAIL.data_type_name, 2))
        model = inst_man.add_new_record(table_entry.data_type_name)
        detail_model = inst_man.wrap(model, ELNSampleDetailModel)
        detail_model.set_SampleId_field("12345")
        rec_man.store_and_commit()

    def test_bad_wrapper_usage(self):
        exp: NotebookExperiment = notebook_man.create_notebook_experiment(InitializeNotebookExperimentPojo("API Test"))
        table_entry = notebook_man.add_experiment_entry(exp.notebook_experiment_id, ElnEntryCriteria(
            ElnEntryType.Table, "Table Entry", ElnBaseDataType.SAMPLE_DETAIL.data_type_name, 2))
        self.assertRaises(SapioRecordModelException, lambda: inst_man.add_new_record_of_type(ELNExperimentDetailModel))
        self.assertRaises(SapioRecordModelException, lambda: inst_man.add_new_record_of_type(ELNSampleDetailModel))
        inst_man.add_new_record_of_type(SampleModel)
        self.assertTrue(True)

    def test_ELN_enum(self):
        self.assertTrue(ElnBaseDataType.is_base_data_type(ELNSampleDetailModel.get_wrapper_data_type_name()))
        self.assertTrue(ElnBaseDataType.is_base_data_type(ELNExperimentDetailModel.get_wrapper_data_type_name()))
        self.assertTrue(ElnBaseDataType.is_base_data_type(ELNExperimentModel.get_wrapper_data_type_name()))
        self.assertTrue(ElnBaseDataType.is_eln_type(ELNSampleDetailModel.get_wrapper_data_type_name()))
        self.assertFalse(ElnBaseDataType.is_base_data_type("ElnSampleDetail_12345"))
        self.assertTrue(ElnBaseDataType.is_eln_type("ElnSampleDetail_12345"))
        self.assertEqual(ElnBaseDataType.get_base_type("ELNSampleDetail_12345"), ElnBaseDataType.SAMPLE_DETAIL)

