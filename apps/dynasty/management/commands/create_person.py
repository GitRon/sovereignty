from django.core.management.base import BaseCommand

from apps.account.models import Savegame
from apps.dynasty.models import Trait
from apps.dynasty.services import PersonService
from apps.dynasty import settings as ps


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('savegame_id', type=int, help='Savegame ID')

    def handle(self, *args, **options):
        savegame_id = options['savegame_id']

        person_service = PersonService()
        savegame = Savegame.objects.get(pk=savegame_id)
        person = person_service.create_random_person(savegame, 65, ps.GENDER_MALE)

        print(f'{person} created.')
