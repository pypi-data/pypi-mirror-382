import sys
import unittest
from io import BytesIO
from pathlib import Path
from typing import Set

from sapiopylib.rest.DataMgmtService import DataMgmtServer
from sapiopylib.rest.utils.autopaging import *
from sapiopylib.rest.utils.recorddatasinks import FileSaveRecordDataSink, InMemoryRecordDataSink, InMemoryStringDataSink

user = SapioUser(url="https://linux-vm:8443/webservice/api", verify_ssl_cert=False,
                 guid="3c232543-f407-4828-aae5-b33d4cd31fa7",
                 username="yqiao_api", password="Password1!")
data_record_manager = DataMgmtServer.get_data_record_manager(user)

class FR51549Test(unittest.TestCase):

    def test_file_write(self):
        example_data: bytes = b"blah blah blah"
        record = data_record_manager.add_data_record("Attachment")
        with BytesIO(example_data) as f:
            data_record_manager.set_attachment_data(record, "file.txt", f)
        file_path: Path = Path("/tmp/blah.txt")
        sink = FileSaveRecordDataSink(file_path, user)
        sink.get_attachment_data(record)

        with open(file_path, "rb") as f:
            data: bytes = f.read()
            self.assertEqual(data, example_data)

    def test_bytes_write(self):
        example_data: bytes = b"blah blah blah"
        record = data_record_manager.add_data_record("Attachment")
        with BytesIO(example_data) as f:
            data_record_manager.set_attachment_data(record, "file.txt", f)
        sink = InMemoryRecordDataSink(user)
        sink.get_attachment_data(record)
        self.assertEqual(sink.data, example_data)

    def test_string_write(self):
        example_data: bytes = b"blah blah blah"
        record = data_record_manager.add_data_record("Attachment")
        with BytesIO(example_data) as f:
            data_record_manager.set_attachment_data(record, "file.txt", f)
        sink = InMemoryStringDataSink(user)
        sink.get_attachment_data(record)
        self.assertEqual(sink.text, example_data.decode("UTF-8"))
