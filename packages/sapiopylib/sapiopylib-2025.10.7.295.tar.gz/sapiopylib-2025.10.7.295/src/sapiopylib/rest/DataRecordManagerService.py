from __future__ import annotations

import urllib.parse
from typing import Union, Any, List, Dict, IO, Callable, Optional
from weakref import WeakValueDictionary

from pandas import DataFrame

from sapiopylib.rest.User import SapioUser, SapioServerException
from sapiopylib.rest.pojo.DataRecord import from_json_record_list, to_record_json_list, DataRecord
from sapiopylib.rest.pojo.DataRecordPaging import DataRecordPojoPageCriteria, DataRecordPojoListPageResult, \
    DataRecordPojoHierarchyPageCriteria, DataRecordPojoHierarchyListPageResult
from sapiopylib.rest.pojo.DataRecordSideLinkPaging import DataRecordSideLinkFromPageCriteria, \
    DataRecordSideLinkFromListPageResult, DataRecordSideLinkToPageCriteria, DataRecordSideLinkToListPageResult
from sapiopylib.rest.pojo.acl import AccessType, DataRecordACL, SetDataRecordACLCriteria


class DataRecordManager:
    """
    Manages data records in Sapio.
    """
    user: SapioUser

    __instances: WeakValueDictionary[SapioUser, DataRecordManager] = WeakValueDictionary()
    __initialized: bool

    def __new__(cls, user: SapioUser):
        """
        Observes singleton pattern per record model manager object.

        :param user: The user that will make the webservice request to the application.
        """
        obj = cls.__instances.get(user)
        if not obj:
            obj = object.__new__(cls)
            obj.__initialized = False
            cls.__instances[user] = obj
        return obj

    def __init__(self, user: SapioUser):
        """
        Obtains data record manager to perform data record operations.

        :param user: The user that will make the webservice request to the application.
        """
        if self.__initialized:
            return
        self.user = user
        self.__initialized = True

    @staticmethod
    def get_data_frame(records: List[DataRecord]) -> DataFrame:
        """
        Get a pandas data frame for a list of records.

        :param records: The records to get data frames for.
        :return: A consolidated data frame among all columns across all data records.
            The data records do not have to be of the same time, and records with same field names
            will be joined under a single key.
        """
        data_dict: Dict[str, List[Any]] = dict()
        cur_length = 0
        for record in records:
            fields = record.get_fields()
            for key, value in fields.items():
                if key not in data_dict:
                    init_list = [None] * cur_length
                    data_dict[key] = init_list
                data_dict[key].append(value)
            cur_length += 1
        return DataFrame.from_dict(data_dict, orient='columns')

    def query_data_records(self, data_type_name: str, data_field_name: str,
                           value_list: list,
                           paging_criteria: DataRecordPojoPageCriteria = None) -> DataRecordPojoListPageResult:
        """
        Query the system for records of the given type that have values in the given field that match the given values.

        :param data_type_name: The data type name of the records being queried for.
        :param data_field_name: The data field name that will be used when querying for records.
        :param value_list: The list of values to be used in the query. Similar in behavior to a SQL "IN" clause.
        :param paging_criteria: Optional paging criteria info for the current page. Note the maximum page size may be
            enforced by the system. If it is, a page size must be given that is less than or equal to the maximum.
            If not provided, returns the first page of results.
        :return: The query results from the current page, containing a list of the data records from the query,
            the current page information, and whether more pages exist after it.
        """
        params = {'dataTypeName': data_type_name,
                  'dataFieldName': data_field_name}
        self._append_query_param(paging_criteria, params)
        sub_path = '/datarecordmanager/querydatarecords'
        response = self.user.post(sub_path, params, value_list)
        self.user.raise_for_status(response)
        json_dict = response.json()
        return DataRecordPojoListPageResult.from_json(json_dict)

    def query_data_records_by_id(self, data_type_name: str, record_id_list: List[int],
                                 paging_criteria: DataRecordPojoPageCriteria = None) -> DataRecordPojoListPageResult:
        """
        Get a list of records given a list of their record IDs. This method will only return records of the given type
        that have one of the provided record IDs. The records are not guaranteed to be returned in the same
        order as the provided list.

        :param data_type_name: The data type name of the records being queried for.
        :param record_id_list: The list of record IDs to be used in the query.
        :param paging_criteria: Optional paging criteria info for the current page. Note the maximum page size may be
            enforced by the system. If it is, a page size must be given that is less than or equal to the maximum.
            If not provided, returns the first page of results.
        :return: The query results from the current page, containing a list of the data records from the query,
            the current page information, and whether more pages exist after it.
        """
        record_id_list.sort()
        params = {'dataTypeName': data_type_name}
        self._append_query_param(paging_criteria, params)
        sub_path = '/datarecordlist'
        response = self.user.post(sub_path, params=params, payload=record_id_list)
        self.user.raise_for_status(response)
        json_dict = response.json()
        return DataRecordPojoListPageResult.from_json(json_dict)

    def query_all_records_of_type(self, data_type_name: str,
                                  paging_criteria: DataRecordPojoPageCriteria = None) -> DataRecordPojoListPageResult:
        """
        Get a list of all records of the given data type.

        :param data_type_name: The data type name of the records being queried for.
        :param paging_criteria: Optional paging criteria info for the current page. Note the maximum page size may be
            enforced by the system. If it is, a page size must be given that is less than or equal to the maximum.
            If not provided, returns the first page of results.
        :return: The query results from the current page, containing a list of the data records from the query,
            the current page information, and whether more pages exist after it.
        """
        params = {'dataTypeName': data_type_name}
        self._append_query_param(paging_criteria, params)
        sub_path = '/datarecordlist/all'
        response = self.user.get(sub_path, params)
        self.user.raise_for_status(response)
        json_dict = response.json()
        return DataRecordPojoListPageResult.from_json(json_dict)

    def query_system_for_record(self, data_type_name: str, record_id: int) -> Optional[DataRecord]:
        """
        Get the record of the given type that has the provided record ID.

        :param data_type_name: The data type name of the record being queried for.
        :param record_id: The record ID of the record in the system.
        :return: The data record if available. None if not found.
        """
        params = {'dataTypeName': data_type_name,
                  'recordId': record_id}
        sub_path = '/datarecord'
        response = self.user.get(sub_path, params)
        self.user.raise_for_status(response)
        if response.status_code == 204 or self.user.is_null_response(response):
            return None
        json_dict = response.json()
        return DataRecord.from_json(json_dict)

    def get_parents(self, record_id: int, child_type_name: str, parent_type_name: str,
                    paging_criteria: Optional[DataRecordPojoPageCriteria] = None) -> DataRecordPojoListPageResult:
        """
        Get the parents of the given data type above the record with the given record ID and data type.

        :param record_id: The record ID of the child record to search from.
        :param child_type_name: The data type name of the child to search from.
        :param parent_type_name: The data type name of the parents to look for above the given record ID.
        :param paging_criteria: Optional paging criteria info for the current page. Note the maximum page size may be
            enforced by the system. If it is, a page size must be given that is less than or equal to the maximum.
            If not provided, returns the first page of results.
        :return: The query results from the current page, containing a list of the data records from the query,
            the current page information, and whether more pages exist after it.
        """
        params = {'recordId': record_id,
                  'childTypeName': child_type_name,
                  'parentTypeName': parent_type_name}
        self._append_query_param(paging_criteria, params)
        sub_path = '/datarecord/parents'
        response = self.user.get(sub_path, params)
        self.user.raise_for_status(response)
        json_dict = response.json()
        return DataRecordPojoListPageResult.from_json(json_dict)

    def get_parents_list(self, record_id_list: List[int], child_type_name: Optional[str], parent_type_name: str,
                         paging_criteria: Optional[DataRecordPojoHierarchyPageCriteria] = None) -> \
            DataRecordPojoHierarchyListPageResult:
        """
        Get the parents of the given type above the records with the given record IDs and data type.

        :param record_id_list: The record IDs of the child records to search from.
        :param child_type_name: The data type name of the children to search from.
            This is only required in high-performance high-volume data retrieval.
        :param parent_type_name: The data type name of the parents to look for above the given record IDs.
        :param paging_criteria: Optional paging criteria info for the current page. Note the maximum page size may be
            enforced by the system. If it is, a page size must be given that is less than or equal to the maximum.
            If not provided, returns the first page of results.
        :return: The query results from the current page, containing a dictionary of the data records from the query
            mapped by their child record, the current page information, and whether more pages exist after it.
        """
        try:
            record_id_list.sort()
            params = {'childTypeName': child_type_name,
                      'parentTypeName': parent_type_name}
            self._append_query_param(paging_criteria, params)
            sub_path = '/datarecordlist/parents'
            response = self.user.post(sub_path, params=params, payload=record_id_list)
            self.user.raise_for_status(response)
            json_dict = response.json()
            return DataRecordPojoHierarchyListPageResult.from_json(json_dict)
        except SapioServerException as e:
            if e.client_error.response.status_code == 405:
                # Method not found. Use the deprecated version to re-request
                self.user.log_warn("""
SAPIO PLATFORM VERSION MISMATCH. USING DEPRECATED WEBSERVICE CALL FORMAT.
This is unsupported. Use at your own risk!
                """)
                params = {'recordIdList': ','.join(str(x) for x in record_id_list),
                          'childTypeName': child_type_name,
                          'parentTypeName': parent_type_name}
                self._append_query_param(paging_criteria, params)
                sub_path = '/datarecordlist/parents'
                response = self.user.get(sub_path, params)
                response.raise_for_status()
                json_dict = response.json()
                return DataRecordPojoHierarchyListPageResult.from_json(json_dict)
            else:
                raise e

    def get_children(self, record_id: int, child_type_name: str,
                     paging_criteria: Optional[DataRecordPojoPageCriteria] = None) -> DataRecordPojoListPageResult:
        """
        Get the children of the given data type below the record with the given record ID.

        :param record_id: The record ID of the parent record to search from.
        :param child_type_name: The data type name of the children to look for below the given record ID.
        :param paging_criteria: Optional paging criteria info for the current page. Note the maximum page size may be
            enforced by the system. If it is, a page size must be given that is less than or equal to the maximum.
            If not provided, returns the first page of results.
        :return: The query results from the current page, containing a list of the data records from the query,
            the current page information, and whether more pages exist after it.
        """
        params = {'recordId': record_id,
                  'childTypeName': child_type_name}
        self._append_query_param(paging_criteria, params)
        sub_path = '/datarecord/children'
        response = self.user.get(sub_path, params)
        self.user.raise_for_status(response)
        json_dict = response.json()
        return DataRecordPojoListPageResult.from_json(json_dict)

    def get_children_list(self, record_id_list: List[int], child_type_name: str,
                          paging_criteria: Optional[DataRecordPojoHierarchyPageCriteria] = None) -> \
            DataRecordPojoHierarchyListPageResult:
        """
        Get the children of the given type below the records with the given record IDs.

        :param record_id_list: The record IDs of the parent records.
        :param child_type_name: The data type name of the children to look for below the given record IDs.
        :param paging_criteria: Optional paging criteria info for the current page. Note the maximum page size may be
            enforced by the system. If it is, a page size must be given that is less than or equal to the maximum.
            If not provided, returns the first page of results.
        :return: The query results from the current page, containing a dictionary of the data records from the query
            mapped by their parent record, the current page information, and whether more pages exist after it.
        """
        try:
            record_id_list.sort()
            params = {'childTypeName': child_type_name}
            self._append_query_param(paging_criteria, params)
            sub_path = '/datarecordlist/childrenbyid'
            response = self.user.post(sub_path, params=params, payload=record_id_list)
            self.user.raise_for_status(response)
            json_dict = response.json()
            return DataRecordPojoHierarchyListPageResult.from_json(json_dict)
        except SapioServerException as e:
            if e.client_error.response.status_code == 405:
                # Method not found. Use the deprecated version to re-request
                self.user.log_warn("""
SAPIO PLATFORM VERSION MISMATCH. USING DEPRECATED WEBSERVICE CALL FORMAT.
This is unsupported. Use at your own risk!
                """)
                params = {'recordIdList': ','.join(str(x) for x in record_id_list),
                          'childTypeName': child_type_name}
                self._append_query_param(paging_criteria, params)
                sub_path = '/datarecordlist/children'
                response = self.user.get(sub_path, params)
                response.raise_for_status()
                json_dict = response.json()
                return DataRecordPojoHierarchyListPageResult.from_json(json_dict)
            else:
                raise e

    def get_ancestors(self, record_id: int, descendant_type_name: str, ancestor_type_name: str,
                      paging_criteria: Optional[DataRecordPojoPageCriteria] = None) -> DataRecordPojoListPageResult:
        """
        Get the ancestors of the given data type above the record with the given record ID and data type.

        :param record_id: The record ID of the parent record to search from.
        :param descendant_type_name: The data type name of the descendant to search from.
        :param ancestor_type_name: The data type name of the ancestors to look for below the given record ID.
        :param paging_criteria: Optional paging criteria info for the current page. Note the maximum page size may be
            enforced by the system. If it is, a page size must be given that is less than or equal to the maximum.
            If not provided, returns the first page of results.
        :return: The query results from the current page, containing a list of the data records from the query,
            the current page information, and whether more pages exist after it.
        """
        params = {'recordId': record_id,
                  'descendantTypeName': descendant_type_name,
                  "ancestorTypeName": ancestor_type_name}
        self._append_query_param(paging_criteria, params)
        sub_path = '/datarecord/ancestors'
        response = self.user.get(sub_path, params)
        self.user.raise_for_status(response)
        json_dict = response.json()
        return DataRecordPojoListPageResult.from_json(json_dict)

    def get_ancestors_list(self, record_id_list: List[int], descendant_type_name: str, ancestor_type_name: str,
                           paging_criteria: Optional[DataRecordPojoHierarchyPageCriteria] = None) -> \
            DataRecordPojoHierarchyListPageResult:
        """
        Get the ancestors of the given type above the records with the given record IDs and data type.

        :param record_id_list: The record IDs of the descendant records to search from.
        :param descendant_type_name: The data type name of the descendants to search from.
        :param ancestor_type_name: The data type name of the ancestors to look for above the given record IDs.
        :param paging_criteria: Optional paging criteria info for the current page. Note the maximum page size may be
            enforced by the system. If it is, a page size must be given that is less than or equal to the maximum.
            If not provided, returns the first page of results.
        :return: The query results from the current page, containing a dictionary of the data records from the query
            mapped by their descendant record, the current page information, and whether more pages exist after it.
        """
        record_id_list.sort()
        params = {'descendantTypeName': descendant_type_name,
                  "ancestorTypeName": ancestor_type_name}
        self._append_query_param(paging_criteria, params)
        sub_path = '/datarecordlist/ancestors'
        response = self.user.post(sub_path, params=params, payload=record_id_list)
        self.user.raise_for_status(response)
        json_dict = response.json()
        return DataRecordPojoHierarchyListPageResult.from_json(json_dict)

    def get_descendants(self, record_id: int, descendant_type_name: str,
                        paging_criteria: Optional[DataRecordPojoPageCriteria] = None) -> DataRecordPojoListPageResult:
        """
        Get the descendants of the given data type below the record with the given record ID.

        :param record_id: The record ID of the ancestor record to search from.
        :param descendant_type_name: The data type name of the descendants to look for below the given record ID.
        :param paging_criteria: Optional paging criteria info for the current page. Note the maximum page size may be
            enforced by the system. If it is, a page size must be given that is less than or equal to the maximum.
            If not provided, returns the first page of results.
        :return: The query results from the current page, containing a list of the data records from the query,
            the current page information, and whether more pages exist after it.
        """
        params = {'recordId': record_id,
                  'descendantTypeName': descendant_type_name}
        self._append_query_param(paging_criteria, params)
        sub_path = '/datarecord/descendants'
        response = self.user.get(sub_path, params)
        self.user.raise_for_status(response)
        json_dict = response.json()
        return DataRecordPojoListPageResult.from_json(json_dict)

    def get_descendants_list(self, record_id_list: List[int], descendant_type_name: str,
                             paging_criteria: Optional[DataRecordPojoHierarchyPageCriteria] = None) -> \
            DataRecordPojoHierarchyListPageResult:
        """
        Get the descendants of the given type below the records with the given record IDs.

        :param record_id_list: The record IDs of the ancestor records.
        :param descendant_type_name: The data type name of the descendants to look for below the given record IDs.
        :param paging_criteria: Optional paging criteria info for the current page. Note the maximum page size may be
            enforced by the system. If it is, a page size must be given that is less than or equal to the maximum.
            If not provided, returns the first page of results.
        :return: The query results from the current page, containing a dictionary of the data records from the query
            mapped by their ancestor record, the current page information, and whether more pages exist after it.
        """
        record_id_list.sort()
        params = {'descendantTypeName': descendant_type_name}
        self._append_query_param(paging_criteria, params)
        sub_path = '/datarecordlist/descendants'
        response = self.user.post(sub_path, params=params, payload=record_id_list)
        self.user.raise_for_status(response)
        json_dict = response.json()
        return DataRecordPojoHierarchyListPageResult.from_json(json_dict)

    def add_data_record(self, data_type_name: str) -> DataRecord:
        """
        Create a single new record of the provided data type. Only default values and system fields will be set on the
        record before it is stored.

        :param data_type_name: The data type name of the record to create in the system.
        :return: The record object representing the data record in the system.
        """
        sub_path = '/datarecord/' + urllib.parse.quote(data_type_name)
        response = self.user.post(sub_path)
        self.user.raise_for_status(response)
        json_dict = response.json()
        return DataRecord.from_json(json_dict)

    def add_data_records(self, data_type_name: str, num_to_add: int) -> List[DataRecord]:
        """
        Create multiple new record of the provided data type. Only default values and system fields will be set on the
        record before it is stored.

        :param data_type_name: The data type name of the records to create in the system.
        :param num_to_add: The number of records to create.
        :return: A list of record objects representing the data records in the system.
        """
        sub_path = '/datarecordlist/' + urllib.parse.quote(data_type_name)
        params = {'numberToAdd': num_to_add}
        response = self.user.post(sub_path, params)
        self.user.raise_for_status(response)
        json_list = response.json()
        return [DataRecord.from_json(json) for json in json_list]

    def add_data_records_with_data(self, data_type_name: str,
                                   field_map_list: List[Dict[str, Any]]
                                   ) -> List[DataRecord]:
        """
        Create new records of the provided data type in the system while also setting fields on the records before
        they are stored.

        :param data_type_name: The data type name of the records to create in the system.
        :param field_map_list: The list of field maps of the data records to be added. Each dictionary in the list
            represents the fields for a new record. The dictionary keys are the data field names of the fields on the
            data type, with the dictionary values being the values that those data fields will be set to.
        :return: A list of record objects representing the data records in the system.
        """
        sub_path = '/datarecordlist/fields/' + urllib.parse.quote(data_type_name)
        response = self.user.post(sub_path, payload=field_map_list)
        self.user.raise_for_status(response)
        json_list = response.json()
        return [DataRecord.from_json(json) for json in json_list]

    def set_attachment_data(self, record: DataRecord,
                            file_name: str, data_stream: IO) -> None:
        """
        Upload file bytes to be used as the attachment data for the given record.

        :param record: The attachment record to upload the file bytes to.
        :param file_name: The name of the file being uploaded as the attachment data.
        :param data_stream: The stream to be consumed as uploaded binary data.
        """
        data_type_name = record.get_data_type_name()
        record_id = record.get_record_id()
        sub_path = '/datarecord/attachment/' + urllib.parse.quote(data_type_name) + "/" + \
                   urllib.parse.quote(str(record_id)) + "/" + urllib.parse.quote(file_name)
        response = self.user.post_data_stream(sub_path, data_stream)
        self.user.raise_for_status(response)

    def get_attachment_data(self, record: DataRecord,
                            data_sink: Callable[[bytes], None]) -> None:
        """
        Take the attachment data stream and consume the data in a data sink method.

        :param record: The record to obtain attachment data from.
        :param data_sink: The data sink method to consume the data stream of the attachment.
        """
        data_type_name = record.get_data_type_name()
        record_id = record.get_record_id()
        sub_path = '/datarecord/attachment/' + urllib.parse.quote(data_type_name) + "/" + \
                   urllib.parse.quote(str(record_id))
        self.user.consume_octet_stream_get(sub_path, data_sink)

    def set_record_image(self, record: DataRecord,
                         data_stream: IO) -> None:
        """
        Set the record image of the given data record.

        :param record: The record to set the image for.
        :param data_stream: The stream to be consumed as uploaded image data.
        """
        data_type_name = record.get_data_type_name()
        record_id = record.get_record_id()
        sub_path = '/datarecord/image/' + urllib.parse.quote(data_type_name) + "/" + \
                   urllib.parse.quote(str(record_id))
        response = self.user.post_data_stream(sub_path, data_stream)
        self.user.raise_for_status(response)

    def get_record_image(self, record: DataRecord,
                         data_sink: Callable[[bytes], None]) -> None:
        """
        Get the record image of the given data record.

        :param record: The record to get image from.
        :param data_sink: The data sink method to consume the data stream of the image.
        """
        data_type_name = record.get_data_type_name()
        record_id = record.get_record_id()
        sub_path = '/datarecord/image/' + urllib.parse.quote(data_type_name) + "/" + urllib.parse.quote(str(record_id))
        self.user.consume_octet_stream_get(sub_path, data_sink)

    def delete_data_record(self, record: DataRecord, recursive_delete: bool = False) -> None:
        """
        Delete a single data record from the system.

        :param record: The record to be deleted.
        :param recursive_delete: Whether to delete the record's descendants if there is no other lineage to those
            records.
        """
        data_type_name = record.get_data_type_name()
        record_id = record.get_record_id()
        sub_path = '/datarecord/' + urllib.parse.quote(data_type_name) + "/" + urllib.parse.quote(str(record_id))
        params = {'recursiveDelete': recursive_delete}
        response = self.user.delete(sub_path, params)
        self.user.raise_for_status(response)

    def delete_data_record_list(self, delete_list: List[DataRecord], recursive_delete: bool = False) -> None:
        """
        Delete a list of data records from the system.

        :param delete_list: The record list to be deleted from Sapio.
        :param recursive_delete: Whether to delete the record's descendants if there is no other lineage to those
            records.
        """
        sub_path = '/datarecordlist/delete/'
        params = {'recursiveDelete': recursive_delete}
        response = self.user.post(sub_path, params, to_record_json_list(delete_list))
        self.user.raise_for_status(response)

    # noinspection PyProtectedMember,PyUnresolvedReferences
    def commit_data_records(self, records_to_update: List[DataRecord]) -> None:
        """
        Update a list of records in the system with their new field maps from the given record objects.

        Unlike the regular web service 'set fields for records' method, only fields that have been changed will be set.
        Should this commit operation be successful, the field data changes being tracked will be cleared,
        and the new field maps will be committed.

        :param records_to_update: A list of data records to be updated in the system.
        """
        sub_path = '/datarecordlist/fields'
        changed_record_list: List[DataRecord] = list()
        for record in records_to_update:
            changed_record = DataRecord(record.get_data_type_name(), record.get_record_id(),
                                        record.get_changed_fields_clone(), record.is_new, record.is_deleted)
            changed_record_list.append(changed_record)
        payload = [x.to_json() for x in changed_record_list]
        response = self.user.put(sub_path, payload=payload)
        try:
            self.user.raise_for_status(response)
            for record in records_to_update:
                record.commit_changes()
        except Exception as e:
            for record in records_to_update:
                record.rollback()
            raise e

    def add_child(self, parent_record: DataRecord, child_record: DataRecord) -> Optional[DataRecord]:
        """
        Add an existing record as a child of another existing record.

        :param parent_record: The parent data record to add the child record to.
        :param child_record: The child data record to be added under the parent.
        :return: The child record that was added, expected to not be None.
        """
        sub_path = self.user.build_url(['datarecord', 'child',
                                        parent_record.get_data_type_name(), str(parent_record.get_record_id())])
        params = {'childTypeName': child_record.get_data_type_name(),
                  'childRecordId': child_record.get_record_id()}
        response = self.user.post(sub_path, params)
        self.user.raise_for_status(response)
        if self.user.is_null_response(response):
            return None
        json = response.json()
        return DataRecord.from_json(json)

    def add_children(self, parent_children_map: Dict[DataRecord, List[DataRecord]]) -> None:
        """
        Create multiple parent/child relationships between existing records in the system at once.

        :param parent_children_map: A dictionary where the keys are the parent data records and the values are a list
            of data records to be added as children of the key data record.
        """
        payload = dict()
        for parent, children_list in parent_children_map.items():
            if parent is None:
                continue
            if children_list is None or len(children_list) == 0:
                continue
            payload[parent.get_map_key_reference()] = to_record_json_list(children_list)
        sub_path = '/datarecordlist/children'
        response = self.user.put(sub_path, payload=payload)
        self.user.raise_for_status(response)

    def remove_children(self, parent_children_map: Dict[DataRecord, List[DataRecord]]) -> None:
        """
        Remove multiple parent/child relationships between existing records in the system at once.

        :param parent_children_map: A dictionary where the keys are the parent data records and the values are a list
            of data records to be removed as children of the key data record.
        """
        payload = dict()
        for parent, children_list in parent_children_map.items():
            if parent is None:
                continue
            if children_list is None or len(children_list) == 0:
                continue
            payload[parent.get_map_key_reference()] = to_record_json_list(children_list)
        sub_path = '/datarecordlist/children/delete'
        response = self.user.post(sub_path, payload=payload)
        self.user.raise_for_status(response)

    def add_children_for_record(self, parent: DataRecord, child_list: List[DataRecord]) -> None:
        """
        Add a list of existing records as children of another existing record.

        :param parent: The parent data record to add the child record to.
        :param child_list: A list of the children data records to be added under the parent.
        """
        data_type_name = parent.get_data_type_name()
        record_id = parent.get_record_id()
        sub_path = '/datarecord/children/' + urllib.parse.quote(data_type_name) + \
                   "/" + urllib.parse.quote(str(record_id))
        response = self.user.put(sub_path, payload=to_record_json_list(child_list))
        self.user.raise_for_status(response)

    def create_children_for_record(self, parent: DataRecord,
                                   child_type_name: str, num_to_add: int) -> List[DataRecord]:
        """
        Create multiple new record of the provided data type while at the same time adding them as children of an
        existing data record. Only default values and system fields will be set on the record before it is stored.

        :param parent: The existing parent data record.
        :param child_type_name: The data type name of the child records that will be created.
        :param num_to_add: The number of child records to be created.
        :return: A list of record objects representing the child data records in the system.
        """
        sub_path = self.user.build_url(['datarecord', 'children',
                                        parent.get_data_type_name(), str(parent.get_record_id())])
        params = {'childTypeName': child_type_name, 'numberToAdd': num_to_add}
        response = self.user.post(sub_path, params=params)
        self.user.raise_for_status(response)
        json_list = response.json()
        return [DataRecord.from_json(json) for json in json_list]

    def create_children_fields_for_record(self, parent: DataRecord, child_type_name: str,
                                          child_field_list: List[Dict[str, Any]]) -> \
            List[DataRecord]:
        """
        Create new records of the provided data type in the system while also setting fields on the records before
        they are stored and adding them as children of an existing data record.

        :param parent: The parent to create children for.
        :param child_type_name: The data type name of the child records to create in the system.
        :param child_field_list: The list of field maps of the data records to be added. Each dictionary in the list
            represents the fields for a new record. The dictionary keys are the data field names of the fields on the
            data type, with the dictionary values being the values that those data fields will be set to.
        :return: A list of record objects representing the child data records in the system.
        """
        sub_path = self.user.build_url(['datarecord', 'children', 'fields',
                                        parent.get_data_type_name(), str(parent.get_record_id())])
        params = {'childTypeName': child_type_name}
        response = self.user.post(sub_path, params, child_field_list)
        self.user.raise_for_status(response)
        json_list = response.json()
        return [DataRecord.from_json(json) for json in json_list]

    def create_children_fields_for_parents(self, child_type_name: str,
                                           children_field_map_list_by_parent:
                                           Dict[DataRecord, List[Dict[str, Any]]]
                                           ) -> Dict[DataRecord, List[DataRecord]]:
        """
        Create new records of the provided data type in the system while also setting fields on the records before
        they are stored and creating multiple parent/child relationships between the new records and existing records
        in the system at once.
        
        :param child_type_name: The data type name of the child records to create in the system.
        :param children_field_map_list_by_parent: A dictionary where the keys are the parent data records and the values
            are a list of field maps to create records that will be added as children of the key data record. Each
            dictionary in this list represents the fields for a new record. The dictionary keys are the data field names
            of the fields on the data type, with the dictionary values being the values that those data fields will be
            set to.
        :return: A dictionary mapping each parent record to a list of their newly created child data records.
        """
        parent_record_by_map_key = {rec.get_map_key_reference(): rec for rec in
                                    children_field_map_list_by_parent.keys()}

        sub_path = self.user.build_url(['datarecordlist', 'children'])
        params = {'childTypeName': child_type_name}
        payload: Dict[str, List[Dict[str, Any]]] = dict()
        for parent, children_field_map_list in children_field_map_list_by_parent.items():
            if parent is None:
                continue
            if children_field_map_list is None or len(children_field_map_list) == 0:
                continue
            payload[parent.get_map_key_reference()] = children_field_map_list
        response = self.user.post(sub_path, params, payload)
        self.user.raise_for_status(response)
        json: dict = response.json()
        ret: Dict[DataRecord, List[DataRecord]] = dict()
        for parent_map_key, value in json.items():
            key_pojo = parent_record_by_map_key.get(parent_map_key)
            value_list = from_json_record_list(value)
            ret[key_pojo] = value_list
        return ret

    def has_access(self, access_type: AccessType, record_list: List[DataRecord]) -> \
            List[DataRecord]:
        """
        Check if the user has the given access type to the provided records.

        :param access_type: The type of access to check for. Access types that can be checked are read, write, and
            delete permissions.
        :param record_list: The list of records to check access for.
        :return: A sub-list of the original list of records that have the requested access; if the input and output
            are equivalent then the user has the requested access for all records of the input, while if the output
            is empty then the user has access to none of the input records.
        """
        sub_path = self.user.build_url(['datarecord', 'access', access_type.name])
        payload = to_record_json_list(record_list)
        response = self.user.post(sub_path, payload=payload)
        self.user.raise_for_status(response)
        json = response.json()
        return from_json_record_list(json)

    def add_data_records_data_pump(self, data_type_name: str, field_map_list: List[Dict[str, Any]]) -> List[int]:
        """
        Create new high volume data type records in the system while also setting their fields.

        This call will bypass overhead surrounding the creation of data records in the server and directly stream data
        to the database. Intended for creating a large number of HVDT records at once.

        :param data_type_name: The data type name to insert records for. The data type must be a high volume data type.
        :param field_map_list: The list of field maps of the data records to be added. Each dictionary in the list
            represents the fields for a new record. The dictionary keys are the data field names of the fields on the
            data type, with the dictionary values being the values that those data fields will be set to.
        :return: An ordered list of record IDs of the records that were added to the database, in the same order as
            the input field map list data.
        """
        sub_path = self.user.build_url(['datarecordlist', 'fields', data_type_name, 'datapump'])
        response = self.user.post(sub_path, payload=field_map_list)
        self.user.raise_for_status(response)
        ret: List[int] = response.json()
        return ret

    def add_children_data_pump(self, child_type_name: str,
                               parent_child_field_map: Dict[DataRecord, List[Dict[str, Any]]]) \
            -> Dict[DataRecord, List[int]]:
        """
        Create new high volume data type records in the system while also setting their fields and creating multiple
        parent/child relationships between the new records and existing records in the system at once.

        This call will bypass overhead surrounding the creation of data records in the server and directly stream data
        to the database. Intended for creating a large number of HVDT records at once.

        :param child_type_name: The data type name to insert records for. The data type must be a high volume data type.
        :param parent_child_field_map: A dictionary where the keys are the parent data records and the values
            are a list of field maps to create records that will be added as children of the key data record. Each
            dictionary in this list represents the fields for a new record. The dictionary keys are the data field names
            of the fields on the data type, with the dictionary values being the values that those data fields will be
            set to.
        :return: A dictionary mapping each parent record to a list of the record IDs of their newly created children.
            The record ID lists are in the same order as the field map lists from the input.
        """
        sub_path = self.user.build_url(['datarecordlist', 'children', 'datapump'])
        params = {
            'childTypeName': child_type_name
        }
        map_key_to_record: Dict[str, DataRecord] = dict()
        parent_child_field_map_pojo: Dict[str, List[Dict[str, Any]]] = dict()
        for record, children_field_map_list in parent_child_field_map.items():
            map_key = record.get_map_key_reference()
            parent_child_field_map_pojo[map_key] = children_field_map_list
            map_key_to_record[map_key] = record
        response = self.user.post(sub_path, params=params, payload=parent_child_field_map_pojo)
        self.user.raise_for_status(response)
        ret_json: Dict[str, List[int]] = response.json()
        ret: Dict[DataRecord, List[int]] = dict()
        for map_key, record_id_list in ret_json.items():
            parent_record: DataRecord = map_key_to_record.get(map_key)
            ret[parent_record] = record_id_list
        return ret

    def get_side_link_to_list(self, data_record_list: List[DataRecord], linked_data_type_name: str,
                              side_link_field_name: str, paging_criteria: Optional[DataRecordSideLinkToPageCriteria]
                              = None) -> DataRecordSideLinkToListPageResult:
        """
        Get the side linked records of the given type that point back to the given records.

        :param data_record_list: The list of records to retrieve side links to.
        :param linked_data_type_name: The data type name of the side linked records.
        :param side_link_field_name: The data field name on the linked_data_type_name that points back to the given
            records.
        :param paging_criteria: Optional paging criteria info for the current page. Note the maximum page size may be
            enforced by the system. If it is, a page size must be given that is less than or equal to the maximum.
            If not provided, returns the first page of results.
        :return: The query results from the current page, containing a dictionary from the record key
            'DataTypeName:RecordId' to arrays of data records that are side linked to the provided list of records,
            the current page information, and whether more pages exist after it.
        """
        data_record_list.sort()
        params = {'linkedDataTypeName': linked_data_type_name,
                  'sideLinkedFieldName': side_link_field_name}
        self._append_query_param(paging_criteria, params)
        sub_path = '/datarecordlist/sidelinksto'
        request_body = [x.to_json() for x in data_record_list]
        response = self.user.post(sub_path, params, request_body)
        self.user.raise_for_status(response)
        json_dict = response.json()
        return DataRecordSideLinkToListPageResult.from_json(json_dict)

    def get_side_link_from_list(self, data_record_list: List[DataRecord], side_link_field_name: str,
                                paging_criteria: Optional[DataRecordSideLinkFromPageCriteria] = None) -> \
            DataRecordSideLinkFromListPageResult:
        """
        Get the side linked records from the given records referenced by the given field name.

        :param data_record_list: The list of records to retrieve side links from.
        :param side_link_field_name: The data field name on the given record that points to the records to retrieve.
        :param paging_criteria: Optional paging criteria info for the current page. Note the maximum page size may be
            enforced by the system. If it is, a page size must be given that is less than or equal to the maximum.
            If not provided, returns the first page of results.
        :return: The query results from the current page, containing a dictionary from the record key
            'DataTypeName:RecordId' to arrays of data records that are side linked from the provided list of records,
            the current page information, and whether more pages exist after it.
        """
        data_record_list.sort()
        params = {'sideLinkedFieldName': side_link_field_name}
        self._append_query_param(paging_criteria, params)
        sub_path = '/datarecordlist/sidelinksfrom'
        request_body = [x.to_json() for x in data_record_list]
        response = self.user.post(sub_path, params, request_body)
        self.user.raise_for_status(response)
        json_dict = response.json()
        return DataRecordSideLinkFromListPageResult.from_json(json_dict)

    def get_data_record_acl(self, data_type_name: str, record_id_list: list[int]) -> list[DataRecordACL]:
        """
        Get the DataRecordACL for the provided list of record IDs.
        The DataRecordACL will be returned as a list of DataRecordACLPojo objects.
        :param data_type_name: The data type name of the records to retrieve ACL for
        :param record_id_list: The list of record IDs of the records to retrieve ACL for.
        :return: The list of data record ACL in the same order as the original record ID list provided.
        """
        sub_path = self.user.build_url(['datarecord', 'datarecordacl', data_type_name])
        response = self.user.post(sub_path, payload=record_id_list)
        self.user.raise_for_status(response)
        json_list: list[dict[str, Any]] = response.json()
        return [DataRecordACL.from_json(x) for x in json_list]

    def set_data_record_acl(self, criteria: SetDataRecordACLCriteria) -> None:
        """
        Set the DataRecordACL for the provided list of records.

        This operation will require ACL Management privilege on either the record or on the user/active group's system privilege.
        :param criteria: The updates to be committed.
        """
        sub_path = "/datarecord/datarecordacl"
        response = self.user.post(sub_path, payload=criteria.to_json())
        self.user.raise_for_status(response)

    def revert_data_record_acl(self, data_record_list: list[DataRecord]) -> None:
        """
        Revert the ACL IDs that are set on the given records so that the records will inherit privileges from their parents again.

        This operation will require ACL Management privilege on either the record or on the user/active group's system privilege.
        :param data_record_list: The list of DataRecordPojos to have their privileges reverted to inherit from their parents.
        """
        sub_path = '/datarecord/datarecordacl/revert'
        response = self.user.post(sub_path, payload=[x.to_json() for x in data_record_list])
        self.user.raise_for_status(response)

    def get_last_saved_field_list(self, data_type_name: str, record_id_list: list[int]) -> dict[int, dict[str, Any]]:
        """
        Get the last saved value list for the list of data records.
        An exception will be thrown for any records that cannot be searched.
        :param data_type_name The data type name for all the records to retrieve.
        :param record_id_list: The list of data records' record IDs to retrieve their last saved values.
        :return: Dictionary of field maps by field name. The list is in order of incoming data record list.
        """
        if not record_id_list or not data_type_name:
            return dict()
        sub_path = '/datarecordlist/getlastsaved'
        response = self.user.post(sub_path, params={'dataTypeName': data_type_name}, payload=list(record_id_list))
        self.user.raise_for_status(response)
        original: dict[str, Any] = dict(response.json())
        return {int(k): v for k, v in original.items()}

    @staticmethod
    def _append_query_param(paging_criteria: Union[
        None, DataRecordPojoPageCriteria, DataRecordPojoHierarchyPageCriteria, DataRecordSideLinkFromPageCriteria,
        DataRecordSideLinkToPageCriteria],
                            params: dict):
        if paging_criteria is None:
            return
        if isinstance(paging_criteria, DataRecordPojoPageCriteria):
            params['lastRetrievedRecordId'] = paging_criteria.last_retrieved_record_id
            params['pageSize'] = paging_criteria.page_size
        if isinstance(paging_criteria, DataRecordPojoHierarchyPageCriteria):
            params['lastSourceRecordId'] = paging_criteria.last_retrieved_source_record_id
            params['lastRetrievedRecordId'] = paging_criteria.last_retrieved_target_record_id
            params['pageSize'] = paging_criteria.page_size
        if isinstance(paging_criteria, DataRecordSideLinkFromPageCriteria):
            params['lastSourceRecordId'] = paging_criteria.last_retrieved_source_record_id
            params['pageSize'] = paging_criteria.page_size
        if isinstance(paging_criteria, DataRecordSideLinkToPageCriteria):
            params['lastSourceRecordId'] = paging_criteria.last_retrieved_source_recordId
            params['lastRetrievedRecordId'] = paging_criteria.last_retrieved_target_recordId
            params['pageSize'] = paging_criteria.page_size
