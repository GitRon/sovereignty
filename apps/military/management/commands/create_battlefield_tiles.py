from django.core.management.base import BaseCommand

from apps.account.models import Savegame
from apps.military.services.battlefield import BattlefieldService


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('savegame_id', type=int, help='Savegame ID')

    def handle(self, *args, **options):
        savegame_id = options['savegame_id']

        savegame = Savegame.objects.get(pk=savegame_id)

        bs = BattlefieldService(savegame)
        bs.create_battlefield_tiles()

        print('Battlefield tiles created.')
