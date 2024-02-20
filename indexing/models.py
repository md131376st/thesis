from django.db import models
from django.utils.translation import gettext_lazy as _


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
