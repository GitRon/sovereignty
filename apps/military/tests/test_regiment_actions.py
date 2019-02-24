from django.test import TestCase

from apps.account.models import Savegame
from apps.dynasty.models import Dynasty
from apps.location.models import County
from apps.military.models import Regiment, BattlefieldTile, Battle, RegimentType
from apps.military.services.battlefield import BattlefieldService
from apps.military.services.regiment_actions import RegimentActionService


class MapServiceTest(TestCase):
    fixtures = ['initial_data']

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        # Constants
        cls.field_size = BattlefieldService.BATTLEFIELD_SIZE - 1

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

        # Services
        cls.battle_service = BattlefieldService(cls.savegame)
        cls.regiment_action_service = RegimentActionService(cls.savegame)

        # Setup battlefield
        cls.battle_service.create_battlefield_tiles()

        # Create regiment
        regiment_type_peasants = RegimentType.objects.get(default_type=True)
        cls.regiment_peasants_1 = Regiment.objects.create(county=cls.county_1, name='1. Testington Peasants',
                                                          type=regiment_type_peasants)
        cls.regiment_peasants_2 = Regiment.objects.create(county=cls.county_1, name='2. Testington Peasants',
                                                          type=regiment_type_peasants)
        cls.regiment_peasants_3 = Regiment.objects.create(county=cls.county_2, name='1. Otherland Peasants',
                                                          type=regiment_type_peasants)

    def setUp(self):
        super().setUp()

        # Setup battlefield
        self.battle_service.initialize_battle()

    def test_det_basic_movement_all_directions_ok(self):
        # Move regiment to middle so we have space around
        self.battle_service.move_regiment(self.regiment_peasants_1, self.field_size / 2, self.field_size / 2)

        directions = self.regiment_action_service.det_basic_movement(self.regiment_peasants_1)

        self.assertEqual(len(directions), 4)

    def test_det_basic_movement_no_left_on_border(self):
        # Move other regiment out of the way
        self.battle_service.move_regiment(self.regiment_peasants_2, 0, 0)
        # Move regiment to middle so we have space around
        self.battle_service.move_regiment(self.regiment_peasants_1, 0, self.field_size / 2)

        directions = self.regiment_action_service.det_basic_movement(self.regiment_peasants_1)

        self.assertIn(self.regiment_action_service.ACTION_MOVE_UP, directions)
        self.assertIn(self.regiment_action_service.ACTION_MOVE_DOWN, directions)
        self.assertIn(self.regiment_action_service.ACTION_MOVE_RIGHT, directions)

    def test_det_basic_movement_no_right_on_border(self):
        # Move regiment to middle so we have space around
        self.battle_service.move_regiment(self.regiment_peasants_1, self.field_size, self.field_size / 2)

        directions = self.regiment_action_service.det_basic_movement(self.regiment_peasants_1)

        self.assertIn(self.regiment_action_service.ACTION_MOVE_UP, directions)
        self.assertIn(self.regiment_action_service.ACTION_MOVE_DOWN, directions)
        self.assertIn(self.regiment_action_service.ACTION_MOVE_LEFT, directions)

    def test_det_basic_movement_no_down_on_border(self):
        # Move regiment to middle so we have space around
        self.battle_service.move_regiment(self.regiment_peasants_1, self.field_size / 2, self.field_size)

        directions = self.regiment_action_service.det_basic_movement(self.regiment_peasants_1)

        self.assertIn(self.regiment_action_service.ACTION_MOVE_UP, directions)
        self.assertIn(self.regiment_action_service.ACTION_MOVE_LEFT, directions)
        self.assertIn(self.regiment_action_service.ACTION_MOVE_RIGHT, directions)
