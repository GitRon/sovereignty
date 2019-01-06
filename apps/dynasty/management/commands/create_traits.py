from django.core.management.base import BaseCommand

from apps.dynasty.models import Trait


class Command(BaseCommand):

    def handle(self, *args, **options):
        counter = 0
        for trait_type in Trait.TRAIT_CHOICES:
            trait, created = Trait.objects.get_or_create(type=trait_type[0])
            counter += 1 if created else 0

        print(f'{counter} trait(s) created.')
