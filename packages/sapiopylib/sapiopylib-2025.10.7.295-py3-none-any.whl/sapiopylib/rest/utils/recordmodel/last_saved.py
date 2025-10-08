# This file is a module to add last saved functionality to record models.
from typing import Any

from buslane.events import EventHandler, E

from sapiopylib.rest.DataMgmtService import DataMgmtServer
from sapiopylib.rest.DataRecordManagerService import DataRecordManager
from sapiopylib.rest.utils.MultiMap import SetMultimap
from sapiopylib.rest.utils.recordmodel.PyRecordModel import PyRecordModel, SapioRecordModelException
from sapiopylib.rest.utils.recordmodel.RecordModelEvents import CommitEvent, RollbackEvent
from sapiopylib.rest.utils.recordmodel.RecordModelManager import RecordModelManagerBase, RecordModelManager, \
    RecordModelInstanceManager
from sapiopylib.rest.utils.recordmodel.RecordModelUtil import RecordModelUtil
from sapiopylib.rest.utils.recordmodel.RecordModelWrapper import AbstractRecordModel


class LastSavedValueManager(RecordModelManagerBase):
    """
    Manages the last saved values for easy retrieval.
    """
    _model_data_cache: dict[PyRecordModel, dict[str, Any]]

    def __init__(self, manager_context: RecordModelManager):
        super().__init__(manager_context)
        self._model_data_cache = dict()
        self.event_bus.subscribe_commit_event(_LastSavedCommitEventHandler(self))
        self.event_bus.subscribe_rollback_event(_LastSavedRollbackEventHandler(self))

    def get_last_saved_cache(self, model: PyRecordModel | AbstractRecordModel) -> dict[str, Any] | None:
        if model.is_new or model.is_new_in_sapio or model.record_id < 0:
            return None
        if not self.is_loaded(model):
            raise SapioRecordModelException("The model's last saved value cache has not yet been loaded.", model)
        return self._model_data_cache.get(RecordModelInstanceManager.unwrap(model))

    def is_loaded(self, model: PyRecordModel | AbstractRecordModel) -> bool:
        """
        Tests whether the current model has been loaded by last save value manager.
        Note: a new model automatically pass this check trivially
        """
        if model.is_new or model.is_new_in_sapio or model.record_id < 0:
            return True
        return RecordModelInstanceManager.unwrap(model) in self._model_data_cache

    def load(self, models: list[PyRecordModel | AbstractRecordModel]) -> None:
        """
        Load the last saved values so to be easily retrievable later.
        """
        all_type_to_load_list: list[PyRecordModel] = RecordModelInstanceManager.unwrap_list(
            [x for x in models if not self.is_loaded(x)])
        if not all_type_to_load_list:
            return
        to_load_by_type: SetMultimap = RecordModelUtil.multi_map_models_by_data_type_name(all_type_to_load_list)
        data_record_manager: DataRecordManager = DataMgmtServer.get_data_record_manager(self.user)
        for data_type_name in to_load_by_type.keys():
            to_load_list = to_load_by_type.get(data_type_name)
            to_load_dict_by_record_id: dict[int, PyRecordModel] = RecordModelUtil.map_model_by_record_id(to_load_list)
            record_id_to_load_list = sorted(list(to_load_dict_by_record_id.keys()))
            results_of_type = data_record_manager.get_last_saved_field_list(data_type_name, record_id_to_load_list)
            for record_id, last_saved_field_map in results_of_type.items():
                model = to_load_dict_by_record_id.get(record_id)
                if model:
                    self._model_data_cache[model] = last_saved_field_map

    def unload(self):
        """
        Unload all saved cache values for the current context.
        This should be automatically triggered by commit and rollback.
        """
        self._model_data_cache.clear()

    def get_last_saved_value(self, model: PyRecordModel | AbstractRecordModel, field_name: str) -> Any:
        """
        Get the last saved value for a particular record's field name.
        Note: requires load() to be called before use.
        """
        cache = self.get_last_saved_cache(model)
        return cache.get(field_name)

    def get_last_saved_fields(self, model: PyRecordModel | AbstractRecordModel) -> Any:
        """
        Get the last saved value clone field map for the provided record.
        Note: requires load() to be called before use.
        """
        cache = self.get_last_saved_cache(model)
        if cache is None:
            return None
        return cache.copy()


class _LastSavedCommitEventHandler(EventHandler[CommitEvent]):
    __manager: LastSavedValueManager

    def __init__(self, manager: LastSavedValueManager):
        self.__manager = manager

    def handle(self, event: E) -> None:
        self.__manager.unload()


class _LastSavedRollbackEventHandler(EventHandler[RollbackEvent]):
    __manager: LastSavedValueManager

    def __init__(self, manager: LastSavedValueManager):
        self.__manager = manager

    def handle(self, event: E) -> None:
        self.__manager.unload()
