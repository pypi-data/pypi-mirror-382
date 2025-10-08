import unittest

from sapiopylib.rest.User import SapioUser

from sapiopylib.rest.DataMgmtService import DataMgmtServer

from sapiopylib.rest.pojo.Message import *

user = SapioUser(url="https://linux-vm:8443/webservice/api", verify_ssl_cert=False,
                 guid="3c232543-f407-4828-aae5-b33d4cd31fa7",
                 username="yqiao_api", password="Password1!")

class EmailAttachmentDataTest(unittest.TestCase):

    def test_email_attachments(self):
        test_data: bytearray
        with open("resources/fr-51846.ssg", "rb") as io:
            test_data = bytearray(io.read())

        email: VeloxEmail = VeloxEmail(addr_to=[VeloxEmailRecipient(email="yqiao@sapiosciences.com", name="Yechen Qiao")],
                                       subject="Test",
                                       plain_text_body="Test",
                                       attachment_list=[VeloxRawEmailAttachment(data=bytes(test_data), attachment_name="test.ssg")])
        DataMgmtServer.get_messenger(user).send_email(email)
