import logging
import random
import string

import uuid

from fileService import settings
from filemanger.utility import get_package_name, get_class_collection_name
from simplePipline.embeder.embeder import OpenAIEmbeder
from simplePipline.preproccess.dataTransfer import DOCXtoHTMLDataTransfer, TransferType
from simplePipline.preproccess.dataprocess.htmlDataPreprocess import HTMLDataPreprocess
from simplePipline.utils.utilities import log_debug, Get_html_filename
from simplePipline.vectorStorage.vectorStorage import ChromadbIndexVectorStorage
import chromadb


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
    def store_embedding(collection_name, chunks, metadata, embedding_type, collection_metadata, is_async=False):
        # log_debug(f"store_embedding len metadata:{len(metadata)} len chunks:{len(chunks)} ")
        if len(metadata) < len(chunks):
            metadata = None
        ids = [chunk['id'] for chunk in chunks]
        texts = [chunk["text"] for chunk in chunks]
        embeder = OpenAIEmbeder(context=chunks)
        embeder.embedding(texts, model=embedding_type, is_async=is_async)
        chunk_embeddings = embeder.get_embedding()
        log_debug(
            f"len of chunk_embeddings: {len(chunk_embeddings)}, len of texts: {len(texts)} , len of chunks: {len(ids)}")

        vectorStore = ChromadbIndexVectorStorage(settings.CHROMA_DB)
        vectorStore.store(texts, chunk_embeddings,
                          metadata, collection_name, collection_metadata, ids)
        log_debug(f"end embedding chunks for collection: {collection_name}")
        return ids

    @staticmethod
    def feature_extraction(input_file, output_file, store, include_images):
        pass

    @staticmethod
    def query_handler(question, classname, embedding_type, n_results):
        # get question embedding
        embeder = OpenAIEmbeder(question)
        embeder.embedding(question, model=embedding_type, is_async=False)
        embedding = embeder.get_embedding()
        # retrive form db
        db = chromadb.PersistentClient(settings.CHROMA_DB)
        # start quering form root
        if classname is None:
            result = []
            collection = db.get_collection(name=settings.INDEXROOT)
            results = collection.query(query_embeddings=embedding,
                                       n_results=n_results)
            for text, metadata in zip(
                    results["documents"][0],
                    results["metadatas"][0]):
                if "package_name" in metadata:
                    package_collection_name = get_package_name(metadata["package_name"])
                    package_collection = db.get_collection(name=package_collection_name)
                    packageResult = package_collection.query(query_embeddings=embedding,
                                                             n_results=n_results)
                    packageinfo = []
                    for package_text, package_meta_data in zip(
                            packageResult["documents"][0],
                            packageResult["metadatas"][0]):
                        data = {
                            "package": package_text,
                            "metadata": package_meta_data
                        }

                        if "qualified_class_name" in package_meta_data:

                            classinfo = []
                            class_collection_name = get_class_collection_name(package_meta_data["qualified_class_name"])
                            class_collection = db.get_collection(name=class_collection_name)
                            classResult = class_collection.query(query_embeddings=embedding,
                                                                 n_results=n_results)
                            for classinfo_text, classinfo_text_meta_data in zip(
                                    classResult["documents"][0],
                                    classResult["metadatas"][0]):
                                classinfo.append(
                                    {
                                        "text": classinfo_text,
                                        "metadata": classinfo_text_meta_data
                                    }
                                )
                            data["class"] = classinfo
                        packageinfo.append(data)
                    result.append(packageinfo)

            return result

        # just returning the level base
        else:
            collection = db.get_collection(name=classname)
            results = collection.query(query_embeddings=embedding,
                                       n_results=n_results)
            result = []
            log_debug(results)
            for text, metadata in zip(
                    results["documents"][0],
                    results["metadatas"][0]):
                result.append(
                    {
                        "text": text,
                        "metadata": metadata
                    }
                )
            return result
