from django.core.management.base import BaseCommand

from apps.location.models import Map


class Command(BaseCommand):

    def handle(self, *args, **options):
        Map.objects.all().delete()
