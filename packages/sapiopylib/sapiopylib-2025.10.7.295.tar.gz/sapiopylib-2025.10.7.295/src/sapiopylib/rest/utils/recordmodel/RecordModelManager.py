from __future__ import annotations

import logging
from abc import ABC
from datetime import datetime
from typing import List, Dict, Set, Any, Tuple, Type, Optional, TypeVar, cast, Iterable
from weakref import WeakValueDictionary

from buslane.events import EventHandler

from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.DataRecord import DataRecord, DataRecordDescriptor
from sapiopylib.rest.pojo.DataRecordBatchUpdate import DataRecordBatchUpdate, DataRecordBatchResult, \
    DataRecordRelationChangePojo, DataRecordNewSideLinkPojo
from sapiopylib.rest.pojo.eln.SapioELNEnums import ElnBaseDataType
from sapiopylib.rest.utils.DataTypeCacheManager import DataTypeCacheManager
from sapiopylib.rest.utils.MultiMap import SetMultimap
from sapiopylib.rest.utils.autopaging import GetParentsListAutoPager, GetChildrenListAutoPager, \
    GetForwardSideLinkListAutoPager, GetBackSideLinkListAutoPager, QueryDataRecordByIdListAutoPager
from sapiopylib.rest.utils.recordmodel.PyRecordModel import PyRecordModel, SapioRecordModelException, \
    RecordModelReverseSideLinkCacheKey, AbstractRecordModelType
from sapiopylib.rest.utils.recordmodel.RecordModelEventBus import RecordModelEventBus
from sapiopylib.rest.utils.recordmodel.RecordModelEvents import RecordAddedEvent, RecordDeletedEvent, \
    FieldChangeEvent, ChildAddedEvent, ChildRemovedEvent, CommitEvent, RollbackEvent, SideLinkChangedEvent, \
    RecordIdAccessionEvent
from sapiopylib.rest.utils.recordmodel.RecordModelUtil import RecordModelUtil
from sapiopylib.rest.utils.recordmodel.RecordModelWrapper import WrappedType, \
    WrappedRecordModel, AbstractRecordModel
from sapiopylib.rest.utils.recordmodel.RelationshipPath import RelationshipPath, RelationshipNodeType, RelationshipNode


class RecordModelManagerBase(ABC):
    _record_model_manager: RecordModelManager

    def __init__(self, manager_context: RecordModelManager):
        if self.enforce_singleton() and manager_context.get_instance_if_exists(self.__class__):
            raise SapioRecordModelException("Singleton violation on the record model manager context for class: " +
                                            self.__class__.__name__, None)
        self._record_model_manager = manager_context

    @property
    def record_model_manager(self):
        return self._record_model_manager

    @property
    def event_bus(self):
        """
        The event bus allows the record models to fire events for various managers handling each event type.

        The default record model system already includes some system events. But you can register more event listeners.
        """
        return self._record_model_manager.event_bus

    @property
    def user(self):
        """
        The user context the record model management will provide services for.
        """
        return self._record_model_manager.user

    @classmethod
    def enforce_singleton(cls):
        """
        If set to true, if another construction for the same context is detected, an error will be raised.
        """
        return True


__MANGER_BASE_INF = TypeVar("__MANGER_BASE_INF", bound=RecordModelManagerBase)


class RecordModelManager:
    """
    Record Model Manager helps to keep track of a user session changes and attempt to batch record changes
    into one call.

    This class is observing a singleton pattern per user instance. Simply attempt to construct it with user.
    """
    _event_bus: RecordModelEventBus
    _user: SapioUser
    _singleton_managers: dict[str, RecordModelManagerBase]

    __instances: WeakValueDictionary[SapioUser, RecordModelManager] = WeakValueDictionary()
    __initialized: bool

    __dt_cache_man: DataTypeCacheManager

    def get_instance(self, clazz: Type[__MANGER_BASE_INF]) -> __MANGER_BASE_INF:
        if clazz.__name__ not in self._singleton_managers:
            obj = clazz(self)
            self._singleton_managers[clazz.__name__] = obj
        return cast(clazz, self._singleton_managers.get(clazz.__name__))

    def get_instance_if_exists(self, clazz: Type[__MANGER_BASE_INF]) -> __MANGER_BASE_INF | None:
        ret = self._singleton_managers.get(clazz.__name__)
        if ret is None:
            return ret
        return cast(clazz, self._singleton_managers.get(clazz.__name__))

    def set_instance(self, instance: __MANGER_BASE_INF, clazz: Type[__MANGER_BASE_INF]) -> None:
        self._singleton_managers[clazz.__name__] = instance

    @property
    def data_type_cache_manager(self) -> DataTypeCacheManager:
        return self.__dt_cache_man

    def __new__(cls, user: SapioUser):
        """
        Observes singleton pattern per user object.
        """
        obj = cls.__instances.get(user)
        if not obj:
            obj = object.__new__(cls)
            obj.__initialized = False
            cls.__instances[user] = obj
        return obj

    def __init__(self, user: SapioUser):
        if self.__initialized:
            return
        self._singleton_managers = dict()
        self._event_bus = RecordModelEventBus()
        self._user = user
        self.__dt_cache_man = DataTypeCacheManager(user)
        self.get_instance(RecordModelInstanceManager)
        self.get_instance(RecordModelRelationshipManager)
        self.get_instance(RecordModelTransactionManager)
        self.__initialized = True

    @property
    def event_bus(self):
        return self._event_bus

    @property
    def user(self):
        return self._user

    @property
    def ancestor_manager(self):
        """
        Get the ancestor manager for the current record model context.
        """
        from sapiopylib.rest.utils.recordmodel.ancestry import RecordModelAncestorManager
        return self.get_instance(RecordModelAncestorManager)

    @property
    def last_saved_manager(self):
        """
        Get the last saved manager to manage the last saved values for each record model.
        """
        from sapiopylib.rest.utils.recordmodel.last_saved import LastSavedValueManager
        return self.get_instance(LastSavedValueManager)

    @property
    def instance_manager(self) -> RecordModelInstanceManager:
        """
        Get the instance manager to manage the record model row-level data in the current context.
        Note: this manager is pre-initialized on construction of manager context.
        """
        return self.get_instance(RecordModelInstanceManager)

    @property
    def relationship_manager(self) -> RecordModelRelationshipManager:
        """
        Get the relationship manager to manage the relationships among record models in the current context.
        Note: this manager is pre-initialized on construction of manager context.
        """
        return self.get_instance(RecordModelRelationshipManager)

    @property
    def transaction_manager(self) -> RecordModelTransactionManager:
        """
        Get the transaction manager to manage the transactions with the server on the current context.
        Note: this manager is pre-initialized on construction of manager context.
        """
        return self.get_instance(RecordModelTransactionManager)

    def store_and_commit(self):
        return self.transaction_manager.commit()

    def rollback(self):
        return self.transaction_manager.rollback()


class RecordModelInstanceManager(RecordModelManagerBase):
    """
    Manages record model creation and retention in memory of user context.
    """

    __known_records_by_type: SetMultimap[str, PyRecordModel]
    __record_by_record_id: Dict[int, PyRecordModel]

    __delete_handler: _InstanceRecordDeletedHandler
    __rollback_handler: _InstanceRecordRollbackHandler
    __commit_handler: _InstanceRecordCommitHandler
    __record_id_accession_handler: _InstanceRecordIdAccessionHandler

    @property
    def data_type_cache_manager(self) -> DataTypeCacheManager:
        return self._record_model_manager.data_type_cache_manager

    def __init__(self, record_model_manager: RecordModelManager):
        super().__init__(record_model_manager)
        self.__known_records_by_type = SetMultimap()
        self.__record_by_record_id = dict()
        self.__delete_handler = _InstanceRecordDeletedHandler(self)
        record_model_manager.event_bus.subscribe_record_delete_event(self.__delete_handler)
        self.__rollback_handler = _InstanceRecordRollbackHandler(self)
        record_model_manager.event_bus.subscribe_rollback_event(self.__rollback_handler)
        self.__commit_handler = _InstanceRecordCommitHandler(self)
        record_model_manager.event_bus.subscribe_commit_event(self.__commit_handler)
        self.__record_id_accession_handler = _InstanceRecordIdAccessionHandler(self)
        record_model_manager.event_bus.subscribe_record_id_accession_event(self.__record_id_accession_handler)

    def _on_rollback(self):
        all_recs = set(self.__record_by_record_id.values())
        new_records: List[PyRecordModel] = [x for x in all_recs if x.is_new]
        for new_record in new_records:
            self.__known_records_by_type.discard_item(new_record.data_type_name, new_record)
            del self.__record_by_record_id[new_record.record_id]
        modified_records = self.__record_by_record_id.values()
        for modified_record in modified_records:
            modified_record.do_rollback()

    def _on_commit(self):
        all_recs = set(self.__record_by_record_id.values())
        for record in all_recs:
            record.do_commit()
            # Update for records with negative Record ID with a new reference point.
            if record.record_id not in self.__record_by_record_id:
                self.__record_by_record_id[record.record_id] = record
        # DO NOT Remove all negative record ID references we have now, for side link cache references.

    def add_new_record(self, data_type_name: str) -> PyRecordModel:
        """
        Add a new record model for a new data record.
        :param data_type_name: the data type name of the new record model
        :return: a root record model for this data type.
        """
        if ElnBaseDataType.is_base_data_type(data_type_name):
            raise SapioRecordModelException("Cannot create ELN Base data type records. "
                                            "Please reference to entry's instance data type name.", None)
        default_field_map: Dict[str, Any] = self.data_type_cache_manager.get_default_field_map(data_type_name)
        record = DataRecord(data_type_name, self.user.get_next_temp_record_id(), default_field_map, is_new=True)
        return self._get_or_add_record(record)

    def add_new_record_of_type(self, wrapper_type: Type[WrappedType]) -> WrappedType:
        """
        Add a new wrapped record model for a new data record.
        :param wrapper_type: the wrapper class (type) of the new record model
        :return: a new wrapped record model of the wrapped class type.
        """
        dt_name: str = wrapper_type.get_wrapper_data_type_name()
        py_model = self.add_new_record(dt_name)
        wrapped_model: WrappedType = RecordModelInstanceManager.wrap(py_model, wrapper_type)
        return wrapped_model

    def add_new_records(self, data_type_name: str, num_records: int) -> List[PyRecordModel]:
        """
        Add multiple record models for multiple new data records.
        :param data_type_name: the data type name of the new record models.
        :param num_records: Number of records to be added.
        :return: a list of new record models.
        """
        if ElnBaseDataType.is_eln_type(data_type_name) and ElnBaseDataType.get_base_type(
                data_type_name) == data_type_name:
            raise SapioRecordModelException("Cannot create ELN Base data type records. "
                                            "Please reference to entry's instance data type name.", None)
        ret: List[PyRecordModel] = list()
        for i in range(num_records):
            ret.append(self.add_new_record(data_type_name))
        return ret

    def add_new_records_of_type(self, num_records: int, wrapper_type: Type[WrappedType]) -> List[WrappedType]:
        """
        Add multiple wrapped record models for multiple new data records.
        :param num_records:the number of records to be added.
        :param wrapper_type: the wrapper class type
        :return: A list of new wrapped record models of wrapper class type.
        """
        ret: List[WrappedType] = list()
        for i in range(num_records):
            ret.append(self.add_new_record_of_type(wrapper_type))
        return ret

    def add_existing_record(self, record: DataRecord) -> PyRecordModel:
        """
        Import an existing data record as a record model.

        If the record model for this data record has already been imported in this record model manager, this call
        will return the existing object, instead of creating a new object.
        :param record: the data record to be imported as a record model
        :return: the imported record model singleton under the record model manager.
        """
        return self._get_or_add_record(record)

    def add_existing_record_of_type(self, record: DataRecord, wrapper_type: Type[WrappedType]) -> WrappedType:
        """
        Import an existing data record as a wrapped record model.

        If the record model for this data record has already been imported in this record model manager, this call
        will return the existing object, instead of creating a new object.
        :param record: the data record to be imported as a record model
        :param wrapper_type: the wrapper class type
        :return: the imported record model singleton wrapped by the class type.
        """
        py_model = self.add_existing_record(record)
        wrapped_model: WrappedType = RecordModelInstanceManager.wrap(py_model, wrapper_type)
        return wrapped_model

    def add_existing_records(self, record_list: List[DataRecord]) -> List[PyRecordModel]:
        """
        Import multiple existing data records as record models.

        If the record model for any record has already been imported in this record model manager, this call shall
        retrieve the existing object in its place in the list, instead of creating a new object.
        :param record_list: the data record list to be imported as record models.
        :return: the imported record model list.
        """
        return [self._get_or_add_record(record) for record in record_list]

    def add_existing_records_of_type(self, record_list: List[DataRecord], wrapper_type: Type[WrappedType]) \
            -> List[WrappedType]:
        """
        Import multiple existing data records as wrapped record models.

        If the record model for any record has already been imported in this record model manager, this call shall
        retrieve the existing object in its place in the list, instead of creating a new object.
        :param record_list: the data record list to be imported as record models.
        :param wrapper_type: the imported wrapped record model list.
        :return:
        """
        return [self.add_existing_record_of_type(record, wrapper_type) for record in record_list]

    def get_known_record_with_record_id(self, record_id: int) -> PyRecordModel | None:
        """
        Retrieve an existing root record model by providing its Record ID.
        :param record_id: the record ID used to retrieve the root record model. This can be a negative number for
        new records that has not been stored yet.
        :return: the root record model in the cache. If such a record does not exist, return None.
        """
        return self.__record_by_record_id.get(record_id)

    def get_all_known_records(self) -> set[PyRecordModel]:
        """
        Get all known records tracked in the instance manager.
        """
        return set(self.__record_by_record_id.values())

    def refresh_data_record_fields(self) -> None:
        """
        Ensure all data records have been updates with the new fields.
        """
        start = datetime.now()
        to_update = [x for x in self.get_all_known_records()
                     if not x.is_deleted and not x.is_deleted_in_sapio and x.record_id >= 0]
        user: SapioUser = self.user
        models_by_dt: SetMultimap[str, PyRecordModel] = RecordModelUtil.multi_map_models_by_data_type_name(to_update)
        for dt_name in models_by_dt.keys():
            models = models_by_dt.get(dt_name)
            record_id_list = [model.record_id for model in models]
            records: list[DataRecord] = QueryDataRecordByIdListAutoPager(dt_name, record_id_list, user).get_all_at_once()
            for record in records:
                model = self.get_known_record_with_record_id(record.record_id)
                if model is None:
                    continue
                model._backing_record = record
                for field_name, field_value in record.fields.items():
                    # noinspection PyProtectedMember
                    model._model_fields._set_field_direct(field_name, field_value)
        end = datetime.now()
        logging.info("Processed Record Model Cache Data All Refresh in " + str((end - start).total_seconds()) + " seconds. This can be disabled in transaction manager if not needed.")


    @staticmethod
    def unwrap(model: AbstractRecordModel | PyRecordModel) -> PyRecordModel:
        """
        Unwrap a record model to its root model.
        :param model: the wrapped record model
        :return: the root record model
        """
        if isinstance(model, PyRecordModel):
            return model
        return model.backing_model

    @staticmethod
    def wrap(model: AbstractRecordModel | PyRecordModel,
             wrapper_type: Type[AbstractRecordModelType]) -> AbstractRecordModelType:
        """
        Wrap the record model with a decorator type.
        :param model the root record model to wrap
        :param wrapper_type the wrapper class type to wrap to
        :return the wrapped record model object
        """
        unwrapped: PyRecordModel = RecordModelInstanceManager.unwrap(model)
        return unwrapped.wrap(wrapper_type)

    @staticmethod
    def unwrap_list(models: Iterable[AbstractRecordModel | PyRecordModel]) -> List[PyRecordModel]:
        """
        Unwrap a list of record models to its root models as another list.
        :param models list of wrapped record models, to unwrap
        :return a list of unwrapped record models in the same order.
        """
        return [RecordModelInstanceManager.unwrap(model) for model in models]

    @staticmethod
    def wrap_list(models: Iterable[AbstractRecordModel | PyRecordModel],
                  wrapper_type: Type[AbstractRecordModelType]) -> List[AbstractRecordModelType]:
        """
        Wrap a list of root record models with a wrapper type.
        :param models list of wrapped record models, to unwrap
        :param wrapper_type the type to wrap these root models to.
        """
        return [RecordModelInstanceManager.wrap(model, wrapper_type) for model in models]

    def _get_or_add_record(self, record: DataRecord):
        if record.get_record_id() in self.__record_by_record_id:
            return self.__record_by_record_id.get(record.get_record_id())
        record_model: PyRecordModel = PyRecordModel(record, self.record_model_manager)
        self.__known_records_by_type.put(record.get_data_type_name(), record_model)
        self.__record_by_record_id[record.get_record_id()] = record_model
        self.event_bus.fire_record_add_event(RecordAddedEvent(record_model))
        return record_model

    def _on_record_delete(self, model: PyRecordModel):
        """
        Internal method to fire on-delete events. Do not use.
        """
        if model.record_id in self.__record_by_record_id:
            del self.__record_by_record_id[model.record_id]
        self.__known_records_by_type.discard_value_from_all_keys(model)

    def _on_record_id_accession(self, record: PyRecordModel, record_id: int):
        """
        Internal method that handles record ID accessioning event.
        """
        self.__record_by_record_id[record_id] = record


class _InstanceRecordIdAccessionHandler(EventHandler[RecordIdAccessionEvent]):
    _inst_man: RecordModelInstanceManager

    def __init__(self, inst_man: RecordModelInstanceManager):
        self._inst_man = inst_man

    def handle(self, event: RecordIdAccessionEvent) -> None:
        # noinspection PyProtectedMember
        self._inst_man._on_record_id_accession(event.source_model, event.accessioned_record_id)


class _InstanceRecordRollbackHandler(EventHandler[RollbackEvent]):
    _inst_man: RecordModelInstanceManager

    def __init__(self, inst_man: RecordModelInstanceManager):
        self._inst_man = inst_man

    def handle(self, event: RollbackEvent) -> None:
        # noinspection PyProtectedMember
        self._inst_man._on_rollback()


class _InstanceRecordCommitHandler(EventHandler[CommitEvent]):
    _inst_man: RecordModelInstanceManager

    def __init__(self, inst_man: RecordModelInstanceManager):
        self._inst_man = inst_man

    def handle(self, event: CommitEvent) -> None:
        # noinspection PyProtectedMember
        self._inst_man._on_commit()


class _InstanceRecordDeletedHandler(EventHandler[RecordDeletedEvent]):
    _inst_man: RecordModelInstanceManager

    def __init__(self, inst_man: RecordModelInstanceManager):
        self._inst_man = inst_man

    def handle(self, event: RecordDeletedEvent) -> None:
        # noinspection PyProtectedMember
        self._inst_man._on_record_delete(event.record)


class RecordModelRelationshipManager(RecordModelManagerBase):
    """
    Manages parent-child relationships in record models.
    """
    _record_model_manager: RecordModelManager

    __side_link_handler: _RelationshipSideLinkHandler

    def __init__(self, record_model_manager: RecordModelManager):
        super().__init__(record_model_manager)
        self._record_model_manager = record_model_manager
        self.__side_link_handler = _RelationshipSideLinkHandler(self)
        self._record_model_manager.event_bus.subscribe_side_link_changed_event(self.__side_link_handler)

    def load_forward_side_links_of_type(self, wrapped_records: List[WrappedRecordModel], field_name: str):
        """
        Load forward side links from these records. This is the wrapper version.
        :param wrapped_records: The wrapped records to be loaded.
        :param field_name: The field name to be loaded for these records.
        """
        self.load_forward_side_links(RecordModelInstanceManager.unwrap_list(wrapped_records), field_name)

    def load_forward_side_links(self, records: list[PyRecordModel | AbstractRecordModel], field_name: str) -> None:
        """
        Load forward side links from these records.
        :param records: The records to be loaded.
        :param field_name: The field name to be loaded for these records.
        """
        if not records:
            return
        root_records = RecordModelInstanceManager.unwrap_list(records)
        records_by_dt_name: SetMultimap[str, PyRecordModel] = \
            RecordModelUtil.multi_map_models_by_data_type_name(root_records)
        for dt_name in records_by_dt_name:
            models_to_load: List[PyRecordModel] = list()
            models_of_type = records_by_dt_name.get(dt_name)
            for model in models_of_type:
                if model.is_deleted:
                    continue
                if model.is_forward_side_link_loaded(field_name):
                    continue
                models_to_load.append(model)
            if not models_to_load:
                continue

            records_to_query: List[DataRecord] = RecordModelUtil.get_data_record_list(models_to_load)
            records_to_query.sort()

            user = self._record_model_manager.user
            auto_pager = GetForwardSideLinkListAutoPager(records_to_query, field_name, user)
            result_map: SetMultimap[DataRecordDescriptor, DataRecord] = auto_pager.get_all_at_once()

            inst_man = self._record_model_manager.instance_manager
            for desc, links in result_map.store.items():
                source_model: PyRecordModel = inst_man.get_known_record_with_record_id(desc.record_id)
                if links:
                    link_rec: DataRecord = next(iter(links))
                    # noinspection PyProtectedMember
                    link = inst_man._get_or_add_record(link_rec)
                    # noinspection PyProtectedMember
                    source_model._mark_forward_side_link_loaded(field_name, link.record_id)
                else:
                    # noinspection PyProtectedMember
                    source_model._mark_forward_side_link_loaded(field_name, None)

    def load_reverse_side_links_of_type(self, wrapped_records: List[WrappedRecordModel],
                                        reverse_link_type: Type[WrappedRecordModel],
                                        reverse_link_field_name: str) -> None:
        """
        Load the reverse side links of provided records (wrapped records version)
        :param wrapped_records: The wrapped records to be loaded
        :param reverse_link_type: The reverse side link data type name of records that will point to these records.
        :param reverse_link_field_name: The field name on the reverse side link data type that will point
        to these records.
        :return: The records that will be linked to at least one of the records provided as input.
        """
        self.load_reverse_side_links(RecordModelInstanceManager.unwrap_list(wrapped_records),
                                     reverse_link_dt_name=reverse_link_type.get_wrapper_data_type_name(),
                                     reverse_link_field_name=reverse_link_field_name)

    def load_reverse_side_links(self, records: List[PyRecordModel | AbstractRecordModel], reverse_link_dt_name: str,
                                reverse_link_field_name: str) -> None:
        """
        Load the reverse side links of provided records
        :param records: The records to be loaded
        :param reverse_link_dt_name: The reverse side link data type name of records that will point to these records.
        :param reverse_link_field_name: The field name on the reverse side link data type that will point
        to these records.
        :return: The records that will be linked to at least one of the records provided as input.
        """
        if not records:
            return
        root_records = RecordModelInstanceManager.unwrap_list(records)
        cache_key = RecordModelReverseSideLinkCacheKey(reverse_link_dt_name, reverse_link_field_name)
        models_to_load: List[PyRecordModel] = list()
        for record in root_records:
            if record.is_deleted:
                continue
            if record.is_reverse_side_link_loaded_key(cache_key):
                continue
            models_to_load.append(record)
        if not models_to_load:
            return

        records_to_query: List[DataRecord] = RecordModelUtil.get_data_record_list(models_to_load)
        records_to_query.sort()
        auto_pager = GetBackSideLinkListAutoPager(records_to_query, reverse_link_dt_name, reverse_link_field_name,
                                                  self._record_model_manager.user)
        result_map: SetMultimap[DataRecordDescriptor, DataRecord] = auto_pager.get_all_at_once()
        inst_man = self._record_model_manager.instance_manager
        for desc, links in result_map.store.items():
            target_model: PyRecordModel = inst_man.get_known_record_with_record_id(desc.record_id)
            # noinspection PyProtectedMember
            link_models = [inst_man._get_or_add_record(x) for x in links]
            # noinspection PyProtectedMember
            target_model._mark_reverse_side_link_loaded(back_side_link_dt_name=reverse_link_dt_name,
                                                        back_side_link_field_name=reverse_link_field_name,
                                                        loaded_side_links=link_models)

    def load_children_of_type(self, wrapped_records: List[WrappedRecordModel],
                              child_wrapped_type: Type[WrappedRecordModel]) \
            -> None:
        """
        Load children that we have not traversed yet.

        This call will not do anything to models that are deleted, models that are new,
        or models with children loaded already.
        :param wrapped_records wrapped records of record model list
        :param child_wrapped_type the wrapped child class type to load for these records.
        """
        child_type_name: str = child_wrapped_type.get_wrapper_data_type_name()
        return self.load_children(RecordModelInstanceManager.unwrap_list(wrapped_records), child_type_name)

    def load_children(self, records: List[PyRecordModel | AbstractRecordModel], child_type_name: str) -> None:
        """
        Load children that we have not traversed yet.

        This call will not do anything to models that are deleted, models that are new,
        or models with children loaded already.

        :param records The records to load the child type.
        :param child_type_name the child data type name to load for these records.
        """
        root_records = RecordModelInstanceManager.unwrap_list(records)
        models_to_load_by_type: Set[PyRecordModel] = set()
        for record in root_records:
            if record.is_children_loaded(child_type_name):
                continue
            models_to_load_by_type.add(record)

        if not models_to_load_by_type:
            return

        record_id_list_to_load: List[int] = [x.record_id for x in models_to_load_by_type]
        pager: GetChildrenListAutoPager = GetChildrenListAutoPager(record_id_list_to_load, child_type_name,
                                                                   self._record_model_manager.user)
        result_map = pager.get_all_at_once()
        inst_man = self._record_model_manager.instance_manager
        for source_record_id, children_record_list in result_map.store.items():
            source_model: PyRecordModel = inst_man.get_known_record_with_record_id(source_record_id)
            children_model_list: List[PyRecordModel] = inst_man.add_existing_records(list(children_record_list))
            # noinspection PyProtectedMember
            source_model._mark_children_loaded(child_type_name, children_model_list)

    def load_parents_of_type(self, wrapped_records: List[WrappedRecordModel],
                             parent_wrapper_type: Type[WrappedRecordModel]) \
            -> None:
        """
        Load parents that we have not traversed yet.

        This call will not do anything to models that are deleted, models that are new,
        or models with parents loaded already.
        :param wrapped_records wrapped record list of record models.
        :param parent_wrapper_type the parent wrapper class type to retrieve parent records for.
        """
        return self.load_parents(RecordModelInstanceManager.unwrap_list(wrapped_records),
                                 parent_wrapper_type.get_wrapper_data_type_name())

    def load_parents(self, records: list[PyRecordModel | AbstractRecordModel], parent_type_name: str) -> None:
        """
        Load parents that we have not traversed yet.

        This call will not do anything to models that are deleted, models that are new,
        or models with parents loaded already.
        :param records record models to be load the parent type.
        :param parent_type_name the parent data type name to load.
        """
        root_records: list[PyRecordModel] = RecordModelInstanceManager.unwrap_list(records)
        models_to_load_by_type: SetMultimap[str, PyRecordModel] = SetMultimap()
        for record in root_records:
            if record.is_parents_loaded(parent_type_name):
                continue
            models_to_load_by_type.put(record.data_type_name, record)

        if not models_to_load_by_type:
            return

        inst_man = self._record_model_manager.instance_manager
        for child_type in models_to_load_by_type.keys():
            models_of_type = models_to_load_by_type.get(child_type)
            record_id_list = [x.record_id for x in models_of_type]
            pager: GetParentsListAutoPager = GetParentsListAutoPager(record_id_list, child_type, parent_type_name,
                                                                     self._record_model_manager.user)
            result_map: SetMultimap[int, DataRecord] = pager.get_all_at_once()
            for source_record_id, parent_record_list in result_map.store.items():
                source_model: PyRecordModel = inst_man.get_known_record_with_record_id(source_record_id)
                parent_model_list: List[PyRecordModel] = inst_man.add_existing_records(list(parent_record_list))
                # noinspection PyProtectedMember
                source_model._mark_parents_loaded(parent_type_name, parent_model_list)

    def load_path_of_type(self, wrapped_records: List[WrappedRecordModel], rel_path: RelationshipPath) -> None:
        """
        Load an entire path of records that we need to load along this path.
        If any parents or children for any records along this way are already loaded, it will not attempt to reload.
        :param wrapped_records: wrapped records list.
        :param rel_path: the relationship path to load.
        """
        unwrapped_records = RecordModelInstanceManager.unwrap_list(wrapped_records)
        return self.load_path(unwrapped_records, rel_path)

    def load_path(self, root_records: list[PyRecordModel | AbstractRecordModel], rel_path: RelationshipPath) -> None:
        """
        Load an entire path of records that we need to load along this path.
        If any parents or children for any records along this way are already loaded, it will not attempt to reload.
        :param root_records: root records list.
        :param rel_path: the relationship path to load.
        """
        import sapiopylib.rest.utils.recordmodel.ancestry as ancestry
        path: List[RelationshipNode] = rel_path.path
        cur_records: List[PyRecordModel] = RecordModelInstanceManager.unwrap_list(root_records)
        visited: Set[PyRecordModel] = set()
        for node in path:
            for x in cur_records:
                visited.add(x)
            direction = node.direction
            dt_name = node.data_type_name
            data_field_name = node.data_field_name
            next_records: List[PyRecordModel] = []
            if direction == RelationshipNodeType.PARENT:
                self.load_parents(cur_records, dt_name)
                for record in cur_records:
                    parents = record.get_parents_of_type(dt_name)
                    for parent in parents:
                        if parent not in next_records:
                            next_records.append(parent)
            elif direction == RelationshipNodeType.CHILD:
                self.load_children(cur_records, dt_name)
                for record in cur_records:
                    children = record.get_children_of_type(dt_name)
                    for child in children:
                        if child not in next_records:
                            next_records.append(child)
            elif direction == RelationshipNodeType.ANCESTOR:
                # Avoiding circular imports here...
                rec_man = self._record_model_manager
                ancestor_man = ancestry.RecordModelAncestorManager(rec_man)
                ancestor_man.load_ancestors_of_type(cur_records, dt_name)
                for record in cur_records:
                    ancestors = ancestor_man.get_ancestors_of_type(record, dt_name)
                    next_records.extend(ancestors)
            elif direction == RelationshipNodeType.DESCENDANT:
                # Avoiding circular imports here...
                rec_man = self._record_model_manager
                ancestor_man = ancestry.RecordModelAncestorManager(rec_man)
                ancestor_man.load_descendant_of_type(cur_records, dt_name)
                for record in cur_records:
                    descendants = ancestor_man.get_descendant_of_type(record, dt_name)
                    next_records.extend(descendants)
            elif direction == RelationshipNodeType.FORWARD_SIDE_LINK:
                self.load_forward_side_links(cur_records, data_field_name)
                for record in cur_records:
                    forward = record.get_forward_side_link(data_field_name)
                    if forward is not None:
                        next_records.append(forward)
            elif direction == RelationshipNodeType.REVERSE_SIDE_LINK:
                self.load_reverse_side_links(cur_records, dt_name, data_field_name)
                for record in cur_records:
                    backwards = record.get_reverse_side_link(dt_name, data_field_name)
                    next_records.extend(backwards)
            else:
                raise ValueError("Unsupported direction: " + direction.name)
            cur_records = list(set([x for x in next_records if x not in visited and x is not None]))


class _RelationshipSideLinkHandler(EventHandler[SideLinkChangedEvent]):
    _rel_man: RecordModelRelationshipManager

    def __init__(self, rel_man: RecordModelRelationshipManager):
        self._rel_man = rel_man

    def handle(self, event: SideLinkChangedEvent) -> None:
        source_model: PyRecordModel = event.source_model
        field_name: str = event.link_field_name
        target_record_id: Optional[int] = event.target_record_id
        # noinspection PyProtectedMember
        source_model._update_side_link_cache(field_name, target_record_id)


class RecordModelTransactionManager(RecordModelManagerBase):
    """
    Holds the transaction properties for batch calls to Sapio server.

    Attributes:
        refresh_on_store_and_commit: If true, on store and commit is called, all data records will be reloaded from server with updated values.
        This can have a signficiant performance impact if the cache is very large, but it will ensure your cache is up-to-date to latest values from server after
        evaluations of rules, on-save plugins, macros, eln formulas, accessioning, and other things.
    """
    refresh_on_store_and_commit: bool

    _records_added: List[PyRecordModel]
    _records_deleted: List[PyRecordModel]
    _records_modified: Dict[PyRecordModel, Dict[str, Any]]
    _children_added: Set[Tuple[PyRecordModel, PyRecordModel]]
    _children_removed: Set[Tuple[PyRecordModel, PyRecordModel]]
    _side_links_to_set: Dict[PyRecordModel, Dict[str, PyRecordModel]]

    __add_handler: _TransactionAddHandler
    __delete_handler: _TransactionDeletedHandler
    __field_change_handler: _TransactionFieldChangedHandler
    __add_child_handler: _TransactionChildAddedHandler
    __remove_child_handler: _TransactionChildRemovedHandler
    __side_link_changed_handler: _TransactionSideLinkChangedHandler

    def __init__(self, record_model_manager: RecordModelManager):
        super().__init__(record_model_manager)
        self.refresh_on_store_and_commit = True
        self._record_model_manager = record_model_manager
        self._records_added = []
        self._records_deleted = []
        self._records_modified = dict()
        self._children_added = set()
        self._children_removed = set()
        self._side_links_to_set = dict()
        self.__add_handler = _TransactionAddHandler(self)
        self.event_bus.subscribe_record_add_event(self.__add_handler)
        self.__delete_handler = _TransactionDeletedHandler(self)
        self.event_bus.subscribe_record_delete_event(self.__delete_handler)
        self.__field_change_handler = _TransactionFieldChangedHandler(self)
        self.event_bus.subscribe_field_change_event(self.__field_change_handler)
        self.__add_child_handler = _TransactionChildAddedHandler(self)
        self.event_bus.subscribe_child_add_event(self.__add_child_handler)
        self.__remove_child_handler = _TransactionChildRemovedHandler(self)
        self.event_bus.subscribe_child_remove_event(self.__remove_child_handler)
        self.__side_link_changed_handler = _TransactionSideLinkChangedHandler(self)
        self.event_bus.subscribe_side_link_changed_event(self.__side_link_changed_handler)

    def rollback(self) -> None:
        """
        Rollback all changes from record model cache without storing.
        """
        self._clear_cache()
        self.event_bus.fire_rollback_event()

    def _clear_cache(self):
        """
        clear all record transaction cache so nothing is being modified as of now.
        """
        self._records_added.clear()
        self._records_deleted.clear()
        self._records_modified.clear()
        self._children_added.clear()
        self._children_removed.clear()
        self._side_links_to_set.clear()

    def commit(self) -> None:
        """
        Store and commit the current changes of record model to Sapio Platform.
        These changes will become permanent.

        New records with temporary negative record IDs will be reassigned with new positive and permanent record IDs.
        """
        records_added: List[DataRecord] = []
        for model_added in self._records_added:
            decorated = DataRecord(model_added.data_type_name, model_added.record_id,
                                   model_added.fields.copy_changes_to_dict(), is_new=True)
            records_added.append(decorated)

        records_deleted: List[DataRecordDescriptor] = []
        for model_deleted in self._records_deleted:
            if model_deleted.is_new:
                continue
            decorated = DataRecordDescriptor(model_deleted.data_type_name, model_deleted.record_id)
            records_deleted.append(decorated)

        record_field_changes: List[DataRecord] = []
        for model_changed in self._records_modified:
            decorated = DataRecord(model_changed.data_type_name, model_changed.record_id,
                                   model_changed.fields.copy_changes_to_dict())
            record_field_changes.append(decorated)

        child_records_added: List[DataRecordRelationChangePojo] = []
        for parent, child in self._children_added:
            parent_desc = DataRecordDescriptor(parent.data_type_name, parent.record_id)
            child_desc = DataRecordDescriptor(child.data_type_name, child.record_id)
            child_records_added.append(DataRecordRelationChangePojo(parent_desc, child_desc))

        child_records_removed: List[DataRecordRelationChangePojo] = []
        for parent, child in self._children_removed:
            parent_desc = DataRecordDescriptor(parent.data_type_name, parent.record_id)
            child_desc = DataRecordDescriptor(child.data_type_name, child.record_id)
            child_records_removed.append(DataRecordRelationChangePojo(parent_desc, child_desc))

        side_links_for_new_records: List[DataRecordNewSideLinkPojo] = []
        for source, fields in self._side_links_to_set.items():
            for field_name, target in fields.items():
                source_desc = DataRecordDescriptor(source.data_type_name, source.record_id)
                target_desc = DataRecordDescriptor(target.data_type_name, target.record_id)
                side_links_for_new_records.append(DataRecordNewSideLinkPojo(source=source_desc,
                                                                            field_name=field_name,
                                                                            target=target_desc))

        updater = DataRecordBatchUpdate(records_added=records_added, records_deleted=records_deleted,
                                        records_fields_changed=record_field_changes,
                                        child_links_added=child_records_added,
                                        child_links_removed=child_records_removed,
                                        side_links_to_new_records=side_links_for_new_records)

        sub_path = '/datarecordlist/runbatchupdate'
        payload = updater.to_json()
        response = self._record_model_manager.user.post(sub_path, payload=payload)
        self._record_model_manager.user.raise_for_status(response)
        json_dict = response.json()

        refreshed_data: DataRecordBatchResult = DataRecordBatchResult.from_json(json_dict)
        record_updates: Dict[int, DataRecordDescriptor] = refreshed_data.added_record_updates
        inst_man: RecordModelInstanceManager = self._record_model_manager.instance_manager

        # Update side links with new record ID values for new records in destination fields.
        for source_model, field_dict in self._side_links_to_set.items():
            for field_name, target_model in field_dict.items():
                desc: DataRecordDescriptor = record_updates.get(target_model.record_id)
                if desc is None:
                    raise SapioRecordModelException("No side link target for temp record ID " +
                                                    str(target_model.record_id) + " on field name " +
                                                    field_name, source_model)
                # noinspection PyProtectedMember
                source_model._set_field_direct(field_name, desc.record_id)

        # Update record ID on record models that are new, with permanent record IDs.
        for temp_record_id, desc in record_updates.items():
            model: PyRecordModel = inst_man.get_known_record_with_record_id(temp_record_id)
            if model is not None:
                model.record_id = desc.record_id


        # Update Record Data Fields after store and commit, since the on-save may have triggered now and values may have become different.
        if self.refresh_on_store_and_commit:
            self.record_model_manager.instance_manager.refresh_data_record_fields()

        self.event_bus.fire_commit_event()
        self._clear_cache()

    def _add_field_change(self, record: PyRecordModel, field_name: str, field_value: Any):
        """
        Internal method to handle field change events. Do not use.
        """
        if record.is_new:
            return
        if record not in self._records_modified:
            self._records_modified[record] = dict()
        field_map: Dict[str, Any] = self._records_modified[record]
        field_map[field_name] = field_value

    def _on_record_delete(self, record_to_delete: PyRecordModel):
        """
        Internal method to handle record delete events. Do not use.
        """
        if record_to_delete.is_new:
            self._records_added.remove(record_to_delete)
        else:
            self._records_deleted.append(record_to_delete)

        # Side Links
        self._side_links_to_set.pop(record_to_delete, None)
        for source, fields in self._side_links_to_set.items():
            to_delete_list: List[str] = []
            for field_name, target in fields.items():
                if target == record_to_delete:
                    to_delete_list.append(field_name)
            for to_delete in to_delete_list:
                fields.pop(to_delete, None)

        # Parents and Children
        for parent, child in self._children_added.copy():
            if parent == record_to_delete:
                self._children_added.discard((parent, child))
            if child == record_to_delete:
                self._children_added.discard((parent, child))
        for parent, child in self._children_removed.copy():
            if parent == record_to_delete:
                self._children_removed.discard((parent, child))
            if child == record_to_delete:
                self._children_removed.discard((parent, child))

    def _on_record_add(self, record_to_add: PyRecordModel):
        """
        Internal method to handle record-add events. Do not use.
        """
        if record_to_add.is_new:
            self._records_added.append(record_to_add)

    def _on_child_add(self, parent_record: PyRecordModel, child_record: PyRecordModel):
        """
        Internal method to handle child-add events. Do not use.
        """
        if parent_record.is_deleted or child_record.is_deleted:
            return
        self._children_added.add((parent_record, child_record))

    def _on_child_remove(self, parent_record: PyRecordModel, child_record: PyRecordModel):
        """
        Internal method to handle child-remove events. Do not use.
        """
        if parent_record.is_deleted or child_record.is_deleted:
            return
        if (parent_record, child_record) in self._children_added:
            self._children_added.discard((parent_record, child_record))
        else:
            self._children_removed.add((parent_record, child_record))

    def _on_side_link_changed(self, source_model: PyRecordModel,
                              side_link_field_name: str, target_record_id: Optional[int]):
        if target_record_id is None or target_record_id > 0:
            return
        target_model: Optional[PyRecordModel] = self._record_model_manager.instance_manager \
            .get_known_record_with_record_id(target_record_id)
        if target_model is None:
            return
        if source_model not in self._side_links_to_set:
            self._side_links_to_set[source_model] = dict()
        self._side_links_to_set[source_model][side_link_field_name] = target_model


class _TransactionChildAddedHandler(EventHandler[ChildAddedEvent]):
    _trans_man: RecordModelTransactionManager

    def __init__(self, trans_man: RecordModelTransactionManager):
        self._trans_man = trans_man

    def handle(self, event: ChildAddedEvent) -> None:
        # noinspection PyProtectedMember
        self._trans_man._on_child_add(event.parent, event.child)


class _TransactionChildRemovedHandler(EventHandler[ChildRemovedEvent]):
    _trans_man: RecordModelTransactionManager

    def __init__(self, trans_man: RecordModelTransactionManager):
        self._trans_man = trans_man

    def handle(self, event: ChildRemovedEvent) -> None:
        # noinspection PyProtectedMember
        self._trans_man._on_child_remove(event.parent, event.child)


class _TransactionFieldChangedHandler(EventHandler[FieldChangeEvent]):
    _trans_man: RecordModelTransactionManager

    def __init__(self, trans_man: RecordModelTransactionManager):
        self._trans_man = trans_man

    def handle(self, event: FieldChangeEvent) -> None:
        record = event.record
        field_name = event.field_name
        new_value = event.new_value
        # noinspection PyProtectedMember
        self._trans_man._add_field_change(record, field_name, new_value)


class _TransactionDeletedHandler(EventHandler[RecordDeletedEvent]):
    _trans_man: RecordModelTransactionManager

    def __init__(self, trans_man: RecordModelTransactionManager):
        self._trans_man = trans_man

    def handle(self, event: RecordDeletedEvent) -> None:
        # noinspection PyProtectedMember
        self._trans_man._on_record_delete(event.record)


class _TransactionAddHandler(EventHandler[RecordAddedEvent]):
    _trans_man: RecordModelTransactionManager

    def __init__(self, trans_man: RecordModelTransactionManager):
        self._trans_man = trans_man

    def handle(self, event: RecordAddedEvent) -> None:
        # noinspection PyProtectedMember
        self._trans_man._on_record_add(event.record)


class _TransactionSideLinkChangedHandler(EventHandler[SideLinkChangedEvent]):
    _trans_man: RecordModelTransactionManager

    def __init__(self, trans_man: RecordModelTransactionManager):
        self._trans_man = trans_man

    def handle(self, event: SideLinkChangedEvent) -> None:
        # noinspection PyProtectedMember
        self._trans_man._on_side_link_changed(event.source_model, event.link_field_name, event.target_record_id)

