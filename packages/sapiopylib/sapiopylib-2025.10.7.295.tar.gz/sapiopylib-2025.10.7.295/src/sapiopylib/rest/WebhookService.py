import sys
import traceback
from abc import ABC, abstractmethod
from typing import Dict, Optional, Type, Any

from flask import Flask, request
from flask.views import MethodView

from sapiopylib.rest.pojo.webhook.WebhookContext import SapioWebhookContext, SapioWebhookContextParser
from sapiopylib.rest.pojo.webhook.WebhookResult import SapioWebhookResult


class AbstractWebhookHandler(ABC, MethodView):
    """
    All webhook implementations should inherit AbstractWebhookHandler,
    which would be registered to a WebhookConfiguration that is sent to WebhookServerFactory configure a Flask server.

    The main implementation method should be written under run() method, in which you are provided with webhook context.
    """
    verify_sapio_cert: bool = True
    client_timeout_seconds: int = 60

    def __init__(self, verify_sapio_cert: bool = True, client_timeout_seconds: int = 60):
        self.verify_sapio_cert = verify_sapio_cert
        self.client_timeout_seconds = client_timeout_seconds

    def post(self) -> Dict[str, Any]:
        """
        Internal method to be executed to translate incoming requests.
        """
        request_body_json = request.json
        context: SapioWebhookContext = SapioWebhookContextParser.parse_webhook(request_body_json,
                                                                               self.client_timeout_seconds,
                                                                               self.verify_sapio_cert)
        # noinspection PyBroadException
        try:
            return self.run(context).to_json()
        except Exception:
            print('Error occurred while running webhook custom logic. See traceback.', file=sys.stderr)
            traceback.print_exc()
            return SapioWebhookResult(False, display_text="Error occurred during webhook execution.").to_json()

    @abstractmethod
    def run(self, context: SapioWebhookContext) -> SapioWebhookResult:
        """
        The execution details for this service.

        :param context: The webhook context provided to you when it is called.
        :return: The webhook result to send back to Sapio.
        """
        pass


class WebhookConfiguration:
    """
    Specifies a webhook configuration for a server.
    """
    verify_sapio_cert: bool
    client_timeout_seconds: int
    debug: bool
    _handlers_by_sub_path: Dict[str, Type[AbstractWebhookHandler]]

    # CR-51508 Set verify_sapio_cert to True by default.
    def __init__(self, verify_sapio_cert: bool = True,
                 client_timeout_seconds: int = 60, debug=False):
        self.verify_sapio_cert = verify_sapio_cert
        self.client_timeout_seconds = client_timeout_seconds
        self.debug = debug
        self._handlers_by_sub_path = dict()

    def register(self, url_path, handler_clazz: Type[AbstractWebhookHandler]):
        """
        Register a new webhook endpoint.

        :param url_path: The endpoint that will be used to invoke the given class.
        :param handler_clazz: The webhook handler class that will be run when this endpoint is called.
        """
        self._handlers_by_sub_path[url_path] = handler_clazz

    @property
    def handlers_by_sub_path(self):
        return self._handlers_by_sub_path


class WebhookServerFactory:
    """
    The class includes methods to configure a new webhook server application.
    """
    @staticmethod
    def configure_flask_app(app: Optional[Flask], config: WebhookConfiguration) -> Flask:
        """
        Configure a new or existing flask server.

        :param app: The existing Flask server. If None is specified, a new server is created with default configs.
        :param config: The Sapio webhook configurations for the Flask server.
        :return: The input Flask app, or a new one if no input was provided.
        """
        if app is None:
            app = Flask('SapioWebhookServer')
        app.debug = config.debug
        for url, handler_clazz in config.handlers_by_sub_path.items():
            if config.debug:
                print("Register POST: " + url)
            app.add_url_rule(url, methods=['POST'], view_func=handler_clazz.
                             as_view(handler_clazz.__name__, verify_sapio_cert=config.verify_sapio_cert,
                                     client_timeout_seconds=config.client_timeout_seconds))
        print("** Registration Completed **")
        return app
