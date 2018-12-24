from difflib import SequenceMatcher
from random import randrange

from apps.location.models import County
from apps.naming.models import LocationNamePostfix, LocationNamePrefix, PersonName


class PersonNameService(object):

    @staticmethod
    def get_name(gender):
        return PersonName.objects.filter(gender=gender).order_by('?').first()


class LocationNameService(object):
    MAX_ITERATIONS = 10000

    @staticmethod
    def create_name():
        prefix = postfix = LocationNamePrefix(text='')
        amount_prefixes = LocationNamePrefix.objects.count()
        amount_postfixes = LocationNamePostfix.objects.count()
        name = ''
        iteration = 0
        while len(name) == 0 or County.objects.filter(name=name).exists():
            iteration += 1
            if iteration > LocationNameService.MAX_ITERATIONS:
                raise Exception('County-Namepool is empty. Add more names!')
            while SequenceMatcher(None, prefix.text.lower(), postfix.text.lower()).ratio() > 0.2:
                prefix = LocationNamePrefix.objects.all()[randrange(0, amount_prefixes)]
                postfix = LocationNamePostfix.objects.all()[randrange(0, amount_postfixes)]
            name = f'{prefix}{postfix}'
        return name
