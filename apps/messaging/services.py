from apps.account.models import Savegame
from apps.dynasty.models import Person
from apps.messaging.models import EventMessage


class MessageService(object):
    savegame = None

    def __init__(self, savegame: Savegame) -> None:
        self.savegame = savegame

    def person_dies_natural_cause(self, person: Person):
        message = EventMessage()
        message.title = f'{person.name} died!'
        message.text = f'Unfortunately {person.name} died at age {person.age} on natural causes. He will be mourned.'
        message.type = EventMessage.TYPE_OK
        message.created_in_year = self.savegame.current_year
        message.savegame = self.savegame
        message.save()
