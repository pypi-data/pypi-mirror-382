from typing import cast

from sapiopylib.rest.DataMgmtService import DataMgmtServer
from sapiopylib.rest.WebhookService import AbstractWebhookHandler, WebhookConfiguration, WebhookServerFactory
from sapiopylib.rest.pojo.datatype.FieldDefinition import VeloxIntegerFieldDefinition, VeloxDoubleFieldDefinition, \
    SapioDoubleFormat, VeloxStringFieldDefinition, VeloxBooleanFieldDefinition
from sapiopylib.rest.pojo.webhook.ClientCallbackRequest import *
from sapiopylib.rest.pojo.webhook.ClientCallbackResult import DataRecordSelectionResult
from sapiopylib.rest.pojo.webhook.WebhookContext import SapioWebhookContext
from sapiopylib.rest.pojo.webhook.WebhookResult import SapioWebhookResult
from sapiopylib.rest.utils.FormBuilder import FormBuilder


def _enter_width_data(context: SapioWebhookContext) -> tuple[int | None, float | None]:
    """
    Let user enter a custom pixel width or percent width.
    :return the tuple of (px entered, percent entered) which can both be None if user did not specify anything.
    """
    width_px_field_name: str = "WidthPx"
    width_percent_field_name: str = "WidthPercent"
    fb = FormBuilder("WidthEntry", "Width Config", "Width Configs")
    width_px_field = VeloxIntegerFieldDefinition(fb.data_type_name, width_px_field_name, "Width (px)",
                                                 1, 5000)
    width_px_field.editable = True
    width_px_field.required = False
    fb.add_field(width_px_field)
    width_percent_field = VeloxDoubleFieldDefinition(fb.data_type_name, width_percent_field_name, "Width (%)",
                                                     0, 100, double_format=SapioDoubleFormat.PERCENTAGE)
    width_percent_field.editable = True
    width_percent_field.required = False
    fb.add_field(width_percent_field)
    temp_dt = fb.get_temporary_data_type()
    # Test icon now.... It should be an orange magnifier from my localhost image library...
    temp_dt.icon_name = '3I0sJcI62yyjBv7aU8vUQYjfmlRstCbtBPySpv5qtY'
    temp_dt.icon_color = "#ff8300"
    client_callback = DataMgmtServer.get_client_callback(context.user)

    response = client_callback.show_form_entry_dialog(FormEntryDialogRequest("Enter Width Testing Parameters",
                                                                             "VERIFY MY ICON IS ORANGE MAGNIFIER!", temp_dt))
    if not response:
        return None, None
    width_px: int | None = response.get(width_px_field_name)
    width_percent: float | None = response.get(width_percent_field_name)
    if width_percent:
        width_percent = width_percent / 100.0
    return width_px, width_percent


def do_width_test(context: SapioWebhookContext) -> SapioWebhookResult:
    width_px, width_percent = _enter_width_data(context)
    client_callback = DataMgmtServer.get_client_callback(context.user)
    fb: FormBuilder = FormBuilder()
    fb.add_field(VeloxStringFieldDefinition(fb.get_data_type_name(), "Test1", "Test 1"))
    fb.add_field(VeloxBooleanFieldDefinition(fb.get_data_type_name(), "Test2", "Test 2"))
    temp_dt = fb.get_temporary_data_type()
    initial_field_map_list: list[dict[str, Any]] = []
    initial_field_map_list.append({"Test1": "aaa", "Test2": True})
    initial_field_map_list.append({"Test1": "bbb", "Test2": False})
    client_callback.show_table_entry_dialog(TableEntryDialogRequest(
        "Test Table Entry Width", "Note that some dialogs have min width so you probably want to set to some higher values for testing...",
        temp_dt, initial_field_map_list,
        width_in_pixels=width_px, width_percentage=width_percent))
    client_callback.show_form_entry_dialog(FormEntryDialogRequest(
        "Test Form Entry  Width", "", temp_dt, width_in_pixels=width_px, width_percentage=width_percent
    ))

    client_callback.show_esign_dialog(ESigningRequestPojo("Test ESign Dialog Width", "", False,
                                                          width_in_pixels=width_px, width_percentage=width_percent))
    client_callback.show_input_dialog(InputDialogCriteria("Test Input Dialog Width", "",
                                                          width_in_pixels=width_px, width_percentage=width_percent))
    client_callback.show_list_dialog(ListDialogRequest("Test List Dialog Width", False, ["I1", "I2"],
                                                       width_in_pixels=width_px, width_percentage=width_percent))
    client_callback.show_option_dialog(OptionDialogRequest("Test Option Dialog Width", "", ["A", "B"],
                                                           width_in_pixels=width_px, width_percentage=width_percent))
    return SapioWebhookResult(True)


def do_table_image_data_test(context):
    from sapiopycommons.chem.IndigoMolecules import indigo, renderer
    indigo.setOption("dearomatize-verification", False)
    fb: FormBuilder = FormBuilder("TableImageDataTest", "Table Image Data Test", "Table Image Data Tests")
    fb.add_field(VeloxStringFieldDefinition(fb.data_type_name, "SMILES", "SMILES"))
    temp_dt = fb.get_temporary_data_type()
    temp_dt.record_image_assignable = True
    # aspirin, nicotin, advil
    smiles_list = ["CC(=O)OC1=CC=CC=C1C(=O)O", "CN1CCC[C@H]1C2=CN=CC=C2", "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O"]
    image_data_list: list[bytes] = []
    field_map_list: list[dict[str, Any]] = []
    for smiles in smiles_list:
        mol = indigo.loadMolecule(smiles)
        mol.dearomatize()
        svg_data = renderer.renderToString(mol).encode()
        image_data_list.append(svg_data)
        field_map_list.append({"SMILES": smiles})
    client_callback = DataMgmtServer.get_client_callback(context.user)
    client_callback.show_table_entry_dialog(TableEntryDialogRequest(
        "Table Entry Test", "", temp_dt, field_map_list, record_image_data_list=image_data_list))
    client_callback.show_temp_table_selection_dialog(TempTableSelectionRequest(
        temp_dt, "Table Selection Test", field_map_list, record_image_data_list=image_data_list))
    return SapioWebhookResult(True)


def do_default_value_form_entry_test(context):
    client_callback = DataMgmtServer.get_client_callback(context.user)
    fb: FormBuilder = FormBuilder()
    fb.add_field(VeloxStringFieldDefinition(fb.get_data_type_name(), "Test1", "Test 1"))
    fb.add_field(VeloxBooleanFieldDefinition(fb.get_data_type_name(), "Test2", "Test 2"))
    temp_dt = fb.get_temporary_data_type()
    default_fields = {"Test1": "aaa", "Test2": True}
    client_callback.show_form_entry_dialog(FormEntryDialogRequest("Test Default Form Entry Values", "",
                                                                  temp_dt, default_values=default_fields))
    return SapioWebhookResult(True)


def do_legacy_data_table_test(context):
    if context.client_callback_result is not None:
        result: DataRecordSelectionResult = cast(DataRecordSelectionResult, context.client_callback_result)
        if result.user_cancelled:
            return SapioWebhookResult(True, display_text="User Cancelled")
        else:
            return SapioWebhookResult(True, display_text="Selected " + str(len(result.selected_field_map_list)) + "Records.")
    fb: FormBuilder = FormBuilder("TableImageDataTest", "Table Image Data Test", "Table Image Data Tests")
    fb.add_field(VeloxStringFieldDefinition(fb.data_type_name, "SMILES", "SMILES"))
    temp_dt = fb.get_temporary_data_type()
    smiles_list = ["CC(=O)OC1=CC=CC=C1C(=O)O", "CN1CCC[C@H]1C2=CN=CC=C2", "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O"]
    field_map_list: list[dict[str, Any]] = []
    for smiles in smiles_list:
        field_map_list.append({"SMILES": smiles})
    return SapioWebhookResult(True, client_callback_request=DataRecordSelectionRequest(
        temp_dt.display_name, temp_dt.plural_display_name, temp_dt.get_field_def_list(), field_map_list, "Legacy Table Test"))


class TestUserInputDialogs(AbstractWebhookHandler):

    def run(self, context: SapioWebhookContext) -> SapioWebhookResult:
        if context.client_callback_result is not None:
            return do_legacy_data_table_test(context)
        options = ["Width Test", "Table Image Data Test", "Default Value in Form Entry Test", "Legacy Data Table Test"]
        client_callback = DataMgmtServer.get_client_callback(context.user)
        option_selected = client_callback.show_option_dialog(OptionDialogRequest("Select Test to Run", "", options, closable=True))
        if option_selected is None:
            return SapioWebhookResult(True)
        if option_selected == 0:
            return do_width_test(context)
        elif option_selected == 1:
            return do_table_image_data_test(context)
        elif option_selected == 2:
            return do_default_value_form_entry_test(context)
        elif option_selected == 3:
            return do_legacy_data_table_test(context)
        client_callback.display_error("I am not sure what you have selected. =_=")
        return SapioWebhookResult(False)


config: WebhookConfiguration = WebhookConfiguration(verify_sapio_cert=False, debug=True)
config.register('/dialog_test', TestUserInputDialogs)

app = WebhookServerFactory.configure_flask_app(app=None, config=config)
app.run(host="0.0.0.0", port=8099)
