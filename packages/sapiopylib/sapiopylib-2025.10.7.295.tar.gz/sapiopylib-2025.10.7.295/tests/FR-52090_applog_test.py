import unittest

from sapiopylib.rest.DataMgmtService import DataMgmtServer
from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.Message import VeloxLogMessage, VeloxLogLevel

user = SapioUser(url="https://linux-vm:8443/webservice/api", verify_ssl_cert=False,
                 guid="3c232543-f407-4828-aae5-b33d4cd31fa7",
                 username="yqiao_api", password="Password1!")
messenger = DataMgmtServer.get_messenger(user)

class TestFR51635(unittest.TestCase):
    def test_logs(self):
        messenger.log_message(VeloxLogMessage("Test Message"))
        messenger.log_message(VeloxLogMessage("Test Warning", VeloxLogLevel.WARNING))
        messenger.log_message(VeloxLogMessage("Test Error", VeloxLogLevel.ERROR))
        print("Manually verify the logs are printed...")
        self.assertTrue(True)


messenger.log_message(VeloxLogMessage("Test logging without stacks."))