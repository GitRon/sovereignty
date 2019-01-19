import random

from django.db import models

from apps.account.managers import SavegameBasedObjectManager
from apps.core.managers import RandomManager


class CountyQuerySet(models.QuerySet):
    def get_random(self):
        count = self.count()
        if count > 0:
            return self[random.randint(0, count - 1)]
        return self


class CountyManager(SavegameBasedObjectManager):
    def get_queryset(self):
        return CountyQuerySet(self.model, using=self._db)  # Important!


class MapDotManager(SavegameBasedObjectManager, RandomManager):
    pass
