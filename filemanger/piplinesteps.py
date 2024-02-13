import logging
import random
import string

import uuid
from fileService import settings
from simplePipline.embeder.embeder import OpenAIEmbeder
from simplePipline.preproccess.dataTransfer import DOCXtoHTMLDataTransfer, TransferType
from simplePipline.preproccess.dataprocess.htmlDataPreprocess import HTMLDataPreprocess
from simplePipline.utils.utilities import log_debug, Get_html_filename
from simplePipline.vectorStorage.vectorStorage import ChromadbIndexVectorStorage


class TaskHandler:
    @staticmethod
    def ensure_id(chunks):
        newchunk = []
        for index, chunk in enumerate(chunks):
            if "id" not in chunk:
                random_id = uuid.uuid4()
                newchunk.append(
                    {
                        "text": chunk["text"],
                        "id": str(random_id)
                    }
                )
            else:
                newchunk.append(chunk)
        return newchunk

    @staticmethod
    def proccess_data(filename, is_async=True):
        log_debug(f"start transfer: {filename}")
        transfer = DOCXtoHTMLDataTransfer(loglevel=logging.INFO, transfer_type=TransferType.FIle)
        html_content = transfer.transfer(f"{settings.MEDIA_ROOT}/{filename}")
        log_debug(f"start preprocessing: {str(filename).split(',')[0]}")
        preprocess = HTMLDataPreprocess(loglevel=logging.INFO, html_content=html_content)
        preprocess.preprocess()

        preprocess.write_content(Get_html_filename(filename))
        if not is_async:
            return preprocess.get_content()
        else:
            return None

    @staticmethod
    def store_embedding(collection_name, chunks, metadata, embedding_type, ids, **kwargs):
        log_debug(f"store_embedding len metadata:{len(metadata)} len chunks:{len(chunks)} ")
        if len(metadata) < len(chunks):
            metadata = None
        log_debug(f"print ids {ids}")
        ids = [chunk['id'] for chunk in chunks]
        log_debug(f"print actual {ids}")
        texts = [chunk["text"] for chunk in chunks]
        embeder = OpenAIEmbeder(context=chunks)
        embeder.embedding(texts, model=embedding_type, **kwargs)
        chunk_embeddings = embeder.get_embedding()

        vectorStore = ChromadbIndexVectorStorage(settings.CHROMA_DB)
        vectorStore.store(texts, chunk_embeddings,
                          metadata, collection_name, ids)
        return ids

    @staticmethod
    def feature_extraction(input_file, output_file, store, include_images):
        pass
