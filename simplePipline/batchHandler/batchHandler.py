import logging

import tiktoken

from simplePipline.baseclass import Baseclass
from simplePipline.utils.utilities import log_debug


class OpenAIRestrictions:
    def __init__(self):
        # self.maxToken = 8192
        self.maxToken = 583
        self.maxArray = 2048


class BatchHandler(Baseclass):
    def __init__(self, loglevel=logging.INFO):
        super().__init__("Batch Handler", loglevel=loglevel)
        self.batch = []

    def createBatchHandler(self, info):
        pass


class EmbeddingBatchHandler(BatchHandler):
    def createBatchHandler(self, info, active_meta_data=True):
        chunks = info["chunks"]
        model = info["model"]
        metaData = info["metadata"]
        tokenCount = 0
        batch_chunks = []
        batch_meta_data = []
        for index, chunk in enumerate(chunks):
            text_count = self.token_count(chunk["text"])
            if (tokenCount + text_count < OpenAIRestrictions().maxToken
                    and len(self.batch) < OpenAIRestrictions().maxArray):
                batch_chunks.append(chunk)
                if active_meta_data and len(metaData) > index:
                    batch_meta_data.append(metaData[index])

                tokenCount += text_count
            else:
                self.batch.append({
                    'chunks': batch_chunks,
                    'metadata': batch_meta_data
                })
                batch_chunks.clear()
                batch_meta_data.clear()
                tokenCount = 0
        # last batch
        self.batch.append({
            'chunks': batch_chunks,
            'metadata': batch_meta_data
        })
        log_debug(len(self.batch))
    def get_batch(self):
        return self.batch

    def token_count(self, text):
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
