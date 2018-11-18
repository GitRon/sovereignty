from random import randrange

from apps.location.models import County
from apps.naming.services import LocationNameService


class CountyService(object):

    @staticmethod
    def create_random_county():
        person = County.objects.create(
            name=LocationNameService.create_name(),
            area_type=randrange(County.AREA_TYPE_FIELDS, County.AREA_TYPE_WOODS),
        )

        return person
