from __future__ import annotations

from typing import Any, List, Dict, IO, Callable, Optional
from weakref import WeakValueDictionary

from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.DataRecord import DataRecord, DataRecordDescriptor


class DataManager:
    """
    Manages data records in Sapio.
    """
    user: SapioUser

    __instances: WeakValueDictionary[SapioUser, DataManager] = WeakValueDictionary()
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
        :param user: The user that will make the webservice request to the application.
        """
        if self.__initialized:
            return
        self.user = user
        self.__initialized = True

    def export_to_xml(self, records: List[DataRecord],
                      data_sink: Callable[[bytes], None],
                      recursive: bool = True,
                      data_types_to_exclude: Optional[List[str]] = None) -> None:
        """
        Export records into zipped XML. The format will be .xml.gz

        :param records: The records to be exported.
        :param data_sink: The sink to receive exported data.
        :param recursive: whether to recursively export all descendant records.
        :param data_types_to_exclude: a black list of data type names.
        """
        sub_path = self.user.build_url(['datamanager', 'exportxml'])
        params = {'dataTypesToExclude': data_types_to_exclude,
                  'recursive': recursive}
        payload: List[Dict[str, Any]] = []
        for record in records:
            desc = DataRecordDescriptor(record.data_type_name, record.record_id)
            payload.append(desc.to_json())
        self.user.consume_octet_stream_post(sub_path, data_sink, params=params, payload=payload)

    def import_from_xml(self, parent_record: DataRecord, data_stream: IO,
                        skip_top_level: bool = False) -> None:
        """
        Import records as children of a parent data record from a .xml.gz file

        :param parent_record: The parent record to import under.
        :param data_stream: The data IO containing the zipped xml
        :param skip_top_level: Whether to skip top-level records we are importing in XML.
        """
        sub_path = self.user.build_url(['datamanager', 'importxml',
                                        parent_record.data_type_name, str(parent_record.record_id)])
        params = {'skipTopLevel': skip_top_level}
        response = self.user.post_data_stream(sub_path, data_stream, params=params)
        self.user.raise_for_status(response)
