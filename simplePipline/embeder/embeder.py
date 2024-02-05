import logging
from enum import Enum

from llama_index import ServiceContext

from simplePipline.baseclass import Baseclass
from openai import OpenAI
from llama_index.embeddings import OpenAIEmbedding


class Embeder(Baseclass):
    def __init__(self, context, loglevel=logging.INFO):
        super().__init__("Generate Text Embeddings", loglevel=loglevel)
        self.context = context

    def embedding(self, **kwargs):
        pass


OpenAIEmbeddingModel = [
    "text-embedding-3-small",
    "text-embedding-3-large"
]


class OpenAIEmbeder(Embeder):
    def __init__(self, context, loglevel=logging.INFO):
        super().__init__(context=context, loglevel=loglevel)
        self.client = OpenAI()
        self.embeddings = []

    def embedding(self, model=OpenAIEmbeddingModel[0], **kwargs):
        for chunk in self.context:
            text = chunk.text.replace("\n", " ").replace("$", " ")
            self.embeddings.append(self.client.embeddings.create(input=[text],
                                                                 model=model).data[0].embedding)
            break
        pass


class LamaIndexEmbeder(Embeder):
    def __init__(self, context, loglevel=logging.INFO, local=None, model=OpenAIEmbeddingModel[0]):
        super().__init__(context=context, loglevel=loglevel)
        self.embed_model = OpenAIEmbedding(model=model)
        if local:
            self.service_context = ServiceContext.from_defaults(embed_model=local)
        else:
            self.service_context = ServiceContext.from_defaults(embed_model=self.embed_model)
        self.embeddings = []

    def embedding(self, **kwargs):
        for chunk in self.context:
            text = chunk.text.replace("\n", " ").replace("$")
            self.embeddings.append(self.embed_model.get_text_embedding(text))

    def get_service_context(self):
        return self.service_context

    def get_embeddings(self):
        return self.embed_model
