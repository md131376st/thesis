from celery import group
from mongoengine import QuerySet

from indexing.models import ClassRecord
from indexing.storageManger.BasicSotrageManger import BasicStorageManger
from indexing.storageManger.ClassStorageManger import ClassStorageManger
from indexing.tasks import generate_embedding
from indexing.types import StoreLevelTypes


class PackageStorageManger(BasicStorageManger):
    def __init__(self, collection_name, codebase_name):
        super().__init__(collection_name, codebase_name)
        self.query_set = ClassRecord.objects()

    def fetch_data_if_exists(self, query_set: QuerySet):
        query_set = query_set.filter(
            package_name=self.collection_name,
            codebase_name=self.codebase_name
        )
        return query_set

    def store(self, refresh: bool):
        self.query_set = self.fetch_data_if_exists(self.query_set)
        if not self.query_set:
            return {
                "error": f"The combination of ({self.collection_name}, {self.codebase_name}) does not exist."
            }
        if not refresh:
            self.query_set = self.check_embedding_exists(self.query_set)
        if self.query_set:
            data = dict()
            job = group(
                generate_embedding.s(
                    record=record.to_dict(),
                    level=StoreLevelTypes.PACKAGE.value
                ) for record in self.query_set
            )
            data["class_taskId"] = job.apply_async().id
            methods = []
            for class_ in self.query_set:
                classStorageManger = ClassStorageManger(class_.qualified_class_name, class_.codebase_name)
                methods.append(classStorageManger.store(refresh=refresh))
            data["methods"] = methods
            return data
        else:
            return {
                "message": "All the requested data is successfully stored in the Chroma DB."
            }
