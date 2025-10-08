from __future__ import annotations

from typing import List, Set, Iterable, Dict

from buslane.events import EventHandler

from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.utils.MultiMap import SetMultimap
from sapiopylib.rest.utils.autopaging import GetAncestorsListAutoPager, GetDescendantsListAutoPager
from sapiopylib.rest.utils.recordmodel.PyRecordModel import PyRecordModel, AbstractRecordModel
from sapiopylib.rest.utils.recordmodel.RecordModelEvents import RecordDeletedEvent
from sapiopylib.rest.utils.recordmodel.RecordModelManager import RecordModelManager, RecordModelInstanceManager, \
    RecordModelManagerBase


class RecordModelAncestorManager(RecordModelManagerBase):
    """
    This allows loading of database ancestry for existing records only.
    This will not load any relationships still pending commit, or any relationships of new records.
    New records will always have ancestry as blank.
    """
    __delete_handler: AncestorRecordDeleteHandler

    _ancestor_multi_map: Dict[PyRecordModel, SetMultimap[str, PyRecordModel]]
    _descendant_multi_map: Dict[PyRecordModel, SetMultimap[str, PyRecordModel]]
    __initialized: bool

    def enforce_singleton(cls):
        # We have custom handling from backward compatibility via the weak dictionary
        return False

    def __new__(cls, record_model_manager: RecordModelManager):
        ret = record_model_manager.get_instance_if_exists(RecordModelAncestorManager)
        if ret is None:
            ret = object.__new__(cls)
            ret.__initialized = False
            record_model_manager.set_instance(ret, cls)
        return ret

    def __init__(self, record_model_manager: RecordModelManager):
        if not self.__initialized:
            super().__init__(record_model_manager)
            self.__delete_handler = AncestorRecordDeleteHandler(self)
            self.__initialized = True
            self._ancestor_multi_map = dict()
            self._descendant_multi_map = dict()
            self._record_model_manager.event_bus.subscribe_record_delete_event(self.__delete_handler)

    def load_ancestors_of_type(self, models_to_load: Iterable[PyRecordModel | AbstractRecordModel], ancestor_data_type: str) -> None:
        """
        Load the ancestors of the models_to_load models on the selected ancestor data type.
        :param models_to_load: The models to load ancestors
        :param ancestor_data_type: The ancestor data type name to load
        """
        actual_load_set: SetMultimap[str, PyRecordModel] = SetMultimap()
        for model in models_to_load:
            if self.is_ancestors_loaded(model, ancestor_data_type):
                continue
            actual_load_set.put(model.data_type_name, model.unwrap())
        if not actual_load_set:
            return
        user: SapioUser = self._record_model_manager.user
        inst_man: RecordModelInstanceManager = self._record_model_manager.instance_manager
        for data_type_name in actual_load_set.keys():
            records_of_type = actual_load_set.get(data_type_name)
            record_id_list: List[int] = [x.record_id for x in records_of_type]
            auto_pager = GetAncestorsListAutoPager(record_id_list, data_type_name, ancestor_data_type, user)
            result_map = auto_pager.get_all_at_once()
            for source_record_id, ancestor_records in result_map.store.items():
                source_model: PyRecordModel = inst_man.get_known_record_with_record_id(source_record_id)
                ancestor_model_list: List[PyRecordModel] = inst_man.add_existing_records(list(ancestor_records))
                if source_model not in self._ancestor_multi_map:
                    self._ancestor_multi_map[source_model] = SetMultimap()
                self._ancestor_multi_map[source_model].put_all(ancestor_data_type, ancestor_model_list)

    def is_ancestors_loaded(self, model: PyRecordModel | AbstractRecordModel, ancestor_data_type: str):
        """
        Tests whether the ancestry had been loaded or not.
        """
        model = model.unwrap()
        if model.is_new:
            return True
        return model in self._ancestor_multi_map and self._ancestor_multi_map.get(model).has_key(ancestor_data_type)

    def get_ancestors_of_type(self, model: PyRecordModel | AbstractRecordModel, ancestor_data_type: str) -> Set[PyRecordModel]:
        """
        If the model has no ancestor load yet, then throw error.
        Return model's currently known ancestors of the specified type.
        """
        model = model.unwrap()
        if not self.is_ancestors_loaded(model, ancestor_data_type):
            raise AssertionError("Model ancestor has not been loaded yet for " + str(model))
        if model.is_new:
            return set()
        multimap = self._ancestor_multi_map.get(model)
        if not multimap:
            return set()
        return multimap.get(ancestor_data_type)

    def is_descendant_loaded(self, model: PyRecordModel | AbstractRecordModel, descendant_data_type: str):
        """
        Tests whether the descendants have been loaded already for the given record model.
        :param model: The record model to test
        :param descendant_data_type: The descendant data type name to test
        """
        model = model.unwrap()
        if model.is_new:
            return True
        return (model in self._descendant_multi_map and
                self._descendant_multi_map.get(model).has_key(descendant_data_type))

    def load_descendant_of_type(self, models_to_load: Iterable[PyRecordModel | AbstractRecordModel], descendant_data_type: str) -> None:
        """
        Load descendant data type for the provided models
        :param models_to_load: The record models to load descendants.
        :param descendant_data_type: The descendant data type name
        """
        actual_load_set: Set[PyRecordModel] = set()
        for model in models_to_load:
            if self.is_descendant_loaded(model, descendant_data_type):
                continue
            actual_load_set.add(model.unwrap())
        if not actual_load_set:
            return
        user: SapioUser = self._record_model_manager.user
        inst_man: RecordModelInstanceManager = self._record_model_manager.instance_manager
        record_id_list: List[int] = [x.record_id for x in actual_load_set]
        auto_pager = GetDescendantsListAutoPager(record_id_list, descendant_data_type, user)
        result_map = auto_pager.get_all_at_once()
        for source_record_id, desc_records in result_map.store.items():
            source_model: PyRecordModel = inst_man.get_known_record_with_record_id(source_record_id)
            desc_model_list: List[PyRecordModel] = inst_man.add_existing_records(list(desc_records))
            if source_model not in self._descendant_multi_map:
                self._descendant_multi_map[source_model] = SetMultimap()
            self._descendant_multi_map[source_model].put_all(descendant_data_type, desc_model_list)

    def get_descendant_of_type(self, model: PyRecordModel | AbstractRecordModel, descendant_data_type: str) -> Set[PyRecordModel]:
        """
        If the model has no descendants load yet, then throw error.
        Return model's currently known ancestors of the specified type.
        """
        model = model.unwrap()
        if not self.is_descendant_loaded(model, descendant_data_type):
            raise AssertionError("Model descendants has not been loaded yet for " + str(model))
        if model.is_new:
            return set()
        multimap = self._descendant_multi_map.get(model)
        if not multimap:
            return set()
        return multimap.get(descendant_data_type)


class AncestorRecordDeleteHandler(EventHandler[RecordDeletedEvent]):
    _ancestor_man: RecordModelAncestorManager

    def __init__(self, ancestor_man: RecordModelAncestorManager):
        self._ancestor_man = ancestor_man

    def handle(self, event: RecordDeletedEvent) -> None:
        if not event.record:
            return
        to_remove = event.record
        # noinspection PyProtectedMember
        self._ancestor_man._ancestor_multi_map.pop(to_remove, None)
        # noinspection PyProtectedMember
        self._ancestor_man._descendant_multi_map.pop(to_remove, None)

