from apps.account.models import Savegame
from apps.location.models import County
from apps.naming.services import LocationNameService


class CreateCountyService(object):

    @staticmethod
    def create_random_county(savegame: Savegame):
        county = County.objects.create(
            name=LocationNameService.create_name(savegame),
            savegame=savegame
        )

        return county
