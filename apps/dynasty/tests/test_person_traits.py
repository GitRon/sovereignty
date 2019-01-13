from unittest import mock

from django.test import TestCase

from apps.account.models import Savegame
from apps.dynasty.models import Person, Dynasty
from apps.dynasty.services import DynastyService, PersonService
from apps.dynasty import settings as ps


class PersonTraitTest(TestCase):
    fixtures = ['initial_data']

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.ps = PersonService()
        cls.savegame = Savegame.objects.create()

    def setUp(self):
        pass

    def test_get_trait_set_regular(self):
        target_traits = 1
        with mock.patch('random.gauss', return_value=target_traits):
            traits = self.ps.get_trait_set()

        self.assertEqual(len(traits), target_traits)

    def test_get_trait_set_multiple(self):
        target_traits = 3
        with mock.patch('random.gauss', return_value=target_traits):
            traits = self.ps.get_trait_set()

        self.assertEqual(len(traits), target_traits)

    def test_get_trait_set_too_many(self):
        target_traits = 99
        with mock.patch('random.gauss', return_value=target_traits):
            traits = self.ps.get_trait_set()

        self.assertEqual(len(traits), self.ps.MAX_STARTING_TRAITS)

    def test_get_trait_set_no_traits(self):
        target_traits = 0
        with mock.patch('random.gauss', return_value=target_traits):
            traits = self.ps.get_trait_set()

        self.assertEqual(len(traits), 0)

    def test_create_random_person(self):
        birth_year = 815
        gender = ps.GENDER_FEMALE
        ds = DynastyService(self.savegame)
        dynasty = ds._create_dynasty_object('Myland')

        target_skill_points = 50
        with mock.patch('random.randrange', return_value=target_skill_points):
            person = self.ps.create_random_person(self.savegame, birth_year, gender, dynasty)

        self.assertEqual(person.first_name.gender, gender)
        self.assertEqual(person.birth_year, birth_year)
        self.assertGreaterEqual(person.leadership, target_skill_points)
        self.assertGreaterEqual(person.intelligence, target_skill_points)
        self.assertGreaterEqual(person.charisma, target_skill_points)
