from django.core.management.base import BaseCommand

from apps.account.models import Savegame
from apps.dynasty.models import Trait
from apps.dynasty.services import PersonService, DynastyService
from apps.dynasty import settings as ps


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('savegame_id', type=int, help='Savegame ID')

    def handle(self, *args, **options):
        savegame_id = options['savegame_id']

        savegame = Savegame.objects.get(pk=savegame_id)
        dynasty_service = DynastyService(savegame)
        dynasty = dynasty_service.create_dynasty('Freinitz')
        savegame.playing_as = dynasty
        savegame.save()

        print(f'{dynasty} (#{dynasty.id}) created and set for savegame.')
