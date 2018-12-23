from django.core.management.base import BaseCommand

from apps.location.services import MapService


class Command(BaseCommand):

    def handle(self, *args, **options):
        ms = MapService()
        ms.populate_map_with_countries()
