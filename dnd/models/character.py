from django.db import models

from . import *


class Character(models.Model):
    _id = models.AutoField(unique=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL)  # TODO: add find orphans endpoint

    # Header info
    name = models.CharField(max_length=255)
    proficiency = models.IntegerField()
    avatar_url = models.URLField(max_length=1023)

    # Info
    _class = models.CharField(max_length=255)
    subclass = models.CharField(max_length=255)
    level = models.IntegerField()
    background = models.CharField(max_length=255)
    race = models.CharField(max_length=255)
    alignment = models.CharField(max_length=255)
    experience = models.IntegerField()
    size = models.CharField(max_length=255)

    # Subinfo
    age = models.CharField(max_length=127)
    height = models.CharField(max_length=127)
    weight = models.CharField(max_length=127)
    eyes = models.CharField(max_length=127)
    skin = models.CharField(max_length=127)
    hair = models.CharField(max_length=127)

    # Stats
    strength = models.IntegerField()
    dexterity = models.IntegerField()
    constitution = models.IntegerField()
    intelligence = models.IntegerField()
    wisdom = models.IntegerField()
    charisma = models.IntegerField()

    strength_mod = models.IntegerField()
    dexterity_mod = models.IntegerField()
    constitution_mod = models.IntegerField()
    intelligence_mod = models.IntegerField()
    wisdom_mod = models.IntegerField()
    charisma_mod = models.IntegerField()

    strength_save = models.IntegerField()
    dexterity_save = models.IntegerField()
    constitution_save = models.IntegerField()
    intelligence_save = models.IntegerField()
    wisdom_save = models.IntegerField()
    charisma_save = models.IntegerField()

    # Skills
    acrobatics_proficient = models.BooleanField()
    acrobatics_base_stat = models.CharField(max_length=4)
    investigation_proficient = models.BooleanField()
    investigation_base_stat = models.CharField(max_length=4)
    athletics_proficient = models.BooleanField()
    athletics_base_stat = models.CharField(max_length=4)
    perception_proficient = models.BooleanField()
    perception_base_stat = models.CharField(max_length=4)
    survival_proficient = models.BooleanField()
    survival_base_stat = models.CharField(max_length=4)
    performance_proficient = models.BooleanField()
    performance_base_stat = models.CharField(max_length=4)
    intimidation_proficient = models.BooleanField()
    intimidation_base_stat = models.CharField(max_length=4)
    history_proficient = models.BooleanField()
    history_base_stat = models.CharField(max_length=4)
    sleight_of_hand_proficient = models.BooleanField()
    sleight_of_hand_base_stat = models.CharField(max_length=4)
    arcana_proficient = models.BooleanField()
    arcana_base_stat = models.CharField(max_length=4)
    medicine_proficient = models.BooleanField()
    medicine_base_stat = models.CharField(max_length=4)
    deception_proficient = models.BooleanField()
    deception_base_stat = models.CharField(max_length=4)
    nature_proficient = models.BooleanField()
    nature_base_stat = models.CharField(max_length=4)
    insight_proficient = models.BooleanField()
    insight_base_stat = models.CharField(max_length=4)
    religion_proficient = models.BooleanField()
    religion_base_stat = models.CharField(max_length=4)
    stealth_proficient = models.BooleanField()
    stealth_base_stat = models.CharField(max_length=4)
    persuasion_proficient = models.BooleanField()
    persuasion_base_stat = models.CharField(max_length=4)
    animal_handling_proficient = models.BooleanField()
    animal_handling_base_stat = models.CharField(max_length=4)

    # Big fields for data
    # data = models.FileField(upload_to="chardata")
    # TODO: this
