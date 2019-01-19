from unittest import mock

from django.test import TestCase

from apps.account.models import Savegame
from apps.dynasty.models import Person, Dynasty
from apps.dynasty.services import DynastyService
from apps.dynasty import settings as ps
from apps.location.models import County


class DynastyTest(TestCase):
    fixtures = ['initial_data']
    CURRENT_YEAR = 800

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.savegame = Savegame.objects.create(current_year=cls.CURRENT_YEAR)
        cls.ds = DynastyService(cls.savegame)

    def setUp(self):
        super().setUp()

    def test_get_year_from_age(self):
        test_age = 50
        self.assertEqual(self.ds._get_year_from_age(50), self.savegame.current_year - test_age)

    def test_get_age_from_year(self):
        test_year = 750
        self.assertEqual(self.ds._get_age_from_year(test_year), self.savegame.current_year - test_year)

    def test_get_parenting_age_male(self):
        with mock.patch('random.gauss', return_value=self.ds.DEFAULT_PARENTING_AGE):
            age = self.ds.get_parenting_age(ps.GENDER_MALE)
        self.assertGreaterEqual(age, self.ds.MIN_PARENTING_AGE_MALE)

    def test_get_parenting_age_female(self):
        with mock.patch('random.gauss', return_value=self.ds.DEFAULT_PARENTING_AGE):
            age = self.ds.get_parenting_age(ps.GENDER_FEMALE)
        self.assertGreaterEqual(age, self.ds.MIN_PARENTING_AGE_FEMALE)

    def test_get_wife_birth_year_based_on_husband_age(self):
        age_husband = 50
        with mock.patch('random.gauss', return_value=self.ds.MOTHER_AGE_OFFSET_TO_HUSBAND):
            age = self.ds.get_wife_birth_year_based_on_husband_age(age_husband)

        self.assertGreaterEqual(age, self.ds.MIN_PARENTING_AGE_FEMALE)

    def test_get_no_of_children(self):
        with mock.patch('random.gauss', return_value=self.ds.AVG_QUANTITY_CHILDREN):
            avg_children = self.ds.get_no_of_children()

        self.assertGreaterEqual(avg_children, 0)

    def test_get_birth_year_of_next_child(self):
        self.ds.dynasty = self.ds._create_dynasty_object('Myland')
        with mock.patch.object(self.ds, 'get_no_of_children', return_value=2):
            father, mother, ruler_quantity_children, age_oldest_ruler_child = self.ds.create_couple()
        self.ds.create_couples_children(ruler_quantity_children, age_oldest_ruler_child, father, mother)
        last_child = Person.objects.filter(father=father).order_by('-birth_year').first()
        with mock.patch('random.gauss', return_value=self.ds.MOTHER_AGE_OFFSET_TO_HUSBAND):
            birth_year = self.ds.get_birth_year_of_next_child(last_child.birth_year)
        self.assertGreater(birth_year - last_child.birth_year, 0)

    def test_create_couple(self):
        self.ds.dynasty = self.ds._create_dynasty_object('Myland')
        father, mother, ruler_quantity_children, age_oldest_ruler_child = self.ds.create_couple()

        self.assertIsInstance(father, Person)
        self.assertIsInstance(mother, Person)
        self.assertGreaterEqual(ruler_quantity_children, 0)
        self.assertGreaterEqual(age_oldest_ruler_child, 0)

    def test_create_couples_children(self):
        self.ds.dynasty = self.ds._create_dynasty_object('Myland')
        target_amount_children = 2
        with mock.patch.object(self.ds, 'get_no_of_children', return_value=target_amount_children):
            father, mother, ruler_quantity_children, age_oldest_ruler_child = self.ds.create_couple()
        self.ds.create_couples_children(
            ruler_quantity_children, age_oldest_ruler_child, father, mother)

        self.assertEqual(father.children.count(), target_amount_children)
        self.assertEqual(mother.children.count(), target_amount_children)

    def test_create_dynasty_object(self):
        self.assertIsInstance(self.ds._create_dynasty_object('Myland'), Dynasty)

    def test_create_dynasty(self):
        dynasty = self.ds.create_dynasty('Myland')
        self.assertIsInstance(dynasty, Dynasty)

    def test_create_dynasty_object_for_county(self):
        county = County.objects.create(name='Myland', savegame=self.savegame)
        dynasty = self.ds._create_dynasty_object('Myland', county)
        self.assertIsInstance(dynasty, Dynasty)
        self.assertEqual(county.ruled_by, dynasty)

    def test_calculate_year_of_death(self):
        with mock.patch('random.gauss', return_value=0.5):
            death_year = self.ds.calculate_year_of_death(750)

        self.assertGreaterEqual(death_year, 0)
