from django.test import TestCase

from apps.account.models import Savegame
from apps.dynasty.models import Dynasty
from apps.location.models import County
from apps.military.models import Regiment, Battle, RegimentType
from apps.military.services.battlefield import BattlefieldService
from apps.military.services.regiment_actions import RegimentActionService


class RegimentActionBaseTest(TestCase):
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
        regiment_type_long_range = RegimentType.objects.filter(is_long_range=True).first()
        cls.regiment_peasants_1 = Regiment.objects.create(county=cls.county_1, name='1. Testington Peasants',
                                                          type=regiment_type_peasants)
        cls.regiment_peasants_2 = Regiment.objects.create(county=cls.county_1, name='2. Testington Peasants',
                                                          type=regiment_type_peasants)
        cls.regiment_peasants_3 = Regiment.objects.create(county=cls.county_2, name='1. Otherland Peasants',
                                                          type=regiment_type_peasants)
        cls.regiment_peasants_4 = Regiment.objects.create(county=cls.county_2, name='2. Otherland Peasants',
                                                          type=regiment_type_peasants)
        cls.regiment_long_range_1 = Regiment.objects.create(county=cls.county_1, name='2. Testington Peasants',
                                                            type=regiment_type_long_range)

    def setUp(self):
        super().setUp()

        # Setup battlefield
        attacking_regiments = self.county_1.regiments.all()
        defending_regiments = self.county_2.regiments.all()
        self.battle_service.initialize_battle(attacking_regiments, defending_regiments)
