from django.test import TestCase

from apps.account.models import Savegame
from apps.dynasty.models import Dynasty
from apps.location.models import County
from apps.military.models import BattlefieldTile, Battle
from apps.military.services.battlefield import BattlefieldService


class BattlefieldTileModelTest(TestCase):
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

        # Meta data
        cls.savegame.playing_as = cls.dynasty
        cls.savegame.save()

        # Battle setup
        cls.battle = Battle.objects.create(year=800, savegame=cls.savegame, attacker=cls.county_1,
                                           defender=cls.county_2)

        # Setup battlefield
        cls.battle_service = BattlefieldService(cls.savegame)
        cls.battle_service.create_battlefield_tiles()

    def test_calculate_distance_weight_attacker_center_tile(self):
        tile = BattlefieldTile.objects.filter(coordinate_x=0, coordinate_y=4).first()
        self.assertAlmostEqual(tile.distance_weight_attacker, 0.5, 2)

    def test_calculate_distance_weight_attacker_corner_tile_second_column(self):
        tile = BattlefieldTile.objects.filter(coordinate_x=1, coordinate_y=9).first()
        self.assertAlmostEqual(tile.distance_weight_attacker, 5.5, 2)

    def test_calculate_distance_weight_defender_center_tile(self):
        tile = BattlefieldTile.objects.filter(coordinate_x=9, coordinate_y=4).first()
        self.assertAlmostEqual(tile.distance_weight_defender, 0.5, 2)

    def test_calculate_distance_weight_defender_corner_tile_second_column(self):
        tile = BattlefieldTile.objects.filter(coordinate_x=8, coordinate_y=9).first()
        self.assertAlmostEqual(tile.distance_weight_defender, 5.5, 2)
