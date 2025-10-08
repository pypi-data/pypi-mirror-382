from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Any, Dict, Set, Optional, TypeVar, Generic, Type, cast

from sapiopylib.rest.pojo.DataRecord import DataRecord
from sapiopylib.rest.pojo.datatype.FieldDefinition import AbstractVeloxFieldDefinition
from sapiopylib.rest.utils.DataRecordUtil import DataRecordUtil
from sapiopylib.rest.utils.DataTypeCacheManager import DataTypeCacheManager
from sapiopylib.rest.utils.MultiMap import SetMultimap


class RecordModelReverseSideLinkCacheKey:
    """
    Cache key within PyRecordModel about loaded reverse side link cache.
    """
    link_data_type_name: str
    link_data_field_name: str

    def __init__(self, link_data_type_name: str, link_data_field_name: str):
        self.link_data_type_name = link_data_type_name
        self.link_data_field_name = link_data_field_name

    def __eq__(self, other):
        if not isinstance(other, RecordModelReverseSideLinkCacheKey):
            return False
        return self.link_data_type_name == other.link_data_type_name and \
            self.link_data_field_name == other.link_data_field_name

    def __hash__(self):
        return hash((self.link_data_type_name, self.link_data_field_name))

    def __str__(self):
        return self.link_data_type_name + "." + self.link_data_field_name


class SapioRecordModelException(Exception):
    """
    This error will be thrown when record model encountered an error while using.
    """
    msg: str
    model: PyRecordModel | None

    def __init__(self, msg: str, model: PyRecordModel | None):
        self.msg = msg
        self.model = model

    def __str__(self):
        if self.model is None:
            return "Record Model Exception: " + self.msg
        else:
            return "Record Model with Record ID " + str(self.model.record_id) + ": " + self.msg

class RecordModelFieldMap:
    """
    Provides record model field map supports.

    This class provides proper views for current state of record model data in a dictionary-like access structure.

    It will also provide fire record model events when any field values are changed.

    This class supports random access. For example py_model.fields[field_name]=field_value
    """
    _model: PyRecordModel
    _model_fields: Dict[str, Any]
    _model_change_fields: Dict[str, Any]

    def __init__(self, model: PyRecordModel, model_fields: Dict[str, Any] = None):
        self._model = model
        # Always make a copy and always be non-trivial.
        if model_fields is None:
            model_fields = dict()
        else:
            model_fields = dict(model_fields)
        self._model_fields = model_fields
        self._model_change_fields = dict()

    def __getitem__(self, field_name: str) -> Any:
        if field_name and "RecordId".lower() == field_name.lower():
            return self._model.record_id
        # TI-52790 YQ: note it's intentionally using get() here for _model_fields to accept non-existence case for field name not in model.
        return self.__translate_macros(field_name, self._model_fields.get(field_name))

    def _set_field_direct(self, field_name: str, field_value: Any):
        """
        Internal method, set field without having any events firing or performing any equality checks.
        """
        self._model_fields[field_name] = field_value

    def get(self, field_name: str):
        """
        Get the value by a field name in this record model.
        Return None if this field does not exist.
        """
        return self.__getitem__(field_name)

    def __setitem__(self, field_name: str, field_value: Any):
        old_value = self._model_fields.get(field_name)
        if old_value == field_value:
            return
        self._model_fields[field_name] = field_value
        self._model_change_fields[field_name] = field_value
        from sapiopylib.rest.utils.recordmodel.RecordModelEvents import FieldChangeEvent
        self._model.record_model_manager.event_bus.fire_field_change_event(FieldChangeEvent(
            self._model, field_name, old_value, field_value))
        # Handle for side links.
        dt_cache_man: DataTypeCacheManager = self._model.record_model_manager.data_type_cache_manager
        if dt_cache_man.is_side_link_field(self._model.data_type_name, field_name):
            if field_value is None:
                self._model.record_model_manager.event_bus.fire_side_link_changed_event(self._model, field_name, None)
            else:
                target_record_id: int = int(field_value)
                self._model.record_model_manager.event_bus.fire_side_link_changed_event(self._model,
                                                                                        field_name, target_record_id)

    def __delitem__(self, field_name: str):
        if field_name not in self._model_fields:
            return
        old_value = self._model_fields.get(field_name)
        del self._model_fields[field_name]
        if field_name in self._model_change_fields:
            del self._model_change_fields[field_name]
        from sapiopylib.rest.utils.recordmodel.RecordModelEvents import FieldChangeEvent
        self._model.record_model_manager.event_bus.fire_field_change_event(FieldChangeEvent(
            self._model, field_name, old_value, None))

    def __hash__(self):
        return hash((self._model, self._model_fields))

    def __eq__(self, other):
        if not isinstance(other, RecordModelFieldMap):
            return False
        return self._model == other._model and self._model_fields == other._model_fields

    def __str__(self):
        return str(self._model_fields)

    def __iter__(self):
        return self._model_fields.__iter__()

    def items(self):
        """
        Return a set-like object with tuples in iterator.
        """
        return self._model_fields.items()

    def copy_to_dict(self) -> dict:
        """
        Copy current state of the data into a dictionary. The copy will not modify the current record model's state.
        """
        return dict(self._model_fields)

    def copy_changes_to_dict(self) -> dict:
        """
        Copy the fields that are changed into a dictionary.
        """
        return dict(self._model_change_fields)

    def on_commit(self):
        self._model_change_fields = dict()

    def __translate_macros(self, field_name: str, value: Any) -> Any:
        """
        Handle translations of server macros temporarily so user is getting a consistent typing for the values even though final value hasn't evaluated yet.
        :param field_name: The field name to translate macros for.
        :param value: The value to be translated.
        :return: Translated macro, or original value if no need for translation.
        """
        if not self._model.is_new and not self._model.is_new_in_sapio:
            return value
        if value is None:
            return None
        if not isinstance(value, str):
            return value
        fields_by_name:  dict[str, AbstractVeloxFieldDefinition] = self._model.record_model_manager.data_type_cache_manager.get_fields_for_type(self._model.data_type_name)
        if fields_by_name is None:
            return None
        field: AbstractVeloxFieldDefinition | None = fields_by_name.get(field_name)
        user = self._model.record_model_manager.user
        return DataRecordUtil.interpret_macro_for_default_value(value, field, user)


class PyRecordModel:
    """
    A record model instance that is backed by a data record.
    """
    _backing_record: DataRecord
    _model_fields: RecordModelFieldMap
    __is_deleted: bool
    __object_id: int

    _children_types_loaded: Set[str]
    _parent_types_loaded: Set[str]
    _children_models_by_type: SetMultimap[str, PyRecordModel]
    _parent_models_by_type: SetMultimap[str, PyRecordModel]
    _forward_side_link_cache: Dict[str, Optional[int]]
    _loaded_forward_side_link_field_names: Set[str]
    _reverse_side_link_cache: SetMultimap[RecordModelReverseSideLinkCacheKey, PyRecordModel]
    _loaded_reverse_side_links: Set[RecordModelReverseSideLinkCacheKey]

    _non_loaded_removed_parents: Set[PyRecordModel]
    _non_loaded_removed_children: Set[PyRecordModel]
    _non_loaded_removed_forward_links: Set[str]
    _non_loaded_removed_reverse_links: SetMultimap[RecordModelReverseSideLinkCacheKey, PyRecordModel]

    _known_wrappings_by_class_name: dict[str, AbstractRecordModel]

    def __str__(self):
        return self.data_type_name + " " + str(self.record_id) + ": " + str(self.fields)

    def __repr__(self):
        return self.__str__()

    def __init__(self, backing_record: DataRecord, record_model_manager):
        self._backing_record = backing_record
        self._model_fields = RecordModelFieldMap(self, backing_record.get_fields())
        self._record_model_manager = record_model_manager
        self.__is_deleted = False
        self._children_types_loaded = set()
        self._parent_types_loaded = set()
        self._children_models_by_type = SetMultimap()
        self._parent_models_by_type = SetMultimap()
        self._forward_side_link_cache = dict()
        self._loaded_forward_side_link_field_names = set()
        self._reverse_side_link_cache = SetMultimap()
        self._loaded_reverse_side_links = set()
        self._non_loaded_removed_parents = set()
        self._non_loaded_removed_children = set()
        self._non_loaded_removed_forward_links = set()
        self._non_loaded_removed_reverse_links = SetMultimap()
        self.__object_id = self._backing_record.record_id
        self._known_wrappings_by_class_name = dict()

    def __hash__(self):
        return self.__object_id.__hash__()

    def __eq__(self, other):
        if not isinstance(other, PyRecordModel):
            return False
        return self._backing_record.__eq__(other._backing_record)

    def unwrap(self):
        """
        The java concept of unwrap on root record model will just return itself.
        """
        return self

    def wrap(self, wrap_type: Type[AbstractRecordModelType]) -> AbstractRecordModelType:
        """
        Wrap the current object as a wrapped object.
        If the object has already been wrapped before, simply retrieve its reference.
        """
        if wrap_type.__name__ in self._known_wrappings_by_class_name:
            return self._known_wrappings_by_class_name.get(wrap_type.__name__)
        ret: AbstractRecordModelType = wrap_type(self)
        self._known_wrappings_by_class_name[wrap_type.__name__] = ret
        return ret

    @property
    def record_id(self) -> int:
        """
        The record ID of the current model.
        It is possible for this number to be negative, if it is a new record.
        """
        return self._backing_record.record_id

    @record_id.setter
    def record_id(self, record_id: int) -> None:
        """
        Record ID on record model will be reset when the added record is now living permanently in Sapio DB.

        This is internal method and should not be used outside
        """
        if self.record_id >= 0:
            raise SapioRecordModelException('Cannot replace record ID when the current ID is non-negative.', self)
        self._backing_record.record_id = record_id
        self.record_model_manager.event_bus.fire_record_id_accession_event(self, record_id)

    @property
    def is_deleted_in_sapio(self) -> bool:
        """
        Tests whether the backing DataRecord object is flagged as deleted in Sapio.
        """
        return self._backing_record.is_deleted

    @property
    def is_new_in_sapio(self) -> bool:
        """
        Tests whether the backing DataRecord object is flagged as new in Sapio.
        """
        return self._backing_record.is_new

    @property
    def is_deleted(self) -> bool:
        """
        Test whether this record is flagged for deletion.
        """
        return self.__is_deleted

    @property
    def is_new(self) -> bool:
        """
        Tests whether this is a new record that has not been stored in Sapio yet.
        """
        return self._backing_record.get_record_id() < 0

    @property
    def fields(self) -> RecordModelFieldMap:
        """
        The field map of the record model, which could include cached changed not committed to data record.
        """
        return self._model_fields

    @property
    def data_type_name(self) -> str:
        """
        The data type name of this record model.
        """
        return self._backing_record.get_data_type_name()

    def is_children_loaded(self, child_type_name: str) -> bool:
        """
        Tests whether the children for this model has been loaded already.
        """
        return self.is_deleted or self.is_new or (child_type_name in self._children_types_loaded)

    def is_parents_loaded(self, parent_type_name: str) -> bool:
        """
        Tests whether the parents for this model has been loaded already.
        """
        return self.is_deleted or self.is_new or (parent_type_name in self._parent_types_loaded)

    def is_forward_side_link_loaded(self, field_name: str):
        """
        Tests whether a particular field name's forward side links has been loaded to record model.
        """
        if self.is_new:
            return True
        return field_name in self._loaded_forward_side_link_field_names

    def is_reverse_side_link_loaded(self, back_link_dt_name: str, back_link_field_name: str):
        """
         Tests whether a backwards side link can be retrieved right now or not.
         If it is not ready then we need to load it first.
        """
        return self.is_reverse_side_link_loaded_key(RecordModelReverseSideLinkCacheKey(
            link_data_type_name=back_link_dt_name, link_data_field_name=back_link_field_name))

    def is_reverse_side_link_loaded_key(self, key: RecordModelReverseSideLinkCacheKey):
        """
        Tests whether a backwards side link can be retrieved right now or not.
         If it is not ready then we need to load it first.
        """
        if self.is_new:
            return True
        return key in self._loaded_reverse_side_links

    def _mark_children_loaded(self, child_type_name: str, children_loaded: List[PyRecordModel]) -> None:
        """
        When record model management finishes loading children for this instance, it calls this method to update the
        children list.

        This is an internal method for record model.
        :param child_type_name: The child type for which we have just loaded for this instance.
        :param children_loaded: The loaded children record models for this instance.
        """
        self._children_types_loaded.add(child_type_name)
        for child in children_loaded:
            if child in self._non_loaded_removed_children:
                continue
            self._children_models_by_type.put(child_type_name, child)

    def _mark_parents_loaded(self, parent_type_name: str, parents_loaded: List[PyRecordModel]) -> None:
        """
        When record model management finishes loading parents for this instance, it calls this method to update the
        parents list.

        This is an internal method for record model.
        :param parent_type_name: The parent type for which we have just loaded for this instance.
        :param parents_loaded: The loaded parent record models for this instance.
        """
        self._parent_types_loaded.add(parent_type_name)
        for parent in parents_loaded:
            if parent in self._non_loaded_removed_parents:
                continue
            self._parent_models_by_type.put(parent_type_name, parent)

    def _mark_forward_side_link_loaded(self, field_name: str, target_record_id: Optional[int]):
        """
        Load a forward link for a particular field name and mark the field as loaded for this record.
        """
        # Mark as loaded
        self._loaded_forward_side_link_field_names.add(field_name)
        # Update cache data
        if target_record_id is not None and field_name in self._non_loaded_removed_forward_links:
            self._forward_side_link_cache[field_name] = None
            self._non_loaded_removed_forward_links.remove(field_name)
        else:
            self._forward_side_link_cache[field_name] = target_record_id

    def _mark_reverse_side_link_loaded(self, back_side_link_dt_name: str,
                                       back_side_link_field_name: str, loaded_side_links: List[PyRecordModel]):
        """
        Load a reverse link for a particular data type and field name and mark this key as loaded.
        """
        # Mark as loaded
        cache_key = RecordModelReverseSideLinkCacheKey(link_data_type_name=back_side_link_dt_name,
                                                       link_data_field_name=back_side_link_field_name)
        self._loaded_reverse_side_links.add(cache_key)
        # Update cache data
        removed_reverse_links: Set[PyRecordModel] = self._non_loaded_removed_reverse_links.get(cache_key)
        actual_loaded_side_links: List[PyRecordModel] = [x for x in loaded_side_links if x not in removed_reverse_links]
        self._reverse_side_link_cache.put_all(cache_key, actual_loaded_side_links)
        self._non_loaded_removed_reverse_links.remove_all(cache_key)

    def get_field_value(self, field_name: str) -> Any:
        """
        Get the model's field value for a field
        """
        return self._model_fields.get(field_name)

    def get_record_field_value(self, field_name: str) -> Any:
        """
        Get the backing record's field value for a field.
        """
        return self._backing_record.get_field_value(field_name)

    def get_data_record(self) -> DataRecord:
        """
        Get the backing data record for this record model instance.
        """
        return self._backing_record

    def add_parent(self, parent_model: AbstractRecordModel | PyRecordModel | None, fire_events: bool = True) -> None:
        """
        Add a record model as a parent for this record model.
        """
        if parent_model is None:
            return
        parent_record: PyRecordModel = _unwrap(parent_model)
        self._parent_models_by_type.put(parent_record.data_type_name, parent_record)
        if fire_events:
            parent_record.add_child(self, fire_events=False)
            from sapiopylib.rest.utils.recordmodel.RecordModelEvents import ChildAddedEvent
            self.record_model_manager.event_bus.fire_child_add_event(ChildAddedEvent(parent_record, self))

    def add_parents(self, parent_records: List[AbstractRecordModel | PyRecordModel | None]) -> None:
        """
        Add multiple record models as parents for this record model.
        """
        for parent_record in parent_records:
            self.add_parent(parent_record)

    def remove_parent(self, parent_model: AbstractRecordModel | PyRecordModel | None, fire_events: bool = True) -> None:
        """
        Remove a parent relation from this record model.
        """
        if parent_model is None:
            return
        parent_record: PyRecordModel = _unwrap(parent_model)
        self._parent_models_by_type.get(parent_record.data_type_name).discard(parent_record)
        if not self.is_parents_loaded(parent_record.data_type_name):
            self._non_loaded_removed_parents.add(parent_record)
        if fire_events:
            parent_record.remove_child(self, fire_events=False)
            from sapiopylib.rest.utils.recordmodel.RecordModelEvents import ChildRemovedEvent
            self.record_model_manager.event_bus.fire_child_remove_event(ChildRemovedEvent(parent_record, self))

    def remove_parents(self, parent_records: List[AbstractRecordModel | PyRecordModel | None]) -> None:
        """
        Remove multiple parent relations from this record model.
        """
        for parent_record in parent_records:
            self.remove_parent(parent_record)

    def add_child(self, child_model: AbstractRecordModel | PyRecordModel | None, fire_events: bool = True) -> None:
        """
        Add a child record model for this record model.
        """
        if child_model is None:
            return None
        child_record: PyRecordModel = _unwrap(child_model)
        self._children_models_by_type.put(child_record.data_type_name, child_record)
        if fire_events:
            child_record.add_parent(self, fire_events=False)
            from sapiopylib.rest.utils.recordmodel.RecordModelEvents import ChildAddedEvent
            self.record_model_manager.event_bus.fire_child_add_event(ChildAddedEvent(self, child_record))

    def add_children(self, children_records: List[AbstractRecordModel | PyRecordModel | None]) -> None:
        """
        Add multiple children record model for this record model.
        """
        for child_record in children_records:
            self.add_child(child_record)

    def remove_child(self, child_model: AbstractRecordModel | PyRecordModel | None, fire_events: bool = True) -> None:
        """
        Remove a child record model relation from this record model.
        """
        if child_model is None:
            return None
        child_record: PyRecordModel = _unwrap(child_model)
        if not self.is_children_loaded(child_record.data_type_name):
            self._non_loaded_removed_children.add(child_record)
        self._children_models_by_type.get(child_record.data_type_name).discard(child_record)
        if fire_events:
            child_record.remove_parent(self, fire_events=False)
            from sapiopylib.rest.utils.recordmodel.RecordModelEvents import ChildRemovedEvent
            self.record_model_manager.event_bus.fire_child_remove_event(ChildRemovedEvent(self, child_record))

    def remove_children(self, children_records: List[PyRecordModel]) -> None:
        """
        Remove multiple children record model relations from this record model.
        """
        for child_record in children_records:
            self.remove_child(child_record)

    def set_side_link(self, field_name: str,
                      link_to_record: Optional[AbstractRecordModel | PyRecordModel | None]) -> None:
        """
        Change the forward side link on this record's field to another record.
        """
        if link_to_record is None:
            self.set_field_value(field_name, None)
            return
        link_to: PyRecordModel = _unwrap(link_to_record)
        if link_to.is_new:
            self.record_model_manager.event_bus.fire_side_link_changed_event(self, field_name, link_to.record_id)
        else:
            self.set_field_value(field_name, link_to.record_id)

    def delete(self) -> None:
        """
        Flag the current record model to be deleted on commit.
        """
        from sapiopylib.rest.utils.recordmodel.RecordModelEvents import RecordDeletedEvent
        self.__is_deleted = True
        self.record_model_manager.event_bus.fire_record_delete_event(RecordDeletedEvent(self))

    def _set_field_direct(self, field_name: str, field_value: Any) -> None:
        """
        Set field directly without firing an event or perform equality check. This is an internal method.
        """
        # noinspection PyProtectedMember
        self._model_fields._set_field_direct(field_name, field_value)

    def set_field_value(self, field_name: str, field_value: Any) -> None:
        """
        Set a current record model's field value to a new value.
        """
        self._model_fields[field_name] = field_value

    def set_field_values(self, field_change_map: Dict[str, Any]) -> None:
        """
        Set multiple field values for this record model to new values.
        """
        for key, value in field_change_map.items():
            self.set_field_value(key, value)

    def get_parents_of_type(self, parent_type_name: str) -> List[PyRecordModel]:
        """
        Get all parents for a particular data type name for this record model.
        """
        if not self.is_parents_loaded(parent_type_name):
            raise SapioRecordModelException("Parent type " + parent_type_name + " was not loaded.", self)
        return list(self._parent_models_by_type.get(parent_type_name))

    def get_children_of_type(self, child_type_name: str) -> List[PyRecordModel]:
        """
        Get all children for a particular data type name for this record model.
        """
        if not self.is_children_loaded(child_type_name):
            raise SapioRecordModelException("Child type " + child_type_name + " was not loaded.", self)
        return list(self._children_models_by_type.get(child_type_name))

    def get_parent_of_type(self, parent_type_name: str) -> Optional[PyRecordModel]:
        """
        Obtains the parent of the current record of the provided data type name.
        If the parent is not found, return None.
        If there are more than one parent exists, then we will throw an exception.
        """
        parents = self.get_parents_of_type(parent_type_name)
        if not parents:
            return None
        if len(parents) > 1:
            raise SapioRecordModelException("Too many parent records of type " + parent_type_name, self)
        return parents[0]

    def get_child_of_type(self, child_type_name: str) -> Optional[PyRecordModel]:
        """
        Obtains the only child of the current record of the provided data type name.
        If the child is not found, return None.
        If there are more than one child exists, then we will throw an exception.
        """
        children = self.get_children_of_type(child_type_name)
        if not children:
            return None
        if len(children) > 1:
            raise SapioRecordModelException("Too many child records of type " + child_type_name, self)
        return children[0]

    def get_forward_side_link(self, field_name: str) -> Optional[PyRecordModel]:
        """
        Get the current forward side links. If the side links have not been loaded, throw an exception.
        :param field_name: The forward link field on this record to load its reference for.
        """
        if not self.is_forward_side_link_loaded(field_name):
            raise SapioRecordModelException("Forward link on field " + field_name + " was not loaded.", self)
        target_record_id: Optional[int] = self._forward_side_link_cache.get(field_name)
        if target_record_id is None:
            return None
        ret: Optional[PyRecordModel] = self.record_model_manager.instance_manager. \
            get_known_record_with_record_id(target_record_id)
        if ret is None:
            raise SapioRecordModelException("Forward link on field " + field_name + " was not loaded.", self)
        return ret

    def get_reverse_side_link(self, reverse_side_link_data_type_name: str, reverse_side_link_field_name: str) \
            -> List[PyRecordModel]:
        """
        Get currently loaded reverse side link models. This will throw exception if it has not been loaded before.
        """
        cache_key = RecordModelReverseSideLinkCacheKey(link_data_type_name=reverse_side_link_data_type_name,
                                                       link_data_field_name=reverse_side_link_field_name)
        if not self.is_reverse_side_link_loaded_key(cache_key):
            raise SapioRecordModelException("Reverse link on field " + reverse_side_link_data_type_name +
                                            "." + reverse_side_link_field_name + " was not loaded.", self)
        return list(self._reverse_side_link_cache.get(cache_key))

    def get(self, getter: AbstractRecordModelPropertyGetter[RecordModelPropertyType]) \
            -> Optional[RecordModelPropertyType]:
        """
        Obtain a specific record model property. This is a java-like syntax sugar for users used the old record models.
        """
        return getter.get_value(self)

    def add(self, adder: AbstractRecordModelPropertyAdder[RecordModelPropertyType]) -> RecordModelPropertyType:
        """
        Add a value to a property, assuming the property itself is an iterable type.
        """
        return adder.add_value(self)

    def remove(self, remover: AbstractRecordModelPropertyRemover[RecordModelPropertyType]) -> RecordModelPropertyType:
        """
        Remove a value from a property, assuming the property itself is an iterable type.
        """
        return remover.remove_value(self)

    def set(self, setter: AbstractRecordModelPropertySetter[RecordModelPropertyType]) -> RecordModelPropertyType:
        """
        Set a value onto a record model property.
        """
        return setter.set_value(self)

    def _update_side_link_cache(self, field_name, target_record_id: Optional[int]) -> None:
        """
        Update the side link cache so that both sides are consistent. This should only be called from forward direction.
        :param field_name: The field name of which the side link cache has been modified on this record.
        :param target_record_id: The new target record ID linked on the field.
        """
        cache_key = RecordModelReverseSideLinkCacheKey(self.data_type_name, field_name)
        old_side_link: Optional[PyRecordModel] = self.get_forward_side_link(field_name)
        # Update forward links
        self._mark_forward_side_link_loaded(field_name, target_record_id)
        # Update reverse links
        if old_side_link is not None:
            old_side_link._reverse_side_link_cache.pop(cache_key, None)
            if not old_side_link.is_reverse_side_link_loaded_key(cache_key):
                old_side_link._non_loaded_removed_reverse_links.put(cache_key, self)
        if target_record_id:
            new_target_model: Optional[PyRecordModel] = self. \
                record_model_manager.instance_manager.get_known_record_with_record_id(target_record_id)
            if new_target_model is not None:
                new_target_model._reverse_side_link_cache.put(cache_key, self)

    def do_rollback(self):
        """
        This method is called by instance manager for referencable record models when a rollback event is fired.
        This is an internal method.
        """
        self.__is_deleted = False
        self._model_fields = RecordModelFieldMap(self, self._backing_record.fields)
        self._non_loaded_removed_parents.clear()
        self._non_loaded_removed_children.clear()
        self._children_types_loaded.clear()
        self._parent_types_loaded.clear()
        self._children_models_by_type.clear()
        self._parent_models_by_type.clear()

    def do_commit(self):
        """
        This method is called by instance manager for referencable record models when a commit event is fired.
        This is an internal method.
        """
        if self.__is_deleted:
            return
        self._backing_record.set_fields(self.fields.copy_changes_to_dict())
        self._backing_record.commit_changes()
        self._model_fields.on_commit()

    @property
    def record_model_manager(self):
        from sapiopylib.rest.utils.recordmodel.RecordModelManager import RecordModelManager
        return cast(RecordModelManager, self._record_model_manager)


RecordModelPropertyType = TypeVar("RecordModelPropertyType")


class AbstractRecordModelPropertyGetter(Generic[RecordModelPropertyType], ABC):
    """
    This is a syntax sugar to make record model behave like our Java version of record models.
    The actual methods are accessible elsewhere if you prefer to call them directly.
    Subclasses of this allows return of a record model's property.
    """

    @abstractmethod
    def get_value(self, model: PyRecordModel) -> Optional[RecordModelPropertyType]:
        pass


class AbstractRecordModelPropertyAdder(Generic[RecordModelPropertyType], ABC):
    """
    Add value to a property
    """

    @abstractmethod
    def add_value(self, add_to: PyRecordModel) -> RecordModelPropertyType:
        pass


class AbstractRecordModelPropertyRemover(Generic[RecordModelPropertyType], ABC):
    """
    Remove value from a property
    """

    @abstractmethod
    def remove_value(self, remove_from: PyRecordModel) -> RecordModelPropertyType:
        pass


class AbstractRecordModelPropertySetter(Generic[RecordModelPropertyType], ABC):
    """
    Set value to a property
    """

    @abstractmethod
    def set_value(self, set_to: PyRecordModel) -> RecordModelPropertyType:
        pass


class AbstractRecordModel(ABC):
    """
    An abstract record model is always backed by a root PyRecordModel and can contain additional data under its model.
    The data is often managed by a manager if there are any.
    On the other hand, it can also be a pure syntax sugar with no additional data (Such as WrappedRecordModel)
    """
    _backing_model: PyRecordModel

    def __init__(self, backing_model: PyRecordModel):
        self._backing_model = backing_model

    def __hash__(self):
        return hash(self._backing_model)

    def __eq__(self, other):
        if not isinstance(other, AbstractRecordModel):
            return False
        return self._backing_model == other._backing_model

    def __str__(self):
        return str(self._backing_model)

    def __repr__(self):
        return self.__str__()

    @property
    def backing_model(self):
        """
        The base model is the root model backing the decorated type.
        """
        return self._backing_model

    @property
    def record_id(self) -> int:
        """
        The system-unique Record ID for this record. It is possible for this to be a negative number for new records.
        """
        return self._backing_model.record_id

    @property
    def is_deleted(self) -> bool:
        """
        Test whether this record is flagged for deletion.
        """
        return self._backing_model.is_deleted

    @property
    def is_new(self) -> bool:
        """
        Tests whether this is a new record that has not been stored in Sapio yet.
        """
        return self._backing_model.is_new

    @property
    def fields(self) -> RecordModelFieldMap:
        """
        The field map of the record model, which could include cached changed not committed to data record.
        """
        return self._backing_model.fields

    @property
    def data_type_name(self) -> str:
        """
        The data type name of this record model.
        """
        return self._backing_model.data_type_name

    def wrap(self, wrap_type: Type[AbstractRecordModelType]) -> AbstractRecordModelType:
        """
        Wrap again the current record model into another type.
        """
        return self.backing_model.wrap(wrap_type)

    def unwrap(self):
        """
        This is the java's record model terminology. It is basically obtaining the backing root model.
        """
        return self.backing_model

    def get_field_value(self, field_name: str) -> Any:
        """
        Get the model's field value for a field
        """
        return self._backing_model.get_field_value(field_name)

    def get_record_field_value(self, field_name: str) -> Any:
        """
        Get the backing record's field value for a field.
        """
        return self._backing_model.get_record_field_value(field_name)

    def get_data_record(self) -> DataRecord:
        """
        Get the backing data record for this record model instance.
        """
        return self._backing_model.get_data_record()

    def add_parent(self, parent_record: AbstractRecordModel | PyRecordModel | None) -> None:
        """
        Add a record model as a parent for this record model.
        """
        if parent_record is None:
            return
        return self.backing_model.add_parent(_unwrap(parent_record))

    def add_parents(self, parent_records: List[AbstractRecordModel | PyRecordModel | None]) -> None:
        """
        Add multiple record models as parents for this record model.
        """
        for record in parent_records:
            self.add_parent(record)

    def remove_parent(self, parent_record: AbstractRecordModel | PyRecordModel | None) -> None:
        """
        Remove a parent relation from this record model.
        """
        if parent_record is None:
            return
        return self.backing_model.remove_parent(_unwrap(parent_record))

    def remove_parents(self, parent_records: List[AbstractRecordModel | PyRecordModel | None]) -> None:
        """
        Remove multiple parent relations from this record model.
        """
        for record in parent_records:
            self.remove_parent(record)

    def add_child(self, child_record: AbstractRecordModel | PyRecordModel | None) -> None:
        """
        Add a child record model for this record model.
        """
        if child_record is None:
            return
        return self.backing_model.add_child(_unwrap(child_record))

    def add_children(self, children_records: List[AbstractRecordModel | PyRecordModel | None]) -> None:
        """
        Add multiple children record model for this record model.
        """
        for record in children_records:
            self.add_child(record)

    def remove_child(self, child_record: AbstractRecordModel | PyRecordModel | None) -> None:
        """
        Remove a child record model relation from this record model.
        """
        if child_record is None:
            return
        return self.backing_model.remove_child(_unwrap(child_record))

    def remove_children(self, children_records: List[AbstractRecordModel | PyRecordModel | None]) -> None:
        """
        Remove multiple children record model relations from this record model.
        """
        for record in children_records:
            self.remove_child(record)

    def set_side_link(self, field_name: str, link_to: Optional[AbstractRecordModel | PyRecordModel | None]) -> None:
        """
        Change the forward side link on this record's field to another record.
        """
        if link_to is None:
            self.backing_model.set_side_link(field_name, None)
        else:
            self.backing_model.set_side_link(field_name, _unwrap(link_to))

    def delete(self) -> None:
        """
        Flag the current record model to be deleted on commit.
        """
        return self._backing_model.delete()

    def set_field_value(self, field_name: str, field_value: Any) -> None:
        """
        Set a current record model's field value to a new value.
        """
        return self._backing_model.set_field_value(field_name, field_value)

    def set_field_values(self, field_change_map: Dict[str, Any]) -> None:
        """
        Set multiple field values for this record model to new values.
        """
        return self._backing_model.set_field_values(field_change_map)

    def get(self, getter: AbstractRecordModelPropertyGetter[RecordModelPropertyType]) \
            -> Optional[RecordModelPropertyType]:
        """
        Obtain a specific record model property. This is a java-like syntax sugar for users used the old record models.
        """
        return getter.get_value(self._backing_model)

    def add(self, adder: AbstractRecordModelPropertyAdder[RecordModelPropertyType]) -> RecordModelPropertyType:
        """
        Add a value to a property, assuming the property itself is an iterable type.
        """
        return adder.add_value(self._backing_model)

    def remove(self, remover: AbstractRecordModelPropertyRemover[RecordModelPropertyType]) -> RecordModelPropertyType:
        """
        Remove a value from a property, assuming the property itself is an iterable type.
        """
        return remover.remove_value(self._backing_model)

    def set(self, setter: AbstractRecordModelPropertySetter[RecordModelPropertyType]) -> RecordModelPropertyType:
        """
        Set a value onto a record model property.
        """
        return setter.set_value(self._backing_model)

    @property
    def is_deleted_in_sapio(self) -> bool:
        """
        Tests whether the backing DataRecord object is flagged as deleted in Sapio.
        """
        return self.backing_model.is_deleted_in_sapio

    @property
    def is_new_in_sapio(self) -> bool:
        """
        Tests whether the backing DataRecord object is flagged as new in Sapio.
        """
        return self.backing_model.is_new_in_sapio


AbstractRecordModelType = TypeVar("AbstractRecordModelType", bound=AbstractRecordModel)


def _unwrap(model: AbstractRecordModel | PyRecordModel):
    if isinstance(model, PyRecordModel):
        return model
    return model.backing_model
