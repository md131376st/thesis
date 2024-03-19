from celery import group
from mongoengine import QuerySet

from indexing.models import PackageRecord
from indexing.storageManger.BasicSotrageManger import BasicStorageManger
from indexing.storageManger.PackageStorageManger import PackageStorageManger
from indexing.tasks import generate_embedding
from indexing.types import StoreLevelTypes


class CodeBaseStorageManger(BasicStorageManger):
    def __init__(self, codebase_name):
        super().__init__(codebase_name, codebase_name)
        self.query_set = PackageRecord.objects()

    def fetch_data_if_exists(self, query_set: QuerySet):
        query_set = query_set.filter(
            codebase_name=self.codebase_name
        )
        return query_set

    def store(self, refresh: bool):
        self.query_set = self.fetch_data_if_exists(self.query_set)
        if not self.query_set:
            return {
                "error": f"The {self.codebase_name} does not exist."
            }
        if not refresh:
            self.query_set = self.check_embedding_exists(self.query_set)
        if self.query_set:
            data = dict()
            job = group(
                generate_embedding.s(
                    record=record.to_dict(),
                    level=StoreLevelTypes.CODEBASE.value
                ) for record in self.query_set
            )
            data["package_taskId"] = job.apply_async().id
            classes = []
            for package in self.query_set:
                packageStorageManger = PackageStorageManger(package.package_name, package.codebase_name)
                classes.append(packageStorageManger.store(refresh=refresh))
            data["classes"] = classes
            return data
        else:
            return {
                "message": "All the requested data is successfully stored in the Chroma DB."
            }
