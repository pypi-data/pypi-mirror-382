from __future__ import annotations

from typing import Optional, List, Dict

from sapiopylib.rest.pojo.DataRecord import DataRecord


class AbstractPageCriteria:
    page_size: Optional[int]

    def __init__(self, page_size=None):
        self.page_size = page_size

    @staticmethod
    def from_json(json_dct: dict) -> Optional[AbstractPageCriteria]:
        if json_dct is None:
            return None
        page_size = json_dct.get('pageSize')
        return AbstractPageCriteria(page_size=page_size)


class DataRecordPojoPageCriteria(AbstractPageCriteria):
    """
    Details describing the page to retrieve from the API.  The page size specified should not be greater than the
    maximum query size that the app is limited to.
    """
    last_retrieved_record_id: Optional[int]

    def __init__(self, last_retrieved_record_id=None, page_size=None):
        """
        Create a new DataRecordPojoPageCriteria
        :param last_retrieved_record_id: The last record ID retrieved from this method in a prior call.
        :param page_size: The number of records to be returned by this method. A max may be enforced by server.
        """
        super().__init__(page_size)
        self.last_retrieved_record_id = last_retrieved_record_id

    @staticmethod
    def from_json(json_dct: dict) -> Optional[DataRecordPojoPageCriteria]:
        if json_dct is None:
            return None
        last_retrieved_record_id = json_dct.get('lastRetrievedRecordId')
        page_size = json_dct.get('pageSize')
        return DataRecordPojoPageCriteria(last_retrieved_record_id=last_retrieved_record_id, page_size=page_size)


class DataRecordPojoListPageResult:
    """
    The page result of a query to a method that queries for DataRecordPojos that return a single list of
    results.  This object contains a list of results as well as the DataRecordPojoPageCriteria that can be
    used to get the next page of results.
    """
    result_list: List[DataRecord]
    next_page_criteria: Optional[DataRecordPojoPageCriteria]
    is_next_page_available: bool

    def __init__(self, is_next_page_available: bool, next_page_criteria: DataRecordPojoPageCriteria, result_list):
        self.is_next_page_available = is_next_page_available
        self.next_page_criteria = next_page_criteria
        self.result_list = result_list

    @staticmethod
    def from_json(json_dct: dict):
        is_next_page_available: bool = json_dct.get('nextPageAvailable')
        next_page_criteria: Optional[DataRecordPojoPageCriteria] = DataRecordPojoPageCriteria.from_json(
            json_dct.get("nextPageCriteria"))
        result_list_json: List[dict] = json_dct.get("resultList")
        result_list: List[DataRecord] = list()
        for record_dict in result_list_json:
            result_list.append(DataRecord.from_json(record_dict))
        return DataRecordPojoListPageResult(is_next_page_available, next_page_criteria, result_list)

    def __str__(self):
        if self.result_list is None:
            return '[]'
        ret = ', '.join(str(x) for x in self.result_list)
        if self.is_next_page_available:
            ret += '[More Pages...]'
        return ret

    def __len__(self):
        return self.result_list.__len__()

    def __iter__(self):
        return self.result_list.__iter__()


class DataRecordPojoHierarchyPageCriteria(AbstractPageCriteria):
    """
    Details describing the page to retrieve from the API.
    The page size specified should not be greater than the maximum query size that the app is limited to.
    """
    last_retrieved_source_record_id: Optional[int]
    last_retrieved_target_record_id: Optional[int]

    def __init__(self, last_retrieved_source_record_id: int = None, last_retrieved_target_record_id: int = None,
                 page_size: int = None):
        super().__init__(page_size)
        self.last_retrieved_source_record_id = last_retrieved_source_record_id
        self.last_retrieved_target_record_id = last_retrieved_target_record_id

    @staticmethod
    def from_json(json_dct: dict) -> Optional[DataRecordPojoHierarchyPageCriteria]:
        if not json_dct:
            return None
        page_size = json_dct.get('pageSize')
        last_retrieved_source_record_id = json_dct.get('lastRetrievedSourceRecordId')
        last_retrieved_target_record_id = json_dct.get('lastRetrievedTargetRecordId')
        return DataRecordPojoHierarchyPageCriteria(last_retrieved_source_record_id, last_retrieved_target_record_id,
                                                   page_size)


class DataRecordPojoHierarchyListPageResult:
    """
    The page result of a query to a method that queries for DataRecordPojo relations and returns a list of lists of
    results.  This object contains a list of lists of results as well as the DataRecordPojoPageCriteria that can be
    used to get the next page of results.
    """
    next_page_criteria: Optional[DataRecordPojoHierarchyPageCriteria]
    result_map: Dict[int, List[DataRecord]]
    is_next_page_available: bool

    def __init__(self, next_page_criteria: DataRecordPojoHierarchyPageCriteria,
                 result_map: Dict[int, List[DataRecord]], is_next_page_available: bool):
        self.next_page_criteria = next_page_criteria
        self.result_map = result_map
        self.is_next_page_available = is_next_page_available

    @staticmethod
    def from_json(json_dct: dict):
        is_next_page_available: bool = json_dct.get('nextPageAvailable')
        result_map_json: Dict[int, List[dict]] = json_dct.get("resultMap")
        next_page_criteria: Optional[DataRecordPojoHierarchyPageCriteria] = (
            DataRecordPojoHierarchyPageCriteria.from_json(json_dct.get("nextPageCriteria")))
        result_map: Dict[int, List[DataRecord]] = dict()
        for source_record_id, record_json_list in result_map_json.items():
            record_list: List[DataRecord] = list()
            for record_json in record_json_list:
                record_list.append(DataRecord.from_json(record_json))
            result_map[int(source_record_id)] = record_list
        return DataRecordPojoHierarchyListPageResult(next_page_criteria, result_map, is_next_page_available)
