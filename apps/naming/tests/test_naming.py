import os

from django.db.models import Count
from django.test import TestCase

from apps.account.models import Savegame
from apps.location.models import MapDot, Map
from apps.location.services.country import CreateCountyService
from apps.location.services.map import MapService
from apps.naming.models import PersonName
from apps.naming.services import PersonNameService, LocationNameService
from apps.dynasty import settings as ps


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
