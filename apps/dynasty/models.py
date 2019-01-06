from django.db import models

import apps.dynasty.settings as ps
from apps.dynasty.managers import TraitManager, PersonManager, DynastyManager
from apps.location.models import County


class Trait(models.Model):
    TRAIT_ALCOHOLIC = 1
    TRAIT_CRUEL = 2
    TRAIT_SODOMIST = 3
    TRAIT_TINY = 4
    TRAIT_GIANT = 5
    TRAIT_STRATEGIST = 6
    TRAIT_RELIGIOUS_ZEAL = 7
    TRAIT_BENEVOLENT = 8
    TRAIT_CHOICES = (
        (TRAIT_ALCOHOLIC, "Alcoholic"),
        (TRAIT_CRUEL, "Cruel"),
        (TRAIT_SODOMIST, "Sodomist"),
        (TRAIT_TINY, "Tiny"),
        (TRAIT_GIANT, "Giant"),
        (TRAIT_STRATEGIST, "Strategist"),
        (TRAIT_RELIGIOUS_ZEAL, "Religious Zeal"),
        (TRAIT_BENEVOLENT, "Benevolent"),
    )

    type = models.PositiveSmallIntegerField(choices=TRAIT_CHOICES)
    incompatible_traits = models.ManyToManyField('self')

    objects = TraitManager()

    def __str__(self):
        return self.get_type_display()


class Dynasty(models.Model):
    from_location = models.CharField(max_length=County.NAME_LENGTH)
    ruling_over = models.ForeignKey(County, related_name='natives', null=True, blank=True, on_delete=models.CASCADE)
    current_dynast = models.ForeignKey("Person", related_name='rules_over', null=True, blank=True,
                                       on_delete=models.CASCADE)
    # System attributes
    savegame = models.ForeignKey('account.Savegame', related_name='dynasties', on_delete=models.CASCADE)

    objects = DynastyManager()

    def __str__(self):
        return f'Dynasty of {self.from_location}'


class Person(models.Model):
    name = models.CharField(max_length=50)
    nobility = models.BooleanField(default=True)
    gender = models.PositiveSmallIntegerField(choices=ps.GENDER_CHOICES)
    birth_year = models.PositiveIntegerField()
    death_year = models.PositiveIntegerField(null=True, blank=True)
    dynasty = models.ForeignKey(Dynasty, related_name='persons', on_delete=models.CASCADE)

    # System attributes
    savegame = models.ForeignKey('account.Savegame', related_name='persons', on_delete=models.CASCADE)

    # Relationship
    father = models.ForeignKey("Person", related_name='fathers_children', null=True, blank=True,
                               on_delete=models.CASCADE)
    mother = models.ForeignKey("Person", related_name='mothers_children', null=True, blank=True,
                               on_delete=models.CASCADE)

    # Skills (scale from 0 - 100)
    leadership = models.PositiveIntegerField(default=50)
    intelligence = models.PositiveIntegerField(default=50)
    charisma = models.PositiveIntegerField(default=50)

    # Further "skills"
    fama = models.PositiveIntegerField(default=0)

    # Traits
    traits = models.ManyToManyField(Trait)

    objects = PersonManager()

    def __str__(self):
        return f'{self.name} von {self.dynasty.from_location}'

    @property
    def age(self):
        if not self.death_year:
            return self.savegame.current_year - self.birth_year
        return self.death_year - self.birth_year
