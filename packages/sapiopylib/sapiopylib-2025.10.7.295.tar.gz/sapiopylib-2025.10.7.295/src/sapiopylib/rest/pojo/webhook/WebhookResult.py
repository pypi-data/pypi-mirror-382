from typing import Any, List, Dict, Optional

from sapiopylib.rest.pojo.eln.ExperimentEntry import ExperimentEntry
from sapiopylib.rest.pojo.reportbuilder.VeloxReportBuilder import RbTemplatePopulatorData
from sapiopylib.rest.pojo.webhook.ClientCallbackRequest import AbstractClientCallbackRequest
from sapiopylib.rest.pojo.webhook.WebhookDirective import AbstractWebhookDirective


class SapioWebhookResult:
    """
    Returned webhook result from webhook handler to sapio platform.

    Attributes:
        passed: Whether the handler had successfully handled request. "False" value may cause transaction to be rolled back.
        display_text: DEPRECATED. USE CLIENT CALLBACK SERVICE INSTEAD.
        directive: Any place we will navigate user to after receiving this request.
        client_callback_request: DEPRECATED. USE CLIENT CALLBACK SERVICE INSTEAD.
        refresh_data: Whether forces the client to refresh existing data in the page.
        auto_invoke_next_row: Used only for action text plugin, whether to automatically shift to next row and trigger.
        commit_message: If the webhook is transactional, the commit message to write when the entire webhook is committing.
        refresh_notebook_experiment: If set to true, the client browser will refresh the entire notebook experiment.
        This typically is not good user experience. Avoid if possible.
        eln_entry_refresh_list: Provide a list of ELN entry to be refreshed in client browser after returning.
        create_eln_snapshot: If set to true, a PDF snapshot will be generated at after returning the result.
        include_entry_description_in_eln_snapshot: Whether to include ELN entry descriptions (usually help texts) in PDF.
    """
    passed: bool
    display_text: Optional[str]
    list_values: Optional[List[str]]
    directive: Optional[AbstractWebhookDirective]
    client_callback_request: Optional[AbstractClientCallbackRequest]
    refresh_data: bool
    report_builder_template_populator_data: Optional[RbTemplatePopulatorData]
    auto_invoke_next_row: bool
    # ELN Plugin Results
    commit_message: Optional[str]
    refresh_notebook_experiment:bool
    eln_entry_refresh_list: Optional[List[ExperimentEntry]]
    create_eln_snapshot: bool
    include_entry_description_in_eln_snapshot: bool


    def __init__(self, passed: bool, display_text: Optional[str] = None,
                 list_values: Optional[List[str]] = None,
                 directive: Optional[AbstractWebhookDirective] = None,
                 client_callback_request: Optional[AbstractClientCallbackRequest] = None,
                 refresh_data: bool = False,
                 report_builder_template_populator_data: Optional[RbTemplatePopulatorData] = None,
                 auto_invoke_next_row: bool = False, commit_message: Optional[str] = None,
                 refresh_notebook_experiment:bool = False,
                 eln_entry_refresh_list: Optional[List[ExperimentEntry]] = None,
                 create_eln_snapshot: bool = False,
                 include_entry_description_in_eln_snapshot: bool = False):
        """
        The objects of this class should not be created by end users.
        The library will create this object on initialization of webhook context.
        """
        self.passed = passed
        self.display_text = display_text
        self.list_values = list_values
        self.directive = directive
        self.client_callback_request = client_callback_request
        self.refresh_data = refresh_data
        self.report_builder_template_populator_data = report_builder_template_populator_data
        self.auto_invoke_next_row = auto_invoke_next_row
        self.commit_message = commit_message
        self.refresh_notebook_experiment = refresh_notebook_experiment
        self.eln_entry_refresh_list = eln_entry_refresh_list
        self.create_eln_snapshot = create_eln_snapshot
        self.include_entry_description_in_eln_snapshot = include_entry_description_in_eln_snapshot

    def to_json(self) -> Dict[str, Any]:
        directive_pojo = None
        if self.directive is not None:
            directive_pojo = self.directive.to_json()
        client_callback_pojo = None
        if self.client_callback_request is not None:
            client_callback_pojo = self.client_callback_request.to_json()
        report_builder_populator_pojo = None
        if self.report_builder_template_populator_data is not None:
            report_builder_populator_pojo = self.report_builder_template_populator_data.to_json()
        eln_entry_id_refresh_list = None
        if self.eln_entry_refresh_list is not None:
            eln_entry_id_refresh_list = [entry.entry_id for entry in self.eln_entry_refresh_list]
        return {
            'passed': self.passed,
            'displayText': self.display_text,
            'listValues': self.list_values,
            'directive': directive_pojo,
            'clientCallbackRequest': client_callback_pojo,
            'refreshData': self.refresh_data,
            'rbTemplatePopulatorDataPojo': report_builder_populator_pojo,
            'autoInvokeNextRow': self.auto_invoke_next_row,
            'commitMessage': self.commit_message,
            'refreshNotebookExperiment': self.refresh_notebook_experiment,
            'experimentEntryIdRefreshList': eln_entry_id_refresh_list,
            'createNotebookExperimentSnapshot': self.create_eln_snapshot,
            'includeEntryDescriptionsInExperimentSnapshot': self.include_entry_description_in_eln_snapshot
        }
