from __future__ import annotations

import warnings
from abc import abstractmethod
from typing import List, Type, TypeVar, Optional, Iterable, Final

from sapiopylib.rest.pojo.datatype.FieldDefinition import FieldType
from sapiopylib.rest.utils.recordmodel.PyRecordModel import (
    PyRecordModel, SapioRecordModelException, AbstractRecordModel, AbstractRecordModelType)


class WrapperField:
    """
    Describes a wrapper field used in auto-generated wrappers
    """
    _field_name: Final[str]
    _field_type: Final[FieldType]
    _display_name: Final[Optional[str]]

    @property
    def field_name(self) -> str:
        """
        The name of the data field represented in this object of the Sapio data type.
        """
        return self._field_name

    @property
    def field_type(self) -> FieldType:
        """
        The data field's type for the data type's data field with the object's field name in Sapio.
        """
        return self._field_type

    @property
    def display_name(self) -> Optional[str]:
        """
        The display name of the field in the Sapio system. If this is generated before 24.12, None will be returned.
        """
        return self._display_name

    def __init__(self, field_name: str, field_type: FieldType, display_name: Optional[str] = None):
        self._field_name = field_name
        self._field_type = field_type
        self._display_name = display_name

    def __repr__(self):
        return self._field_name

    def __str__(self):
        if self._display_name:
            return self._display_name
        return self._field_name

    def __hash__(self):
        return hash((self._field_name, self._field_type))

    def __eq__(self, other):
        if not isinstance(other, WrapperField):
            return False
        return self._field_name == other._field_name and self._field_type == other._field_type


class WrappedRecordModel(AbstractRecordModel):
    """
    Wraps a record model so that it can be extended via interfacing types.
    Supporting auto-generated interfaces or any other decorations for base record model impl.

    A wrapped record model maintains its singleton under the record model root in the record model manager.
    You can create multiple instances of wrapper objects, but they will share the same data and cache.
    """
    _backing_model: PyRecordModel

    def __init__(self, backing_model: PyRecordModel):
        super().__init__(backing_model)

    @classmethod
    @abstractmethod
    def get_wrapper_data_type_name(cls) -> str:
        """
        The name of the data type in Sapio system that the wrapper class's attributes and methods will represent.
        """
        pass

    def get_parents_of_type(self, parent_type: Type[WrappedType]) -> List[WrappedType]:
        """
        Get all parents for a particular data type name for this record model.
        """
        models: List[PyRecordModel] = self._backing_model.get_parents_of_type(parent_type.get_wrapper_data_type_name())
        from sapiopylib.rest.utils.recordmodel.RecordModelManager import RecordModelInstanceManager
        return RecordModelInstanceManager.wrap_list(models, parent_type)

    def get_children_of_type(self, child_type: Type[WrappedType]) -> List[WrappedType]:
        """
        Get all children for a particular data type name for this record model.
        """
        models: List[PyRecordModel] = self._backing_model.get_children_of_type(child_type.get_wrapper_data_type_name())
        from sapiopylib.rest.utils.recordmodel.RecordModelManager import RecordModelInstanceManager
        return RecordModelInstanceManager.wrap_list(models, child_type)

    def get_parent_of_type(self, parent_type: Type[WrappedType]) -> Optional[WrappedType]:
        """
        Obtains the parent of the current record of the provided data type name.
        If the parent is not found, return None.
        If there are more than one parent exists, then we will throw an exception.
        """
        parents = self.get_parents_of_type(parent_type)
        if not parents:
            return None
        if len(parents) > 1:
            raise SapioRecordModelException("Too many parent records of type " +
                                            parent_type.get_wrapper_data_type_name(), self._backing_model)
        return parents[0]

    def get_child_of_type(self, child_type: Type[WrappedType]) -> Optional[WrappedType]:
        """
        Obtains the only child of the current record of the provided data type name.
        If the child is not found, return None.
        If there are more than one child exists, then we will throw an exception.
        """
        children = self.get_children_of_type(child_type)
        if not children:
            return None
        if len(children) > 1:
            raise SapioRecordModelException("Too many child records of type " + child_type.get_wrapper_data_type_name(),
                                            self._backing_model)
        return children[0]

    def get_forward_side_link(self, field_name: str, forward_link_type: Type[WrappedType]) -> Optional[WrappedType]:
        """
        Get the current forward side links. If the side links have not been loaded, throw an exception.
        :param field_name: The forward link field on this record to load its reference for.
        :param forward_link_type: The returned forward link record's class type.
        """
        ret: Optional[PyRecordModel] = self._backing_model.get_forward_side_link(field_name)
        if ret is None:
            return None
        from sapiopylib.rest.utils.recordmodel.RecordModelManager import RecordModelInstanceManager
        return RecordModelInstanceManager.wrap(ret, forward_link_type)

    def get_reverse_side_link(self, field_name: str, reverse_link_type: Type[WrappedType]) -> List[WrappedType]:
        """
        Get currently loaded reverse side link models. This will throw exception if it has not been loaded before.
        :param field_name: The reverse link's field name on the record that will point to one of provided records.
        :param reverse_link_type: The reverse link's model class type of records that will point to provided records.
        """
        ret: List[PyRecordModel] = self._backing_model.get_reverse_side_link(
            reverse_side_link_data_type_name=reverse_link_type.get_wrapper_data_type_name(),
            reverse_side_link_field_name=field_name)
        from sapiopylib.rest.utils.recordmodel.RecordModelManager import RecordModelInstanceManager
        return RecordModelInstanceManager.wrap_list(ret, reverse_link_type)


WrappedType = TypeVar("WrappedType", bound=WrappedRecordModel)


class RecordModelWrapperUtil:
    """
    Wraps or unwraps a record model that has a wrapper function.

    This really should no longer be needed. We can use instance manager to do the same.
    """
    @staticmethod
    def unwrap(wrapped_record_model: AbstractRecordModel | PyRecordModel) -> PyRecordModel:
        warnings.warn("RecordModelWrapperUtil is redundant. Use instance manager directly.", PendingDeprecationWarning)
        from sapiopylib.rest.utils.recordmodel.RecordModelManager import RecordModelInstanceManager
        return RecordModelInstanceManager.unwrap(wrapped_record_model)

    @staticmethod
    def unwrap_list(wrapped_record_model_list: Iterable[AbstractRecordModel | PyRecordModel]) -> List[PyRecordModel]:
        warnings.warn("RecordModelWrapperUtil is redundant. Use instance manager directly.", PendingDeprecationWarning)
        from sapiopylib.rest.utils.recordmodel.RecordModelManager import RecordModelInstanceManager
        return [RecordModelInstanceManager.unwrap(x) for x in wrapped_record_model_list]

    @staticmethod
    def wrap(py_record_model: PyRecordModel | AbstractRecordModel,
             clazz: Type[AbstractRecordModelType]) -> AbstractRecordModelType:
        warnings.warn("RecordModelWrapperUtil is redundant. Use instance manager directly.", PendingDeprecationWarning)
        from sapiopylib.rest.utils.recordmodel.RecordModelManager import RecordModelInstanceManager
        return RecordModelInstanceManager.wrap(py_record_model, clazz)

    @staticmethod
    def wrap_list(py_record_model_list: Iterable[PyRecordModel | AbstractRecordModel],
                  clazz: Type[AbstractRecordModelType]) \
            -> List[AbstractRecordModelType]:
        warnings.warn("RecordModelWrapperUtil is redundant. Use instance manager directly.", PendingDeprecationWarning)
        from sapiopylib.rest.utils.recordmodel.RecordModelManager import RecordModelInstanceManager
        return [RecordModelInstanceManager.wrap(x, clazz) for x in py_record_model_list]
