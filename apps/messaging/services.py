from apps.account.models import Savegame
from apps.dynasty.models import Person
from apps.dynasty.settings import GENDER_MALE
from apps.messaging.models import EventMessage


class MessageService(object):
    savegame = None

    def __init__(self, savegame: Savegame) -> None:
        self.savegame = savegame

    def person_dies_natural_cause(self, person: Person):
        message = EventMessage()
        message.title = f'{person.name} died!'
        # todo add some random reasons like this or that sickness
        pronoun = "He" if person.gender == GENDER_MALE else "She"
        message.text = f'Unfortunately {person} died at age {person.age} by natural causes. {pronoun} will be mourned.'
        message.type = EventMessage.TYPE_OK
        message.created_in_year = self.savegame.current_year
        message.savegame = self.savegame
        message.save()
