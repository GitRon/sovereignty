from django.db import models

import apps.dynasty.settings as ps
from apps.account.models import Savegame
from apps.dynasty.managers import TraitManager
from apps.location.models import County


class Trait(models.Model):
    TRAIT_ALCOHOLIC = 1
    TRAIT_CRUEL = 2
    TRAIT_SODOMIST = 3
    TRAIT_TINY = 4
    TRAIT_GIANT = 5
    TRAIT_STRATEGIST = 6
    TRAIT_CHOICES = (
        (TRAIT_ALCOHOLIC, "Alcoholic"),
        (TRAIT_CRUEL, "Cruel"),
        (TRAIT_SODOMIST, "Sodomist"),
        (TRAIT_TINY, "Tiny"),
        (TRAIT_GIANT, "Giant"),
        (TRAIT_STRATEGIST, "Strategist"),
    )

    type = models.PositiveSmallIntegerField(choices=TRAIT_CHOICES)

    objects = TraitManager()

    def __str__(self):
        return self.get_type_display()


class Dynasty(models.Model):
    # todo was sind dynastien genau? wie löse ich das?
    # todo county braucht feld "ruling_dynasty"
    pass


class Person(models.Model):
    name = models.CharField(max_length=50)
    nobility = models.BooleanField(default=True)
    from_location = models.ForeignKey(County, related_name='natives', on_delete=models.CASCADE)
    gender = models.PositiveSmallIntegerField(choices=ps.GENDER_CHOICES)
    birth_year = models.PositiveIntegerField()

    # System attributes
    savegame = models.ForeignKey(Savegame, related_name='persons', on_delete=models.CASCADE)

    # Relationship
    father = models.ManyToManyField("Person", related_name='fathers_children')
    mother = models.ManyToManyField("Person", related_name='mothers_children')

    # Skills (scale from 0 - 100)
    leadership = models.PositiveIntegerField(default=50)
    intelligence = models.PositiveIntegerField(default=50)
    charisma = models.PositiveIntegerField(default=50)

    # Further "skills"
    fama = models.PositiveIntegerField(default=0)

    # Traits
    traits = models.ManyToManyField(Trait)

    def __str__(self):
        return f'{self.name} von {self.from_location}'
