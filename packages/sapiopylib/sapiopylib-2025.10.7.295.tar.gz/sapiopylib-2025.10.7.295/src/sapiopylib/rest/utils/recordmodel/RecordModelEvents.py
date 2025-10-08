from typing import Any, Optional

from buslane.events import Event

from sapiopylib.rest.utils.recordmodel.PyRecordModel import PyRecordModel


class ChildAddedEvent(Event):
    """
    This event is fired when a new parent-child relationship is added through record model.
    """
    __parent: PyRecordModel
    __child: PyRecordModel

    def __init__(self, parent: PyRecordModel, child: PyRecordModel):
        self.__parent = parent
        self.__child = child

    @property
    def parent(self) -> PyRecordModel:
        return self.__parent

    @property
    def child(self) -> PyRecordModel:
        return self.__child


class ChildRemovedEvent(Event):
    """
    This event is fired when an existing parent-child relationship is removed through record model.
    """
    __parent: PyRecordModel
    __child: PyRecordModel

    def __init__(self, parent: PyRecordModel, child: PyRecordModel):
        self.__parent = parent
        self.__child = child

    @property
    def parent(self) -> PyRecordModel:
        return self.__parent

    @property
    def child(self) -> PyRecordModel:
        return self.__child


class FieldChangeEvent(Event):
    """
    This event is fired when a data field value is changed through record model.
    """
    __record: PyRecordModel
    __field_name: str
    __old_value: Any
    __new_value: Any

    def __init__(self, record: PyRecordModel, field_name: str, old_value: Any, new_value: Any):
        self.__record = record
        self.__field_name = field_name
        self.__old_value = old_value
        self.__new_value = new_value

    @property
    def record(self) -> PyRecordModel:
        return self.__record

    @property
    def field_name(self) -> str:
        return self.__field_name

    @property
    def old_value(self) -> Any:
        return self.__old_value

    @property
    def new_value(self) -> Any:
        return self.__new_value


class RecordAddedEvent(Event):
    """
    This event is fired when a new data record is added through record model.
    """
    __record: PyRecordModel

    def __init__(self, record: PyRecordModel):
        self.__record = record

    @property
    def record(self) -> PyRecordModel:
        return self.__record


class RecordDeletedEvent(Event):
    """
    This event is fired when an existing record is deleted through record model.
    """
    __record: PyRecordModel

    def __init__(self, record: PyRecordModel):
        self.__record = record

    @property
    def record(self) -> PyRecordModel:
        return self.__record


class RollbackEvent(Event):
    """
    This event is fired when rollback happens from transaction manager.
    """


class CommitEvent(Event):
    """
    This event is fired when commit happens from transaction manager.
    """


class SideLinkChangedEvent(Event):
    """
    This event is fired when a side link has been modified.
    """
    __source_model: PyRecordModel
    __link_field_name: str
    __target_record_id: Optional[int]

    def __init__(self, source_model: PyRecordModel, link_field_name: str, target_record_id: Optional[int]):
        self.__source_model = source_model
        self.__link_field_name = link_field_name
        self.__target_record_id = target_record_id

    @property
    def source_model(self) -> PyRecordModel:
        return self.__source_model

    @property
    def link_field_name(self) -> str:
        return self.__link_field_name

    @property
    def target_record_id(self) -> Optional[int]:
        return self.__target_record_id

class RecordIdAccessionEvent(Event):
    """
    This is fired when record id has been accessioned to a record model.
    """
    __source_model: PyRecordModel
    __accessioned_record_id: int

    def __init__(self, source_model: PyRecordModel, accessioned_record_id: int):
        self.__source_model = source_model
        self.__accessioned_record_id = accessioned_record_id

    @property
    def source_model(self) -> PyRecordModel:
        """
        The model that obtained the new record ID in this event.
        """
        return self.__source_model

    @property
    def accessioned_record_id(self) -> int:
        """
        The new record ID accessioned in this event.
        """
        return self.__accessioned_record_id