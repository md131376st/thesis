import logging

from simplePipline.preproccess.baseclass import Baseclass


class FeatureExtraction(Baseclass):
    def __init__(self, content, loglevel=logging.INFO):
        super().__init__("Feature Extractions", loglevel)
        self.content = content
        self.instances = []
        pass

    def extract_node_data(self):
        pass

    def get_instance(self):
        return self.instances


