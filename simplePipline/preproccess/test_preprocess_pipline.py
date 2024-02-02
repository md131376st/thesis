import logging

from simplePipline.preproccess.dataTransfer import DOCXtoHTMLDataTransfer, TransferType, DOCXtoHTMLDataTransfer
from simplePipline.preproccess.dataprocess.htmlDataPreprocess import HTMLDataPreprocess
from simplePipline.preproccess.featureExtraction.featureExtraction import HTMLFeatureExtraction

if __name__ == '__main__':
    transfer = DOCXtoHTMLDataTransfer(loglevel=logging.DEBUG, transfer_type=TransferType.FIle)
    html_content = transfer.transfer("../data/(Isybank)AFU - ISY_Archivio_v2.docx")
    preprocess = HTMLDataPreprocess(loglevel=logging.DEBUG, html_content=html_content)
    preprocess.preprocess()
    preprocess.write_content("out.html")
    process_html = preprocess.get_content()
    feature_extractor = HTMLFeatureExtraction(process_html, loglevel=logging.DEBUG)
    feature_extractor.extract_node_data()
    data = feature_extractor.get_instance()

    pass
