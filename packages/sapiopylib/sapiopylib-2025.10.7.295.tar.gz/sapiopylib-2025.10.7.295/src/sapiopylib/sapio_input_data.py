import pickle

from sapiopylib import sapio_input_config


class SapioInputData:
    """
    Sapio Input Data captures what is fed by Sapio application.

    Only one instance should be created per python script. Then it should be passed around when needed.

    Author: Yechen Qiao
    """

    def __init__(self):
        """
        Perform I/O read to read and parse the data from Sapio application.
        """
        with open(sapio_input_config.inputPath, 'rb') as handle:
            input_data: dict = pickle.load(handle)
            self.payload = input_data.get("payload")
            self.attachmentDict = input_data.get("attachments")
            self.tempDirectory = input_data.get("temp.dir")
            self.outFile = input_data.get("out.file")
            self.inputFileDict = input_data.get("additional.input.files")

    def get_attachment_record_id_list(self):
        """
        Get list of attachment data records that have been passed to this context.
        :return: list of long record Ids
        """
        return sorted(self.attachmentDict.keys())

    def get_attachment_file(self, record_id: int):
        """
        Get the attachment file by record ID of attachment data record. This record ID must have been passed from Sapio
        :param record_id: The record ID to search for.
        :return: The file if exists. If not found, then return None.
        """
        if record_id in self.attachmentDict:
            return self.attachmentDict[record_id]
        return None

    def get_additional_payload(self):
        """
        Get additional payload sent from Sapio application.

        This can be any python object type. But it must be a python base class.

        :return: The payload object from Sapio
        """
        return self.payload

    def get_additional_input_file(self, input_file_key: str):
        """
        Get the file absolute path based on the input file key specified in Java side of Sapio Plugins.
        This is useful for libraries that requires input as files.
        :param input_file_key: The key entered in Sapio Plugins when constructing this context.
        :return: The absolute path where the script can access the file.
         Can be fed into open() or other libaries that requires a file name.
        """
        return self.inputFileDict[input_file_key]

    def get_temp_dir(self):
        """
        It is possible that some python tools will be dumping files as results or during processing.
        This is where it should be dumped.
        """
        return self.tempDirectory

    def get_output_file(self):
        return self.outFile
