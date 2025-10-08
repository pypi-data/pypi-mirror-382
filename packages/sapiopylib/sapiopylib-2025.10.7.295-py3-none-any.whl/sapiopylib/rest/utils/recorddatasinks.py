# FR-51549 Added class
# Holds utility classes to handle data record streaming common operations.
from abc import ABC, abstractmethod
from io import BytesIO
from pathlib import Path
from typing import IO

from sapiopylib.rest.DataMgmtService import DataMgmtServer
from sapiopylib.rest.DataRecordManagerService import DataRecordManager
from sapiopylib.rest.DataService import DataManager
from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.DataRecord import DataRecord
from sapiopylib.rest.pojo.webhook.ClientCallbackRequest import FilePromptRequest


class AbstractRecordDataSink(ABC):
    """
    A data sink can be used together with data record manager's consumption methods for attachment/image data.
    This is abstarct class and should not be used directly. Use one of its child class.
    """
    _user: SapioUser
    _data_record_manager: DataRecordManager
    _data_manager: DataManager

    def __init__(self, user: SapioUser):
        self._user = user
        self._data_record_manager = DataMgmtServer.get_data_record_manager(user)
        self._data_manager = DataMgmtServer.get_data_manager(user)

    @abstractmethod
    def __enter__(self) -> IO:
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @abstractmethod
    def consume_data(self, chunk: bytes, context_obj: IO) -> None:
        pass

    def get_record_image(self, record: DataRecord) -> None:
        """
        Consume the record image using the specified data sink's method.
        """
        with self as io:
            def do_consume(chunk: bytes) -> None:
                return self.consume_data(chunk, io)

            self._data_record_manager.get_record_image(record, do_consume)

    def get_attachment_data(self, record: DataRecord) -> None:
        """
        Consume the attachment data using the specified data sink's method.
        """
        with self as io:
            def do_consume(chunk: bytes) -> None:
                return self.consume_data(chunk, io)

            self._data_record_manager.get_attachment_data(record, do_consume)

    def export_to_xml(self, records: list[DataRecord], recursive: bool = True,
                      data_types_to_exclude: list[str | None] = None):
        """
        Export the selected files into an .xml.zip file format, to be able to be imported later via data manager.
        """
        with self as io:
            def do_consume(chunk: bytes) -> None:
                return self.consume_data(chunk, io)

            self._data_manager.export_to_xml(records, do_consume,
                                             recursive=recursive, data_types_to_exclude=data_types_to_exclude)

    def upload_single_file_to_webhook_server(self, request: FilePromptRequest) -> str | None:
        """
        Requests user to upload a single file in a browser file window, and then receive the file into the sink.
        This method requires the session to have active client callback object (such as from webhook).
        :param request The file prompt client callback request object.
        """
        with self as io:
            def do_consume(chunk: bytes) -> None:
                return self.consume_data(chunk, io)

            client_callback = DataMgmtServer.get_client_callback(self._user)
            file_path = client_callback.show_file_dialog(request, do_consume)
            return file_path

    def consume_client_callback_file_path_data(self, fake_file_path: str) -> None:
        """
        To be used together with a multi-file dialog. When a multi-file dialog returns sucessfully, a list of fake file paths are given to the webhook server as a response object.
        For every one of these fake file paths, we should be able to read the data inside.

        This method requires the session to have active client callback object (such as from webhook).
        :param fake_file_path: The particular fake file path we are reading in the list.
        """
        with self as io:
            def do_consume(chunk: bytes) -> None:
                return self.consume_data(chunk, io)

            client_callback = DataMgmtServer.get_client_callback(self._user)
            client_callback.get_file(fake_file_path, do_consume)


class FileSaveRecordDataSink(AbstractRecordDataSink):
    """
    This data sink stores the data into a specific file path.
    """
    _file_path_to_save: Path
    _file_obj: IO

    def __init__(self, file_path_to_save: Path, user: SapioUser):
        super().__init__(user)
        self._file_path_to_save = file_path_to_save

    def __enter__(self):
        self._file_obj = open(self._file_path_to_save, mode="wb")
        return self._file_obj

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._file_obj.flush()
        self._file_obj.close()

    def consume_data(self, chunk: bytes, context_obj: IO) -> None:
        context_obj.write(chunk)


class InMemoryRecordDataSink(AbstractRecordDataSink):
    """
    Write into an in-memory byte array.
    After run, you can retrieve it with the data property
    Be careful to not run out of your own RAM.
    It will take 2x the space to perform this operation in RAM but is efficient in speed.
    """
    _mem_io: BytesIO
    _data: bytes

    @property
    def data(self) -> bytes:
        if not hasattr(self, "_data"):
            raise ValueError("Data has not been created yet. Please execute run() method to return it before getting.")
        return self._data

    def __enter__(self):
        self._mem_io = BytesIO()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._mem_io.flush()
        self._mem_io.seek(0)
        # Even if we use memoryview the tobytes() of that will do a copy from buffer... So regardless we need 1 copy.
        self._data = self._mem_io.read()
        self._mem_io.close()

    def consume_data(self, chunk: bytes, context_obj: IO) -> None:
        self._mem_io.write(chunk)


class InMemoryStringDataSink(AbstractRecordDataSink, ABC):
    """
    Writes the result into a string of specified encoding.
    After run, you can retrieve it with the text property
    Be careful to not run out of your own RAM.
    It will take 3x the space to perform this operation in RAM but is efficient in speed.
    """
    _mem_io: BytesIO
    _encoding: str
    _text: str

    @property
    def encoding(self) -> str:
        return self._encoding

    @property
    def text(self) -> str:
        if not hasattr(self, "_text"):
            raise ValueError("Text has not been created yet. Please execute run() method to return it before getting.")
        return self._text

    def __init__(self, user: SapioUser, encoding: str = "UTF-8"):
        super().__init__(user)
        self._encoding = encoding

    def __enter__(self):
        self._mem_io = BytesIO()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._mem_io.flush()
        self._mem_io.seek(0)
        # Even if we use memoryview the tobytes() of that will do a copy from buffer... So regardless we need 1 copy.
        self._text = self._mem_io.read().decode(self._encoding)
        self._mem_io.close()

    def consume_data(self, chunk: bytes, context_obj: IO) -> None:
        self._mem_io.write(chunk)
