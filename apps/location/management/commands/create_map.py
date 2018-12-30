from django.core.management.base import BaseCommand

from apps.location.services import MapService


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('map_size', type=int, help='Map dimensions')

    def handle(self, *args, **options):
        map_size = options['map_size']
        ms = MapService()
        if map_size:
            ms.CANVAS_HEIGHT = ms.CANVAS_WIDTH = map_size
        ms.create_world()
