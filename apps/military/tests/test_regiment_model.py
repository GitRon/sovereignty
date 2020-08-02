from django.test import TestCase

from apps.account.models import Savegame
from apps.dynasty.models import Dynasty
from apps.location.models import County
from apps.military.models import Regiment, RegimentType


class RegimentModelTest(TestCase):
    fixtures = ['initial_data']

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        # Create savegame
        cls.savegame = Savegame.objects.create()
        cls.county_1 = County.objects.create(savegame=cls.savegame, name='Testington')
        cls.county_2 = County.objects.create(savegame=cls.savegame, name='Otherland')
        cls.dynasty = Dynasty.objects.create(
            from_location='Testington',
            home_county=cls.county_1,
            savegame=cls.savegame
        )

        # Create regiment
        cls.regiment_peasants = Regiment.objects.create(county=cls.county_1, name='1. Testington Peasants',
                                                        type=RegimentType.objects.get(name='Peasants'))
        cls.regiment_crossbowmen = Regiment.objects.create(county=cls.county_1, name='2. Testington Archers',
                                                           type=RegimentType.objects.get(name='Crossbowmen'))
        cls.regiment_archers = Regiment.objects.create(county=cls.county_1, name='2. Testington Archers',
                                                       type=RegimentType.objects.get(name='Archers'))
        cls.regiment_spearmen = Regiment.objects.create(county=cls.county_1, name='2. Testington Spearmen',
                                                        type=RegimentType.objects.get(name='Spearmen'))
        cls.regiment_heavy_infantry = Regiment.objects.create(county=cls.county_1, name='2. Testington H. Infantry',
                                                              type=RegimentType.objects.get(name='Heavy Infantry'))
        cls.regiment_light_cavalry = Regiment.objects.create(county=cls.county_1, name='2. Testington Cavalry',
                                                             type=RegimentType.objects.get(name='Light Cavalry'))
        cls.regiment_knights = Regiment.objects.create(county=cls.county_1, name='2. Testington Knights',
                                                       type=RegimentType.objects.get(name='Knights'))

    def test_calculate_linup_weight_peasants(self):
        self.assertAlmostEqual(self.regiment_peasants.lineup_weight, 0.91, 2)

    def test_calculate_linup_weight_crossbowmen(self):
        self.assertAlmostEqual(self.regiment_crossbowmen.lineup_weight, 0.5, 2)

    def test_calculate_linup_weight_archers(self):
        self.assertAlmostEqual(self.regiment_archers.lineup_weight, 0.33, 2)

    def test_calculate_linup_weight_spearmen(self):
        self.assertAlmostEqual(self.regiment_spearmen.lineup_weight, 0.83, 2)

    def test_calculate_linup_weight_heavy_infantry(self):
        self.assertAlmostEqual(self.regiment_heavy_infantry.lineup_weight, 0.3, 2)

    def test_calculate_linup_weight_light_cavalry(self):
        self.assertAlmostEqual(self.regiment_light_cavalry.lineup_weight, 0.36, 2)

    def test_calculate_linup_weight_knights(self):
        self.assertAlmostEqual(self.regiment_knights.lineup_weight, 0.16, 2)
