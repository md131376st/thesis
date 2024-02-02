import logging

from simplePipline.preproccess.dataTransfer import HTMLDataTransfer, TransferType
from simplePipline.preproccess.htmlDataPreprocess import HTMLDataPreprocess

if __name__ == '__main__':
    transfer = HTMLDataTransfer(loglevel=logging.DEBUG, transfer_type=TransferType.FIle)
    html_content = transfer.transfer("../data/(Isybank)AFU - ISY_Archivio_v2.docx")
    Preprocess = HTMLDataPreprocess(loglevel=logging.DEBUG, html_content=html_content)
    Preprocess.preprocess()
    Preprocess.write_content("out.html")

    pass
