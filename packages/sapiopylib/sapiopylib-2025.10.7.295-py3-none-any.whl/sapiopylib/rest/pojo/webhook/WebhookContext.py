from typing import Optional, List, Dict, Any

from sapiopylib.rest.DataMgmtService import DataMgmtServer
from sapiopylib.rest.DataRecordManagerService import DataRecordManager
from sapiopylib.rest.ELNService import ElnManager
from sapiopylib.rest.User import SapioUser, UserSessionAdditionalData, parse_session_additional_data
from sapiopylib.rest.pojo.CustomReport import CustomReport
from sapiopylib.rest.pojo.DataRecord import DataRecord
from sapiopylib.rest.pojo.eln.ElnEntryPosition import ElnEntryPosition
from sapiopylib.rest.pojo.eln.ElnExperiment import ElnExperiment, ELNExperimentParser
from sapiopylib.rest.pojo.eln.ExperimentEntry import ExperimentEntry, ExperimentEntryParser
from sapiopylib.rest.pojo.reportbuilder.VeloxReportBuilder import RbTemplatePopulatorData, VeloxReportBuilderParser
from sapiopylib.rest.pojo.webhook.ClientCallbackResult import ClientCallbackResultParser, AbstractClientCallbackResult
from sapiopylib.rest.pojo.webhook.VeloxRules import VeloxTypedRuleResult, ElnEntryRecordResult, VeloxRuleParser, \
    VeloxTypeRuleFieldMapResult, ElnEntryFieldMapResult
from sapiopylib.rest.pojo.webhook.WebhookEnums import WebhookEndpointType
from sapiopylib.rest.utils.Protocols import AbstractProtocol, ElnExperimentProtocol, \
    AbstractStep, ElnEntryStep


class SapioWebhookContext:
    """
    The webhook context structure after receiving a request from Sapio Informatics Platform.

    Obtain your context variables here.

    Attributes:
        user: The user object contains your session and credentials. Typically, this is an interactive session with client callback enabled.
        data_record_manager: The convenient way to retrieve DataRecordManager class object directly without using DataMgmtServer.
        eln_manager: The convenient way to retrieve ElnManager class object directly without using DataMgmtServer.
        active_protocol: The current protocol in protocol/step interface. It can be None if there is none in the context.
        active_step: The current step in protocol/step interface. It can be None if there is none in the context.
        end_point_type: The invocation point of the current endpoint.
        data_record: The current data record of the context. It can be None if not applicable.
        base_data_record: The current base data record of the context. This usually is only relevant in IDV and temporary record views. It can be None if not applicable.
        data_record_list: The list of data records of the context. It can be None if not applicable.
        data_type_name: The data type name of the context. It can be None if not applicable.
        data_field_name: The data field name of the context. It can be None if not applicable.
        velox_on_save_result_map: on save rule result context. It can be None if not applicable.
        velox_on_save_field_map_result_map: on save rule result context for any triggered records that is no longer accessible. That is, objects that are deleted or is rendered otherwise inaccessible to the user. It can be None if not applicable.
        velox_eln_rule_result_map: eln rule result context. It can be None if not applicable.
        velox_eln_rule_field_map_result_map: eln rule context for any triggered records that is no longer accessible. That is, objects that are deleted or is rendered otherwise inaccessible to the user. It can be None if not applicable.
        experiment_entry_list: ELN experiment entry list context. It can be None if not applicable.
        experiment_entry: ELN experiment entry context. It can be None if not applicable.
        eln_experiment: ELN experiment context. It can be None if not applicable.
        client_callback_result: DEPRECATED. USE CLIENT CALLBACK SERVICE INSTEAD.
        is_client_callback_available: DEPRECATED. USE CLIENT CALLBACK SERVICE INSTEAD.
        report_builder_template_populator_data: Report builder context. It can be None if not applicable.
        field_map_list: list of field map data. It can be None if not applicable. Generally, this is only non-blank in searches and temporary contexts.
        field_map: field map data. It can be None if not applicable. Generally, this is only non-blank in selection list plugins of temporary data types.
        selected_field_map_index_list: A list of 0-based indexes to the field_map_list of user selections. It can be None if not applicable.
        data_field_name_list: A list of data field names. It can be None if not applicable.
        context_data: any additional carrying data, usually from client-side plugins or another plugin installed in BLS that triggers the webhook.
        entry_position: ELN entry position data. It can be None if not applicable. This is only filled if there is position data but no ELN entry, such as the case for grabber context when ELN entry has not been created.
        custom_report: The custom report object of the current context. It can be None if not applicable. This object can be decorated already by the client, and may not contain result data.
    """
    user: SapioUser

    data_record_manager: DataRecordManager
    eln_manager: ElnManager
    active_protocol: Optional[AbstractProtocol]
    active_step: Optional[AbstractStep]

    end_point_type: WebhookEndpointType

    data_record: Optional[DataRecord]
    base_data_record: Optional[DataRecord]
    data_record_list: Optional[List[DataRecord]]
    data_type_name: Optional[str]
    data_field_name: Optional[str]

    # records for record rules that have accessible data record reference in server will be in this one.
    velox_on_save_result_map: Optional[Dict[int, List[VeloxTypedRuleResult]]]
    # velox_on_save_field_map_result_map is only populated for triggered records where there is no longer a record ref.
    # (e.g. deleted records or otherwise no longer accessible records)
    velox_on_save_field_map_result_map: Optional[Dict[int, List[VeloxTypeRuleFieldMapResult]]]
    # records for eln rules that have accessible data record reference in server will be in this one.
    velox_eln_rule_result_map: Optional[Dict[str, List[ElnEntryRecordResult]]]
    # velox_eln_rule_field_map_result_map is only populated for triggered records where there is no longer a record ref.
    # (e.g. deleted records or otherwise no longer accessible records)
    velox_eln_rule_field_map_result_map: Optional[Dict[str, List[ElnEntryFieldMapResult]]]

    experiment_entry_list: Optional[List[ExperimentEntry]]
    experiment_entry: Optional[ExperimentEntry]
    eln_experiment: Optional[ElnExperiment]
    client_callback_result: Optional[AbstractClientCallbackResult]
    is_client_callback_available: bool

    report_builder_template_populator_data: Optional[RbTemplatePopulatorData]

    field_map_list: Optional[List[Dict[str, Any]]]
    field_map: Optional[Dict[str, Any]]
    selected_field_map_index_list: Optional[List[int]]
    data_field_name_list: list[str] | None

    context_data: str

    entry_position: Optional[ElnEntryPosition]

    custom_report: CustomReport

    def __init__(self, user: SapioUser, end_point_type: WebhookEndpointType):
        self.user = user
        self.end_point_type = end_point_type
        self.data_record_manager = DataMgmtServer.get_data_record_manager(user)
        self.eln_manager = DataMgmtServer.get_eln_manager(user)


class SapioWebhookContextParser:
    @staticmethod
    def parse_endpoint_type_from_display_name(endpoint_type_display_name: str):
        for endpoint in WebhookEndpointType:
            if endpoint.display_name == endpoint_type_display_name:
                return endpoint
        return None

    @staticmethod
    def parse_webhook(json_dct: Dict[str, Any],
                      timeout_seconds=60,
                      verify_ssl_cert=True) -> SapioWebhookContext:
        endpoint_type_display_name = json_dct.get('endpointType')
        end_point_type = SapioWebhookContextParser.parse_endpoint_type_from_display_name(endpoint_type_display_name)
        webservice_url: str = json_dct.get('webserviceUrl')
        # Remove trailing "/"
        if webservice_url.endswith('/'):
            webservice_url = webservice_url[:-len('/')]
        api_token: str = json_dct.get('webhookApiToken')
        username: str = json_dct.get('username')
        app_guid: str = json_dct.get('appGuid')
        context_data: str = json_dct.get('contextData')
        session_additional_data: Optional[UserSessionAdditionalData] = None
        session_additional_data_raw: Dict[str, Any] = json_dct.get('sessionAdditionalData')
        # CR-53279: Also populate the SapioUser's direct group_name attribute if available.
        group_name: str | None = None
        if session_additional_data_raw:
            session_additional_data = parse_session_additional_data(session_additional_data_raw)
            group_name = session_additional_data.current_group_name
        user: SapioUser = SapioUser(url=webservice_url, verify_ssl_cert=verify_ssl_cert,
                                    timeout_seconds=timeout_seconds, api_token=api_token,
                                    username=username, guid=app_guid, group_name=group_name,
                                    session_additional_data=session_additional_data)
        data_record: Optional[DataRecord] = None
        if json_dct.get('dataRecordPojo') is not None:
            data_record = DataRecord.from_json(json_dct.get('dataRecordPojo'))
        base_data_record: Optional[DataRecord] = None
        if json_dct.get('baseDataRecordPojo') is not None:
            base_data_record = DataRecord.from_json(json_dct.get('baseDataRecordPojo'))
        data_record_list: Optional[List[DataRecord]] = None
        if json_dct.get('dataRecordPojoList') is not None:
            data_record_list = [DataRecord.from_json(x) for x in json_dct.get('dataRecordPojoList')]
        data_type_name: Optional[str] = json_dct.get('dataTypeName')
        data_field_name: Optional[str] = json_dct.get('dataFieldName')
        data_field_name_list: list[str] | None = json_dct.get('dataFieldNameList')
        custom_report: CustomReport | None = None
        if json_dct.get('customReportPojo') is not None:
            custom_report = CustomReport.from_json(json_dct.get('customReportPojo'))

        velox_on_save_result_map: Optional[Dict[int, List[VeloxTypedRuleResult]]] = None
        if json_dct.get('veloxOnSaveResultMap') is not None:
            velox_on_save_result_map = dict()
            pojo_map: Dict[int, List[Dict[str, Any]]] = json_dct.get('veloxOnSaveResultMap')
            for key, value in pojo_map.items():
                result_list: List[VeloxTypedRuleResult] = [VeloxRuleParser.parse_velox_typed_rule_result(x)
                                                           for x in value]
                velox_on_save_result_map[int(key)] = result_list
        velox_on_save_field_map_result_map: Optional[Dict[int, List[VeloxTypeRuleFieldMapResult]]] = None
        if json_dct.get('veloxOnSaveFieldMapResultMap') is not None:
            velox_on_save_field_map_result_map = dict()
            pojo_map: Dict[int, List[Dict[str, Any]]] = json_dct.get("veloxOnSaveFieldMapResultMap")
            for key, value in pojo_map.items():
                result_list: List[VeloxTypeRuleFieldMapResult] = [
                    VeloxTypeRuleFieldMapResult.from_json(x) for x in value]
                velox_on_save_field_map_result_map[int(key)] = result_list

        velox_eln_rule_result_map: Optional[Dict[str, List[ElnEntryRecordResult]]] = None
        if json_dct.get('veloxElnRuleResultMap') is not None:
            velox_eln_rule_result_map = dict()
            pojo_map: Dict[str, List[Dict[str, Any]]] = json_dct.get('veloxElnRuleResultMap')
            for key, value in pojo_map.items():
                result_list: List[ElnEntryRecordResult] = [VeloxRuleParser.parse_eln_record_result(x) for x in value]
                velox_eln_rule_result_map[key] = result_list
        velox_eln_rule_field_map_result_map: Optional[Dict[int, List[ElnEntryFieldMapResult]]] = None
        if json_dct.get('veloxElnRuleFieldMapResultMap') is not None:
            velox_eln_rule_field_map_result_map = dict()
            pojo_map: Dict[int, List[Dict[str, Any]]] = json_dct.get("veloxElnRuleFieldMapResultMap")
            for key, value in pojo_map.items():
                result_list: List[ElnEntryFieldMapResult] = [
                    ElnEntryFieldMapResult.from_json(x) for x in value]
                velox_eln_rule_field_map_result_map[key] = result_list

        experiment_entry_list: Optional[List[ExperimentEntry]] = None
        if json_dct.get('elnExperimentEntryPojoList') is not None:
            experiment_entry_list = [ExperimentEntryParser.parse_experiment_entry(x) for
                                     x in json_dct.get('elnExperimentEntryPojoList')]
        experiment_entry: Optional[ExperimentEntry] = None
        if json_dct.get('elnExperimentEntryPojo') is not None:
            experiment_entry = ExperimentEntryParser.parse_experiment_entry(json_dct.get('elnExperimentEntryPojo'))
        notebook_experiment: Optional[ElnExperiment] = None
        if json_dct.get('notebookExperimentPojo') is not None:
            notebook_experiment = ELNExperimentParser.parse_eln_experiment(json_dct.get('notebookExperimentPojo'))
        client_callback_result: Optional[AbstractClientCallbackResult] = None
        if json_dct.get('clientCallbackResult') is not None:
            client_callback_result = ClientCallbackResultParser.parse_client_callback_result(
                json_dct.get('clientCallbackResult'))
        is_client_callback_available: bool = json_dct.get('clientCallbackAvailable')

        report_builder_template_populator_data: Optional[RbTemplatePopulatorData] = None
        if json_dct.get('rbTemplatePopulatorDataPojo') is not None:
            report_builder_template_populator_data = VeloxReportBuilderParser.parse_template_populator_data(
                json_dct.get('rbTemplatePopulatorDataPojo'))

        field_map_list: Optional[List[Dict[str, Any]]] = json_dct.get('fieldMapList')
        field_map: Optional[Dict[str, Any]] = json_dct.get('fieldMap')
        selected_field_map_index_list: Optional[List[int]] = json_dct.get('selectedFieldMapIdxList')

        entry_position: Optional[ElnEntryPosition] = None
        if json_dct.get("elnExperimentEntryPositionPojo") is not None:
            entry_position = ElnEntryPosition.from_json(json_dct.get("elnExperimentEntryPositionPojo"))

        ret: SapioWebhookContext = SapioWebhookContext(user, end_point_type)
        ret.context_data = context_data
        ret.data_record = data_record
        ret.base_data_record = base_data_record
        ret.data_record_list = data_record_list
        ret.data_type_name = data_type_name
        ret.data_field_name = data_field_name
        ret.velox_on_save_result_map = velox_on_save_result_map
        ret.velox_on_save_field_map_result_map = velox_on_save_field_map_result_map
        ret.velox_eln_rule_result_map = velox_eln_rule_result_map
        ret.velox_eln_rule_field_map_result_map = velox_eln_rule_field_map_result_map
        ret.experiment_entry_list = experiment_entry_list
        ret.experiment_entry = experiment_entry
        ret.eln_experiment = notebook_experiment
        ret.client_callback_result = client_callback_result
        ret.is_client_callback_available = is_client_callback_available
        ret.report_builder_template_populator_data = report_builder_template_populator_data
        ret.field_map_list = field_map_list
        ret.field_map = field_map
        ret.selected_field_map_index_list = selected_field_map_index_list
        ret.entry_position = entry_position
        ret.data_field_name_list = data_field_name_list
        ret.custom_report = custom_report

        if ret.eln_experiment is not None:
            if ret.experiment_entry is None and ret.experiment_entry_list is not None and len(ret.experiment_entry_list) == 1:
                ret.experiment_entry = ret.experiment_entry_list[0]
            ret.active_protocol = ElnExperimentProtocol(eln_experiment=ret.eln_experiment, user=ret.user)
            if ret.experiment_entry is not None:
                ret.active_step = ElnEntryStep(protocol=ret.active_protocol, eln_entry=ret.experiment_entry)
        if ret.data_record is None and ret.data_record_list is not None and len(ret.data_record_list) == 1:
            ret.data_record = ret.data_record_list[0]

        return ret
