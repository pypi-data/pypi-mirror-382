from __future__ import annotations

from typing import Iterable, Any
from weakref import WeakValueDictionary

from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.DataRecord import DataRecord
from sapiopylib.rest.pojo.reportbuilder.ReportBuilderEntryContext import AbstractReportEntryDataContext
from sapiopylib.rest.pojo.reportbuilder.VeloxReportBuilder import ReportTemplateInfo, VeloxReportBuilderParser, \
    ReportEntryInfo, ReportDataContext
from sapiopylib.rest.utils.recordmodel.PyRecordModel import PyRecordModel
from sapiopylib.rest.utils.recordmodel.RecordModelManager import RecordModelInstanceManager
from sapiopylib.rest.utils.recordmodel.RecordModelUtil import RecordModelUtil
from sapiopylib.rest.utils.recordmodel.RecordModelWrapper import WrappedRecordModel


class ReportManager:
    """
    Implements report builder addon features.
    """
    user: SapioUser
    __instances: WeakValueDictionary[SapioUser, ReportManager] = WeakValueDictionary()
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
        Obtains REST report manager to perform reporting operations.

        :param user: The user that will make the webservice request to the application.
        """
        if self.__initialized:
            return
        self.user = user
        self.__initialized = True

    def get_report_template_info_list(self) -> list[ReportTemplateInfo]:
        """
        Get the details about the report templates currently in the system.

        :return: A list of report template info for every report template in the system.
        """
        url = self.user.build_url(['reporttemplate'])
        response = self.user.get(url)
        json_data = response.json()
        template_info_list = []
        for template_json in json_data:
            template_info = VeloxReportBuilderParser.parse_report_template_info(template_json)
            template_info_list.append(template_info)
        return template_info_list

    def get_report_entry_info_list(self, template_id: str) -> list[ReportEntryInfo]:
        """
        Get the details about the report entries contained in the report template with the provided ID currently in
        the system.

        :param template_id: The ID of the report template from which to retrieve the entries.
        :return: A list of report entry info for the matching report template ID.
        """
        url = self.user.build_url(['reporttemplate', 'entries', template_id])
        response = self.user.get(url)
        self.user.raise_for_status(response)
        json_data = response.json()
        entry_info_list = []
        for entry_json in json_data:
            entry_info = VeloxReportBuilderParser.parse_report_entry_info(entry_json)
            entry_info_list.append(entry_info)
        return entry_info_list

    def generate_report_pdf(self, template_id: str, attachment_data_type: str, data_context: ReportDataContext) -> None:
        """
        Generate a Report PDF in the system using the provided template and data.
        This method will start an asynchronous process to generate the Report PDF and store it as a record in the system
        using the provided attachment data type.
        Optionally, a parent record can be provided to identify where the newly created attachment data type will be
        stored.
        If no parent data record is provided, then the attachment record will be stored in the aether with no parents.

        :param template_id: The ID of the Report Template from which the PDF will be generated.
        :param attachment_data_type: The attachment data type name that defines the type of attachment record that will
            be created to store the generated PDF.  This data type must exist in the system and must be a valid
            attachment data type.
        :param data_context: The data context that should be used when generating the PDF from the Report Template.
        """
        url = self.user.build_url(['reporttemplate', 'pdf', template_id, attachment_data_type])
        payload = data_context.to_json()
        response = self.user.post(url, payload=payload)
        self.user.raise_for_status(response)

    def initialize_report_data_context(self, record_models: Iterable[PyRecordModel | WrappedRecordModel], template_id: str,
                                       parent_model: PyRecordModel | WrappedRecordModel | None = None,
                                       attachment_file_name: str | None = None) -> ReportDataContext:
        """
        This is a helper tool that allows you to quickly set up a new report data context.

        :param record_models: The record models that participate in this report.
        :param template_id: The template ID to retrieve entry definition.
        :param parent_model: If specified, the PDF attachment will be attached as child of this record.
        :param attachment_file_name: The file name of the attachment.
        :return: A newly constructed report data context.
        """
        unwrapped_models = RecordModelInstanceManager.unwrap_list(record_models)
        RecordModelUtil.validate_backing_records(unwrapped_models)
        parent_model_unwrapped: PyRecordModel | None = None
        if parent_model:
            parent_model_unwrapped = RecordModelInstanceManager.unwrap(parent_model)
            RecordModelUtil.validate_backing_records([parent_model_unwrapped])
        models_by_type = RecordModelUtil.multi_map_models_by_data_type_name(unwrapped_models)
        field_map_by_record_id_by_type: dict[str, dict[int, dict[str, Any]]] = dict()
        for dt_name in models_by_type.keys():
            models_of_type = models_by_type.get(dt_name)
            dict_of_type: dict[int, dict[str, Any]] = dict()
            for model in models_of_type:
                dict_of_type[model.record_id] = model.fields.copy_to_dict()
            field_map_by_record_id_by_type[dt_name] = dict_of_type

        entry_info_list = self.get_report_entry_info_list(template_id)
        entry_data_context_map: dict[str, AbstractReportEntryDataContext] = {}
        for entry_info in entry_info_list:
            entry_data_context_map[entry_info.entry_id] = entry_info.entry_data_context

        parent_record: DataRecord | None = None
        if parent_model_unwrapped:
            parent_record = parent_model_unwrapped.get_data_record()
        return ReportDataContext(field_map_by_record_id_by_type, entry_data_context_map, parent_record, attachment_file_name)