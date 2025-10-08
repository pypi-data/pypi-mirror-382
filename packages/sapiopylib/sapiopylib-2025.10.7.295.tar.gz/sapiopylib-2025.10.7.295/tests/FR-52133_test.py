import unittest

from sapiopylib.rest.utils.recordmodel.RelationshipPath import RelationshipPath

from sapiopylib.rest.utils.recordmodel.properties import *

from data_type_models import *
from sapiopylib.rest.utils.recordmodel.RecordModelManager import RecordModelManager

from sapiopylib.rest.DataMgmtService import DataMgmtServer

from sapiopylib.rest.User import SapioUser

user = SapioUser(url="https://linux-vm:8443/webservice/api", verify_ssl_cert=False,
                 guid="66c2bea5-7cb2-4bfc-a413-304a3f4c3f33",
                 username="yqiao_api", password="Password1!")
data_record_manager = DataMgmtServer.get_data_record_manager(user)


# Directory => Location => Department => Project => Sample

class TestFR52133(unittest.TestCase):

    def test_relationship_paths(self):
        rec_man = RecordModelManager(user)
        inst_man = rec_man.instance_manager

        root_directory: DirectoryModel = inst_man.add_existing_record_of_type(data_record_manager.query_system_for_record(DirectoryModel.DATA_TYPE_NAME, 1), DirectoryModel)

        location: VeloxLocationModel = root_directory.add(Child.create(VeloxLocationModel))
        location.set_LocationName_field("FR-52133")
        department: VeloxDepartmentModel = location.add(Child.create(VeloxDepartmentModel))
        department.set_DepartmentName_field("D1")
        for i in range(3):
            project: ProjectModel = department.add(Child.create(ProjectModel))
            project.set_ProjectId_field("P" + str(i + 1))
            for j in range(4):
                request: RequestModel = project.add(Child.create(RequestModel))
                request.set_RequestId_field(project.get_ProjectId_field() + "_R" + str(j + 1))
        rec_man.store_and_commit()

        location_rec = data_record_manager.query_system_for_record(VeloxLocationModel.DATA_TYPE_NAME, location.record_id)
        self.assertTrue(location_rec)
        rec_man = RecordModelManager(user)
        inst_man = rec_man.instance_manager
        relationship_man = rec_man.relationship_manager
        location = inst_man.add_existing_record_of_type(location_rec, VeloxLocationModel)
        relationship_man.load_path([location], RelationshipPath().child_type(VeloxDepartmentModel).descendant_type(RequestModel))
        department = location.get(Child.of_type(VeloxDepartmentModel))
        self.assertTrue(department)
        requests = department.get(Descendants.of_type(RequestModel))
        self.assertTrue(len(requests) == 3 * 4)
        for i in range(3):
            project_name = "P" + str(i+1)
            for j in range(4):
                request_id = project_name + "_R" + str(j+1)
                self.assertTrue(any(request.get_RequestId_field() == request_id for request in requests))

    def test_forward_reverse_link_paths(self):
        sample_rec = data_record_manager.add_data_record(SampleModel.get_wrapper_data_type_name())
        assay_result_rec = data_record_manager.add_data_record(ComputedAssayResultsModel.get_wrapper_data_type_name())
        assay_result_rec.set_field_value(ComputedAssayResultsModel.SAMPLESIDELINK__FIELD_NAME.field_name, sample_rec.get_record_id())
        data_record_manager.commit_data_records([sample_rec, assay_result_rec])

        rec_man = RecordModelManager(user)
        inst_man = rec_man.instance_manager
        relationship_man = rec_man.relationship_manager

        assay_result: ComputedAssayResultsModel = inst_man.add_existing_record_of_type(assay_result_rec, ComputedAssayResultsModel)
        relationship_man.load_path([assay_result], RelationshipPath().forward_side_link(ComputedAssayResultsModel.SAMPLESIDELINK__FIELD_NAME.field_name)
                                   .reverse_side_link(ComputedAssayResultsModel.get_wrapper_data_type_name(), ComputedAssayResultsModel.SAMPLESIDELINK__FIELD_NAME.field_name))
        side_sample = assay_result.get(ForwardSideLink.of(ComputedAssayResultsModel.SAMPLESIDELINK__FIELD_NAME.field_name, SampleModel))
        reverse_computed_assays: list[ComputedAssayResultsModel] = side_sample.get(ReverseSideLink.of_type(ComputedAssayResultsModel, ComputedAssayResultsModel.SAMPLESIDELINK__FIELD_NAME.field_name))
        self.assertTrue(assay_result in reverse_computed_assays and len(reverse_computed_assays) == 1)
