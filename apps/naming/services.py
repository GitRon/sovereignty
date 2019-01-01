from difflib import SequenceMatcher
from random import randrange

from apps.account.models import Savegame
from apps.location.models import County
from apps.naming.models import LocationNamePostfix, LocationNamePrefix, PersonName


class PersonNameService(object):

    @staticmethod
    def get_name(gender):
        # TODO order by ? is very inperformant!
        return PersonName.objects.filter(gender=gender).order_by('?').first()


class LocationNameService(object):
    MAX_ITERATIONS = 10000
    STRING_SIMILARITY_FACTOR = 0.5

    @staticmethod
    def create_name(savegame: Savegame):
        prefix = postfix = LocationNamePrefix(text='')
        amount_prefixes = LocationNamePrefix.objects.count()
        amount_postfixes = LocationNamePostfix.objects.count()
        name = ''
        iteration = 0
        while len(name) == 0 or County.objects.filter(name=name, savegame=savegame).exists():
            iteration += 1
            if iteration > LocationNameService.MAX_ITERATIONS:
                raise Exception('County-Namepool is empty. Add more names!')
            while SequenceMatcher(None, prefix.text.lower(), postfix.text.lower()).ratio() > \
                    LocationNameService.STRING_SIMILARITY_FACTOR:
                prefix = LocationNamePrefix.objects.all()[randrange(0, amount_prefixes)]
                postfix = LocationNamePostfix.objects.all()[randrange(0, amount_postfixes)]
            name = f'{prefix}{postfix}'
        return name
