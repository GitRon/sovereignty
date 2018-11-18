from difflib import SequenceMatcher

from apps.location.models import County
from apps.naming.models import LocationNamePostfix, LocationNamePrefix, PersonName


class PersonNameService(object):

    @staticmethod
    def get_name(gender):
        return PersonName.objects.filter(gender=gender).order_by('?').first()


class LocationNameService(object):

    @staticmethod
    def create_name():
        prefix = postfix = LocationNamePrefix(text='')
        name = ''
        # todo count iterations
        while len(name) == 0 or County.objects.filter(name=name).exists():
            while SequenceMatcher(None, prefix.text.lower(), postfix.text.lower()).ratio() > 0.2:
                prefix = LocationNamePrefix.objects.order_by('?').first()
                postfix = LocationNamePostfix.objects.order_by('?').first()
            name = f'{prefix}{postfix}'
        return name
