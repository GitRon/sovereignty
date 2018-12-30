from random import randint

from django.db import models


class MapDotQuerySet(models.QuerySet):
    def get_random(self):
        count = self.count()
        if count > 0:
            return self[randint(0, count - 1)]
        return self


class MapDotManager(models.Manager):
    def get_queryset(self):
        return MapDotQuerySet(self.model, using=self._db)  # Important!
