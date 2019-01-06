import random

from django.db import models


class RandomQuerySet(models.QuerySet):
    def get_random(self):
        count = self.count()
        if count > 0:
            return self[random.randint(0, count - 1)]
        return self


class RandomManager(models.Manager):
    def get_queryset(self):
        return RandomQuerySet(self.model, using=self._db)  # Important!
