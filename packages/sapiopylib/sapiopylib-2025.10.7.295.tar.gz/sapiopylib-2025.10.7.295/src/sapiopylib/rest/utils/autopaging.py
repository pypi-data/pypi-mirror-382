import logging
from abc import ABC, abstractmethod
from copy import copy
from queue import Queue
from typing import TypeVar, Generic, Optional, List, Iterator, Any

from sapiopylib.rest.DataRecordManagerService import DataRecordManager
from sapiopylib.rest.ELNService import ElnManager
from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.CustomReport import CustomReportCriteria, CustomReport
from sapiopylib.rest.pojo.DataRecord import DataRecord, DataRecordDescriptor
from sapiopylib.rest.pojo.DataRecordPaging import AbstractPageCriteria, DataRecordPojoHierarchyPageCriteria, \
    DataRecordPojoHierarchyListPageResult, DataRecordPojoPageCriteria, DataRecordPojoListPageResult
from sapiopylib.rest.pojo.DataRecordSideLinkPaging import DataRecordSideLinkFromPageCriteria, \
    DataRecordSideLinkFromListPageResult, DataRecordSideLinkToPageCriteria, DataRecordSideLinkToListPageResult
from sapiopylib.rest.utils.MultiMap import SetMultimap

PagerResultType = TypeVar("PagerResultType")
PagerResultCriteriaType = TypeVar("PagerResultCriteriaType", bound=AbstractPageCriteria)
# FR-52729 adjusted default page size for reference.
# our current SaaS default limit for data record page size.
_default_record_page_size = 1000
# our current SaaS default limit for report page size.
_default_report_page_size = 10000
_max_page_size = 1000000


class SapioPyAutoPager(ABC, Generic[PagerResultCriteriaType, PagerResultType], Iterator[PagerResultType]):
    """
    This class is a single-user iterator that operates on a paged data record manager query.
    """
    next_page_criteria: Optional[PagerResultCriteriaType]
    last_page_result: Optional[Queue[PagerResultType]]
    user: SapioUser
    data_record_manager: DataRecordManager
    has_iterated: bool
    cur_page: int
    max_page: Optional[int]

    def __init__(self, user: SapioUser, first_page_criteria: Optional[PagerResultCriteriaType] = None):
        if not first_page_criteria:
            first_page_criteria = self.default_first_page_criteria()
        if first_page_criteria.page_size < 1 or first_page_criteria.page_size > _max_page_size:
            raise ValueError("Page Size cannot be less than 1 or above " + str(_max_page_size))
        self.user = user
        self.data_record_manager = DataRecordManager(user)
        self.next_page_criteria = first_page_criteria
        self.last_page_result = None
        self.has_iterated = False
        self.cur_page = 0
        self.max_page = None

    @abstractmethod
    def get_next_page_result(self) -> (Optional[PagerResultCriteriaType], Queue[PagerResultType]):
        """
        A method that returns tuple of:
        1. The next page criteria if available.
        2. The next page result.
        """
        pass

    @abstractmethod
    def default_first_page_criteria(self) -> PagerResultCriteriaType:
        """
        Create the page criteria of the first page
        """
        pass

    def __next__(self) -> PagerResultType:
        self.has_iterated = True
        if self.last_page_result and not self.last_page_result.empty():
            return self.last_page_result.get_nowait()
        if self.next_page_criteria is not None:
            self.cur_page += 1
            logging.debug("Swapping to next page with auto-paging. Next page is available. "
                          "Current page is " + str(self.cur_page))
            if self.max_page is not None and 0 < self.max_page < self.cur_page:
                logging.debug("Auto-pager stopped because maximum page size had been exceeded.")
                raise StopIteration
            self.next_page_criteria, self.last_page_result = self.get_next_page_result()
            return self.__next__()
        logging.debug("Auto-paging has no further elements to visit.")
        raise StopIteration


class AbstractRecordHierarchyAutoPager(SapioPyAutoPager[DataRecordPojoHierarchyPageCriteria, (int, List[DataRecord])]):
    def get_all_at_once(self) -> SetMultimap[int, DataRecord]:
        """
        Get the results of all pages. Be cautious of client memory usage.
        """
        if self.has_iterated:
            raise BrokenPipeError("Cannot use this method if the iterator has already been used.")
        ret: SetMultimap[int, DataRecord] = SetMultimap()
        for record_id, partial_list in self:
            ret.put_all(record_id, partial_list)
        return ret

    def __init__(self, user: SapioUser, first_page_criteria: DataRecordPojoHierarchyPageCriteria = None):
        super().__init__(user, first_page_criteria)

    def default_first_page_criteria(self) -> PagerResultCriteriaType:
        return DataRecordPojoHierarchyPageCriteria(page_size=_default_record_page_size)

    @abstractmethod
    def get_page_result(self) -> DataRecordPojoHierarchyListPageResult:
        pass

    def get_next_page_result(self) -> (Optional[PagerResultCriteriaType], Queue[PagerResultType]):
        page_result: DataRecordPojoHierarchyListPageResult = self.get_page_result()
        result_queue: Queue[(int, List[DataRecord])] = Queue()
        for item in page_result.result_map.items():
            result_queue.put(item)
        if not page_result.is_next_page_available:
            return None, result_queue
        return page_result.next_page_criteria, result_queue


class GetAncestorsListAutoPager(AbstractRecordHierarchyAutoPager):
    """
    Obtain ancestor results in a memory-efficient iterator that spans through all pages.
    Note that the item sematic is (descendant record ID) -> (PARTIAL list of ancestor records)
    """
    descendant_record_id_list: List[int]
    descendant_type_name: str
    ancestor_type_name: str

    def get_page_result(self) -> DataRecordPojoHierarchyListPageResult:
        return self.data_record_manager.get_ancestors_list(
            self.descendant_record_id_list, self.descendant_type_name, self.ancestor_type_name, self.next_page_criteria)

    def __init__(self, descendant_record_id_list: List[int], descendant_type_name: str,
                 ancestor_type_name: str,
                 user: SapioUser, first_page_criteria: DataRecordPojoHierarchyPageCriteria = None):
        super().__init__(user, first_page_criteria)
        self.descendant_record_id_list = descendant_record_id_list
        self.descendant_type_name = descendant_type_name
        self.ancestor_type_name = ancestor_type_name


class GetDescendantsListAutoPager(AbstractRecordHierarchyAutoPager):
    """
    Obtain descendant results in a memory-efficient iterator that spans through all pages.
    Note that the item sematic is (ancestor record ID) -> (PARTIAL list of descendant records)
    """
    ancestor_record_id_list: List[int]
    descendant_type_name: str

    def get_page_result(self) -> DataRecordPojoHierarchyListPageResult:
        return self.data_record_manager.get_descendants_list(
            self.ancestor_record_id_list, self.descendant_type_name, self.next_page_criteria)

    def __init__(self, ancestor_record_id_list: List[int], descendant_type_name: str,
                 user: SapioUser, first_page_criteria: DataRecordPojoHierarchyPageCriteria = None):
        super().__init__(user, first_page_criteria)
        self.ancestor_record_id_list = ancestor_record_id_list
        self.descendant_type_name = descendant_type_name


class GetParentsListAutoPager(AbstractRecordHierarchyAutoPager):
    """
    Obtain parent results in a memory-efficient iterator that spans through all pages.
    Note that the item sematic is (child record ID) -> (PARTIAL list of parent records)
    """
    child_record_id_list: List[int]
    child_type_name: str
    parent_type_name: str

    def get_page_result(self) -> DataRecordPojoHierarchyListPageResult:
        return self.data_record_manager.get_parents_list(
            self.child_record_id_list, self.child_type_name, self.parent_type_name, self.next_page_criteria)

    def __init__(self, child_record_list: List[int], child_type_name: str, parent_type_name: str,
                 user: SapioUser, first_page_criteria: DataRecordPojoHierarchyPageCriteria = None):
        super().__init__(user, first_page_criteria)
        self.child_record_id_list = child_record_list
        self.child_type_name = child_type_name
        self.parent_type_name = parent_type_name


class GetChildrenListAutoPager(AbstractRecordHierarchyAutoPager):
    """
    Obtain child results in a memory-efficient iterator that spans through all pages.
    Note that the item sematic is (parent record ID) -> (PARTIAL list of child records)
    """
    child_record_id_list: List[int]
    child_type_name: str

    def get_page_result(self) -> DataRecordPojoHierarchyListPageResult:
        return self.data_record_manager.get_children_list(
            self.child_record_id_list, self.child_type_name, self.next_page_criteria)

    def __init__(self, child_record_list: List[int], child_type_name: str,
                 user: SapioUser, first_page_criteria: DataRecordPojoHierarchyPageCriteria = None):
        super().__init__(user, first_page_criteria)
        self.child_record_id_list = child_record_list
        self.child_type_name = child_type_name


class GetForwardSideLinkListAutoPager(SapioPyAutoPager[
                                            DataRecordSideLinkFromPageCriteria, (
                                            DataRecordDescriptor, List[DataRecord])]):
    """
    Obtain forward side link results in a memory-efficient iterator that spans through all pages.
    Note that the item sematic is (Record Descriptor) -> (PARTIAL list of forward link data records)
    """
    records_to_query: List[DataRecord]
    side_link_field_name: str

    def get_all_at_once(self) -> SetMultimap[DataRecordDescriptor, DataRecord]:
        """
        Get the results of all pages. Be cautious of client memory usage.
        """
        if self.has_iterated:
            raise BrokenPipeError("Cannot use this method if the iterator has already been used.")
        ret: SetMultimap[DataRecordDescriptor, DataRecord] = SetMultimap()
        for desc, partial_list in self:
            ret.put_all(desc, partial_list)
        return ret

    def __init__(self, records_to_query: List[DataRecord], side_link_field_name: str, user: SapioUser,
                 first_page_criteria: DataRecordSideLinkFromPageCriteria = None):
        super().__init__(user, first_page_criteria)
        self.records_to_query = records_to_query
        self.side_link_field_name = side_link_field_name

    def get_next_page_result(self) -> (Optional[PagerResultCriteriaType], Queue[PagerResultType]):
        page_result: DataRecordSideLinkFromListPageResult = self.data_record_manager.get_side_link_from_list(
            self.records_to_query, self.side_link_field_name, self.next_page_criteria)
        result_queue: Queue[(DataRecordDescriptor, List[DataRecord])] = Queue()
        for item in page_result.result_map.items():
            result_queue.put(item)
        if not page_result.is_next_page_available:
            return None, result_queue
        return page_result.next_page_criteria, result_queue

    def default_first_page_criteria(self) -> PagerResultCriteriaType:
        return DataRecordSideLinkFromPageCriteria(page_size=_default_record_page_size)


class GetBackSideLinkListAutoPager(SapioPyAutoPager[
                                         DataRecordSideLinkToPageCriteria, (DataRecordDescriptor, List[DataRecord])]):
    """
    Obtain reverse side link results in a memory-efficient iterator that spans through all pages.
    Note that the item sematic is (Record Descriptor) -> (PARTIAL list of reverse link data records)
    """
    records_to_query: List[DataRecord]
    reverse_link_dt_name: str
    reverse_link_field_name: str

    def get_all_at_once(self) -> SetMultimap[DataRecordDescriptor, DataRecord]:
        """
        Get the results of all pages. Be cautious of client memory usage.
        """
        if self.has_iterated:
            raise BrokenPipeError("Cannot use this method if the iterator has already been used.")
        ret: SetMultimap[DataRecordDescriptor, DataRecord] = SetMultimap()
        for desc, partial_list in self:
            ret.put_all(desc, partial_list)
        return ret

    def __init__(self, records_to_query: List[DataRecord], reverse_link_dt_name: str, reverse_link_field_name: str,
                 user: SapioUser, first_page_criteria: DataRecordSideLinkToPageCriteria = None):
        super().__init__(user, first_page_criteria)
        self.records_to_query = records_to_query
        self.reverse_link_dt_name = reverse_link_dt_name
        self.reverse_link_field_name = reverse_link_field_name

    def get_next_page_result(self) -> (Optional[PagerResultCriteriaType], Queue[PagerResultType]):
        page_result: DataRecordSideLinkToListPageResult = self.data_record_manager.get_side_link_to_list(
            self.records_to_query, linked_data_type_name=self.reverse_link_dt_name,
            side_link_field_name=self.reverse_link_field_name, paging_criteria=self.next_page_criteria)
        result_queue: Queue[(DataRecordDescriptor, List[DataRecord])] = Queue()
        for item in page_result.result_map.items():
            result_queue.put(item)
        if not page_result.is_next_page_available:
            return None, result_queue
        return page_result.next_page_criteria, result_queue

    def default_first_page_criteria(self) -> PagerResultCriteriaType:
        return DataRecordSideLinkToPageCriteria(page_size=_default_record_page_size)


class AbstractSimpleRecordAutoPager(SapioPyAutoPager[DataRecordPojoPageCriteria, DataRecord], ABC):

    def get_all_at_once(self) -> List[DataRecord]:
        if self.has_iterated:
            raise BrokenPipeError("Cannot use this method if the iterator has already been used.")
        ret: List[DataRecord] = []
        for record in self:
            ret.append(record)
        return ret

    def __init__(self, user: SapioUser, first_page_criteria: DataRecordPojoPageCriteria = None):
        super().__init__(user, first_page_criteria)

    def default_first_page_criteria(self) -> PagerResultCriteriaType:
        return DataRecordPojoPageCriteria(page_size=_default_record_page_size)

    @abstractmethod
    def get_page_result(self) -> DataRecordPojoListPageResult:
        pass

    def get_next_page_result(self) -> (Optional[PagerResultCriteriaType], Queue[PagerResultType]):
        page_result = self.get_page_result()
        queue: Queue[DataRecord] = Queue()
        for record in page_result.result_list:
            queue.put(record)
        if not page_result.is_next_page_available:
            return None, queue
        else:
            return page_result.next_page_criteria, queue


class GetElnEntryRecordAutoPager(AbstractSimpleRecordAutoPager):
    """
    Auto pages all records in an ELN entry.
    """
    eln_experiment_id: int
    entry_id: int
    eln_manager: ElnManager

    def __init__(self, eln_experiment_id: int, entry_id: int,
                 user: SapioUser, first_page_criteria: DataRecordPojoPageCriteria = None):
        super().__init__(user, first_page_criteria)
        self.eln_experiment_id = eln_experiment_id
        self.entry_id = entry_id
        self.eln_manager = ElnManager(user)

    def get_page_result(self) -> DataRecordPojoListPageResult:
        return self.eln_manager.get_data_records_for_entry(
            self.eln_experiment_id, self.entry_id, self.next_page_criteria)


class QueryDataRecordsAutoPager(AbstractSimpleRecordAutoPager):
    """
    This handles the auto paging for query_data_records taking in type name, field name, value list
    """
    data_type_name: str
    data_field_name: str
    value_list: list

    def __init__(self, data_type_name: str, data_field_name: str, value_list: list,
                 user: SapioUser, first_page_criteria: DataRecordPojoPageCriteria = None):
        super().__init__(user, first_page_criteria)
        self.data_type_name = data_type_name
        self.data_field_name = data_field_name
        self.value_list = value_list

    def get_page_result(self) -> DataRecordPojoListPageResult:
        return self.data_record_manager.query_data_records(
            self.data_type_name, self.data_field_name, self.value_list, self.next_page_criteria)


class QueryDataRecordByIdListAutoPager(AbstractSimpleRecordAutoPager):
    """
    This handles auto paging for query_data_records_by_id
    """
    data_type_name: str
    record_id_list: List[int]

    def __init__(self, data_type_name: str, record_id_list: List[int],
                 user: SapioUser, first_page_criteria: DataRecordPojoPageCriteria = None):
        super().__init__(user, first_page_criteria)
        self.data_type_name = data_type_name
        self.record_id_list = record_id_list

    def get_page_result(self) -> DataRecordPojoListPageResult:
        return self.data_record_manager.query_data_records_by_id(
            self.data_type_name, self.record_id_list, self.next_page_criteria)


class QueryAllRecordsOfTypeAutoPager(AbstractSimpleRecordAutoPager):
    """
    This handles auto paging of getting all records for query_all_records_of_type
    """
    data_type_name: str

    def __init__(self, data_type_name: str,
                 user: SapioUser, first_page_criteria: DataRecordPojoPageCriteria = None):
        super().__init__(user, first_page_criteria)
        self.data_type_name = data_type_name

    def get_page_result(self) -> DataRecordPojoListPageResult:
        return self.data_record_manager.query_all_records_of_type(self.data_type_name, self.next_page_criteria)


class GetParentsSingleRecordAutoPager(AbstractSimpleRecordAutoPager):
    """
    This is get parents of a single data record. Avoid using this class in a loop for multiple records by using batch.
    """
    record_id: int
    child_type_name: str
    parent_type_name: str

    def __init__(self, record_id: int, child_type_name: str, parent_type_name: str,
                 user: SapioUser, first_page_criteria: DataRecordPojoPageCriteria = None):
        super().__init__(user, first_page_criteria)
        self.record_id = record_id
        self.child_type_name = child_type_name
        self.parent_type_name = parent_type_name

    def get_page_result(self) -> DataRecordPojoListPageResult:
        return self.data_record_manager.get_parents(
            self.record_id, self.child_type_name, self.parent_type_name, self.next_page_criteria)


class GetChildrenSingleRecordAutoPager(AbstractSimpleRecordAutoPager):
    """
    This is get children of a single data record. Avoid using this class in a loop for multiple records by using batch.
    """
    record_id: int
    child_type_name: str

    def __init__(self, record_id: int, child_type_name: str,
                 user: SapioUser, first_page_criteria: DataRecordPojoPageCriteria = None):
        super().__init__(user, first_page_criteria)
        self.record_id = record_id
        self.child_type_name = child_type_name

    def get_page_result(self) -> DataRecordPojoListPageResult:
        return self.data_record_manager.get_children(
            self.record_id, self.child_type_name, self.next_page_criteria)


class GetAncestorsSingleRecordAutoPager(AbstractSimpleRecordAutoPager):
    """
    This is get ancestors of a single data record. Avoid using this class in a loop for multiple records by using batch.
    """
    record_id: int
    descendant_type_name: str
    ancestor_type_name: str

    def __init__(self, record_id: int, descendant_type_name: str, ancestor_type_name: str,
                 user: SapioUser, first_page_criteria: DataRecordPojoPageCriteria = None):
        super().__init__(user, first_page_criteria)
        self.record_id = record_id
        self.descendant_type_name = descendant_type_name
        self.ancestor_type_name = ancestor_type_name

    def get_page_result(self) -> DataRecordPojoListPageResult:
        return self.data_record_manager.get_ancestors(
            self.record_id, self.descendant_type_name, self.ancestor_type_name, self.next_page_criteria)


class GetDescendantsSingleRecordAutoPager(AbstractSimpleRecordAutoPager):
    """
    Get descendants of a single data record. Avoid using this class in a loop for multiple records by using batch.
    """
    record_id: int
    descendant_type_name: str

    def __init__(self, record_id: int, descendant_type_name: str,
                 user: SapioUser, first_page_criteria: DataRecordPojoPageCriteria = None):
        super().__init__(user, first_page_criteria)
        self.record_id = record_id
        self.descendant_type_name = descendant_type_name

    def get_page_result(self) -> DataRecordPojoListPageResult:
        return self.data_record_manager.get_descendants(
            self.record_id, self.descendant_type_name, self.next_page_criteria)


class CustomReportAutoPager(SapioPyAutoPager[CustomReportCriteria, list[Any]]):

    def get_all_at_once(self) -> list[list[Any]]:
        """
        Get the results of all pages. Be cautious of client memory usage.
        """
        if self.has_iterated:
            raise BrokenPipeError("Cannot use this method if the iterator has already been used.")
        ret: list[list[Any]] = list()
        for row in self:
            ret.append(row)
        return ret

    def __init__(self, user: SapioUser, report_criteria: CustomReportCriteria):
        """
        IMPORTANT NOTICE: Custom reports that are not single data type (i.e. they have terms or columns from multiple
        data types) may not be 100% time accurate. Such reports use the system's ancestor table to retrieve the
        relationships, and this table takes some time to update after relationships are updated, especially for more
        populous data types. If you need 100% time accurate results to the current state of the records and
        relationships in the database, you should query for the records directly instead of using a custom report.
        """
        first_page_criteria = copy(report_criteria)
        if first_page_criteria.page_number is None or first_page_criteria.page_number < 0:
            first_page_criteria.page_number = 0
        if first_page_criteria.page_size is None or first_page_criteria.page_size <= 0:
            first_page_criteria.page_size = _default_report_page_size
        super().__init__(user, first_page_criteria)

    def default_first_page_criteria(self) -> PagerResultCriteriaType:
        raise ValueError("The custom report criteria is required field.")

    def get_next_page_result(self) -> (Optional[PagerResultCriteriaType], Queue[PagerResultType]):
        from sapiopylib.rest.DataMgmtService import DataMgmtServer
        report_man = DataMgmtServer.get_custom_report_manager(self.user)
        report: CustomReport = report_man.run_custom_report(self.next_page_criteria)
        queue: Queue[list[Any]] = Queue()
        for row in report.result_table:
            queue.put(row)
        if report.has_next_page:
            next_page_criteria = copy(self.next_page_criteria)
            next_page_criteria.page_number += 1
            return next_page_criteria, queue
        else:
            return None, queue