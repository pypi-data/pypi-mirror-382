import sys
import unittest
from io import BytesIO
from pathlib import Path
from typing import Set

from sapiopylib.rest.pojo.eln.ElnExperiment import TemplateExperimentQuery, ElnTemplate
from sapiopylib.rest.pojo.eln.SapioELNEnums import LocationAssignmentType

from sapiopylib.rest.utils.recordmodel.RelationshipPath import RelationshipPath

from sapiopylib.rest.utils.recordmodel.properties import *

from sapiopylib.rest.utils.recordmodel.RecordModelManager import RecordModelManager

from sapiopylib.rest.DataMgmtService import DataMgmtServer
from sapiopylib.rest.utils.autopaging import *
from data_type_models import *
from sapiopylib.rest.utils.recorddatasinks import InMemoryRecordDataSink

user = SapioUser(url="https://linux-vm:8443/webservice/api", verify_ssl_cert=False,
                 guid="3c232543-f407-4828-aae5-b33d4cd31fa7",
                 username="yqiao_api", password="Password1!")
data_record_manager = DataMgmtServer.get_data_record_manager(user)
data_manager = DataMgmtServer.get_data_manager(user)
eln_man = DataMgmtServer.get_eln_manager(user)
rec_man: RecordModelManager = RecordModelManager(user)
inst_man = rec_man.instance_manager
relationship_man = rec_man.relationship_manager

class PR51842Test(unittest.TestCase):
    def test_xml(self):
        root_directory: DirectoryModel = inst_man.add_existing_record_of_type(data_record_manager.query_system_for_record("Directory", 1), DirectoryModel)
        batch = root_directory.add(Child.create(BatchModel))
        for i in range(5):
            sample: SampleModel = batch.add(Child.create(SampleModel))
            sample.set_OtherSampleId_field("S" + str(i))
        rec_man.store_and_commit()

        sink = InMemoryRecordDataSink(user)
        sink.export_to_xml([batch])
        self.assertTrue(sink.data)

        target_dir_rec: DataRecord = data_record_manager.add_data_record("Directory")
        with BytesIO(sink.data) as io:
            data_manager.import_from_xml(target_dir_rec, io, False)
        target_dir: DirectoryModel = inst_man.add_existing_record_of_type(target_dir_rec, DirectoryModel)
        relationship_man.load_path_of_type([target_dir], RelationshipPath().child_type(BatchModel).child_type(SampleModel))
        batch = target_dir.get(Child.of_type(BatchModel))
        self.assertIsNotNone(batch)
        samples = batch.get(Children.of_type(SampleModel))
        self.assertTrue(len(samples) == 5)

    def test_template_info(self):
        template_list = eln_man.get_template_experiment_list(TemplateExperimentQuery(latest_version_only=True, active_templates_only=True))
        qa_template: ElnTemplate | None = None
        compound_reg_template: ElnTemplate | None = None
        for template in template_list:
            name = template.template_name
            if name == 'Compound Registration':
                compound_reg_template = template
            elif name == 'ELN Quality Control':
                qa_template = template
        self.assertIsNotNone(qa_template)
        self.assertIsNotNone(compound_reg_template)
        self.assertFalse(qa_template.modifiable)
        self.assertTrue(compound_reg_template.modifiable)
        self.assertTrue(qa_template.location_assignment_type == LocationAssignmentType.REQUIRE_ASSIGNMENT)
        self.assertTrue(compound_reg_template.location_assignment_type == LocationAssignmentType.OPTIONAL_ASSIGNMENT)
        print(qa_template.__dict__)
