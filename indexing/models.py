from django.db import models
from django.utils.translation import gettext_lazy as _
from mongoengine import Document, fields


class Record(models.Model):
    class Type(models.IntegerChoices):
        Package = 1, _('Package')
        Class = 2, _('class')
        Method = 3, _('Method')

    collection_name = models.CharField(max_length=255)
    type = models.IntegerField(
        choices=Type.choices,
        default=Type.Method,
    )
    chromaDb_id = models.UUIDField()
    name = models.CharField(max_length=255)
    pass


class MethodRecord(Document):
    method_name = fields.StringField()
    qualified_class_name = fields.StringField()
    package_name = fields.StringField()
    codebase_name = fields.StringField()
    chromadb_collection_name = fields.StringField()
    collection_metadata = fields.DictField()

    description = fields.StringField()
    metadata = fields.DictField()
    technical_questions = fields.ListField()
    functional_questions = fields.ListField()
    meta = {
        'indexes': [
            'codebase_name'
        ]
    }


class ClassRecord(Document):
    qualified_class_name = fields.StringField()
    package_name = fields.StringField()
    codebase_name = fields.StringField()
    chromadb_collection_name = fields.StringField()

    description = fields.StringField()
    metadata = fields.DictField()
    technical_questions = fields.ListField()
    functional_questions = fields.ListField()
    meta = {
        'indexes': [
            'codebase_name'
        ]
    }


class PackageRecord(Document):
    package_name = fields.StringField()
    codebase_name = fields.StringField()
    chromadb_collection_name = fields.StringField()

    description = fields.StringField()
    metadata = fields.DictField()
    technical_questions = fields.ListField()
    functional_questions = fields.ListField()
    meta = {
        'indexes': [
            'codebase_name'
        ]
    }
