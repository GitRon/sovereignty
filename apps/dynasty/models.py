from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save
from django.dispatch import receiver

import apps.dynasty.settings as ps
from apps.dynasty.managers import TraitManager, PersonManager, DynastyManager
from apps.location.models import County
from apps.naming.models import PersonName


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
    home_county = models.OneToOneField(County, related_name='native_dynasty', null=True, blank=True,
                                       on_delete=models.CASCADE)
    current_dynast = models.ForeignKey("Person", related_name='rules_over', null=True, blank=True,
                                       on_delete=models.CASCADE)
    # System attributes
    savegame = models.ForeignKey('account.Savegame', related_name='dynasties', on_delete=models.CASCADE)

    objects = DynastyManager()

    def __str__(self):
        return f'Dynasty of {self.from_location}'


class Person(models.Model):
    first_name = models.ForeignKey(PersonName, related_name='first_name_persons', on_delete=models.CASCADE)
    middle_name = models.ForeignKey(PersonName, related_name='middle_name_persons', null=True, blank=True,
                                    on_delete=models.CASCADE)
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
    spouse = models.OneToOneField("Person", related_name='married_to', null=True, blank=True,
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
        # If person is not already dead show current age
        if self.death_year > self.savegame.current_year:
            return self.savegame.current_year - self.birth_year
        # Show final age instead
        return self.death_year - self.birth_year

    @property
    def name(self):
        if self.middle_name:
            return f'{self.first_name.name} {self.middle_name.name}'
        return self.first_name.name

    @property
    def is_dead(self):
        return self.death_year <= self.savegame.current_year

    @property
    def siblings(self):
        return Person.objects.filter(Q(father=self.father) | Q(mother=self.mother))

    @property
    def children(self):
        return Person.objects.filter(Q(father=self) | Q(mother=self))

    def get_siblings_by_gender(self, gender):
        # todo write test!
        return self.siblings.filter(gender=gender).exclude(id=self.id)

    def get_person_names(self):
        name_list = [self.first_name]
        if self.middle_name:
            name_list.append(self.middle_name)
        return name_list

    def get_sibling_names(self):
        name_list = [self.get_person_names()]

        for sibling in self.get_siblings_by_gender(self.gender):
            name_list.append(sibling.get_person_names())

        return name_list

    def get_children_names(self):
        name_list = []

        for child in self.children:
            name_list.append(child.get_person_names())

        return name_list

    def get_title_claims(self):
        # todo write test
        from apps.location.services.country import CountyRulerService
        claims = []
        counties = County.objects.get_visible(savegame=self.savegame)
        for county in counties:
            crs = CountyRulerService(self.savegame, county)
            line_of_succession = crs.get_succession_line()
            if self in line_of_succession:
                claims.append({'county': county, 'position': line_of_succession.index(self) + 1})

        return claims


@receiver(pre_save, sender=Person, dispatch_uid="person.set_death_year")
def set_death_year(sender, instance, **kwargs):
    if not instance.death_year:
        from apps.dynasty.services import DynastyService
        ds = DynastyService(instance.savegame)
        instance.death_year = ds.calculate_year_of_death(instance.birth_year)
