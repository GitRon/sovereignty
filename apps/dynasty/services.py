import random

from apps.account.managers import SavegameManager
from apps.core.utils import get_rand_bool
from apps.location.models import County
from apps.naming.models import PersonName
from apps.naming.services import PersonNameService
from apps.dynasty.models import Person, Trait, Dynasty

from apps.dynasty import settings as ps


class PersonService(object):
    DEFAULT_TRAIT_QUANTITY = 0.5
    TRAIT_QUANTITY_SIGMA = 0.5
    MAX_STARTING_TRAITS = 3

    pns = PersonNameService()

    def get_trait_set(self):
        """
        Returns 0-3 traits for a new person
        :return:
        """
        quantity_traits = round(random.gauss(self.DEFAULT_TRAIT_QUANTITY, self.TRAIT_QUANTITY_SIGMA))
        quantity_traits = max(min(quantity_traits, self.MAX_STARTING_TRAITS), 0)

        trait_list = []

        for x in range(0, quantity_traits):
            new_trait = Trait.objects.all().get_random(trait_list)
            while new_trait in trait_list:
                new_trait = Trait.objects.all().get_random(trait_list)
            trait_list.append(new_trait)

        return trait_list

    def create_random_person(self, savegame, birth_year, gender, dynasty, father=None, mother=None):

        # Get name of other children to avoid duplicate naming
        if father:
            name_exclude_list = father.get_children_names()
        elif mother:
            name_exclude_list = mother.get_children_names()
        else:
            name_exclude_list = []

        # Get first name and optional middle name
        first_name = self.pns.get_name(gender, name_exclude_list)
        name_exclude_list.append(first_name)
        middle_name = self.pns.get_middle_name(gender, name_exclude_list)

        person = Person.objects.create(
            first_name=first_name,
            middle_name=middle_name,
            nobility=True,
            dynasty=dynasty,
            gender=gender,
            birth_year=birth_year,
            father=father,
            mother=mother,
            savegame=savegame,
            leadership=random.randrange(0, ps.MAX_SKILL_POINTS),  # todo make this more fancy
            intelligence=random.randrange(0, ps.MAX_SKILL_POINTS),
            charisma=random.randrange(0, ps.MAX_SKILL_POINTS),
        )

        # Traits M2M
        trait_list = self.get_trait_set()
        for trait in trait_list:
            person.traits.add(trait)

        print(f'Created person {person}.')

        return person


class DynastyService(object):
    DEFAULT_PARENTING_AGE = 22
    DEFAULT_PARENTING_SIGMA = 8
    MIN_PARENTING_AGE_MALE = 17
    MIN_PARENTING_AGE_FEMALE = 15
    AVG_QUANTITY_CHILDREN = 3
    AVG_QUANTITY_CHILDREN_SIGMA = 4
    DEFAULT_CHILDREN_INTERVAL = 2
    DEFAULT_CHILDREN_INTERVAL_SIGMA = 2
    CHILD_MORTALITY_RATE = 0.4
    MAX_AGE_FIRST_CHILD_ON_CREATION = 20
    MOTHER_AGE_OFFSET_TO_HUSBAND = 5
    MOTHER_AGE_OFFSET_TO_SIGMA = 5

    person_service = PersonService()
    savegame = None
    dynasty = None

    def __init__(self, savegame) -> None:
        self.savegame = savegame

    def _get_year_from_age(self, age):
        return self.savegame.current_year - age

    def _get_age_from_year(self, birth_year):
        return self.savegame.current_year - birth_year

    def get_parenting_age(self, gender):
        """
        Get age when a person got his first child
        :return:
        """
        min_age = self.MIN_PARENTING_AGE_MALE if gender == ps.GENDER_MALE else self.MIN_PARENTING_AGE_FEMALE
        return round(max(random.gauss(self.DEFAULT_PARENTING_AGE, self.DEFAULT_PARENTING_SIGMA), min_age))

    def get_no_of_children(self):
        """
        Get number of children a person has
        :return:
        """
        return round(max(random.gauss(self.AVG_QUANTITY_CHILDREN, self.AVG_QUANTITY_CHILDREN_SIGMA), 0))

    def get_wife_birth_year_based_on_husband_age(self, age_husband):
        year = self._get_year_from_age(round(max(
            age_husband + random.gauss(
                self.MOTHER_AGE_OFFSET_TO_HUSBAND,
                self.MOTHER_AGE_OFFSET_TO_SIGMA),
            self.MIN_PARENTING_AGE_FEMALE)))
        print(f'Wife birth year {year}')
        return year

    def get_birth_year_of_next_child(self, birth_year_previous_child):
        year = round(birth_year_previous_child + max(random.gauss(self.DEFAULT_CHILDREN_INTERVAL,
                                                                  self.DEFAULT_CHILDREN_INTERVAL_SIGMA), 1))
        print(f'Birth year of next child {year}')
        return year

    def create_couple(self):
        ruler_parenting_age = self.get_parenting_age(ps.GENDER_MALE)
        ruler_quantity_children = self.get_no_of_children()
        if ruler_quantity_children:
            age_oldest_ruler_child = random.randrange(0, self.MAX_AGE_FIRST_CHILD_ON_CREATION)
        else:
            age_oldest_ruler_child = 0

        ruler_birth_year = self._get_year_from_age(ruler_parenting_age + age_oldest_ruler_child)
        print(f'Father birth year {ruler_birth_year}')

        # Create parents of current regent
        father = self.person_service.create_random_person(self.savegame, ruler_birth_year, ps.GENDER_MALE, self.dynasty)

        mother = self.person_service.create_random_person(self.savegame,
                                                          self.get_wife_birth_year_based_on_husband_age(
                                                              self._get_year_from_age(ruler_birth_year)),
                                                          ps.GENDER_FEMALE, self.dynasty)

        print(f'Created father {father} and mother {mother} which are supposed to have {ruler_quantity_children} '
              f'children.')

        return father, mother, ruler_quantity_children, age_oldest_ruler_child

    def calculate_year_of_death(self, birth_year):
        dice = random.random()

        # Determine which age group he will reach
        # With 20% chance person dies as a baby
        if dice < 0.2:
            death_age = random.choice([0, 1])
        # With another 20% he'll dies as a child
        elif dice > 0.4:
            death_age = random.randint(2, 12)
        # Otherwise he'll reaches adulthood
        else:
            death_age = 62 * pow(dice,  2.5) + 12

        return birth_year + round(death_age)

    def create_couples_children(self, ruler_quantity_children, age_oldest_ruler_child, father, mother):
        # Create children
        counter = 1
        child = None
        for x in range(0, ruler_quantity_children):
            if counter == 1:
                birth_year = self._get_year_from_age(age_oldest_ruler_child)
            else:
                birth_year = self.get_birth_year_of_next_child(child.birth_year)
            gender = random.choice(ps.GENDER_CHOICES)[0]  # todo boy/girl ratio wasn't 50:50
            child = self.person_service.create_random_person(self.savegame, birth_year, gender, self.dynasty, father,
                                                             mother)
            counter += 1

            # Child mortality
            death_year = self.calculate_year_of_death(child.birth_year)
            if death_year and death_year < self.savegame.current_year:
                print(f'{child} dies in year {death_year}.')
                child.death_year = death_year
                child.save()

        print(f'Created {counter - 1} children.')

    def _create_dynasty_object(self, from_location, county=None):
        dynasty = Dynasty.objects.create(
            from_location=from_location,
            home_county=county,
            savegame=self.savegame
        )
        if county:
            county.ruled_by = dynasty
            county.save()

        return dynasty

    def create_dynasty(self, from_location, county=None):

        # Create dynasty itself
        self.dynasty = self._create_dynasty_object(from_location, county)

        # Create parents
        father, mother, ruler_quantity_children, age_oldest_ruler_child = self.create_couple()

        # Create their children
        self.create_couples_children(ruler_quantity_children, age_oldest_ruler_child, father, mother)

        # Adjust savegame starting year
        # todo this is crap!
        youngest_child = Person.objects.filter(father=father).order_by('-birth_year').first()
        if youngest_child:
            if youngest_child.age < 0:
                self.savegame.current_year -= (youngest_child.age - random.randrange(0, 5))

        # Set dynasty ruler
        self.dynasty.current_dynast = father
        self.dynasty.save()

        return self.dynasty
