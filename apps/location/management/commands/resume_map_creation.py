from django.core.management.base import BaseCommand

from apps.location.models import Map
from apps.location.services import MapService


class Command(BaseCommand):

    def handle(self, *args, **options):
        ms = MapService()
        ms.canvas_map = Map.objects.order_by('-id').first()
        ms.populate_map_with_countries()
