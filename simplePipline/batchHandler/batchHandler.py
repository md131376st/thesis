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
        metaData = info["metadata"]
        # log_debug(f"embbederlen(metadata): {len(metaData)} ")
        tokenCount = 0
        batch_chunks = []
        batch_meta_data = []
        for index, chunk in enumerate(chunks):
            text_count = self.token_count(chunk["text"])
            if (tokenCount + text_count < OpenAIRestrictions().maxToken
                    and len(self.batch) < OpenAIRestrictions().maxArray):
                # log_debug(f"chunk added : {chunk}" )
                batch_chunks.append(chunk)
                if active_meta_data and len(metaData) > index:
                    batch_meta_data.append(metaData[index])

                tokenCount += text_count
            else:
                if len(batch_chunks) == 0:
                    # log_debug(f"chunk added : {chunk}")
                    batch_chunks.append(chunk)
                    if active_meta_data and len(metaData) > index:
                        # log_debug(f"index {index}")
                        # log_debug(f"metadata {metaData[index]}")
                        batch_meta_data.append(metaData[index])
                # log_debug(f"batch_chunks : {batch_chunks}")
                # log_debug(f"batch_meta_data : {batch_meta_data}")
                self.batch.append({
                    'chunks': batch_chunks,
                    'metadata': batch_meta_data
                })
                # log_debug(f" after add : {self.batch} ")
                batch_chunks = []
                batch_meta_data = []
                tokenCount = 0
                # log_debug(f" after clear : {self.batch} ")
        # last batch
        self.batch.append({
            'chunks': batch_chunks,
            'metadata': batch_meta_data
        })
        # log_debug(f"end of batch: {self.batch} ")
    def get_batch(self):
        return self.batch

    def token_count(self, text):
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
