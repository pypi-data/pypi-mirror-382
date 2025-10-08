import base64
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, List, Dict, Optional

from sapiopylib.rest.pojo.CustomReport import CustomReport
from sapiopylib.rest.pojo.DataRecord import DataRecord
from sapiopylib.rest.pojo.datatype.DataTypeLayout import DataTypeLayout
from sapiopylib.rest.pojo.datatype.FieldDefinition import AbstractVeloxFieldDefinition
from sapiopylib.rest.pojo.datatype.TemporaryDataType import TemporaryDataType
from sapiopylib.rest.pojo.eln.SapioELNEnums import ElnExperimentStatus, ExperimentEntryStatus
from sapiopylib.rest.pojo.webhook.WebhookEnums import CallbackType, SearchType, ScanToSelectCriteria, FormAccessLevel
from sapiopylib.utils.string import to_base64


class PopupType(Enum):
    """
    The different client callback toastr pop up types.
    """
    Success = 0
    Info = 1
    Warning = 2
    Error = 3


class DisplayPopupRequest:
    """
    A request payload to indicate what toastr message we want to send to human end user.
    """
    title: str
    message: str
    popup_type: PopupType

    def __init__(self, title: str, message: str, popup_type: PopupType):
        self.title = title
        self.message = message
        self.popup_type = popup_type

    def to_json(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "message": self.message,
            "popupType": self.popup_type.name
        }


class AbstractClientCallbackRequest(ABC):
    """
    A request for a client callback to be shown to the user that invoked the webhook.
    """
    callback_context_data: Optional[str]

    def __init__(self, callback_context_data: Optional[str] = None):
        self.callback_context_data = callback_context_data

    @abstractmethod
    def get_callback_type(self) -> CallbackType:
        """
        Get the callback data type for this client callback result.
        """
        pass

    def to_json(self) -> Dict[str, Any]:
        return {
            'callbackType': self.get_callback_type().name,
            'callbackContextData': self.callback_context_data
        }


class DataRecordSelectionRequest(AbstractClientCallbackRequest):
    """
    A callback request to select a list of field map rows.
    """
    data_type_display_name: str
    data_type_plural_display_name: str
    field_def_list: List[AbstractVeloxFieldDefinition]
    field_map_list: List[Dict[str, Any]]
    dialog_message: Optional[str]
    multi_select: bool

    def __init__(self, data_type_display_name: str, data_type_plural_display_name: str,
                 field_def_list: List[AbstractVeloxFieldDefinition],
                 field_map_list: List[Dict[str, Any]],
                 dialog_message: Optional[str] = None, multi_select: bool = False,
                 callback_context_data: Optional[str] = None):
        super().__init__(callback_context_data)
        self.data_type_display_name = data_type_display_name
        self.data_type_plural_display_name = data_type_plural_display_name
        self.field_def_list = field_def_list
        self.field_map_list = field_map_list
        self.dialog_message = dialog_message
        self.multi_select = multi_select

    def get_callback_type(self) -> CallbackType:
        return CallbackType.DATA_RECORD_SELECTION

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_json()
        ret['dialogMessage'] = self.dialog_message
        ret['dataTypeDisplayName'] = self.data_type_display_name
        ret['dataTypePluralDisplayName'] = self.data_type_plural_display_name
        ret['fieldDefinitionList'] = [x.to_json() for x in self.field_def_list]
        ret['fieldMapList'] = self.field_map_list
        ret['multiSelect'] = self.multi_select
        return ret


class TempTableSelectionRequest(AbstractClientCallbackRequest):
    """
    A callback request to select a list of field map rows.

    Attributes:
        temporary_data_type: The data type definition that will be displayed in the table.
        dialog_message: The message that will be displayed in the selection dialog.
        field_map_list: The list of field maps that will be displayed in the table.
        record_image_data_list: The list of record images in order of field map list. If this is not specified, the record images will not be displayed.
        preselected_record_ids: For this option to work, a RecordId field definition must be defined in the temporary data type, and unique values must be populated in field map list.
        multi_select: whether user is allowed to select more than 1 item in this dialog.
    """
    temporary_data_type: TemporaryDataType
    dialog_message: str
    field_map_list: List[Dict[str, Any]]
    record_image_data_list: list[bytes] | None
    preselected_record_ids: list[int] | None
    multi_select: bool

    def __init__(self, temporary_data_type: TemporaryDataType, dialog_message: str,
                 field_map_list: List[Dict[str, Any]], record_image_data_list: list[bytes] | None = None,
                 preselected_record_ids: list[int] | None = None,
                 multi_select: bool = False,
                 callback_context_data: Optional[str] = None):
        super().__init__(callback_context_data)
        self.temporary_data_type = temporary_data_type
        self.field_map_list = field_map_list
        self.record_image_data_list = record_image_data_list
        self.preselected_record_ids = preselected_record_ids
        self.dialog_message = dialog_message
        self.multi_select = multi_select

    def get_callback_type(self) -> CallbackType:
        return CallbackType.DATA_RECORD_SELECTION

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_json()
        ret['temporaryDataType'] = self.temporary_data_type.to_json()
        ret['dialogMessage'] = self.dialog_message
        ret['fieldMapList'] = self.field_map_list
        if self.record_image_data_list:
            ret['encodedRecordImageList'] = [to_base64(x) for x in self.record_image_data_list]
        ret['preselectedRecordIds'] = self.preselected_record_ids
        ret['multiSelect'] = self.multi_select
        return ret


class MultiFilePromptRequest(AbstractClientCallbackRequest):
    """
    Request the user to upload multiple files. User will be asked fo upload one or more files.
    """
    dialog_title: str
    show_image_editor: bool
    file_extension: str
    show_camera_button: bool

    def __init__(self, dialog_title: str, show_image_editor: bool = False, file_extension: str = "",
                 show_camera_button: bool = False, callback_context_data: Optional[str] = None):
        """
        Request the user to upload multiple files.
        :param dialog_title: The title of the file prompt
        :param show_image_editor: Whether the user will see an image editor when image is uploaded in this file prompt.
        :param show_camera_button: Whether the user will be able to use camera to take a picture as an upload request,
        rather than selecting an existing file.
        :param file_extension: The acceptable file extensions for the file prompt. Comma separated.
        """
        super().__init__(callback_context_data)
        self.dialog_title = dialog_title
        self.show_image_editor = show_image_editor
        self.file_extension = file_extension
        self.show_camera_button = show_camera_button

    def get_callback_type(self):
        return CallbackType.MULTI_FILE_PROMPT

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_json()
        ret.update({
            'dialogTitle': self.dialog_title,
            'fileExtension': self.file_extension,
            'showImageEditor': self.show_image_editor,
            'showCameraButton': self.show_camera_button
        })
        return ret


class FilePromptRequest(AbstractClientCallbackRequest):
    """
    Request for a single file prompt to be displayed to the user. User will be asked to upload a file.

    dialog_title: The title of the file prompt

    show_image_editor: Whether the user will see an image editor when image is uploaded in this file prompt.

    show_camera_button: Whether the user will be able to use camera to take a picture as an upload request, rather
    than selecting an existing file.

    file_extension: The acceptable file extensions for the file prompt. Comma separated.
    """
    dialog_title: str
    show_image_editor: bool
    file_extension: Optional[str]
    show_camera_button: bool

    def __init__(self, dialog_title: str, show_image_editor: bool = False, file_extension: Optional[str] = None,
                 show_camera_button: bool = False, callback_context_data: Optional[str] = None):
        """
        Request for a file prompt to be displayed to the user.

        :param dialog_title: The title of the file prompt
        :param show_image_editor: Whether the user will see an image editor when image is uploaded in this file prompt.
        :param show_camera_button: Whether the user will be able to use camera to take a picture as an upload request,
        rather than selecting an existing file.
        :param file_extension: The acceptable file extensions for the file prompt. Comma separated.
        """
        super().__init__(callback_context_data)
        self.dialog_title = dialog_title
        self.show_image_editor = show_image_editor
        self.file_extension = file_extension
        self.show_camera_button = show_camera_button

    def get_callback_type(self):
        return CallbackType.FILE_PROMPT

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_json()
        ret.update({
            'dialogTitle': self.dialog_title,
            'fileExtension': self.file_extension,
            'showImageEditor': self.show_image_editor,
            'showCameraButton': self.show_camera_button
        })
        return ret


class FormEntryDialogRequest(AbstractClientCallbackRequest):
    """
    Requests the current context's user to pop up a client callback asking user to enter info in a form.

    title: The title of the form entry dialog
    message: The message to show on top of the entry dialog.
    data_type_def: The type definition, including field definitions and layouts, for this form.
    width_in_pixels: The width of the form entry dialog.
    width_percentage: The width of the input dialog as a percentage of the screen width. If pixel width is set, this will be ignored.
    """
    title: str
    message: str
    data_type_def: TemporaryDataType
    default_values: dict[str, Any] | None
    width_in_pixels: int | None
    width_percentage: float | None

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_json()
        ret['title'] = self.title
        ret['message'] = self.message
        ret['temporaryDataTypePojo'] = self.data_type_def.to_json()
        ret['defaultValues'] = self.default_values
        ret['widthInPixels'] = self.width_in_pixels
        ret['widthPercentage'] = self.width_percentage
        return ret

    def __init__(self, title: str, message: str, data_type_def: TemporaryDataType,
                 default_values: dict[str, Any] | None = None,
                 width_in_pixels: int | None = None, width_percentage: float | None = None,
                 callback_context_data: Optional[str] = None):
        """
        Requests the current context's user to pop up a client callback asking user to enter info in a form.

        :param title: The title of the form entry dialog
        :param message: The message to show on top of the entry dialog.
        :param data_type_def: The type definition, including field definitions and layouts, for this form.
        """
        super().__init__(callback_context_data)
        self.title = title
        self.message = message
        self.data_type_def = data_type_def
        self.default_values = default_values
        self.width_in_pixels = width_in_pixels
        self.width_percentage = width_percentage

    def get_callback_type(self) -> CallbackType:
        return CallbackType.FORM_ENTRY_DIALOG


class ListDialogRequest(AbstractClientCallbackRequest):
    """
    Payload for request for the user to select an option in a list dialog displayed.

    title: title of the list dialog prompt
    multi_select: Whether we allow user to multi-select in this list dialog.
    option_list: The available options text for the user.
    """
    title: str
    multi_select: bool
    option_list: List[str]
    pre_selected_values: list[str] | None
    width_in_pixels: int | None
    width_percentage: float | None

    def get_callback_type(self) -> CallbackType:
        return CallbackType.LIST_DIALOG

    def __init__(self, title: str, multi_select: bool, option_list: List[str],
                 pre_selected_values: list[str] | None = None,
                 width_in_pixels: int | None = None, width_percentage: float | None = None,
                 callback_context_data: Optional[str] = None):
        """
        Payload for request for the user to select an option in a list dialog displayed.

        :param title: title of the list dialog prompt
        :param multi_select: Whether we allow user to multi-select in this list dialog.
        :param option_list: The available options text for the user.
        """
        super().__init__(callback_context_data)
        self.title = title
        self.multi_select = multi_select
        self.option_list = option_list
        self.pre_selected_values = pre_selected_values
        self.width_in_pixels = width_in_pixels
        self.width_percentage = width_percentage

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_json()
        ret['title'] = self.title
        ret['multiSelect'] = self.multi_select
        ret['optionList'] = self.option_list
        ret['preselectedValues'] = self.pre_selected_values
        ret['widthInPixels'] = self.width_in_pixels
        ret['widthPercentage'] = self.width_percentage
        return ret


class OptionDialogRequest(AbstractClientCallbackRequest):
    """
    Payload to request for the user to select a button option displayed in a dialog.

    title: The title of this dialog
    message: The message to show on top of the dialog body
    button_list: The buttons user can press, in order of user's theme button order style.
    default_selection: What user would select if the user has cancelled.
    closable: Whether the user can close (cancel) the dialog.
    width_in_pixels: The width of the input dialog in pixels.
    width_percentage: The width of the input dialog as a percentage of the screen width. If pixel width is set, this will be ignored.
    """
    title: str
    message: str
    button_list: List[str]
    default_selection: int
    closable: bool
    width_in_pixels: int | None
    width_percentage: float | None

    def __init__(self, title: str, message: str, button_list: List[str], default_selection: int = 0,
                 closable: bool = False, callback_context_data: Optional[str] = None,
                 width_in_pixels: int | None = None, width_percentage: float | None = None):
        super().__init__(callback_context_data)
        self.title = title
        self.message = message
        self.button_list = button_list
        self.default_selection = default_selection
        self.closable = closable
        self.width_in_pixels = width_in_pixels
        self.width_percentage = width_percentage

    def get_callback_type(self) -> CallbackType:
        return CallbackType.OPTION_DIALOG

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_json()
        ret['title'] = self.title
        ret['message'] = self.message
        ret['buttonList'] = self.button_list
        ret['defaultSelection'] = self.default_selection
        ret['closable'] = self.closable
        ret['widthInPixels'] = self.width_in_pixels
        ret['widthPercentage'] = self.width_percentage
        return ret


class TableEntryDialogRequest(AbstractClientCallbackRequest):
    """
    Client callback request prompting user a table entry dialog.

    Attributes:
        title: The title to show in the table entry dialog
        message: The message to show on top of the dialog body
        data_type_def: The field definition and layouts for this dialog.
        field_map_list: The default values in this table before user started to edit. Note: this must be filled with number of rows you want to edit (if user is presented with 5 rows, enter 5 dictionaries inside the list)
        record_image_data_list: a list of record image data, to be sent in order of field map list. If this is not set, no record image will be displayed in the table.
        group_by_field: The default field to group by.  This will be used to group the data in the table by default.
        width_in_pixels: The width of the input dialog in pixels.
        width_percentage: The width of the input dialog as a percentage of the screen width. If pixel width is set, this will be ignored.
    """
    title: str
    message: str
    data_type_def: TemporaryDataType
    field_map_list: List[Dict[str, Any]]
    record_image_data_list: list[bytes] | None
    group_by_field: str | None
    width_in_pixels: int | None
    width_percentage: float | None

    def __init__(self, title: str, message: str, data_type_def: TemporaryDataType,
                 field_map_list: List[Dict[str, Any]], callback_context_data: Optional[str] = None,
                 record_image_data_list: list[bytes] | None = None, group_by_field: str | None = None,
                 width_in_pixels: int | None = None, width_percentage: float | None = None):
        """
        Client callback request prompting user a table entry dialog.

        :param title: The title to show in the table entry dialog
        :param message: The message to show on top of the dialog body
        :param data_type_def: The field definition and layouts for this dialog.
        :param field_map_list: The default values in this table before user started to edit.
        Note: this must be filled with number of rows you want to edit
        (if user is presented with 5 rows, enter 5 dictionaries inside the list)
        """
        super().__init__(callback_context_data)
        self.title = title
        self.message = message
        self.data_type_def = data_type_def
        self.field_map_list = field_map_list
        self.record_image_data_list = record_image_data_list
        self.group_by_field = group_by_field
        self.width_in_pixels = width_in_pixels
        self.width_percentage = width_percentage

    def get_callback_type(self) -> CallbackType:
        return CallbackType.TABLE_ENTRY_DIALOG

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_json()
        ret['title'] = self.title
        ret['message'] = self.message
        ret['temporaryDataTypePojo'] = self.data_type_def.to_json()
        ret['fieldMapList'] = self.field_map_list
        if self.record_image_data_list:
            encoded_image_list: list[str] = [to_base64(x) for x in self.record_image_data_list]
            ret['encodedRecordImageList'] = encoded_image_list
        ret['groupByField'] = self.group_by_field
        ret['widthInPixels'] = self.width_in_pixels
        ret['widthPercentage'] = self.width_percentage
        return ret


class WriteFileRequest(AbstractClientCallbackRequest):
    """
    Write a short amount of file data onto the client. The user will download this file from browser.

    The return object from server is of type WriteFileResult, which you can use to check if user has cancelled.
    Note: file data will be stored in RAM in this operation.

    file_bytes: The file data to write.
    file_path: The filename of the written file.
    """
    file_bytes: bytes
    file_path: str

    def __init__(self, file_bytes: bytes, file_path: str, callback_context_data: Optional[str] = None):
        super().__init__(callback_context_data)
        self.file_bytes = file_bytes
        self.file_path = file_path

    def get_callback_type(self) -> CallbackType:
        return CallbackType.WRITE_FILE

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_json()
        ret['filePath'] = self.file_path
        encoded_data: bytes = base64.b64encode(self.file_bytes)
        ret['fileBytes'] = encoded_data.decode("utf-8")
        return ret


class MultiFileRequest(AbstractClientCallbackRequest):
    """
    Write multiple files to the user browser all at once. To fill the request, you can use it like a dictionary.

    The return object from server is of type WriteFileResult, which you can use to check if user has cancelled.
    """

    json_built: Dict[str, str]

    def __init__(self, initial_data: Dict[str, bytes] = None, callback_context_data: Optional[str] = None):
        super().__init__(callback_context_data)
        self.json_built = dict()
        if initial_data is not None:
            for key, value in initial_data.items():
                self.put(key, value)

    def __setitem__(self, key: str, value: bytes):
        self.put(key, value)

    def __getitem__(self, key: str):
        return self.json_built.get(key)

    def __iter__(self):
        return self.json_built.__iter__()

    def __hash__(self):
        return hash(self.json_built)

    def __eq__(self, other):
        if not isinstance(other, MultiFileRequest):
            return False
        return self.json_built == other.json_built

    def __len__(self):
        return len(self.json_built)

    def put(self, file_name: str, file_data: bytes) -> None:
        """
        Add a file to upload into this request.
        :param file_name: The file name to upload
        :param file_data: The file data to upload.
        """
        if not file_name or not file_data:
            return
        encoded_data: bytes = base64.b64encode(file_data)
        if not encoded_data:
            return
        self.json_built[file_name] = encoded_data.decode("utf-8")

    def get_callback_type(self) -> CallbackType:
        return CallbackType.WRITE_FILE

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_json()
        ret['files'] = self.json_built
        return ret


class InputSelectionRequest(AbstractClientCallbackRequest):
    """
    Select from records of the given data type that exist in the system.

    Attributes:
        data_type_name: The name of the data type to search for as input.
        dialog_message: The message that will be displayed in the selection dialog.
        enabled_search_type_set: The type of search that will be made available to the user through the dialog.
        show_only_key_fields: Whether only key fields of the selected data type should be displayed in the table of data in the dialog.
        record_id_black_list: Set of record IDs matching records that should not be seen as possible options in the dialog.
        record_id_white_list: Set of record IDs matching records matching the only records that should be seen as possible options in the dialog.
        preselected_record_id_list: The record IDs that should be selected in the dialog when it is initially displayed to the user.
        custom_search:  An alternate search to be used in the quick search section. If null or if the search is cross data type or not a report of the type specified, all records of the type will be shown (normal quick search results).
        scan_to_select_criteria: If set, will show a scan-to-select editor in the quick search section that allows for picking a field to match on and scanning a value to select records.
        multi_select: Whether the user can select multiple rows in the dialog.
        show_create_new_option: Whether the 'Create New' button will be visible to user to create new records in aether.
        num_default_add_new_records: Number of records to be added when user clicks "Create New" button. Note: multi-select must be set to True, and the data type needs to be group addable, or this will have no effect!
    """

    data_type_name: str
    dialog_message: str | None
    enabled_search_type_set: list[SearchType] | None
    show_only_key_fields: bool
    record_id_black_list: list[int] | None
    record_id_white_list: list[int] | None
    preselected_record_id_list: list[int] | None
    custom_search: CustomReport | None
    scan_to_select_criteria: ScanToSelectCriteria | None
    multi_select: bool
    show_create_new_option: bool
    num_default_add_new_records: int | None

    def get_callback_type(self) -> CallbackType:
        return CallbackType.INPUT_SELECTION

    def __init__(self, data_type_name: str, dialog_message: str | None = None,
                 enabled_search_type_set: list[SearchType] | None = None,
                 show_only_key_fields: bool = True,
                 record_id_black_list: list[int] | None = None,
                 record_id_white_list: list[int] | None = None,
                 preselected_record_id_list: list[int] | None = None,
                 custom_search: CustomReport | None = None,
                 scan_to_select_criteria: ScanToSelectCriteria | None = None,
                 multi_select: bool = False,
                 show_create_new_option: bool = False, num_default_add_new_records: int | None = None,
                 callback_context_data: Optional[str] = None):
        super().__init__(callback_context_data)
        self.data_type_name = data_type_name
        self.dialog_message = dialog_message
        self.enabled_search_type_set = enabled_search_type_set
        self.show_only_key_fields = show_only_key_fields
        self.record_id_black_list = record_id_black_list
        self.record_id_white_list = record_id_white_list
        self.preselected_record_id_list = preselected_record_id_list
        self.custom_search = custom_search
        self.scan_to_select_criteria = scan_to_select_criteria
        self.multi_select = multi_select
        self.show_create_new_option = show_create_new_option
        self.num_default_add_new_records = num_default_add_new_records
        if num_default_add_new_records and num_default_add_new_records > 1 and not multi_select:
            raise ValueError("When creating InputSelectionRequest: the num_default_add_new_records cannot be greater than 1 when multi select is set to False.")

    def to_json(self) -> dict[str, Any]:
        ret: dict[str, Any] = super().to_json()
        ret['dataTypeName'] = self.data_type_name
        ret['dialogMessage'] = self.dialog_message
        ret['enabledSearchTypeSet'] = None
        if self.enabled_search_type_set:
            ret['enabledSearchTypeSet'] = [x.name for x in self.enabled_search_type_set]
        ret['showOnlyKeyFields'] = self.show_only_key_fields
        ret['recordIdBlackList'] = self.record_id_black_list
        ret['recordIdWhiteList'] = self.record_id_white_list
        ret['preselectedRecordIds'] = self.preselected_record_id_list
        ret['customSearchPojo'] = None
        if self.custom_search:
            ret['customSearchPojo'] = self.custom_search.to_json()
        ret['scanToSelectCriteriaPojo'] = None
        if self.scan_to_select_criteria:
            ret['scanToSelectCriteriaPojo'] = self.scan_to_select_criteria.to_json()
        ret['multiSelect'] = self.multi_select
        ret['showCreateNewOption'] = self.show_create_new_option
        ret['numDefaultAddNewRecords'] = self.num_default_add_new_records
        return ret


class DataRecordDialogRequest(AbstractClientCallbackRequest):
    """
    Requests the current context's user to display a client callback showing the user a data record layout that can be used to either view the record or modify it.

    Attributes:
        title: The title of the dialog to be displayed to the user.
        data_record: The record to be displayed in the dialog.
        data_type_layout: The layout that will be used to display the record in the dialog. If this is not provided, then the layout assigned to the current user's group for this data type will be used.
        is_initially_minimized: If true, then the dialog will only show key fields and required fields initially until the expand button is clicked (similar to when using the build in add buttons to create new records).
        form_access_level: The level of access that the user will have on this field entry dialog. This attribute determines whether the user will be able to edit the fields in the dialog, use core features, or use toolbar plugins.
        plugin_path_list: A white list of plugins that should be displayed in the dialog. This white list includes plugins that would be displayed on sub tables in the layout.
        width_in_pixels: Dialog width override in number of pixels.
        width_percentage: Dialog width override in percent to total of window.
    """
    title: str
    data_record: DataRecord
    data_type_layout: DataTypeLayout | None
    is_initially_minimized: bool
    form_access_level: FormAccessLevel | None
    plugin_path_list: list[str] | None
    width_in_pixels: int | None
    width_percentage: float | None

    def get_callback_type(self) -> CallbackType:
        return CallbackType.DATA_RECORD_DIALOG

    def __init__(self, title: str, data_record: DataRecord,
                 data_type_layout: DataTypeLayout | None = None, is_initially_minimized: bool = True,
                 form_access_level: FormAccessLevel | None = None, plugin_path_list: list[str] | None = None,
                 callback_context_data: Optional[str] = None,
                 width_in_pixels: int | None = None, width_percentage: float | None = None):
        super().__init__(callback_context_data)
        self.title = title
        self.data_record = data_record
        self.data_type_layout = data_type_layout
        self.is_initially_minimized = is_initially_minimized
        self.form_access_level = form_access_level
        self.plugin_path_list = plugin_path_list
        self.width_in_pixels = width_in_pixels
        self.width_percentage = width_percentage

    def to_json(self) -> dict[str, Any]:
        ret: dict[str, Any] = super().to_json()
        ret['title'] = self.title
        ret['dataRecordPojo'] = self.data_record.to_json()
        ret['dataTypeLayoutPojo'] = None
        if self.data_type_layout:
            ret['dataTypeLayoutPojo'] = self.data_type_layout.to_pojo()
        ret['initiallyMinimalView'] = self.is_initially_minimized
        ret['formAccessLevel'] = None
        if self.form_access_level:
            ret['formAccessLevel'] = self.form_access_level.name
        ret['pluginPathList'] = self.plugin_path_list
        ret['widthInPixels'] = self.width_in_pixels
        ret['widthPercentage'] = self.width_percentage
        return ret


class InputDialogCriteria:
    """
    The criteria for input dialog asking a single field's value from a user.

    Attributes:
        title: The title of the input dialog.
        message: The full message to be displayed inside the input dialog.
        field_definition: If not specified, this is assumed to be a string field. If specified, you can set it as any other field type, such as an integer field or boolean field when prompting user.
        width_in_pixels: Dialog width override in number of pixels.
        width_percentage: Dialog width override in percent to total of window.
    """
    title: str
    message: str
    field_definition: AbstractVeloxFieldDefinition | None
    width_in_pixels: int | None
    width_percentage: float | None

    def __init__(self, title: str, message: str, field_definition: AbstractVeloxFieldDefinition | None = None,
                 width_in_pixels: int | None = None, width_percentage: float | None = None):
        self.title = title
        self.message = message
        self.field_definition = field_definition
        self.width_in_pixels = width_in_pixels
        self.width_percentage = width_percentage

    def to_json(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "message": self.message,
            "fieldDefinition": self.field_definition.to_json() if self.field_definition else None,
            "widthInPixels": self.width_in_pixels,
            "widthPercentage": self.width_percentage
        }


class ESigningRequestPojo:
    """
    E-sign request payload

    Attributes:
        title: The title of the E-sign dialog
        message: The full message inside the E-sign dialog
        show_comment: Whether to require user to enter comment. If this is set to true, then user MUST enter comment in the dialog for stating the "Meaning of Action".
        temporary_data_type: If you want to prompt any other fields, specify a temporary data type here. It can be left as None if there is nothing else you need to ask from user in the same dialog.
        width_in_pixels: The width of the input dialog in pixels.
        width_percentage: The width of the input dialog as a percentage of the screen width. If pixel width is set, this will be ignored.
        eln_experiment_id: If we are e-signing a notebook experiment, provide this ID.
        eln_experiment_status: If we are e-signing a notebook experiment, provide the new status after e-sign is successful.
        eln_entry_id: If we are e-signing an experiment entry, provide this ID along with notebook experiment ID.
        eln_entry_status: If we are e-signing a experiment entry, provide the new entry status after e-sign is successful.
    """
    title: str
    message: str
    show_comment: bool
    temporary_data_type: TemporaryDataType | None
    width_in_pixels: int | None
    width_percentage: float | None
    eln_experiment_id: int | None
    eln_experiment_status: ElnExperimentStatus | None
    experiment_entry_id: int | None
    experiment_entry_status: ExperimentEntryStatus | None

    def __init__(self, title: str, message: str, show_comment: bool, temp_dt: TemporaryDataType | None = None,
                 width_in_pixels: int | None = None, width_percentage: float | None = None,
                 eln_experiment_id: int | None = None, eln_experiment_status: ElnExperimentStatus | None = None,
                 experiment_entry_id: int | None = None, experiment_entry_status: ExperimentEntryStatus | None = None):
        self.title = title
        self.message = message
        self.show_comment = show_comment
        self.temporary_data_type = temp_dt
        self.width_in_pixels = width_in_pixels
        self.width_percentage = width_percentage
        self.eln_experiment_id = eln_experiment_id
        self.eln_experiment_status = eln_experiment_status
        self.experiment_entry_id = experiment_entry_id
        self.experiment_entry_status = experiment_entry_status

    def to_json(self) -> dict[str, Any]:
        eln_experiment_status_str = None
        if self.eln_experiment_status is not None:
            eln_experiment_status_str = self.eln_experiment_status.name
        eln_entry_stats_str = None
        if self.experiment_entry_status is not None:
            eln_entry_stats_str = self.experiment_entry_status.name
        return {
            "title": self.title,
            "message": self.message,
            "showComment": self.show_comment,
            "temporaryDataType": self.temporary_data_type.to_json() if self.temporary_data_type else None,
            "widthInPixels": self.width_in_pixels,
            "widthPercentage": self.width_percentage,
            "notebookExperimentId": self.eln_experiment_id,
            "notebookExperimentStatus": eln_experiment_status_str,
            "experimentEntryId": self.experiment_entry_id,
            "experimentEntryStatus": eln_entry_stats_str
        }
