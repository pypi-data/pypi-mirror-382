from abc import ABC, abstractmethod
from typing import Any, List, Dict

from sapiopylib.rest.pojo.CustomReport import CustomReport
from sapiopylib.rest.pojo.DataRecord import DataRecord
from sapiopylib.rest.pojo.webhook.WebhookEnums import WebhookDirectiveType


class AbstractWebhookDirective(ABC):
    """
    A webhook directive links client to a specific page after the webhook handling result had returned back to user.
    """

    @abstractmethod
    def get_directive_type(self) -> WebhookDirectiveType:
        pass

    def to_json(self) -> Dict[str, Any]:
        return {'type': self.get_directive_type().jackson_type}


# FR-53281: Add a layout name parameter to the Form and Table directives.
class FormDirective(AbstractWebhookDirective):
    """
    A directive implementation that will route the user to a specific data record.
    """
    data_record: DataRecord
    layout_name: str | None

    def __init__(self, data_record: DataRecord, layout_name: str | None = None):
        self.data_record = data_record
        self.layout_name = layout_name

    def get_directive_type(self) -> WebhookDirectiveType:
        return WebhookDirectiveType.FORM

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_json()
        ret['dataRecord'] = self.data_record.to_json()
        ret['dataTypeLayoutName'] = self.layout_name
        return ret


class TableDirective(AbstractWebhookDirective):
    """
    A directive implementation that will route the user to a list of data records.
    """
    data_record_list: List[DataRecord]
    layout_name: str | None

    def __init__(self, data_record_list: List[DataRecord], layout_name: str | None = None):
        self.data_record_list = data_record_list
        self.layout_name = layout_name

    def get_directive_type(self) -> WebhookDirectiveType:
        return WebhookDirectiveType.TABLE

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_json()
        ret['dataRecordPojoList'] = [x.to_json() for x in self.data_record_list]
        ret['dataTypeLayoutName'] = self.layout_name
        return ret


class CustomReportDirective(AbstractWebhookDirective):
    """
    Launches a custom report search to user UI.
    """
    custom_report: CustomReport

    def __init__(self, custom_report: CustomReport):
        self.custom_report = custom_report

    def get_directive_type(self) -> WebhookDirectiveType:
        return WebhookDirectiveType.CUSTOM_REPORT

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_json()
        ret['customReportPojo'] = self.custom_report.to_json()
        return ret


class ExperimentEntryDirective(AbstractWebhookDirective):
    """
    A directive implementation that will route the user to the provided experiment entry within the provided ELN Exp.
    """
    eln_experiment_id: int
    experiment_entry_id: int

    def __init__(self, eln_experiment_id: int, experiment_entry_id: int):
        self.eln_experiment_id = eln_experiment_id
        self.experiment_entry_id = experiment_entry_id

    def get_directive_type(self) -> WebhookDirectiveType:
        return WebhookDirectiveType.EXPERIMENT_ENTRY

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_json()
        ret['notebookExperimentId'] = self.eln_experiment_id
        ret['experimentEntryId'] = self.experiment_entry_id
        return ret


class ElnExperimentDirective(AbstractWebhookDirective):
    """
    A directive implementation that will route the user to the provided notebook experiment.
    """
    eln_experiment_id: int

    def __init__(self, eln_experiment_id: int):
        self.eln_experiment_id = eln_experiment_id

    def get_directive_type(self) -> WebhookDirectiveType:
        return WebhookDirectiveType.ELN_EXPERIMENT

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_json()
        ret['notebookExperimentId'] = self.eln_experiment_id
        return ret


class HomePageDirective(AbstractWebhookDirective):
    """
    A directive implementation that will route the user to the Home Page on return of this webhook.
    """
    def get_directive_type(self) -> WebhookDirectiveType:
        return WebhookDirectiveType.HOME_PAGE
