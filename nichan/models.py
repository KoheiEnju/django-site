from django.db import models
from django.utils import timezone

# Create your models here.
class Comment(models.Model):
    text = models.CharField(max_length=200)
    name = models.CharField(max_length=20)
    pub_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.text