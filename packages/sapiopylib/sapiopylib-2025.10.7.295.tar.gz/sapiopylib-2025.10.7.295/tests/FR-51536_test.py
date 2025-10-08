import sys
import unittest

from data_type_models import *
from sapiopylib.rest.DataMgmtService import DataMgmtServer
from sapiopylib.rest.pojo.eln.ElnExperiment import InitializeNotebookExperimentPojo, ElnExperiment
from sapiopylib.rest.pojo.eln.ExperimentEntryCriteria import ElnEntryCriteria
from sapiopylib.rest.pojo.eln.SapioELNEnums import ElnEntryType
from sapiopylib.rest.utils.Protocols import ElnExperimentProtocol, ElnEntryStep
from sapiopylib.rest.utils.autopaging import *
from sapiopylib.rest.utils.recordmodel.PyRecordModel import PyRecordModel
from sapiopylib.rest.utils.recordmodel.RecordModelManager import RecordModelManager
from sapiopylib.rest.utils.recordmodel.ancestry import RecordModelAncestorManager
from sapiopylib.rest.utils.recordmodel.properties import Children, Descendants, Ancestors, Child, Parent, Parents

user = SapioUser(url="https://linux-vm:8443/webservice/api", verify_ssl_cert=False,
                 guid="66c2bea5-7cb2-4bfc-a413-304a3f4c3f33",
                 username="yqiao_api", password="Password1!")
data_record_manager = DataMgmtServer.get_data_record_manager(user)
eln_manager = DataMgmtServer.get_eln_manager(user)
rec_man = RecordModelManager(user)
inst_man = rec_man.instance_manager

class TestFR51536(unittest.TestCase):
    def test_auto_paging(self):
        # Auto paging
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        logging.getLogger().setLevel(logging.DEBUG)

        pager = QueryAllRecordsOfTypeAutoPager("Directory", user, DataRecordPojoPageCriteria(page_size=3))
        records: List[DataRecord] = pager.get_all_at_once()
        logging.info([str(x) for x in records])
        test_records = data_record_manager.query_all_records_of_type("Directory",
                                                                     DataRecordPojoPageCriteria(page_size=100000))
        self.assertEqual(records, test_records.result_list)

        # We assume there are directories that are children of other directories right now.
        children_pager = GetChildrenListAutoPager([x.record_id for x in records], "Directory",
                                                  user, DataRecordPojoHierarchyPageCriteria(page_size=3))
        children_result_map: SetMultimap[int, DataRecord] = children_pager.get_all_at_once()
        test_children_result_map: dict[int, list[DataRecord]] = data_record_manager.get_children_list(
            [x.record_id for x in records],"Directory",
            DataRecordPojoHierarchyPageCriteria(page_size=100000)).result_map
        self.assertEqual(set(children_result_map.keys()), set(test_children_result_map.keys()))
        for key in test_children_result_map.keys():
            values = set(children_result_map.get(key))
            test_values = set(test_children_result_map.get(key))
            self.assertEqual(values, test_values)

        parent_pager = GetParentsListAutoPager([x.record_id for x in records], "Directory", "Directory",
                                               user, DataRecordPojoHierarchyPageCriteria(page_size=3))
        parent_result_map: SetMultimap[int, DataRecord] = parent_pager.get_all_at_once()
        test_parent_result_map: dict[int, list[DataRecord]] = data_record_manager.get_parents_list(
            [x.record_id for x in records], "Directory", "Directory",
            DataRecordPojoHierarchyPageCriteria(page_size=100000)).result_map
        self.assertEqual(set(parent_result_map.keys()), set(test_parent_result_map.keys()))
        for key in test_parent_result_map.keys():
            values = set(parent_result_map.get(key))
            test_values = set(test_parent_result_map.get(key))
            self.assertEqual(values, test_values)

        ancestor_pager = GetAncestorsListAutoPager([x.record_id for x in records], "Directory", "Directory",
                                                   user, DataRecordPojoHierarchyPageCriteria(page_size=3))
        ancestor_result_map: SetMultimap[int, DataRecord] = ancestor_pager.get_all_at_once()
        test_ancestor_result_map: dict[int, list[DataRecord]] = data_record_manager.get_ancestors_list(
            [x.record_id for x in records], "Directory", "Directory",
            DataRecordPojoHierarchyPageCriteria(page_size=100000)).result_map
        self.assertEqual(set(ancestor_result_map.keys()), set(test_ancestor_result_map.keys()))
        for key in test_ancestor_result_map.keys():
            values = set(ancestor_result_map.get(key))
            test_values = set(test_ancestor_result_map.get(key))
            self.assertEqual(values, test_values)

        descendant_pager = GetDescendantsListAutoPager([x.record_id for x in records], "Directory",
                                                       user, DataRecordPojoHierarchyPageCriteria(page_size=10))
        descendant_result_map: SetMultimap[int, DataRecord] = descendant_pager.get_all_at_once()
        test_descendant_result_map: dict[int, list[DataRecord]] = data_record_manager.get_descendants_list(
            [x.record_id for x in records], "Directory",
            DataRecordPojoHierarchyPageCriteria(page_size=100000)).result_map
        self.assertEqual(set(descendant_result_map.keys()), set(test_descendant_result_map.keys()))
        for key in test_descendant_result_map.keys():
            values = set(descendant_result_map.get(key))
            test_values = set(test_descendant_result_map.get(key))
            self.assertEqual(values, test_values)

    def test_eln_record_paging(self):
        exp: ElnExperiment = eln_manager.create_notebook_experiment(
            InitializeNotebookExperimentPojo("Test ELN Record Paging"))
        entry = eln_manager.add_experiment_entry(exp.notebook_experiment_id, ElnEntryCriteria(
            ElnEntryType.Table, "Samples", "Sample", 2))
        samples = data_record_manager.add_data_records("Sample", 5)
        protocol = ElnExperimentProtocol(exp, user)
        sample_step = ElnEntryStep(protocol, entry)
        sample_step.add_records(samples)

        self.assertEqual(set(samples), set(sample_step.get_records()))
        pager = GetElnEntryRecordAutoPager(exp.notebook_experiment_id, entry.entry_id, user,
                                           DataRecordPojoPageCriteria(page_size=2))
        pager_records = pager.get_all_at_once()
        self.assertEqual(set(pager_records), set(samples))
        self.assertEqual(pager.cur_page, 3)

    def test_ancestor_descendants(self):
        # Test hybrid abstract type and root PyRecordModel at same time.
        level_1_samples: set[SampleModel] = set()
        level_1_samples.add(inst_man.add_new_record_of_type(SampleModel))
        level_2_samples: set[SampleModel] = set()
        level_3_samples: set[PyRecordModel] = set()
        for sample in level_1_samples:
            samples = sample.add(Children.create(SampleModel, 3))
            for x in samples:
                level_2_samples.add(x)
            for sample_2 in level_2_samples:
                samples = sample_2.add(Children.create_by_name("Sample", 3))
                for x in samples:
                    level_3_samples.add(x)
        rec_man.store_and_commit()
        descendant_samples = level_2_samples.union(level_3_samples)
        descendant_samples = inst_man.unwrap_list(descendant_samples)
        ancestor_samples: set[SampleModel] = level_1_samples.union(level_2_samples)
        ancestor_man = RecordModelAncestorManager(rec_man)
        ancestor_man.load_descendant_of_type(level_1_samples, "Sample")
        ancestor_man.load_ancestors_of_type(level_3_samples, "Sample")
        descendant_set_test = set()
        for x in level_1_samples:
            descendants = set(x.get(Descendants.of_type_name("Sample")))
            descendant_set_test = descendant_set_test.union(descendants)
        descendant_set_test = inst_man.unwrap_list(descendant_set_test)
        self.assertEqual(descendant_set_test, descendant_samples)
        ancestor_set_test = set()
        for x in level_3_samples:
            ancestors = set(x.get(Ancestors.of_type(SampleModel)))
            ancestor_set_test = ancestor_set_test.union(ancestors)
        self.assertEqual(ancestor_set_test, ancestor_samples)
        ancestor_man.load_ancestors_of_type(level_1_samples, "Sample")
        for x in level_1_samples:
            ancestors = set(x.get(Ancestors.of_type_name("Sample")))
            self.assertEqual(set(), ancestors)

    def test_new_syntax_sugars_1(self):
        parent_sample = inst_man.add_new_record_of_type(SampleModel)
        child_sample: SampleModel = parent_sample.add(Child.create(SampleModel))
        child_sample_test: SampleModel = parent_sample.get(Child.of_type(SampleModel))
        self.assertEqual(child_sample_test, child_sample)
        child_sample_root_test: PyRecordModel = parent_sample.get(Child.of_type_name("Sample"))
        self.assertEqual(child_sample_root_test, child_sample.backing_model)

        parent_sample_test: SampleModel = child_sample.get(Parent.of_type(SampleModel))
        self.assertEqual(parent_sample_test, parent_sample)
        parent_sample_root_test = child_sample.get(Parent.of_type_name("Sample"))
        self.assertEqual(parent_sample_root_test, parent_sample.backing_model)

        children_sample_test: List[SampleModel] = parent_sample.get(Children.of_type(SampleModel))
        self.assertEqual(set(children_sample_test), {child_sample})
        children_sample_root_test: List[PyRecordModel] = parent_sample.backing_model.get(Children.of_type_name("Sample"))
        self.assertEqual(set(children_sample_root_test), {child_sample.backing_model})

        parents_sample_test: List[SampleModel] = child_sample.get(Parents.of_type(SampleModel))
        self.assertEqual(set(parents_sample_test), {parent_sample})
        parents_sample_root_test: List[PyRecordModel] = child_sample.get(Parents.of_type_name("Sample"))
        self.assertEqual(set(parents_sample_root_test), {parent_sample.backing_model})

        rec_man.rollback()

    def test_syntax_sugar_2(self):
        # This tests the getter adder removers for root
        parent_sample: PyRecordModel = inst_man.add_new_record("Sample")
        children_samples = parent_sample.add(Children.create_by_name("Sample", 5))
        children_samples_test = parent_sample.get(Children.of_type_name("Sample"))
        self.assertEqual(set(children_samples_test), set(children_samples))
        parent_sample.remove(Children.refs(children_samples))
        children_samples_test = parent_sample.get(Children.of_type_name("Sample"))
        self.assertEqual(set(children_samples_test), set())
        parent_sample.add(Children.refs(children_samples))
        children_samples_test = parent_sample.get(Children.of_type_name("Sample"))
        self.assertEqual(set(children_samples_test), set(children_samples))

        rec_man.rollback()

if __name__ == '__main__':
    unittest.main()
