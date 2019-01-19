from django.db.models import Sum

from apps.account.models import Savegame
from apps.dynasty.models import Person
from apps.dynasty.services import DynastyService
from apps.messaging.services import MessageService


class FinishYearService(object):

    def __init__(self, savegame_id: int):
        self.savegame = Savegame.objects.get(id=savegame_id)
        self.ms = MessageService(self.savegame)
        self.ds = DynastyService(self.savegame)

    def process(self, ):
        # Execute over-year-logic
        self._change_savegame()
        self._gather_resources()
        self._grim_reaper()

    def _change_savegame(self):
        self.savegame.current_year += 1
        self.savegame.save()

    def _gather_resources(self):
        county = self.savegame.playing_as.home_county
        resource_gold = self.savegame.map.map_dots.filter(county=county).aggregate(sum_gold=Sum('gold'))
        resource_manpower = self.savegame.map.map_dots.filter(county=county).aggregate(sum_manpower=Sum('manpower'))

        county.gold += resource_gold['sum_gold']
        county.manpower += resource_manpower['sum_manpower']
        county.save()

    def _grim_reaper(self):

        # Get all living persons
        person_list = Person.objects.get_visible(savegame=self.savegame).filter(death_year__isnull=True)

        for person in person_list:
            # todo this kills basically everyone...
            target_death_year = self.ds.calculate_year_of_death(person.birth_year)
            if target_death_year <= self.savegame.current_year:
                person.death_year = self.savegame.current_year
                person.save()
                self.ms.person_dies_natural_cause(person)
