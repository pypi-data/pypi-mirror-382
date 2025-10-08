from enum import Enum
from typing import Any


class CallbackType(Enum):
    """
    All possible client callbacks a webhook handler could use.
    """
    FILE_PROMPT = 0
    MULTI_FILE_PROMPT = 1
    WRITE_FILE = 2
    DATA_RECORD_SELECTION = 3
    TABLE_ENTRY_DIALOG = 4
    FORM_ENTRY_DIALOG = 5
    LIST_DIALOG = 6
    OPTION_DIALOG = 7
    INPUT_SELECTION = 8
    DATA_RECORD_DIALOG = 9


class WebhookEndpointType(Enum):
    """
    Invocation point type that the webhook endpoint will be called by Sapio.
    """
    ACTIONMENU = 'Action Menu', False
    FORMTOOLBAR = 'Form Toolbar', False
    TABLETOOLBAR = 'Table Toolbar', False
    TEMP_DATA_FORM_TOOLBAR = 'Temporary Data Form Toolbar', False
    TEMP_DATA_TABLE_TOOLBAR = 'Temporary Data Table Toolbar', False
    VELOXONSAVERULEACTION = 'Velox On Save Rule Action', True
    VELOX_RULE_ACTION = 'Velox Rule Action', True
    VELOXELNRULEACTION = 'Velox ELN Rule Action', True
    NOTEBOOKEXPERIMENTMAINTOOLBAR = 'Notebook Experiment Main Toolbar Button', False
    EXPERIMENTENTRYTOOLBAR = 'Notebook Experiment Entry Toolbar Button', False
    SELECTIONDATAFIELD = 'Selection Data Field', False
    REPORT_BUILDER_TEMPLATE_DATA_POPULATOR = 'Report Builder Template Data Populator Plugin', False
    SCHEDULEDPLUGIN = 'Scheduled Plugin', False,
    ACTIONDATAFIELD = 'Action Data Field', False
    CALENDAR_EVENT_CLICK_HANDLER = 'Calendar Event Click Handler Plugin', False
    CUSTOM = 'Custom Plugin Point', False,
    ACTION_TEXT_FIELD = 'Action Text Field Plugin', False
    NOTEBOOKEXPERIMENTGRABBER = 'Notebook Experiment Grabber', False
    CONVERSATION_BOT = 'Conversation Bot', False
    REPORTTOOLBAR = 'Advanced Search Toolbar', False

    display_name: str
    retry_endpoint: bool

    def __init__(self, display_name: str, retry_endpoint: bool):
        self.display_name = display_name
        self.retry_endpoint = retry_endpoint


class WebhookDirectiveType(Enum):
    """
    All client callback directives available to a Sapio webhook.
    """
    FORM = 'FormDirectivePojo'
    TABLE = 'TableDirectivePojo'
    CUSTOM_REPORT = 'CustomReportDirectivePojo'
    EXPERIMENT_ENTRY = 'ExperimentEntryDirectivePojo'
    ELN_EXPERIMENT = 'NotebookExperimentDirectivePojo'
    HOME_PAGE = 'HomePageDirectivePojo'

    jackson_type: str

    def __init__(self, jackson_type: str):
        self.jackson_type = jackson_type

class SearchType(Enum):
    """
    Different ways to search a data record.

    Attributes:
        QUICK_SEARCH: Display the quick search option in the dialog.
        ADVANCED_SEARCH: Display the advanced search option in the dialog.
        BROWSE_TREE: Display the data tree option in the dialog.
    """
    QUICK_SEARCH = 0
    ADVANCED_SEARCH = 1
    BROWSE_TREE = 2


class FormAccessLevel(Enum):
    """
    What can user do with the form?

    Attributes:
        EDITABLE: The dialog will be fully editable based on the data type definition backing the record.
        NOT_EDITABLE: All fields displayed on the layout in the dialog will be read only.
        READ_ONLY: The view will be completely read only.  No core features or plugins will be displayed and all fields on the layout will be disabled.
    """
    EDITABLE = 0
    NOT_EDITABLE = 1
    READ_ONLY = 2


class ScanToSelectCriteria:
    """
    scan-to-select-feature

    Attributes:
        match_on_field_names_to_show: If not null or empty, the scan-to-select editor will show these fields only to match on. otherwise, all non-html, string-based, single line fields of the specified type will show to choose from.
        default_match_on_field_name: The default value to set the scan-to-select editor to when initialized.
    """
    match_on_field_names_to_show: list[str] | None
    default_match_on_field_name: str | None

    def __init__(self, match_on_field_names_to_show: list[str] | None = None,
                             default_match_on_field_name: str | None = None):
        self.match_on_field_names_to_show = match_on_field_names_to_show
        self.default_match_on_field_name = default_match_on_field_name

    def to_json(self) -> dict[str, Any]:
        return {
            'matchOnFieldNamesToShow': self.match_on_field_names_to_show,
            'defaultMatchOnFieldName': self.default_match_on_field_name
        }
