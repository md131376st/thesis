from mongoengine import QuerySet

from indexing.models import MethodRecord
from indexing.storageManger.BasicSotrageManger import BasicStorageManger


class ClassStorageManger(BasicStorageManger):
    def __init__(self, collection_name, codebase_name):
        super().__init__()
        # this combination is unique
        self.qualified_class_name = collection_name
        self.codebase_name = codebase_name

    def fetch_data_if_exists(self):
        methodRecords = MethodRecord.objects(
            qualified_class_name=self.qualified_class_name,
            codebase_name=self.codebase_name
        )
        return methodRecords

    def check_embedding_exists(self, methodRecords: QuerySet):
        methodRecords = methodRecords.filter(chromadb_collection_name__exists=False)
        return methodRecords


    def store(self, methodRecords:QuerySet):
        pass
