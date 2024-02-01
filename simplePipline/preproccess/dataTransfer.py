import logging

import mammoth
from simplePipline.utils.logger import Logger


class DataTransfer:
    def __init__(self, loglevel=logging.INFO):
        self.logger = Logger("TestLamaIndexPipeline",
                             f'quality_log_{self.version}.txt', console=True,
                             level=loglevel).get_logger()

    def transfer(self,**kwargs):
        pass



class HTMLDataTransfer(DataTransfer):
    def __init__(self, type):
        super().__init__()
        self.type =type

    def transfer(self):

    def convert_docx_to_html(self, docx_file_path):
        with open(docx_file_path, "rb") as docx_file:
            return self.conver_docx_bytes_io_to_html(docx_file)

        pass

    def conver_docx_bytes_io_to_html(self, fd):
        result = mammoth.convert_to_html(fd)
        html = result.value
        messages = result.messages

        return html
