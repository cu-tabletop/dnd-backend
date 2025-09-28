from django.db import models


class Campaign(models.Model):
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=1023, default="")
    icon = models.ImageField(upload_to="campaign_icons")
