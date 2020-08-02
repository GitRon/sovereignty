import random

from django.db import models

from apps.account.managers import SavegameBasedObjectManager


class TraitQuerySet(models.QuerySet):
    def get_random(self, to_be_compatible_with_traits):
        count = self.count() - len(to_be_compatible_with_traits)
        if count > 0:
            return self.exclude(incompatible_traits__in=to_be_compatible_with_traits)[random.randint(0, count - 1)]
        return self


class TraitManager(models.Manager):
    def get_queryset(self):
        return TraitQuerySet(self.model, using=self._db)  # Important!


class DynastyManager(SavegameBasedObjectManager):
    pass


class PersonQuerySet(models.QuerySet):
    def get_alive(self, savegame):
        # todo write test!
        return self.filter(death_year__gte=savegame.current_year)


class PersonManager(SavegameBasedObjectManager):
    def get_queryset(self):
        return PersonQuerySet(self.model, using=self._db)
