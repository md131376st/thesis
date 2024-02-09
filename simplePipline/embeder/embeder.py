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
        self.embeddings = []

    def embedding(self, **kwargs):
        pass

    def get_embedding(self):
        return self.embeddings


class EmbederType(Enum):
    OpenAI_3_s = "text-embedding-3-small"
    OpenAI_3_l = "text-embedding-3-large"
    OpenAI_2 = "text-embedding-ada-002"
    DEFULT = "text-embedding-ada-002"


class OpenAIEmbeder(Embeder):
    def __init__(self, context, loglevel=logging.INFO):
        super().__init__(context=context, loglevel=loglevel)
        self.logger.debug("init open ai")
        self.client = OpenAI()
        self.logger.debug("finish init open ai")

    def embedding(self, model=EmbederType.OpenAI_3_s.value, **kwargs):
        for chunk in self.context:
            text = chunk["text"].replace("\n", " ").replace("$", " ")
            self.logger.debug(text)
            self.logger.debug("open ai result")
            self.embeddings.append(self.client.embeddings.create(input=[text],
                                                                 model=model).data[0].embedding)

        pass


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

    def embedding(self, **kwargs):
        for chunk in self.context:
            text = chunk.text.replace("\n", " ").replace("$")
            self.embeddings.append(self.embed_model.get_text_embedding(text))

    def get_service_context(self):
        return self.service_context

    def get_embeddings(self):
        return self.embed_model
