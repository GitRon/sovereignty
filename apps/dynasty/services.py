import random

from apps.location.models import County
from apps.naming.services import PersonNameService
from apps.dynasty.models import Person, Trait

from apps.dynasty import settings as ps


class PersonService(object):
    DEFAULT_TRAIT_QUANTITY = 0.5
    TRAIT_QUANTITY_SIGMA = 0.5
    MAX_STARTING_TRAITS = 3

    def get_trait_set(self):
        """
        Returns 0-3 traits for a new person
        :return:
        """
        quantity_traits = round(random.gauss(self.DEFAULT_TRAIT_QUANTITY, self.TRAIT_QUANTITY_SIGMA))
        quantity_traits = max(min(quantity_traits, self.MAX_STARTING_TRAITS), 0)

        trait_list = []

        for x in range(0, quantity_traits):
            new_trait = Trait.objects.get_random_trait()
            while new_trait in trait_list:
                new_trait = Trait.objects.get_random_trait()
            trait_list.append(new_trait)

        return trait_list

    def create_random_person(self, savegame, birth_year, gender):
        person = Person.objects.create(
            name=PersonNameService.get_name(gender),
            nobility=True,
            from_location=County.objects.all().first(),  # todo build this!
            gender=gender,
            birth_year=birth_year,
            savegame=savegame,
            leadership=random.randrange(0, ps.MAX_SKILL_POINTS),  # todo make this more fancy
            intelligence=random.randrange(0, ps.MAX_SKILL_POINTS),
            charisma=random.randrange(0, ps.MAX_SKILL_POINTS),
        )

        # Traits M2M
        trait_list = self.get_trait_set()
        for trait in trait_list:
            person.traits.add(trait)

        return person
