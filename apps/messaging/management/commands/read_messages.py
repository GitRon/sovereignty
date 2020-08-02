from django.core.management.base import BaseCommand

from apps.messaging.models import EventMessage


class Command(BaseCommand):

    def handle(self, *args, **options):
        updated_messages = EventMessage.objects.update(done=True)

        print(f'Marked {updated_messages} messages as read.')
