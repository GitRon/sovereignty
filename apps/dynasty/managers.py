import random

from django.db import models


class TraitManager(models.Manager):

    def get_random_trait(self):
        trait_type = random.choice(self.model.TRAIT_CHOICES)[0]
        trait, created = self.model.objects.get_or_create(type=trait_type)
        return trait
