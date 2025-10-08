from datetime import datetime
from typing import Optional, Any, Dict, List

from sapiopylib.rest.pojo.DataRecord import DataRecord
from sapiopylib.rest.pojo.reportbuilder.ReportBuilderEntryContext import RbEntryType, AbstractReportEntryDataContext, \
    ReportBuilderEntryContextParser
from sapiopylib.rest.utils.SapioDateUtils import java_millis_to_datetime


# Report Builder is currently used in hCRM/COM product.
class ReportTemplateInfo:
    """
    Details about a Report Template in the system.  These objects can be used to generate PDFs in the system
    provided some additional data context.

    template_id: The identifier of the Report Template.

    template_name: The name of the Report Template

    category: User provided categories specified on the Report Template.

    description: A description of this Report Template.

    created_by: The username of the user that created this Report Template.

    date_created: The timestamp in milliseconds since Unix Epoch when this Report Template was created.

    last_modified_by: The username of the user that modified this Report Template most recently.

    date_last_modified: The timestamp in milliseconds since Unix Epoch when this Report Template was last modified.
    """
    template_id: str
    template_name: str
    category: Optional[str]
    description: Optional[str]
    created_by: Optional[str]
    date_created: Optional[int]
    last_modified_by: Optional[str]
    date_last_modified: Optional[int]

    def __hash__(self):
        return hash((self.template_id, self.template_name))

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, ReportTemplateInfo):
            return False
        return (self.template_id, self.template_name) == (other.template_id, other.template_name)

    def __init__(self, template_id: str, template_name: str, category: Optional[str],
                 description: Optional[str], created_by: Optional[str], date_created: Optional[int],
                 last_modified_by: Optional[str], date_last_modified: Optional[int]):
        self.template_id = template_id
        self.template_name = template_name
        self.category = category
        self.description = description
        self.created_by = created_by
        self.date_created = date_created
        self.last_modified_by = last_modified_by
        self.date_last_modified = date_last_modified

    def to_json(self) -> Dict[str, Any]:
        return {
            'templateId': self.template_id,
            'templateName': self.template_name,
            'category': self.category,
            'description': self.description,
            'createdBy': self.created_by,
            'dateCreated': self.date_created,
            'lastModifiedBy': self.last_modified_by,
            'dateLastModified': self.date_last_modified
        }

    def get_last_modified_date(self) -> datetime:
        return java_millis_to_datetime(self.date_last_modified)

    def get_date_created(self) -> datetime:
        return java_millis_to_datetime(self.date_created)


class ReportEntryInfo:
    """
    Details about a Report Entry contained within a Report Template in the system.  These objects can be
    used to determine the entries in a template when providing data in a AbstractReportDataContext to generate
    a PDF.

    entry_id: The identifier of the Report Entry.

    entry_name: The name of the Report Entry.

    entry_type: The type of the Report Entry.

    entry_data_context: The data context information that is currently specified on this entry.
    """
    _entry_id: str
    entry_name: str
    entry_type: RbEntryType
    entry_data_context: AbstractReportEntryDataContext

    @property
    def entry_id(self):
        return self._entry_id

    def get_entry_id(self) -> str:
        return self._entry_id

    def __init__(self, entry_id: str, entry_name: str,
                 entry_type: RbEntryType, entry_data_context: AbstractReportEntryDataContext):
        self._entry_id = entry_id
        self.entry_name = entry_name
        self.entry_type = entry_type
        self.entry_data_context = entry_data_context

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = dict()
        ret['entryId'] = self._entry_id
        ret['entryName'] = self.entry_name
        ret['entryType'] = self.entry_type.name
        entry_data_context: Dict[str, Any] = self.entry_data_context.to_json_supply_entry_type(self.entry_type)
        for key in entry_data_context.keys():
            ret[key] = entry_data_context[key]
        return ret


class ReportDataContext:
    """
    Context object used to provide details about the data that should be added to a Report Template when
    generating a PDF.

    Attributes:
        field_map_by_record_id_by_type: A map from data type name to a map from record ID to a field map.
        entry_data_context_map: A map from Report Entry ID to the data context that should be used for the entry.
        parent_data_record: The parent record under which the newly generated attachment record will be added.  If this value is not specified, the new record will be added to the aether without any parents.
        attachment_file_name: The name of the new file that will be set on the newly created attachment record.
    """
    field_map_by_record_id_by_type: Dict[str, Dict[int, Dict[str, Any]]]
    entry_data_context_map: Dict[str, AbstractReportEntryDataContext]
    parent_data_record: Optional[DataRecord]
    attachment_file_name: str
    existing_attachment_record_id: Optional[int]
    attachment_additional_fields: dict[str, Any]

    def __init__(self, field_map_by_record_id_by_type: Dict[str, Dict[int, Dict[str, Any]]],
                 entry_data_context_map: Dict[str, AbstractReportEntryDataContext],
                 parent_data_record: Optional[DataRecord] = None, attachment_file_name: Optional[str] = None,
                 existing_attachment_record_id: Optional[int] = None, attachment_additional_fields: Optional[Dict[str, Any]] = None):
        self.field_map_by_record_id_by_type = field_map_by_record_id_by_type
        self.entry_data_context_map = entry_data_context_map
        self.parent_data_record = parent_data_record
        if attachment_file_name is None:
            attachment_file_name = "result.pdf"
        self.attachment_file_name = attachment_file_name
        self.existing_attachment_record_id = existing_attachment_record_id
        self.attachment_additional_fields = attachment_additional_fields

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = dict()
        ret['fieldMapByRecIdByType'] = self.field_map_by_record_id_by_type

        entry_context_data_pojo_map = dict()
        for key, context in self.entry_data_context_map.items():
            entry_context_data_pojo_map[key] = context.to_json()
        ret['entryDataContextMap'] = entry_context_data_pojo_map

        if self.parent_data_record is not None:
            ret['parentDataRecord'] = self.parent_data_record.to_json()

        ret['attachmentFileName'] = self.attachment_file_name
        ret['existingAttachmentRecordId'] = self.existing_attachment_record_id
        ret['attachmentAdditionalFields'] = self.attachment_additional_fields
        return ret


class RbTemplatePopulatorData:
    template_info: ReportTemplateInfo
    report_entry_info_list: List[ReportEntryInfo]
    report_data_context: ReportDataContext

    def __init__(self, template_info: ReportTemplateInfo, report_entry_info_list: List[ReportEntryInfo],
                 report_data_context: ReportDataContext):
        self.template_info = template_info
        self.report_entry_info_list = report_entry_info_list
        self.report_data_context = report_data_context

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = dict()
        ret['templateInfoPojo'] = self.template_info.to_json()
        ret['reportEntryInfoPojos'] = [x.to_json() for x in self.report_entry_info_list]
        ret['reportDataContextPojo'] = self.report_data_context.to_json()
        return ret


class VeloxReportBuilderParser:
    @staticmethod
    def parse_report_template_info(json_dct: Dict[str, Any]) -> ReportTemplateInfo:
        template_id: str = json_dct.get('templateId')
        template_name: str = json_dct.get('templateName')
        category: Optional[str] = json_dct.get('category')
        description: Optional[str] = json_dct.get('description')
        created_by: Optional[str] = json_dct.get('createdBy')
        date_created: Optional[int] = json_dct.get('dateCreated')
        last_modified_by: Optional[str] = json_dct.get('lastModifiedBy')
        date_last_modified: Optional[int] = json_dct.get('dateLastModified')
        return ReportTemplateInfo(template_id, template_name, category, description=description,
                                  created_by=created_by, date_created=date_created, last_modified_by=last_modified_by,
                                  date_last_modified=date_last_modified)

    @staticmethod
    def parse_report_entry_info(json_dct: Dict[str, Any]) -> ReportEntryInfo:
        _entry_id: str = json_dct.get('entryId')
        entry_name: str = json_dct.get('entryName')
        entry_type: RbEntryType = RbEntryType[json_dct.get('entryType')]
        entry_data_context: AbstractReportEntryDataContext = \
            ReportBuilderEntryContextParser.parse_report_builder_entry_context(json_dct.get('entryDataContextPojo'))
        return ReportEntryInfo(_entry_id, entry_name, entry_type, entry_data_context)

    @staticmethod
    def parse_report_data_context(json_dct: Dict[str, Any]) -> ReportDataContext:
        field_map_by_record_id_by_type: Dict[str, Dict[int, Dict[str, Any]]] = dict()
        if json_dct.get('fieldMapByRecIdByType') is not None:
            field_map_by_record_id_by_type = json_dct.get('fieldMapByRecIdByType')
        entry_data_context_map: Dict[str, AbstractReportEntryDataContext] = dict()
        if json_dct.get('entryDataContextMap') is not None:
            entry_context_data_pojo_map: Dict[str, Dict[str, Any]] = json_dct.get('entryDataContextMap')
            for key, pojo in entry_context_data_pojo_map.items():
                entry_data_context_map[key] = ReportBuilderEntryContextParser.parse_report_builder_entry_context(pojo)
        parent_data_record: Optional[DataRecord] = None
        if json_dct.get('parentDataRecord') is not None:
            parent_data_record = DataRecord.from_json(json_dct.get('parentDataRecord'))
        attachment_file_name: Optional[str] = json_dct.get('attachmentFileName')
        return ReportDataContext(field_map_by_record_id_by_type, entry_data_context_map,
                                 parent_data_record, attachment_file_name)

    @staticmethod
    def parse_template_populator_data(json_dct: Dict[str, Any]) -> RbTemplatePopulatorData:
        template_info: ReportTemplateInfo = VeloxReportBuilderParser.parse_report_template_info(
            json_dct.get('templateInfoPojo'))
        report_entry_pojo_list: List[Dict[str, Any]] = json_dct.get('reportEntryInfoPojos')
        report_entry_info_list: List[ReportEntryInfo] = [VeloxReportBuilderParser.parse_report_entry_info(x)
                                                         for x in report_entry_pojo_list]
        report_data_context: ReportDataContext = VeloxReportBuilderParser.parse_report_data_context(
            json_dct.get('reportDataContextPojo'))
        return RbTemplatePopulatorData(template_info, report_entry_info_list, report_data_context)

