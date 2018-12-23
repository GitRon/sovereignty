from django.core.management.base import BaseCommand

from apps.location.models import County


class Command(BaseCommand):

    def handle(self, *args, **options):
        County.objects.all().delete()
