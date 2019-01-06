import random

from django.db import models

from apps.account.managers import SavegameBasedObjectManager


class TraitQuerySet(models.QuerySet):
    def get_random(self, to_be_compatible_with_traits):
        count = self.count()
        if count > 0:
            return self.exclude(incompatible_traits__in=to_be_compatible_with_traits)[random.randint(0, count - 1)]
        return self


class TraitManager(models.Manager):
    def get_queryset(self):
        return TraitQuerySet(self.model, using=self._db)  # Important!


class DynastyManager(SavegameBasedObjectManager):
    pass


class PersonManager(SavegameBasedObjectManager):
    pass
