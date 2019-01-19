from django.core.management.base import BaseCommand

from apps.account.models import Savegame
from apps.dynasty.models import Dynasty
from apps.dynasty.services import DynastyService


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('savegame_id', type=int, help='Savegame ID')

    def handle(self, *args, **options):
        savegame_id = options['savegame_id']

        savegame = Savegame.objects.get(pk=savegame_id)

        county = savegame.counties.all().get_random()

        # Reset all dynasty home counties
        Dynasty.objects.all().update(home_county=None)

        dynasty_service = DynastyService(savegame)
        dynasty = dynasty_service.create_dynasty(county.name, county)
        savegame.playing_as = dynasty
        savegame.save()

        print(f'{dynasty} (#{dynasty.id}) created and set for savegame.')
