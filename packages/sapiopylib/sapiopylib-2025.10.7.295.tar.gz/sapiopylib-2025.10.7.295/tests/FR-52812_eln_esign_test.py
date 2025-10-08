
from sapiopylib.rest.DataMgmtService import DataMgmtServer
from sapiopylib.rest.User import SapioServerException
from sapiopylib.rest.WebhookService import WebhookConfiguration, AbstractWebhookHandler, WebhookServerFactory
from sapiopylib.rest.pojo.datatype.FieldDefinition import VeloxBooleanFieldDefinition
from sapiopylib.rest.pojo.eln.ElnExperiment import InitializeNotebookExperimentPojo, ElnExperiment
from sapiopylib.rest.pojo.eln.ExperimentEntry import ExperimentEntry
from sapiopylib.rest.pojo.eln.ExperimentEntryCriteria import ElnEntryCriteria
from sapiopylib.rest.pojo.eln.SapioELNEnums import ElnExperimentStatus, ElnEntryType, ExperimentEntryStatus
from sapiopylib.rest.pojo.webhook.ClientCallbackRequest import ESigningRequestPojo, OptionDialogRequest
from sapiopylib.rest.pojo.webhook.WebhookContext import SapioWebhookContext
from sapiopylib.rest.pojo.webhook.WebhookResult import SapioWebhookResult
from sapiopylib.rest.utils.FormBuilder import FormBuilder


def do_experiment_test(user) -> SapioWebhookResult:
    eln_man = DataMgmtServer.get_eln_manager(user)
    exp: ElnExperiment = eln_man.create_notebook_experiment(InitializeNotebookExperimentPojo('Test E-Sign'))
    client_callback = DataMgmtServer.get_client_callback(user)
    try:
        client_callback.show_esign_dialog(ESigningRequestPojo('E-Signing Experiment ' + exp.notebook_experiment_name, '', True,
                                                              eln_experiment_id=exp.notebook_experiment_id, eln_experiment_status=ElnExperimentStatus.Completed))
        exp = eln_man.get_eln_experiment_by_id(exp.notebook_experiment_id)
        client_callback.display_info("The current status of the experiment is: " + exp.notebook_experiment_status.name)

        signatures_by_id = eln_man.get_eln_experiment_signatures([exp.notebook_experiment_id])
        sigs = signatures_by_id.get(exp.notebook_experiment_id)
        client_callback.display_info("Number of signatures inside the new experiment is: " + str(len(sigs)))
        if len(sigs) != 1:
            client_callback.display_error("Expected number of signatures to be 1 in the signature list.")
        for sig in sigs:
            client_callback.display_info(str(sig))
    except SapioServerException as e:
        client_callback.display_error("E-Sign had failed: " + str(e))
    return SapioWebhookResult(True)

def do_entry_test(user) -> SapioWebhookResult:
    eln_man = DataMgmtServer.get_eln_manager(user)
    exp: ElnExperiment = eln_man.create_notebook_experiment(InitializeNotebookExperimentPojo('Test E-Sign'))
    client_callback = DataMgmtServer.get_client_callback(user)
    entry: ExperimentEntry = eln_man.add_experiment_entry(exp.notebook_experiment_id, ElnEntryCriteria(ElnEntryType.Table, "Samples", "Sample", 2))
    try:
        client_callback.show_esign_dialog(ESigningRequestPojo('E-Signing Entry ' + exp.notebook_experiment_name, '', True,
                                                              eln_experiment_id=exp.notebook_experiment_id,
                                                              experiment_entry_id=entry.entry_id, experiment_entry_status=ExperimentEntryStatus.Completed))
        sigs = eln_man.get_entry_signatures(exp.notebook_experiment_id, entry.entry_id)
        client_callback.display_info("Number of signatures inside the new experiment is: " + str(len(sigs)))
        if len(sigs) != 1:
            client_callback.display_error("Expected number of signatures to be 1 in the signature list.")
        for sig in sigs:
            client_callback.display_info(str(sig))
    except SapioServerException as e:
        client_callback.display_error("E-Sign had failed: " + str(e))
    return SapioWebhookResult(True)

def do_regression_test(user) -> SapioWebhookResult:
    client_callback = DataMgmtServer.get_client_callback(user)
    fb = FormBuilder()
    field = VeloxBooleanFieldDefinition("Test", "Test", "Test", default_value=True)
    field.editable = True
    fb.add_field(field)
    temp_dt = fb.get_temporary_data_type()
    dialog_result = client_callback.show_esign_dialog(ESigningRequestPojo("Esign Test Title", "Esign Test Message", True, temp_dt))
    if dialog_result is None:
        client_callback.display_info("User has cancelled E-sign operation.")
    else:
        msg = "User has E-signed.\n"
        if dialog_result.authenticated:
            msg += "The e-sign attempt was successful. The person who authenticated was " + dialog_result.user_info.username
            if not dialog_result.same_user:
                msg += " which was not the same user as the current user."
            else:
                msg += "."
        else:
            msg += "The user has failed authentication. Error was: " + dialog_result.validation_msg
        if dialog_result.user_comment:
            msg += "\nUser comment was: " + dialog_result.user_comment
        flag: bool = bool(dialog_result.additional_fields_map['Test'])
        if flag:
            msg += "\nAnd the flag was checked."
        client_callback.display_info(msg)
    return SapioWebhookResult(True)


class MainDialogHandler(AbstractWebhookHandler):

    def run(self, context: SapioWebhookContext) -> SapioWebhookResult:
        user = context.user
        client_callback = DataMgmtServer.get_client_callback(user)
        option_result = client_callback.show_option_dialog(OptionDialogRequest('Select Test', '', ['Experiment E-Sign', 'Entry E-Sign', 'Regular E-sign']))
        if option_result is None:
            return SapioWebhookResult(True)
        if option_result == 0:
            return do_experiment_test(user)
        elif option_result == 1:
            return do_entry_test(user)
        else:
            return do_regression_test(user)


config: WebhookConfiguration = WebhookConfiguration(verify_sapio_cert=False, debug=True)
config.register('/dialog_test', MainDialogHandler)

app = WebhookServerFactory.configure_flask_app(app=None, config=config)
app.run(host="0.0.0.0", port=8099)
