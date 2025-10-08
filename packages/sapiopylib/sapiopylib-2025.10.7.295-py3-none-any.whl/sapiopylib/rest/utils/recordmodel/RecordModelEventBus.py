from buslane.events import EventBus, EventHandler

from sapiopylib.rest.utils.recordmodel.RecordModelEvents import *


class RecordModelEventBus:
    """
    Record model event bus is attached to each record model manager to transfer events among multiple managers.
    """
    _publisher: EventBus

    def __init__(self):
        self._publisher = EventBus()

    def fire_rollback_event(self):
        """
        Internal method that is called when rollback is demanded.
        """
        self._publisher.publish(RollbackEvent())

    def subscribe_rollback_event(self, handler: EventHandler[RollbackEvent]):
        """
        Subscribes an event handler to listen to rollback events fired from this event bus.
        """
        self._publisher.register(handler)

    def fire_commit_event(self):
        """
        Internal method that is called when commit main logic finishes and manager processing is demanded.
        """
        self._publisher.publish(CommitEvent())

    def subscribe_commit_event(self, handler: EventHandler[CommitEvent]):
        """
        Subscribes an event handler to listen to commit events fired from this event bus.
        """
        self._publisher.register(handler)

    def fire_child_add_event(self, event: ChildAddedEvent):
        """
        Internal method that is called when a new relationship is added.
        """
        self._publisher.publish(event)

    def subscribe_child_add_event(self, handler: EventHandler[ChildAddedEvent]):
        """
        Subscribes an event handler to listen to events that adds a relationship fired from this event bus.
        """
        self._publisher.register(handler)

    def fire_child_remove_event(self, event: ChildRemovedEvent):
        """
        Internal method that is called when an existing relationship is removed.
        """
        self._publisher.publish(event)

    def subscribe_child_remove_event(self, handler: EventHandler[ChildRemovedEvent]):
        """
        Subscribes an event handler to listen to events that removes a relationship fired from this event bus.
        """
        self._publisher.register(handler)

    def fire_field_change_event(self, event: FieldChangeEvent):
        """
        Internal method that is called when data field values are changed on any record model.
        """
        self._publisher.publish(event)

    def subscribe_field_change_event(self, handler: EventHandler[FieldChangeEvent]):
        """
        Subscribes an event handler to listen to events that changes field values that are fired from this event bus.
        """
        self._publisher.register(handler)

    def fire_record_add_event(self, event: RecordAddedEvent):
        """
        Internal method that is called when new record models are added.
        """
        self._publisher.publish(event)

    def subscribe_record_add_event(self, handler: EventHandler[RecordAddedEvent]):
        """
        Subscribes an event handler to listen to addition of new records that are fired from this event bus.
        """
        self._publisher.register(handler)

    def fire_record_delete_event(self, event: RecordDeletedEvent):
        """
        Internal method that is called when existing record models are deleted.
        """
        self._publisher.publish(event)

    def subscribe_record_delete_event(self, handler: EventHandler[RecordDeletedEvent]):
        """
        Subscribes an event handler to listen to deletion of existing records that are fired from this event bus.
        """
        self._publisher.register(handler)

    def fire_side_link_changed_event(self, source_model: PyRecordModel, field_name: str,
                                     target_record_id: Optional[int]):
        self._publisher.publish(SideLinkChangedEvent(source_model=source_model,
                                                     link_field_name=field_name, target_record_id=target_record_id))

    def subscribe_side_link_changed_event(self, handler: EventHandler[SideLinkChangedEvent]) -> None:
        self._publisher.register(handler)

    def fire_record_id_accession_event(self, source_model: PyRecordModel, record_id: int) -> None:
        self._publisher.publish(RecordIdAccessionEvent(source_model, record_id))

    def subscribe_record_id_accession_event(self, handler: EventHandler[RecordIdAccessionEvent]) -> None:
        self._publisher.register(handler)
