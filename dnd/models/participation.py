from django.db import models

from .room import Room
from .player import Player
from .campaign import Campaign
from .character import Character


class RoomParticipation(models.Model):
    user = models.ForeignKey(Player, models.CASCADE)
    room = models.ForeignKey(Room, models.CASCADE)
    character = models.ForeignKey(Character, models.CASCADE)

class CampaignMembership(models.Model):
    user = models.ForeignKey(Player, models.CASCADE)
    campaign = models.ForeignKey(Campaign, models.CASCADE)
    status = models.PositiveSmallIntegerField(default=0)  # Role. 0 - player, 1 - master, 2 - owner
