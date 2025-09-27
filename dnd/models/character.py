from django.core.files.base import ContentFile
from django.db import models
import json

from . import *


class Character(models.Model):
    _id = models.AutoField(unique=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    data = models.FileField(upload_to="chardata")

    def _load_data(self):
        """ Internal function that loads data from file stored in database. """
        with self.data.open('r') as f:
            return json.load(f)

    def _save_data(self, data):
        """ Internal function that saves data to a file stored in database. """
        self.data.save(self.data.name, ContentFile(json.dumps(data)), save=False)

    def get(self, *args):
        """
        Gets specific parameter from character data.
        Usage: Put path to the param into args
        """
        cur = self._load_data()
        for arg in args:
            try:
                cur = cur[arg]
            except (KeyError, IndexError, TypeError):
                return None
        return cur

    def set(self, *args, **kwargs) -> bool:
        """
        Sets specific parameter(-s) in character data to a value
        Usage: Put path to the param into args and what should we change to kwargs
        Returns True if set successfully and False if path not found
        """
        data = self._load_data()
        cur = data
        for arg in args:
            try:
                cur = cur[arg]
            except (KeyError, IndexError, TypeError):
                return False
        for n, v in kwargs:
            cur[n] = v
        self._save_data(data)
        return True
