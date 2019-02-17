from django.core.management.base import BaseCommand

from apps.account.models import Savegame
from apps.military.models import Regiment, RegimentType


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('savegame_id', type=int, help='Savegame ID')

    def handle(self, *args, **options):
        savegame_id = options['savegame_id']

        savegame = Savegame.objects.get(pk=savegame_id)

        counties = savegame.counties.all()

        for county in counties:

            if county.army_size > 0:
                continue

            counter = 0
            for i in range(1, county.max_regiments + 1):
                Regiment.objects.create(
                    name=f'{i}. Regiment',
                    county=county,
                    type=RegimentType.objects.get(default_type=True)

                )
                counter += 1

            print(f'{counter} regiments created for county {county}.')
        print(f'{counties.count()} counties processed.')
