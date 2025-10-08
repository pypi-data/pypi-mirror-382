from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Optional, List, Iterable

from sapiopylib.rest.pojo.chartdata.ChartData import ChartDataSource, ChartDataParser
from sapiopylib.rest.utils.recordmodel.PyRecordModel import PyRecordModel
from sapiopylib.rest.utils.recordmodel.RecordModelManager import RecordModelInstanceManager
from sapiopylib.rest.utils.recordmodel.RecordModelUtil import RecordModelUtil
from sapiopylib.rest.utils.recordmodel.RecordModelWrapper import WrappedRecordModel


class RbEntryType(Enum):
    TABLE_VIEW = "TableEntryDataContextPojo"
    FORM_VIEW = "FormEntryDataContextPojo"
    DASHBOARD = "DashboardEntryDataContextPojo"
    IMAGE = "ImageEntryDataContextPojo"
    STATIC_TEXT = "StaticTextEntryDataContextPojo"
    DATE = "DateEntryDataContextPojo"
    PLUGIN = "PluginEntryDataContextPojo"
    PAGE_NUMBERER = "PageNumbererEntryDataContextPojo"

    class_name: str

    def __init__(self, class_name: str):
        self.class_name = class_name


class AbstractReportEntryDataContext(ABC):

    @property
    def entry_type(self) -> RbEntryType:
        return self.get_entry_type()

    @abstractmethod
    def get_entry_type(self) -> RbEntryType:
        pass

    def _do_set_records(self, models: Iterable[PyRecordModel]):
        raise NotImplementedError("The set records method is not available for this class.")

    def set_records(self, models: Iterable[PyRecordModel | WrappedRecordModel] | None) -> None:
        """
        Set records onto this entry context.
        If this entry context does not support the passed in records, an exception will be thrown.
        Some context supports no records, or a single record only.
        :param models: The records to set onto the context.
        """
        if not models:
            self._do_set_records([])
        else:
            unwrapped_models = RecordModelInstanceManager.unwrap_list(models)
            RecordModelUtil.validate_backing_records(unwrapped_models)
            self._do_set_records(unwrapped_models)

    def to_json_supply_entry_type(self, entry_type: RbEntryType) -> Dict[str, Any]:
        return {
            '@type': entry_type.class_name,
            'entryType': entry_type.name
        }

    def to_json(self) -> Dict[str, Any]:
        return {
            '@type': self.entry_type.class_name,
            'entryType': self.entry_type.name
        }


class DashboardEntryDataContextPojo(AbstractReportEntryDataContext):
    record_ids: Optional[List[int]]
    chart_data_source: Optional[ChartDataSource]

    def get_entry_type(self) -> RbEntryType:
        return RbEntryType.DASHBOARD

    def __init__(self, record_ids: Optional[List[int]] = None,
                 chart_data_source: Optional[ChartDataSource] = None):
        self.record_ids = record_ids
        self.chart_data_source = chart_data_source

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_json()
        ret['recordIds'] = self.record_ids
        if self.chart_data_source is not None:
            ret['chartDataSourcePojo'] = self.chart_data_source.to_json()
        return ret

    def _do_set_records(self, models: Iterable[PyRecordModel]):
        self.record_ids = [model.record_id for model in models]


class DateEntryDataContext(AbstractReportEntryDataContext):
    """
    An entry data context object that backs a date entry that will display a date in the Report PDF.

    _data_type_name: The data type name of the record that will be used to get the static text to display. (Read-Only)

    _data_field_name: The data field name that the text value will be retrieved from on the dataTypeName. (Read-Only)

    data_record_id: The record ID of the data record that the date will be retrieved from.
    If the staticTimestamp attribute is specified, then this value will be ignored.

    static_timestamp: The timestamp that represents the date that should be displayed in this entry.
    This value will take precedence over the dataRecordId.
    """
    _data_type_name: str
    _data_field_name: str
    data_record_id: Optional[int]
    static_timestamp: Optional[int]

    def __init__(self, data_type_name: str, data_field_name: str,
                 data_record_id: Optional[int] = None, static_timestamp: Optional[int] = None):
        self._data_type_name = data_type_name
        self._data_field_name = data_field_name
        self.data_record_id = data_record_id
        self.static_timestamp = static_timestamp

    def get_data_type_name(self) -> str:
        return self._data_type_name

    def get_data_field_name(self) -> str:
        return self._data_field_name

    def _do_set_records(self, models: Iterable[PyRecordModel]):
        if not models:
            self.data_record_id = None
        else:
            model_list = list(models)
            if (len(model_list)) > 1:
                raise ValueError("There can be at most 1 model configured for this entry context.")
            model = next(iter(models))
            self.data_record_id = model.record_id

    def to_json_supply_entry_type(self, entry_type: RbEntryType) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_json_supply_entry_type(entry_type)
        ret['dataTypeName'] = self._data_type_name
        ret['dataFieldName'] = self._data_field_name
        ret['dataRecordId'] = self.data_record_id
        ret['staticTimestamp'] = self.static_timestamp
        return ret

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_json()
        ret['dataTypeName'] = self._data_type_name
        ret['dataFieldName'] = self._data_field_name
        ret['dataRecordId'] = self.data_record_id
        ret['staticTimestamp'] = self.static_timestamp
        return ret

    def get_entry_type(self) -> RbEntryType:
        return RbEntryType.DATE


class FormEntryDataContext(AbstractReportEntryDataContext):
    """
    An entry data context object that backs a form entry that will display a form of information in the Report PDF.

    _data_type_name_list: The list of data types that are displayed on this entry for which data needs to be retrieved.
    (Read-Only)

    record_ids_by_type: A map from data type name to the record ID that should be used to retrieve the data.
    The fields that should be used in this entry will be retrieved from the field_map_by_rec_id_by_type in
    ReportDataContext by using the values set in this map.
    """
    _data_type_name_list: List[str]
    record_ids_by_type: Optional[Dict[str, int]]

    def __init__(self, data_type_name_list: List[str], record_ids_by_type: Optional[Dict[str, int]] = None):
        self._data_type_name_list = data_type_name_list
        self.record_ids_by_type = record_ids_by_type

    def _do_set_records(self, models: Iterable[PyRecordModel]):
        if not models:
            self.record_ids_by_type = None
        else:
            record_ids_by_type: dict[str, int] = dict()
            for model in models:
                if model.data_type_name in self._data_type_name_list:
                    if model.data_type_name in record_ids_by_type:
                        raise ValueError("Cannot assign more than one record to the same data type " + model.data_type_name)
                    record_ids_by_type[model.data_type_name] = model.record_id
            self.record_ids_by_type = record_ids_by_type

    def get_data_type_name_list(self) -> List[str]:
        return self._data_type_name_list

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_json()
        ret['dataTypeNameSet'] = self._data_type_name_list
        ret['recordIdByType'] = self.record_ids_by_type
        return ret

    def get_entry_type(self) -> RbEntryType:
        return RbEntryType.FORM_VIEW


class ImageEntryDataContext(AbstractReportEntryDataContext):
    """
    An entry data context object that backs an image entry that will display as an image in the Report PDF

    _data_type_name: The data type name of the record that will be used to get the static image to display.
    This value is required with the dataRecordId attribute. Cannot be modified.

    data_record_id: The record ID of the data record that the bytes will be retrieved from.
    This value will be ignored if the staticImageUri is specified.

    static_image_uri: The base64 representation of a static image to be displayed in the entry.
    This value will take precedence over the dataRecordId attribute.
    """
    _data_type_name: str
    data_record_id: Optional[int]
    static_image_uri: Optional[str]

    def __init__(self, data_type_name: str, data_record_id: Optional[int] = None,
                 static_image_uri: Optional[str] = None):
        self._data_type_name = data_type_name
        self.data_record_id = data_record_id
        self.static_image_uri = static_image_uri

    def _do_set_records(self, models: Iterable[PyRecordModel]):
        if not models:
            self.data_record_id = None
        else:
            model_list = list(models)
            if (len(model_list)) > 1:
                raise ValueError("There can be at most 1 model configured for this entry context.")
            model = next(iter(models))
            self.data_record_id = model.record_id

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_json()
        ret['dataTypeName'] = self._data_type_name
        ret['dataRecordId'] = self.data_record_id
        ret['staticImageUri'] = self.static_image_uri
        return ret

    def get_data_type_name(self) -> str:
        return self._data_type_name

    def get_entry_type(self) -> RbEntryType:
        return RbEntryType.IMAGE


class PageNumbererDataContext(AbstractReportEntryDataContext):
    """
    An entry data context object that backs an entry that will display a page number when generating the Report PDF.
    """

    def get_entry_type(self) -> RbEntryType:
        return RbEntryType.PAGE_NUMBERER


class PluginEntryDataContext(AbstractReportEntryDataContext):
    """
    HTML text that is provided by a plugin that is run when generating the PDF.  Any value specified in this will
    likely get overwritten by other logic when the PDF is generated.

    html: HTML text that is provided by a plugin that is run when generating the PDF.  Any value specified in this will
    likely get overwritten by other logic when the PDF is generated.
    """
    html: str

    def __init__(self, html: str):
        self.html = html

    def get_entry_type(self) -> RbEntryType:
        return RbEntryType.PLUGIN

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_json()
        ret['html'] = self.html
        return ret


class StaticTextEntryDataContext(AbstractReportEntryDataContext):
    """
    An entry data context object that backs a static text entry that will display a block of text in the Report PDF.

    _data_type_name: The data type name of the record that will be used to get the static text to display.
    This value cannot be modified.

    _data_field_name: The data field name that the text value will be retrieved from on the dataTypeName.
    This value cannot be modified.

    dataRecordId: The record ID of the data record that the static text will be retrieved from.
    If the staticHtml attribute is specified, then this value will be ignored.

    staticHtml: The static HTML text that will be displayed on this text entry.
    This value will take precedence of the data record Id if both are specified.
    """
    _data_type_name: str
    _data_field_name: str
    data_record_id: Optional[int]
    static_html: Optional[str]

    def __init__(self, _data_type_name: str, _data_field_name: str, data_record_id: Optional[int] = None,
                 static_html: Optional[str] = None):
        self._data_type_name = _data_type_name
        self._data_field_name = _data_field_name
        self.data_record_id = data_record_id
        self.static_html = static_html

    def _do_set_records(self, models: Iterable[PyRecordModel]):
        if not models:
            self.data_record_id = None
        else:
            model_list = list(models)
            if (len(model_list)) > 1:
                raise ValueError("There can be at most 1 model configured for this entry context.")
            model = next(iter(models))
            self.data_record_id = model.record_id

    def get_entry_type(self) -> RbEntryType:
        return RbEntryType.STATIC_TEXT

    def to_json_supply_entry_type(self, entry_type: RbEntryType) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_json_supply_entry_type(entry_type)
        ret['dataTypeName'] = self._data_type_name
        ret['dataFieldName'] = self._data_field_name
        ret['dataRecordId'] = self.data_record_id
        ret['staticHtml'] = self.static_html
        return ret

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_json()
        ret['dataTypeName'] = self._data_type_name
        ret['dataFieldName'] = self._data_field_name
        ret['dataRecordId'] = self.data_record_id
        ret['staticHtml'] = self.static_html
        return ret

    def get_data_type_name(self) -> str:
        return self._data_type_name

    def get_data_field_name(self) -> str:
        return self._data_field_name


class TableEntryDataContext(AbstractReportEntryDataContext):
    """
    An entry data context object that backs a date entry that will display a date in the Report PDF.

    _data_type_name: The data type that is displayed on this entry for which data needs to be retrieved.
    This value cannot be modified.

    record_id_list: The set of record IDs that the table data will be retrieved from.
    """
    _data_type_name: str
    record_id_list: Optional[List[int]]

    def __init__(self, _data_type_name: str, record_id_list: Optional[List[int]]):
        self._data_type_name = _data_type_name
        self.record_id_list = record_id_list

    def _do_set_records(self, models: Iterable[PyRecordModel]):
        self.record_id_list = [model.record_id for model in models]

    def get_data_type_name(self) -> str:
        return self._data_type_name

    def get_entry_type(self) -> RbEntryType:
        return RbEntryType.TABLE_VIEW

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_json()
        ret['dataTypeName'] = self._data_type_name
        ret['recordIds'] = self.record_id_list
        return ret


class ReportBuilderEntryContextParser:
    @staticmethod
    def parse_entry_type_from_jackson_class_name(class_name: str) -> Optional[RbEntryType]:
        for entry_type in RbEntryType:
            if entry_type.class_name == class_name:
                return entry_type
        return None

    @staticmethod
    def parse_report_builder_entry_context(json_dct: Dict[str, Any]) -> AbstractReportEntryDataContext:
        entry_type_class_name = json_dct.get('@type')
        entry_type: Optional[RbEntryType] = ReportBuilderEntryContextParser.parse_entry_type_from_jackson_class_name(
            entry_type_class_name)
        if entry_type == RbEntryType.DASHBOARD:
            record_ids: Optional[List[int]] = json_dct.get('recordIds')
            chart_data_source: Optional[ChartDataSource] = None
            if json_dct.get('chartDataSourcePojo') is not None:
                chart_data_source = ChartDataParser.parse_chart_data_source(json_dct.get('chartDataSourcePojo'))
            return DashboardEntryDataContextPojo(record_ids, chart_data_source)
        elif entry_type == RbEntryType.DATE:
            _data_type_name: str = json_dct.get('dataTypeName')
            _data_field_name: str = json_dct.get('dataFieldName')
            data_record_id: Optional[int] = json_dct.get('dataRecordId')
            static_timestamp: Optional[int] = json_dct.get('staticTimestamp')
            return DateEntryDataContext(_data_type_name, _data_field_name, data_record_id, static_timestamp)
        elif entry_type == RbEntryType.FORM_VIEW:
            _data_type_name_list: List[str] = json_dct.get('dataTypeNameSet')
            record_ids_by_type: Optional[Dict[str, int]] = json_dct.get('recordIdByType')
            return FormEntryDataContext(_data_type_name_list, record_ids_by_type)
        elif entry_type == RbEntryType.IMAGE:
            _data_type_name: str = json_dct.get('dataTypeName')
            data_record_id: Optional[int] = json_dct.get('dataRecordId')
            static_image_uri: Optional[str] = json_dct.get('staticImageUri')
            return ImageEntryDataContext(_data_type_name, data_record_id, static_image_uri)
        elif entry_type == RbEntryType.PAGE_NUMBERER:
            return PageNumbererDataContext()
        elif entry_type == RbEntryType.PLUGIN:
            html: str = json_dct.get('html')
            return PluginEntryDataContext(html)
        elif entry_type == RbEntryType.STATIC_TEXT:
            _data_type_name: str = json_dct.get('dataTypeName')
            _data_field_name: str = json_dct.get('dataFieldName')
            data_record_id: Optional[int] = json_dct.get('dataRecordId')
            static_html: Optional[str] = json_dct.get('staticHtml')
            return StaticTextEntryDataContext(_data_type_name, _data_field_name, data_record_id, static_html)
        elif entry_type == RbEntryType.TABLE_VIEW:
            _data_type_name: str = json_dct.get('dataTypeName')
            record_id_list: Optional[List[int]] = json_dct.get('recordIds')
            return TableEntryDataContext(_data_type_name, record_id_list)
