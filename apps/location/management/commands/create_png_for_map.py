from django.core.management.base import BaseCommand

from apps.location.models import Map
from apps.location.services import MapService


class Command(BaseCommand):

    def handle(self, *args, **options):
        canvas_map = Map.objects.order_by('-id').first()

        if not canvas_map:
            print('No map found.')
            return

        ms = MapService()
        ms.canvas_map = canvas_map
        ms.save_image_in_map()
