import enum

from django.contrib.auth.models import AbstractUser
from django.db import models

class Role(enum.Enum):
    PLAYER = 0
    MASTER = 1

    @classmethod
    def is_valid(cls, n: int):
        return n in [member.value for member in cls]

class User(AbstractUser):
    # Add any additional fields here
    _id = models.BigIntegerField()
    pfp = models.ImageField()
    bio = models.TextField(blank=True, null=True)
    admin = models.BooleanField(default=False)

class Room(models.Model):
    _id = models.AutoField(unique=True)
    title = models.CharField(max_length=256)

class Participation(models.Model):
    user = models.ForeignKey(User, models.CASCADE)
    room = models.ForeignKey(Room, models.CASCADE)
    status = models.SmallIntegerField(default=0)  # Role

class Character(models.Model):
    _id = models.AutoField(unique=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL) # TODO: add find orphans endpoint
    # TODO: fill in needed information
