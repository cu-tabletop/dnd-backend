from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    _id = models.BigIntegerField()
    pfp = models.ImageField()
    bio = models.TextField(blank=True, null=True)
    admin = models.BooleanField(default=False)
    # You can add any additional fields here
