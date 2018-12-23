from difflib import SequenceMatcher

from apps.location.models import County
from apps.naming.models import LocationNamePostfix, LocationNamePrefix, PersonName


class PersonNameService(object):

    @staticmethod
    def get_name(gender):
        return PersonName.objects.filter(gender=gender).order_by('?').first()


class LocationNameService(object):
    MAX_ITERATIONS = 1000

    @staticmethod
    def create_name():
        prefix = postfix = LocationNamePrefix(text='')
        name = ''
        iteration = 0
        while len(name) == 0 or County.objects.filter(name=name).exists():
            iteration += 1
            if iteration > LocationNameService.MAX_ITERATIONS:
                raise Exception('County-Namepool is empty. Add more names!')
            while SequenceMatcher(None, prefix.text.lower(), postfix.text.lower()).ratio() > 0.2:
                prefix = LocationNamePrefix.objects.order_by('?').first()
                postfix = LocationNamePostfix.objects.order_by('?').first()
            name = f'{prefix}{postfix}'
        return name
