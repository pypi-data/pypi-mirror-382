import unittest

from data_type_models import *
from sapiopylib.rest.DataMgmtService import DataMgmtServer
from sapiopylib.rest.ELNService import ElnManager
from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.eln.ElnExperiment import InitializeNotebookExperimentPojo
from sapiopylib.rest.pojo.eln.ExperimentEntry import ExperimentEntry
from sapiopylib.rest.pojo.eln.ExperimentEntryCriteria import ElnEntryCriteria
from sapiopylib.rest.pojo.eln.SapioELNEnums import ElnEntryType
from sapiopylib.rest.utils.DataTypeCacheManager import DataTypeCacheManager
from sapiopylib.rest.utils.recordmodel.RecordModelManager import RecordModelManager

user = SapioUser(url="https://linux-vm:8443/webservice/api", verify_ssl_cert=False,
                 guid="3c232543-f407-4828-aae5-b33d4cd31fa7",
                 username="yqiao_api", password="Password1!")

class CR52168Test(unittest.TestCase):

    def test_add_records_to_table_entry(self):
        eln_man: ElnManager = DataMgmtServer.get_eln_manager(user)
        exp = eln_man.create_notebook_experiment(InitializeNotebookExperimentPojo("Test"))
        rec_man = RecordModelManager(user)
        inst_man = rec_man.instance_manager
        entry: ExperimentEntry = eln_man.add_experiment_entry(
            exp.notebook_experiment_id, ElnEntryCriteria(ElnEntryType.Table, "Table", EmailModel.DATA_TYPE_NAME, 1))
        model_to_add = inst_man.add_new_record_of_type(EmailModel)
        self.assertRaises(ValueError, lambda : eln_man.add_records_to_table_entry(exp.notebook_experiment_id, entry.entry_id,
                                                                                  [model_to_add.get_data_record()], also_set_fields=False))
        rec_man.store_and_commit()
        # Allow missing required fields to pass through without set fields in server call.
        eln_man.add_records_to_table_entry(exp.notebook_experiment_id, entry.entry_id, [model_to_add.get_data_record()], also_set_fields=False)
        record_id_list = [x.record_id for x in eln_man.get_data_records_for_entry(exp.notebook_experiment_id, entry.entry_id).result_list]
        self.assertTrue(model_to_add.record_id in record_id_list)

    def test_is_side_link(self):
        dt_helper = DataTypeCacheManager(user)
        self.assertTrue(dt_helper.is_side_link_field(ComputedAssayResultsModel.DATA_TYPE_NAME, ComputedAssayResultsModel.COMPOUNDPARTLINK__FIELD_NAME.field_name))
        self.assertFalse(dt_helper.is_side_link_field(ComputedAssayResultsModel.DATA_TYPE_NAME, ComputedAssayResultsModel.ASSAYTYPE__FIELD_NAME.field_name))
        self.assertFalse(dt_helper.is_side_link_field(ComputedAssayResultsModel.DATA_TYPE_NAME, "NonExistentFieldLoL"))