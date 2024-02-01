from django.db import models


# Create your models here.
class Document(models.Model):
    # name = models.FilePathField(max_length=256)
    content = models.FileField(upload_to='files')

    def __str__(self):
        return self.content
