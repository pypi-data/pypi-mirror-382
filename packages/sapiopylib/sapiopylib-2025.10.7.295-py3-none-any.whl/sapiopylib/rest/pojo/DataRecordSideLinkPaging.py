from __future__ import annotations

from typing import Optional, List, Dict, Any

from sapiopylib.rest.pojo.DataRecord import DataRecord, DataRecordDescriptor
from sapiopylib.rest.pojo.DataRecordPaging import AbstractPageCriteria


def _get_result_map(json_dct):
    result_map: Dict[DataRecordDescriptor, List[DataRecord]] = dict()
    result_map_list: Dict[str, List[Dict[str, Any]]] = json_dct.get("resultMap")
    for record_key, dict_list in result_map_list.items():
        descriptor = DataRecordDescriptor.from_str(record_key)
        record_list = [DataRecord.from_json(x) for x in dict_list]
        result_map[descriptor] = record_list
    return result_map


class DataRecordSideLinkToPageCriteria(AbstractPageCriteria):
    """
    Details describing the page to retrieve from the API.
    The page size specified should not be greater than the maximum query size that the app is limited to.
    """
    last_retrieved_source_recordId: Optional[int]
    last_retrieved_target_recordId: Optional[int]

    def __init__(self, last_retrieved_source_record_id: Optional[int] = None,
                 last_retrieved_target_record_id: Optional[int] = None, page_size: Optional[int] = None):
        super().__init__(page_size=page_size)
        self.last_retrieved_source_recordId = last_retrieved_source_record_id
        self.last_retrieved_target_recordId = last_retrieved_target_record_id

    def to_json(self) -> Dict[str, Any]:
        return {
            'lastRetrievedSourceRecordId': self.last_retrieved_source_recordId,
            'lastRetrievedTargetRecordId': self.last_retrieved_target_recordId,
            'pageSize': self.page_size
        }

    @staticmethod
    def from_json(json_dct: Dict[str, Any]) -> Optional[DataRecordSideLinkToPageCriteria]:
        if not json_dct:
            return None
        last_retrieved_source_record_id: Optional[int] = json_dct.get('lastRetrievedSourceRecordId')
        last_retrieved_target_record_id: Optional[int] = json_dct.get('lastRetrievedTargetRecordId')
        page_size: Optional[int] = json_dct.get('pageSize')
        return DataRecordSideLinkToPageCriteria(last_retrieved_source_record_id=last_retrieved_source_record_id,
                                                last_retrieved_target_record_id=last_retrieved_target_record_id,
                                                page_size=page_size)


class DataRecordSideLinkToListPageResult:
    """
    The page result of a query to a method that queries for DataRecord side links to and returns
    a map of record key DataRecordDescriptor to a list of results.
    This object also contains the DataRecordPojoSideLinkToPageCriteria that can be used to get the next page of results.
    """
    next_page_criteria: DataRecordSideLinkToPageCriteria
    result_map: Dict[DataRecordDescriptor, List[DataRecord]]
    is_next_page_available: bool

    def __init__(self, next_page_criteria: DataRecordSideLinkToPageCriteria,
                 result_map: Dict[DataRecordDescriptor, List[DataRecord]], is_next_page_available: bool):
        self.next_page_criteria = next_page_criteria
        self.result_map = result_map
        self.is_next_page_available = is_next_page_available

    @staticmethod
    def from_json(json_dct: Dict[str, Any]) -> DataRecordSideLinkToListPageResult:
        next_page_criteria: DataRecordSideLinkToPageCriteria = DataRecordSideLinkToPageCriteria.from_json(
            json_dct.get("nextPageCriteria"))
        result_map = _get_result_map(json_dct)
        # PR-53358: The key is nextPageAvailable, not isNextPageAvailable.
        is_next_page_available: bool = json_dct.get('nextPageAvailable')
        return DataRecordSideLinkToListPageResult(next_page_criteria, result_map, is_next_page_available)


class DataRecordSideLinkFromPageCriteria(AbstractPageCriteria):
    """
    Details describing the page to retrieve from the API.
    The page size specified should not be greater than the maximum query size that the app is limited to.
    """
    last_retrieved_source_record_id: Optional[int]

    def __init__(self, last_retrieved_source_record_id: Optional[int] = None,
                 page_size: Optional[int] = None):
        super().__init__(page_size=page_size)
        self.last_retrieved_source_record_id = last_retrieved_source_record_id

    def to_json(self) -> Dict[str, Any]:
        return {
            'lastRetrievedSourceRecordId': self.last_retrieved_source_record_id,
            'pageSize': self.page_size
        }

    @staticmethod
    def from_json(json_dct: Dict[str, Any]) -> Optional[DataRecordSideLinkFromPageCriteria]:
        if not json_dct:
            return None
        last_retrieved_source_record_id: Optional[int] = json_dct.get('lastRetrievedSourceRecordId')
        page_size: Optional[int] = json_dct.get('pageSize')
        return DataRecordSideLinkFromPageCriteria(last_retrieved_source_record_id=last_retrieved_source_record_id,
                                                  page_size=page_size)


class DataRecordSideLinkFromListPageResult:
    """
    The page result of a query to a method that queries for DataRecordPojo relations and returns a map of lists of
    results.  This object contains a map of lists of results as well as the DataRecordSideLinkFromPageCriteria
    that can be used to get the next page of results.
    """
    next_page_criteria: DataRecordSideLinkFromPageCriteria
    result_map: Dict[DataRecordDescriptor, List[DataRecord]]
    is_next_page_available: bool

    def __init__(self, next_page_criteria: DataRecordSideLinkFromPageCriteria,
                 result_map: Dict[DataRecordDescriptor, List[DataRecord]],
                 is_next_page_available: bool):
        self.next_page_criteria = next_page_criteria
        self.result_map = result_map
        self.is_next_page_available = is_next_page_available

    @staticmethod
    def from_json(json_dct: Dict[str, Any]) -> DataRecordSideLinkFromListPageResult:
        next_page_criteria: DataRecordSideLinkFromPageCriteria = DataRecordSideLinkFromPageCriteria.from_json(
            json_dct.get("nextPageCriteria"))
        result_map: Dict[DataRecordDescriptor, List[DataRecord]] = _get_result_map(json_dct)
        # PR-53358: The key is nextPageAvailable, not isNextPageAvailable.
        is_next_page_available: bool = json_dct.get('nextPageAvailable')
        return DataRecordSideLinkFromListPageResult(next_page_criteria, result_map, is_next_page_available)
