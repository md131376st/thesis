from django.db import models
from django.utils.translation import gettext_lazy as _
from filemanger.custome_storage import OverwriteStorage


# Create your models here.
class Document(models.Model):
    class State(models.IntegerChoices):
        FileUpload = 1, _('fileupload')
        FilePreporcess = 2, _('filepreprocess')
        FeatureExtraction = 3, _('featureextraction'),
        ImageTextGenerate = 4, _('ImageTextGenerate')
        ImagrDescriptionReview = 5, _('ImagerDescriptionReview')
        indexed = 6, _('indexed')

    state = models.IntegerField(
        choices=State.choices,
        default=State.FileUpload,
    )
    file_name = models.CharField(max_length=255, unique=True)
    content_hash = models.CharField(max_length=64, blank=True, null=True)
    content = models.FileField(upload_to='files', storage=OverwriteStorage())

    def __str__(self):
        return self.content
