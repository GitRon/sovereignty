from django.test import TestCase

from apps.account.models import Savegame
from apps.dynasty.models import Dynasty, Person
from apps.dynasty.services import PersonService
from apps.dynasty.settings import GENDER_MALE, GENDER_FEMALE
from apps.location.models import County
from apps.location.services.country import CountyRulerService


class RulerServiceTest(TestCase):
    fixtures = ['initial_data']

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        person_service = PersonService()

        cls.savegame = Savegame.objects.create(current_year=1250)
        cls.county_1 = County.objects.create(name='Meinland', savegame=cls.savegame)
        cls.county_2 = County.objects.create(name='Weitwegingen', savegame=cls.savegame)
        cls.dynasty_1 = Dynasty.objects.create(
            from_location='Testhausen',
            home_county=cls.county_1,
            savegame=cls.savegame
        )
        cls.dynasty_2 = Dynasty.objects.create(
            from_location='Guttesten',
            home_county=cls.county_2,
            savegame=cls.savegame
        )
        cls.county_1.ruled_by = cls.dynasty_1
        cls.county_1.save()
        cls.county_2.ruled_by = cls.dynasty_2
        cls.county_2.save()

        cls.crs = CountyRulerService(cls.savegame, cls.county_1)

        # Main dynasty
        cls.ruler = person_service.create_random_person(cls.savegame, 1200, GENDER_MALE, cls.dynasty_1)
        cls.queen = person_service.create_random_person(cls.savegame, 1210, GENDER_FEMALE, cls.dynasty_1)
        cls.oldest_daughter = person_service.create_random_person(cls.savegame, 1233, GENDER_FEMALE, cls.dynasty_1,
                                                                  cls.ruler, cls.queen)
        cls.heir = person_service.create_random_person(cls.savegame, 1235, GENDER_MALE, cls.dynasty_1,
                                                       cls.ruler, cls.queen)
        cls.second_son = person_service.create_random_person(cls.savegame, 1237, GENDER_MALE, cls.dynasty_1,
                                                             cls.ruler, cls.queen)

        cls.dynasty_1.current_dynast = cls.ruler
        cls.dynasty_1.save()

        # Other dynasty
        cls.other_dynast = person_service.create_random_person(cls.savegame, 1190, GENDER_MALE, cls.dynasty_2)

        cls.dynasty_2.current_dynast = cls.other_dynast
        cls.dynasty_2.save()

        # Marriage
        cls.oldest_daughter.spouse = cls.other_dynast
        cls.oldest_daughter.save()

        # Ensure nobody is dead yet
        Person.objects.update(death_year=1400)

    def test_get_succession_line_oldest_son_on_first_place(self):
        succession_line = self.crs.get_succession_line()
        self.assertGreaterEqual(len(succession_line), 2)
        self.assertEqual(succession_line[0], self.heir)
        self.assertEqual(succession_line[1], self.second_son)

    def test_get_succession_line_husband_of_daughter(self):
        succession_line = self.crs.get_succession_line()
        self.assertGreaterEqual(len(succession_line), 3)
        self.assertEqual(succession_line[2], self.other_dynast)

    # todo add more tests
