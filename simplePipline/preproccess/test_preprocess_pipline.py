import json
import logging

from simplePipline.preproccess.dataTransfer import DOCXtoHTMLDataTransfer, TransferType, DOCXtoHTMLDataTransfer
from simplePipline.preproccess.dataprocess.htmlDataPreprocess import HTMLDataPreprocess
from simplePipline.preproccess.featureExtraction.htmlFeatureExtraction import HTMLFeatureExtraction
from simplePipline.preproccess.imgTextConvertor import ImgTextConvertor
from simplePipline.utils.utilities import write_html_file, img_to_html_template, save_NodeMetadata_to_json

if __name__ == '__main__':
    transfer = DOCXtoHTMLDataTransfer(loglevel=logging.DEBUG, transfer_type=TransferType.FIle)
    html_content = transfer.transfer("../data/(Isybank)AFU - ISY_Archivio_v2.docx")
    preprocess = HTMLDataPreprocess(loglevel=logging.DEBUG, html_content=html_content)
    preprocess.preprocess()
    # preprocess.write_content("out.html")
    process_html = preprocess.get_content()
    feature_extractor = HTMLFeatureExtraction(process_html, loglevel=logging.DEBUG)
    feature_extractor.extract_node_data()
    data = feature_extractor.get_instance()
    image_description_html = ""
    for node in data:
        if len(node.image) != 0:
            imgTxtCon = ImgTextConvertor(node.all_text, node.image, loglevel=logging.DEBUG)
            description = imgTxtCon.convert()
            node.img_placeholder_to_description(description)
            image_description_html += node.img_info_to_html(description)

            break
    write_html_file("decription",
                    img_to_html_template(image_description_html)
                    )
    save_NodeMetadata_to_json('hi', data)

    pass
