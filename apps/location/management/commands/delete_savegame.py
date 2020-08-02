from django.core.management.base import BaseCommand

from apps.account.models import Savegame


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('savegame_id', type=int)

    def handle(self, *args, **options):
        savegame_id = options['savegame_id']
        if savegame_id:
            Savegame.objects.filter(id=savegame_id).delete()
