from django.core.management.base import BaseCommand

from apps.dynasty.models import Person


class Command(BaseCommand):

    def handle(self, *args, **options):
        Person.objects.update(death_year=None)

        person_list = Person.objects.all()

        for person in person_list:
            person.save()

        print(f'Saved {person_list.count()} persons.')
