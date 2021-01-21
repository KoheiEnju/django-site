from django.db import models

# Create your models here.
class Video(models.Model):
    upload = models.FileField(upload_to="upload/")

    def __str__(self):
        return self.upload.name