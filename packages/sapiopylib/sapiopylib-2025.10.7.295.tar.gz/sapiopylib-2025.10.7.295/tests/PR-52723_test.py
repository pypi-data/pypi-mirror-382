import unittest

from sapiopylib.rest.DataMgmtService import DataMgmtServer

from sapiopylib.rest.utils.recordmodel.properties import Parent

from data_type_models import SampleModel, StudyModel, DNAPartModel
from sapiopylib.rest.utils.recordmodel.RecordModelManager import RecordModelManager

from sapiopylib.rest.User import SapioUser

user = SapioUser(url="https://linux-vm:8443/webservice/api", verify_ssl_cert=False,
                 guid="66c2bea5-7cb2-4bfc-a413-304a3f4c3f33",
                 username="yqiao_api", password="Password1!")
rec_man = RecordModelManager(user)

inst_man = rec_man.instance_manager
relationship_man = rec_man.relationship_manager
data_record_manager = DataMgmtServer.get_data_record_manager(user)
dt_man = DataMgmtServer.get_data_type_manager(user)

class TestPR52723(unittest.TestCase):

    def test_add_remove_child_under_restrictions(self):
        # test that single parent/single child changes do not blow up anymore for a record.
        study = inst_man.add_new_record_of_type(StudyModel)
        study2 = inst_man.add_new_record_of_type(StudyModel)
        sample = inst_man.add_new_record_of_type(SampleModel)
        sample.add(Parent.ref(study))
        rec_man.store_and_commit()
        sample.remove(Parent.ref(study))
        sample.add(Parent.ref(study2))
        rec_man.store_and_commit()

        children_recs = data_record_manager.get_children(study2.record_id, SampleModel.DATA_TYPE_NAME)
        self.assertTrue(len(children_recs.result_list) == 1 and children_recs.result_list[0].record_id == sample.record_id)
        children_recs = data_record_manager.get_children(study.record_id, SampleModel.DATA_TYPE_NAME)
        self.assertFalse(children_recs.result_list)

    def test_data_type_def_tag_retrieval(self):
        #Note: as of now no data type def has a tag. So we need to make one first on DNA Part as "Test Tag" before start running this test.
        dt = dt_man.get_data_type_definition(DNAPartModel.DATA_TYPE_NAME)
        self.assertTrue("Test Tag" == dt.tag)