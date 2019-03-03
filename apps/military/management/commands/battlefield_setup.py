from django.core.management.base import BaseCommand

from apps.account.models import Savegame
from apps.location.models import County
from apps.military.services.battlefield import BattlefieldService


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('savegame_id', type=int, help='Savegame ID')

    def handle(self, *args, **options):
        savegame_id = options['savegame_id']

        savegame = Savegame.objects.get(pk=savegame_id)

        # Regiment fighting
        attacker = savegame.current_county
        attacking_regiments = attacker.regiments.all()
        defender = County.objects.filter(savegame=savegame).exclude(id=savegame.playing_as.home_county.id).first()
        defending_regiments = defender.regiments.all()

        bs = BattlefieldService(savegame)
        bs.battle.attacker = attacker
        bs.battle.defender = defender
        bs.initialize_battle(attacking_regiments, defending_regiments)
