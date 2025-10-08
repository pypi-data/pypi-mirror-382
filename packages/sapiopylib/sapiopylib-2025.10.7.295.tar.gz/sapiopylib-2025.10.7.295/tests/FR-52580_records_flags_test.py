from sapiopylib.rest.DataMgmtService import DataMgmtServer
from sapiopylib.rest.SesssionManagerService import SessionManager
from sapiopylib.rest.WebhookService import WebhookConfiguration, WebhookServerFactory, AbstractWebhookHandler
from sapiopylib.rest.pojo.session import AuditLogEntry
from sapiopylib.rest.pojo.webhook.WebhookContext import SapioWebhookContext
from sapiopylib.rest.pojo.webhook.WebhookResult import SapioWebhookResult
from sapiopylib.rest.utils.recordmodel.RecordModelManager import RecordModelManager
from sapiopylib.rest.utils.recordmodel.last_saved import LastSavedValueManager

# YQ:  Make sure "Invoke prior to commit changes set to true on the rules before using these.
# Hook on delete directory to delete rule for example...
# Audit log entry test is on new records. it will add a new message custom for the one that found as new :)


class TestDeleteFlagOnRule(AbstractWebhookHandler):

    def run(self, context: SapioWebhookContext) -> SapioWebhookResult:
        has_deleted: bool = False
        for record in context.data_record_list:
            if record.is_deleted:
                print("Is Deleted Found: " + str(record.record_id))
                has_deleted = True
            else:
                print("Not Deleted: " + str(record.fields))
        if not has_deleted:
            print("Can't find the deleted record.")
        return SapioWebhookResult(True)


class TestNewFlagOnRule(AbstractWebhookHandler):

    def run(self, context: SapioWebhookContext) -> SapioWebhookResult:
        has_new: bool = False
        session_man = SessionManager(context.user)
        for record in context.data_record_list:
            if record.is_new:
                print("Is New Found: " + str(record.record_id))
                has_new = True
                session_man.insert_audit_log([AuditLogEntry(
                    record.data_type_name, record.record_id, record.data_record_name, "I found new record!")])
            else:
                print("Not New: " + str(record.fields))
        if not has_new:
            print("Can't find the new record.")
        return SapioWebhookResult(True)


class TestLastSavedValuesRule(AbstractWebhookHandler):

    def run(self, context: SapioWebhookContext) -> SapioWebhookResult:
        model_man = RecordModelManager(context.user)
        last_save_man = model_man.last_saved_manager
        inst_man = model_man.instance_manager
        models = inst_man.add_existing_records(context.data_record_list)
        last_save_man.load(models)
        print(str(last_save_man._model_data_cache))
        client_callback = DataMgmtServer.get_client_callback(context.user)
        for model in models:
            client_callback.display_info(last_save_man.get_last_saved_fields(model))
        return SapioWebhookResult(True)


config: WebhookConfiguration = WebhookConfiguration(verify_sapio_cert=False, debug=True)
config.register('/delete_test', TestDeleteFlagOnRule)
config.register('/new_test', TestNewFlagOnRule)
config.register('/last_saved_test', TestLastSavedValuesRule)

app = WebhookServerFactory.configure_flask_app(app=None, config=config)
app.run(host="0.0.0.0", port=8099)
