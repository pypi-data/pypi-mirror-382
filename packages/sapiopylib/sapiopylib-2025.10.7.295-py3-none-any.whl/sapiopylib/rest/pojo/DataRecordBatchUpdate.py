from __future__ import annotations

from typing import List, Dict, Any

from sapiopylib.rest.pojo.DataRecord import DataRecord, DataRecordDescriptor


class DataRecordNewSideLinkPojo:
    """
    Describes a side link into a new data record created in batch request right now,
    which will have a negative Record ID.

    If the side link is made to an existing record,
    then it needs not be set here and can be directly set as field value.
    """
    source: DataRecordDescriptor
    field_name: str
    target: DataRecordDescriptor

    def __init__(self, source: DataRecordDescriptor, field_name: str, target: DataRecordDescriptor):
        self.source = source
        self.field_name = field_name
        self.target = target

    def to_json(self) -> Dict[str, Any]:
        return {
            'source': self.source.to_json(),
            'fieldName': self.field_name,
            'target': self.target.to_json()
        }

class DataRecordRelationChangePojo:
    """
    Describes changes to a data record relation.
    """
    parent: DataRecordDescriptor
    child: DataRecordDescriptor

    def __init__(self, parent: DataRecordDescriptor, child: DataRecordDescriptor):
        self.parent = parent
        self.child = child

    def to_json(self) -> Dict[str, Any]:
        return {
            'parent': self.parent.to_json(),
            'child': self.child.to_json()
        }


class DataRecordBatchUpdate:
    """
    Provides an entire graph of all data record updates in one single webservice call.

    This is used to support record model. It probably has no utility outside the library.
    """
    records_added: List[DataRecord]
    records_deleted: List[DataRecordDescriptor]
    records_fields_changed: List[DataRecord]
    child_links_added: List[DataRecordRelationChangePojo]
    child_links_removed: List[DataRecordRelationChangePojo]
    side_links_to_new_records: List[DataRecordNewSideLinkPojo]

    def __init__(self, records_added: List[DataRecord], records_deleted: List[DataRecordDescriptor],
                 records_fields_changed: List[DataRecord], child_links_added: List[DataRecordRelationChangePojo],
                 child_links_removed: List[DataRecordRelationChangePojo],
                 side_links_to_new_records: List[DataRecordNewSideLinkPojo]):
        self.records_added = records_added
        self.records_deleted = records_deleted
        self.records_fields_changed = records_fields_changed
        self.child_links_added = child_links_added
        self.child_links_removed = child_links_removed
        self.side_links_to_new_records = side_links_to_new_records

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = dict()
        ret['recordsAdded'] = [x.to_json() for x in self.records_added]
        ret['recordsDeleted'] = [x.to_json() for x in self.records_deleted]
        ret['recordFieldsChanged'] = [x.to_json() for x in self.records_fields_changed]
        ret['childRecordsAdded'] = [x.to_json() for x in self.child_links_added]
        ret['childRecordsRemoved'] = [x.to_json() for x in self.child_links_removed]
        ret['sideLinksToNewRecords'] = [x.to_json() for x in self.side_links_to_new_records]
        return ret


class DataRecordBatchResult:
    """
    Returned result object from data record batch update.

    This is used to support record model. It probably has no utility outside the library.
    """
    added_record_updates: Dict[int, DataRecordDescriptor]

    def __init__(self, added_record_updates: Dict[int, DataRecordDescriptor]):
        self.added_record_updates = added_record_updates

    @staticmethod
    def from_json(json_dct: Dict[str, Any]) -> DataRecordBatchResult:
        added_record_updates_json: Dict[int, Dict[str, Any]] = json_dct.get('addedRecordUpdates')
        added_record_updates: Dict[int, DataRecordDescriptor] = dict()
        for key, value in added_record_updates_json.items():
            descriptor: DataRecordDescriptor = DataRecordDescriptor.from_json(value)
            added_record_updates[int(key)] = descriptor
        return DataRecordBatchResult(added_record_updates)
