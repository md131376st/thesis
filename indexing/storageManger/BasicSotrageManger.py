from abc import ABC

from mongoengine import QuerySet


class BasicStorageManger(ABC):
    def __init__(self, collection_name, codebase_name):
        self.collection_name = collection_name
        self.codebase_name = codebase_name

        pass

    def fetch_data_if_exists(self, query_set: QuerySet):
        pass

    def check_embedding_exists(self, query_set: QuerySet):
        query_set.filter(chromadb_collection_name__exists=False)
        return query_set

    def store(self, refresh: bool):
        pass
