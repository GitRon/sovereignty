import random

from django.db import models
from numpy.random import normal

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

    def upgrade_province(self, *, province, savegame):
        home_county = savegame.playing_as.home_county
        # Validate that county has the money for upgrading...
        if province.level_upgrade_price < home_county.gold:
            # Handle upgrade
            province.level = province.level + 1
            province.gold = round(province.gold + abs(normal(loc=self.model.LEVEL_GOLD_AVG, scale=3)))
            province.manpower = round(province.manpower + abs(normal(loc=self.model.LEVEL_MANPOWER_AVG, scale=20)))
            province.save()

            # Pay for upgrade
            home_county.gold -= province.level_upgrade_price
            home_county.save()

            return True
        return False
