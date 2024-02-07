import logging
import random
import string

from fileService import settings
from simplePipline.embeder.embeder import OpenAIEmbeder
from simplePipline.preproccess.dataTransfer import DOCXtoHTMLDataTransfer, TransferType
from simplePipline.preproccess.dataprocess.htmlDataPreprocess import HTMLDataPreprocess
from simplePipline.utils.utilities import log_debug
from simplePipline.vectorStorage.vectorStorage import ChromadbIndexVectorStorage


class TaskHandler:
    @staticmethod
    def generate_random_string(length=8):
        """Generate a random string of fixed length."""
        letters_and_digits = string.ascii_letters + string.digits
        return ''.join(random.choice(letters_and_digits) for i in range(length))

    @staticmethod
    def ensure_id(chunks):
        return [chunk['id'] if 'id' in chunk else TaskHandler.generate_random_string() for chunk in chunks]

    @staticmethod
    def proccess_data(filename, is_async=True):
        log_debug(f"start transfer: {filename}")
        transfer = DOCXtoHTMLDataTransfer(loglevel=logging.INFO, transfer_type=TransferType.FIle)
        html_content = transfer.transfer(f"{settings.MEDIA_ROOT}/{filename}")
        log_debug(f"start preprocessing: {str(filename).split(',')[0]}")
        preprocess = HTMLDataPreprocess(loglevel=logging.INFO, html_content=html_content)
        preprocess.preprocess()

        preprocess.write_content(f"{settings.PROCESSFIELS}/{str(filename.name).split('.')[0]}.html")
        if not is_async:
            return preprocess.get_content()
        else:
            return None

    @staticmethod
    def store_embedding(collection_name, chunks, metadata, embedding_type, ids=None):
        if ids is None:
            ids = TaskHandler.ensure_id(chunks)
        if len(metadata) < len(chunks):
            metadata = None
        texts = [chunk["text"] for chunk in chunks]
        embeder = OpenAIEmbeder(context=chunks)
        embeder.embedding(model=embedding_type)
        chunk_embeddings = embeder.get_embedding()

        vectorStore = ChromadbIndexVectorStorage(settings.CHROMA_DB)
        vectorStore.store(texts, chunk_embeddings,
                          metadata, collection_name, ids)
        return ids
