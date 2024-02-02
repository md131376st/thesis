import logging
from enum import Enum

import mammoth
from simplePipline.utils.logger import Logger


class DataTransfer:
    def __init__(self, loglevel=logging.INFO):
        self.logger = Logger("Data Conversion",
                             None,
                             console=True,
                             level=loglevel).get_logger()

    def transfer(self, **kwargs):
        pass


class TransferType(Enum):
    FIle = 0
    BYTEIO = 1


class HTMLDataTransfer(DataTransfer):
    def __init__(self, loglevel=logging.INFO, transfer_type=TransferType.BYTEIO):
        super().__init__(loglevel)
        self.type = transfer_type

    def transfer(self, info):
        if self.type == TransferType.BYTEIO:
            return self.convert_docx_bytes_io_to_html(info)
        elif self.type == TransferType.FIle:
            return self.convert_docx_to_html(info)
        pass

    def convert_docx_to_html(self, docx_file_path):
        with open(docx_file_path, "rb") as docx_file:
            return self.convert_docx_bytes_io_to_html(docx_file)

        pass

    def convert_docx_bytes_io_to_html(self, fd):
        result = mammoth.convert_to_html(fd)
        html = result.value
        messages = result.messages
        if messages:
            self.logger.warning(messages)
        return html
