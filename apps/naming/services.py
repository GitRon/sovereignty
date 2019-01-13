import random
from difflib import SequenceMatcher
from random import randrange

from apps.account.models import Savegame
from apps.location.models import County
from apps.naming.models import LocationNameSuffix, LocationNamePrefix, PersonName


class PersonNameService(object):
    PROBABILITY_OF_MIDDLE_NAME = 0.33

    @staticmethod
    def get_name(gender, name_exclude_list=None):
        if not name_exclude_list:
            name_exclude_list = []

        qs = PersonName.objects.filter(gender=gender)
        if name_exclude_list:
            qs = qs.exclude(name__in=name_exclude_list)
        return qs.get_random()

    def get_middle_name(self, gender, name_exclude_list=None):
        # Middle name
        if random.random() < self.PROBABILITY_OF_MIDDLE_NAME:
            return self.get_name(gender, name_exclude_list)

        return None


class LocationNameService(object):
    MAX_ITERATIONS = 10000
    STRING_SIMILARITY_FACTOR = 0.5

    @staticmethod
    def create_name(savegame: Savegame):
        prefix = suffix = LocationNamePrefix(text='')
        amount_prefixes = LocationNamePrefix.objects.count()
        amount_suffixes = LocationNameSuffix.objects.count()
        name = ''
        iteration = 0
        while len(name) == 0 or County.objects.filter(name=name, savegame=savegame).exists():
            iteration += 1
            if iteration > LocationNameService.MAX_ITERATIONS:
                raise Exception('County-Namepool is empty. Add more names!')
            while SequenceMatcher(None, prefix.text.lower(), suffix.text.lower()).ratio() > \
                    LocationNameService.STRING_SIMILARITY_FACTOR:
                prefix = LocationNamePrefix.objects.all()[randrange(0, amount_prefixes)]
                suffix = LocationNameSuffix.objects.all()[randrange(0, amount_suffixes)]
            name = f'{prefix}{suffix}'
        return name
