from abc import ABC

from mongoengine import QuerySet


class BasicStorageManger(ABC):
    def __init__(self):
        pass

    def to_dict(self):
        pass

    def store(self, queryset: QuerySet):
        pass
