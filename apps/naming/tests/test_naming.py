from unittest import mock

from django.test import TestCase

from apps.account.models import Savegame
from apps.dynasty import settings as ps
from apps.naming.models import PersonName
from apps.naming.services import PersonNameService, LocationNameService


class NamingTest(TestCase):
    fixtures = ['initial_data']

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.ps = PersonNameService()
        cls.ls = LocationNameService()
        cls.savegame = Savegame.objects.create()

    def setUp(self):
        pass

    def test_get_random_person_name_for_gender_male(self):
        test_gender = ps.GENDER_MALE
        random_name = self.ps.get_name(test_gender)
        self.assertIsInstance(random_name, PersonName)
        self.assertEqual(random_name.gender, test_gender)

    def test_get_random_person_name_for_gender_female(self):
        test_gender = ps.GENDER_MALE
        random_name = self.ps.get_name(test_gender)
        self.assertIsInstance(random_name, PersonName)
        self.assertEqual(random_name.gender, test_gender)

    def test_create_location_name(self):
        self.assertGreater(len(self.ls.create_name(self.savegame)), 0)

    def test_middle_name_has_name(self):
        test_gender = ps.GENDER_MALE
        with mock.patch('random.random', return_value=0.2):
            middle_name = self.ps.get_middle_name(test_gender)

        self.assertIsInstance(middle_name, PersonName)

    def test_middle_name_has_no_name(self):
        test_gender = ps.GENDER_MALE
        with mock.patch('random.random', return_value=0.4):
            middle_name = self.ps.get_middle_name(test_gender)

        self.assertEqual(middle_name, None)
