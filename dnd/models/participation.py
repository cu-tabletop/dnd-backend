from django.db import models

from . import *


class Participation(models.Model):
    user = models.ForeignKey(User, models.CASCADE)
    room = models.ForeignKey(Room, models.CASCADE)
    status = models.SmallIntegerField(default=0)  # Role
