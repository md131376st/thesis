from celery import group
from django.core.exceptions import ObjectDoesNotExist
from mongoengine import QuerySet

from rest_framework import status

from indexing.models import MethodRecord
from indexing.storageManger.BasicSotrageManger import BasicStorageManger
from indexing.tasks import generate_embedding
from indexing.types import StoreLevelTypes


class ClassStorageManger(BasicStorageManger):
    def __init__(self, collection_name, codebase_name):
        super().__init__(collection_name, codebase_name)
        self.query_set = MethodRecord.objects()

    def store(self, refresh: bool):
        self.query_set = self.fetch_data_if_exists(self.query_set)
        if not self.query_set:
            return {
                "error": "The combination of (collectionName, codebaseName) does not exist."
            }

        if not refresh:
            self.query_set = self.check_embedding_exists(self.query_set)
        if self.query_set:
            job = group([generate_embedding.s(record=record.to_dict(), level=StoreLevelTypes.CLASS.value) for record in
                         self.query_set])
            return {
                "taskId": job.apply_async().id
            }
        else:
            return {
                "message": "All the requested data is successfully stored in the Chroma DB."
            }
