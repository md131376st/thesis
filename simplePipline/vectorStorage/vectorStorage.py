import logging
import chromadb
from llama_index import StorageContext, VectorStoreIndex, DocumentSummaryIndex
from llama_index.vector_stores import ChromaVectorStore

from simplePipline.baseclass import Baseclass


class VectorStorage(Baseclass):
    def __init__(self, loglevel=logging.INFO):
        super().__init__("Storing and retriving", loglevel=loglevel)

    def store(self, **kwargs):
        pass

    def retrieve(self, question):
        pass


class ChromadbVectorStorage(VectorStorage):
    def __init__(self, path, collection_name, loglevel=logging.INFO):
        super().__init__(loglevel=loglevel)
        self.path = path
        self.db = chromadb.PersistentClient(path=self.path)
        collection = self.db.get_or_create_collection(collection_name)
        self.vector_store = ChromaVectorStore(chroma_collection=collection)
        self.index = None
        self.queryEngine = None

    def store(self, nodes, service_context):
        storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        self.logger.debug("create vector storage ")
        self.index = VectorStoreIndex(
            nodes=nodes, storage_context=storage_context, service_context=service_context
        )

    def load(self, service_context):
        self.logger.debug("Load Vector storage ")
        self.index = VectorStoreIndex.from_vector_store(
            self.vector_store,
            service_context=service_context,
        )

    def retrieve(self, question, **kwargs):
        self.queryEngine = self.index.as_query_engine()
        return self.queryEngine.query(question)

    def get_query_engine(self):
        return self.index.as_query_engine()


''' need too work on it in case needed  '''
# class ChromadbSummaryVectorStorage(VectorStorage):
#     def __init__(self, path, collection_name, loglevel=logging.INFO):
#         super().__init__(loglevel=loglevel)
#         self.path = path
#         self.db = chromadb.PersistentClient(path=self.path)
#         collection = self.db.get_or_create_collection(collection_name)
#         self.vector_store = ChromaVectorStore(chroma_collection=collection)
#         self.index = None
#         self.queryEngine = None
#
#     def store(self, nodes, service_context):
#         storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
#         self.logger.debug("create vector storage ")
#         self.index = DocumentSummaryIndex(
#             nodes=nodes, storage_context=storage_context, service_context=service_context
#         )
#
#     def load(self, service_context):
#         self.logger.debug("Load Vector storage ")
#         self.index = DocumentSummaryIndex.from_vector_store(
#             self.vector_store,
#             service_context=service_context,
#         )
#
#     def retrieve(self, question, **kwargs):
#         self.queryEngine = self.index.as_query_engine()
#         return self.queryEngine.query(question)
#
#     def get_query_engine(self):
#         return self.index.as_query_engine()
