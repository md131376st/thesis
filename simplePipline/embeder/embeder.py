import logging
from enum import Enum

from celery import group
from llama_index import ServiceContext

from simplePipline.baseclass import Baseclass
from openai import OpenAI
from llama_index.embeddings import OpenAIEmbedding
import tiktoken
from simplePipline.tasks import call_embedding
from simplePipline.utils.utilities import log_debug


class Embeder(Baseclass):
    def __init__(self, context, loglevel=logging.INFO):
        super().__init__("Generate Text Embeddings", loglevel=loglevel)
        self.context = context
        self.embeddings = []

    def embedding(self, **kwargs):
        pass

    def get_embedding(self):
        return self.embeddings


class EmbederType(Enum):
    OpenAI_3_s = "text-embedding-3-small"
    OpenAI_3_l = "text-embedding-3-large"
    OpenAI_2 = "text-embedding-ada-002"
    DEFULT = "text-embedding-3-large"


class OpenAIEmbeder(Embeder):
    def __init__(self, context, loglevel=logging.INFO):
        super().__init__(context=context, loglevel=loglevel)
        self.logger.debug("init open ai")
        self.client = OpenAI()
        self.logger.debug("finish init open ai")
        self.reorderText = []

    def embedding(self, texts, model=EmbederType.OpenAI_3_s.value, is_async=False):
        if is_async:
            self.apply_embeddings(texts, model)
        else:
            if isinstance(texts, list):
                for text in texts:
                    self.apply_embeddings(text, model)
            else:
                self.apply_embeddings(texts, model)

    def apply_embeddings(self, text, model):
        openaiembeding = self.client.embeddings.create(input=text,
                                                       model=model).data
        embedding = [embed.embedding for embed in openaiembeding]
        self.embeddings += embedding


class LamaIndexEmbeder(Embeder):
    def __init__(self, context, loglevel=logging.INFO,
                 local=None, model=EmbederType.OpenAI_3_s.value,
                 **kwargs):
        super().__init__(context=context, loglevel=loglevel)
        self.embed_model = OpenAIEmbedding(model=model)
        if local:
            self.service_context = ServiceContext.from_defaults(embed_model=local)
        else:
            self.service_context = ServiceContext.from_defaults(embed_model=self.embed_model)

    def embedding(self, text, **kwargs):
        for chunk in self.context:
            text = chunk.text.replace("\n", " ").replace("$")
            self.embeddings.append(self.embed_model.get_text_embedding(text))

    def get_service_context(self):
        return self.service_context

    def get_embeddings(self):
        return self.embed_model
