# Test that input selection works as expected manually for input of default values of null (default),
# and 5 respecitvely.
import unittest

from sapiopylib.rest.DataMgmtService import DataMgmtServer
from sapiopylib.rest.WebhookService import WebhookConfiguration, AbstractWebhookHandler, WebhookServerFactory
from sapiopylib.rest.pojo.webhook.ClientCallbackRequest import InputDialogCriteria, InputSelectionRequest
from sapiopylib.rest.pojo.webhook.WebhookContext import SapioWebhookContext
from sapiopylib.rest.pojo.webhook.WebhookResult import SapioWebhookResult


class InputSelectionNumToCreateTestHandler(AbstractWebhookHandler, unittest.TestCase):
    def run(self, context: SapioWebhookContext) -> SapioWebhookResult:
        if context.client_callback_result is not None:
            return SapioWebhookResult(True)
        user = context.user
        client_callback = DataMgmtServer.get_client_callback(user)
        client_callback.show_input_selection_dialog(InputSelectionRequest(
            "Directory","Null test for num to create. Click Create New and see.", multi_select=True, show_create_new_option=True))
        client_callback.show_input_selection_dialog(InputSelectionRequest(
            "Directory","Single Select, Null num defaults to create case",multi_select=False, show_create_new_option=True))
        def test_fun():
            # Should fail since multi-select is off and num defaults to create is 10 > 0
            client_callback.show_input_selection_dialog(
                InputSelectionRequest("Directory", "Exception Test. This fails if you see it.",
                                      multi_select=False, show_create_new_option=True, num_default_add_new_records=10))

        self.assertRaises(ValueError, test_fun)
        client_callback.show_input_selection_dialog(
            InputSelectionRequest("Directory", "5 test for number to create. Click Create New and see.",
                                  multi_select=True, show_create_new_option=True, num_default_add_new_records=5))
        return SapioWebhookResult(True,
                                  client_callback_request=InputSelectionRequest("Directory", "10 return create test",
                                                                                multi_select=True,
                                                                                show_create_new_option=True,
                                                                                num_default_add_new_records=10))


config: WebhookConfiguration = WebhookConfiguration(verify_sapio_cert=False, debug=True)
config.register('/dialog_test', InputSelectionNumToCreateTestHandler)

app = WebhookServerFactory.configure_flask_app(app=None, config=config)
app.run(host="0.0.0.0", port=8099)
