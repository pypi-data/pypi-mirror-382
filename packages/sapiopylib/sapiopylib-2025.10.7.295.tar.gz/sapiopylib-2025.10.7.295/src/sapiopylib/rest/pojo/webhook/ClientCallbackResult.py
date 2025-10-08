from __future__ import annotations

import base64
from abc import ABC, abstractmethod
from typing import Any, List, Dict, Optional

from sapiopylib.rest.pojo.DataRecord import DataRecord
from sapiopylib.rest.pojo.UserInfo import UserInfo
from sapiopylib.rest.pojo.webhook.WebhookEnums import CallbackType


class AbstractClientCallbackResult(ABC):
    """
    If this is filled in a webhook context, this means user has entered a data after a previous run on same context.
    Usually a webhook that uses client callback will have if-else branch:
    If the client callback is None, then ask user to enter something.
    If the client callback is not None, then we returned for continued processing after user entered some values.

    Attributes:
        user_cancelled = whether user has cancelled the dialog instead of pressing 'OK'.
    """
    user_cancelled: bool
    callback_context_data: Optional[str]

    @abstractmethod
    def get_callback_type(self):
        """
        Get the callback data type for this client callback result.
        """
        pass

    def __init__(self, user_cancelled: bool, callback_context_data: Optional[str]):
        self.user_cancelled = user_cancelled
        self.callback_context_data = callback_context_data


class DataRecordSelectionResult(AbstractClientCallbackResult):
    """
    Client callback result that is returned following successful retrieve of user input from a selection request.
    This result will contain the list of field maps that were selected by the user.

    Attributes:
        selected_field_map_list = The field map list user has selected in the client callback.
    """
    selected_field_map_list: Optional[List[Dict[str, Any]]]

    def get_callback_type(self):
        return CallbackType.DATA_RECORD_SELECTION

    def __init__(self, user_cancelled: bool, callback_context_data: Optional[str],
                 selected_field_map_list: Optional[List[Dict[str, Any]]]):
        super().__init__(user_cancelled, callback_context_data)
        self.selected_field_map_list = selected_field_map_list


class MultiFilePromptResult(AbstractClientCallbackResult):
    """
    Client callback result that is returned after successful upload of user file data through the browser.
    This result will contain the file data by file names.

    Attributes:
        files: A dictionary of (file name) to (file data in byte array)
    """
    files: Optional[Dict[str, bytes]]

    def get_callback_type(self):
        return CallbackType.MULTI_FILE_PROMPT

    def __init__(self, user_cancelled: bool, callback_context_data: Optional[str],
                 files: Optional[Dict[str, bytes]] = None):
        super().__init__(user_cancelled, callback_context_data)
        self.files = files


class FilePromptResult(AbstractClientCallbackResult):
    """
    Client callback result that is returned following the successful retrieval of user input from a file prompt request.
    This result will contain the file bytes retrieved from the user as well as the file name.
    """
    file_bytes: Optional[bytes]
    file_path: Optional[str]

    def get_callback_type(self):
        return CallbackType.FILE_PROMPT

    def __init__(self, user_cancelled: bool, callback_context_data: Optional[str],
                 file_bytes: Optional[bytes], file_path: Optional[str]):
        super().__init__(user_cancelled, callback_context_data)
        self.file_path = file_path
        self.file_bytes = file_bytes


class FormEntryDialogResult(AbstractClientCallbackResult):
    """
    Client callback result that is returned following the successful retrieval of user input from a form UI request.
    """
    user_response_map: Optional[Dict[str, Any]]

    def get_callback_type(self):
        return CallbackType.FORM_ENTRY_DIALOG

    def __init__(self, user_cancelled: bool, callback_context_data: Optional[str],
                 user_response_map: Optional[Dict[str, Any]]):
        super().__init__(user_cancelled, callback_context_data)
        self.user_response_map = user_response_map


class ListDialogResult(AbstractClientCallbackResult):
    """
    Payload for response for the user to select an option in a list dialog displayed.
    """
    selected_options_list: Optional[List[str]]

    def get_callback_type(self):
        return CallbackType.LIST_DIALOG

    def __init__(self, user_cancelled: bool, callback_context_data: Optional[str],
                 selected_options_list: Optional[List[str]]):
        super().__init__(user_cancelled, callback_context_data)
        self.selected_options_list = selected_options_list


class OptionDialogResult(AbstractClientCallbackResult):
    """
    Payload in response to a request for the user to select a button option displayed in a dialog.

    selection: The selected button index that the user made in the dialog.
    This value can be null if the user cancelled the dialog.
    button_text: The button text associated with the selected button index that the user made in the dialog.
    This value can be null if the user cancelled the dialog.
    """
    selection: Optional[int]
    button_text: Optional[str]

    def get_callback_type(self):
        return CallbackType.OPTION_DIALOG

    def __init__(self, user_cancelled: bool, callback_context_data: Optional[str],
                 selection: Optional[int], button_text: Optional[str]):
        super().__init__(user_cancelled, callback_context_data)
        self.selection = selection
        self.button_text = button_text


class TableEntryDialogResult(AbstractClientCallbackResult):
    """
    Client callback result returning user response of a table entry dialog.

    user_response_data_list: The field map list of the data user have provided.
    This can be null if user has cancelled.
    """
    user_response_data_list: Optional[List[Dict[str, Any]]]

    def get_callback_type(self):
        return CallbackType.TABLE_ENTRY_DIALOG

    def __init__(self, user_cancelled: bool, callback_context_data: Optional[str],
                 user_response_data_list: Optional[List[Dict[str, Any]]]):
        super().__init__(user_cancelled, callback_context_data)
        self.user_response_data_list = user_response_data_list


class WriteFileResult(AbstractClientCallbackResult):
    """
    Returns the result code for whether the user successfully downloaded a file data uploaded earlier.
    """

    def get_callback_type(self):
        return CallbackType.WRITE_FILE

    def __init__(self, user_cancelled: bool, callback_context_data: Optional[str]):
        super().__init__(user_cancelled, callback_context_data)

class InputSelectionResult(AbstractClientCallbackResult):
    selected_record_list: list[DataRecord]

    def get_callback_type(self):
        return CallbackType.INPUT_SELECTION

    def __init__(self, user_cancelled: bool, callback_context_data: Optional[str],
                 selected_record_list: list[DataRecord]):
        super().__init__(user_cancelled, callback_context_data)
        self.selected_record_list = selected_record_list

class DataRecordDialogResponse(AbstractClientCallbackResult):
    """
    Result from a data record form editor dialog.

    Attributes:
        dialog_result: True if OK button was pressed by user.
    """
    dialog_result: bool

    def get_callback_type(self):
        return CallbackType.DATA_RECORD_DIALOG

    def __init__(self, user_cancelled: bool, callback_context_data: Optional[str],
                 dialog_result: bool):
        super().__init__(user_cancelled, callback_context_data)
        self.dialog_result = dialog_result


class ClientCallbackResultParser:
    @staticmethod
    def parse_client_callback_result(json_dct: Dict[str, Any]) -> AbstractClientCallbackResult:
        user_cancelled: bool = json_dct.get('userCancelled')
        callback_context_data: Optional[str] = json_dct.get("callbackContextData")
        callback_type = CallbackType[json_dct.get('callbackType')]
        if callback_type == CallbackType.DATA_RECORD_SELECTION:
            selected_field_map_list: Optional[List[Dict[str, Any]]] = \
                json_dct.get('selectedFieldMapList')
            return DataRecordSelectionResult(user_cancelled, callback_context_data,
                                             selected_field_map_list=selected_field_map_list)
        elif callback_type == CallbackType.MULTI_FILE_PROMPT:
            encoded: Optional[Dict[str, str]] = json_dct.get('files')
            files: Optional[Dict[str, bytes]] = dict()
            if encoded:
                for key, value in encoded.items():
                    if key and value:
                        decoded_value: bytes = base64.b64decode(value.encode('utf-8'))
                        files[key] = decoded_value
            return MultiFilePromptResult(user_cancelled, callback_context_data, files)
        elif callback_type == CallbackType.FILE_PROMPT:
            file_bytes: Optional[bytes] = None
            if json_dct.get('fileBytes'):
                file_bytes = base64.b64decode(json_dct.get('fileBytes'))
            file_path: Optional[str] = json_dct.get('filePath')
            return FilePromptResult(user_cancelled, callback_context_data, file_bytes=file_bytes, file_path=file_path)
        elif callback_type == CallbackType.FORM_ENTRY_DIALOG:
            user_response_map: Optional[Dict[str, Any]] = json_dct.get('userResponseMap')
            return FormEntryDialogResult(user_cancelled, callback_context_data, user_response_map=user_response_map)
        elif callback_type == CallbackType.LIST_DIALOG:
            selected_options_list: Optional[List[str]] = json_dct.get('selectedOptionList')
            return ListDialogResult(user_cancelled, callback_context_data, selected_options_list=selected_options_list)
        elif callback_type == CallbackType.OPTION_DIALOG:
            selection: Optional[int] = json_dct.get('selection')
            button_text: Optional[str] = json_dct.get('buttonText')
            return OptionDialogResult(user_cancelled, callback_context_data,
                                      selection=selection, button_text=button_text)
        elif callback_type == CallbackType.TABLE_ENTRY_DIALOG:
            user_response_data_list: Optional[List[Dict[str, Any]]] = \
                json_dct.get('userResponseDataList')
            return TableEntryDialogResult(user_cancelled, callback_context_data,
                                          user_response_data_list=user_response_data_list)
        elif callback_type == CallbackType.WRITE_FILE:
            return WriteFileResult(user_cancelled, callback_context_data)
        elif callback_type == CallbackType.INPUT_SELECTION:
            selected_record_list: list[DataRecord] = []
            selected_records_json = json_dct.get('selectedDataRecordList')
            if selected_records_json:
                selected_record_list = [DataRecord.from_json(x) for x in selected_records_json]
            return InputSelectionResult(user_cancelled, callback_context_data,
                                        selected_record_list)
        elif callback_type == CallbackType.DATA_RECORD_DIALOG:
            dialog_result: bool = json_dct.get('dialogResult')
            return DataRecordDialogResponse(user_cancelled, callback_context_data,
                                            dialog_result)
        else:
            raise NotImplemented("Unexpected callback type " + callback_type.name)


class ESigningResponsePojo:
    """
    An E-sign completion result object for webservices.

    Attributes:
        id: A globally unique ID that tracks the current E-sign session.
        authenticated: Whether the user was successfully authenticated.
        same_user: Whether the user making the request to authenticate is the same as the user being authenticated.
        user_comment: The comment user has entered.
        user_info: Get the UserInfo for the user that attempted authentication
        validation_msg: A message about the success or failure of the authentication request, including errors or reasons for rejecting the request or information about what type of authentication was used (ie. LDAP)
        additional_fields_map: A field map representing additional values that were custom added to the E-Sign dialog in the custom temporary data type provided in request.
    """
    id: str
    authenticated: bool
    same_user: bool
    user_comment: str | None
    user_info: UserInfo | None
    validation_msg: str
    additional_fields_map: dict[str, Any] | None

    def __init__(self):
        self.id = ""
        self.authenticated = False
        self.same_user = False
        self.user_info = None
        self.user_comment = None
        self.validation_msg = ""
        self.additional_fields_map = None

    @staticmethod
    def from_json(json_dct: dict[str, Any]) -> ESigningResponsePojo:
        ret = ESigningResponsePojo()
        ret.id = json_dct.get('id')
        ret.authenticated = json_dct.get('authenticated')
        ret.same_user = json_dct.get('requestingUser')
        ret.user_comment = json_dct.get('userComment')
        if json_dct.get('userInfo'):
            ret.user_info = UserInfo.parse(json_dct.get('userInfo'))
        ret.validation_msg = json_dct.get('validationMessage')
        ret.additional_fields_map = json_dct.get('additionalFieldsMap')
        return ret

