from django.db import models


class Room(models.Model):
    _id = models.AutoField(unique=True)
    title = models.CharField(max_length=256)
