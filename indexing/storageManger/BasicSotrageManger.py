from abc import ABC

from mongoengine import QuerySet


class BasicStorageManger(ABC):
    def __init__(self, collection_name, codebase_name):
        self.qualified_class_name = collection_name
        self.codebase_name = codebase_name

        pass

    def fetch_data_if_exists(self, query_set: QuerySet):
        query_set = query_set.filter(
            qualified_class_name=self.qualified_class_name,
            codebase_name=self.codebase_name
        )
        return query_set

    def check_embedding_exists(self, query_set: QuerySet):
        query_set.filter(chromadb_collection_name__exists=False)
        return query_set

    def store(self, refresh: bool):
        pass
