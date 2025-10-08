from sapiopylib.rest.pojo.webhook.VeloxRules import VeloxTypeRuleFieldMapResult

from sapiopylib.rest.WebhookService import AbstractWebhookHandler, WebhookConfiguration, WebhookServerFactory
from sapiopylib.rest.pojo.webhook.WebhookContext import SapioWebhookContext
from sapiopylib.rest.pojo.webhook.WebhookResult import SapioWebhookResult


class TestDeleteHandler(AbstractWebhookHandler):
    def run(self, context: SapioWebhookContext) -> SapioWebhookResult:
        field_map_results = context.velox_on_save_field_map_result_map
        value: list[VeloxTypeRuleFieldMapResult]
        for key, value in field_map_results.items():
            for v in value:
                velox_type = v.velox_type_pojo
                field_map_list = v.field_map_list
                print(velox_type.data_type_name + ": " + str(field_map_list))
        return SapioWebhookResult(True)

class TestStatusHandler(AbstractWebhookHandler):
    def run(self, context: SapioWebhookContext) -> SapioWebhookResult:
        entry = context.experiment_entry
        print("Entry Status is: " + entry.entry_status.description)
        return SapioWebhookResult(True)

config: WebhookConfiguration = WebhookConfiguration(verify_sapio_cert=False, debug=True)
config.register('/test_delete_rule', TestDeleteHandler)
config.register("/eln_experiment_status_test", TestStatusHandler)

app = WebhookServerFactory.configure_flask_app(app=None, config=config)
app.run(host="0.0.0.0", port=8099)
