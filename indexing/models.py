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
    name = fields.StringField()
    description = fields.StringField()
    qualified_class_name = fields.StringField()
    package_name = fields.StringField()
    metadata = fields.DictField()
    technical_questions = fields.ListField()
    functional_questions = fields.ListField()


class ClassRecord(models.Model):
    name = models.TextField()
    package_name = models.TextField()
    description = models.TextField()
    metadata = models.JSONField()
    technical_questions = models.JSONField()
    functional_questions = models.JSONField()


class PackageRecord(models.Model):
    name = models.TextField()
    description = models.TextField()
    metadata = models.JSONField()
    technical_questions = models.JSONField()
    functional_questions = models.JSONField()
