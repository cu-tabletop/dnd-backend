from django.db import models
from django.conf import settings

from .room import Room
from .player import Player


class Participation(models.Model):
    user = models.ForeignKey(
        Player,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    room = models.ForeignKey(Room, models.CASCADE)
    status = models.SmallIntegerField(default=0)  # Role
