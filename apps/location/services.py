from random import randrange

import numpy
from django.db.models import F

from apps.location.models import County, Map, MapDot
from apps.naming.services import LocationNameService


class CountyService(object):

    @staticmethod
    def create_random_county():
        person = County.objects.create(
            name=LocationNameService.create_name(),
            area_type=randrange(County.AREA_TYPE_FIELDS, County.AREA_TYPE_WOODS),
        )

        return person


class MapService(object):
    # Constants
    CANVAS_HEIGHT = 100
    CANVAS_WIDTH = 100
    BASE_COUNTY_AFFILIATION_MU = (CANVAS_HEIGHT * CANVAS_WIDTH) / 10
    BASE_COUNTY_AFFILIATION_SIGMA = (CANVAS_HEIGHT * CANVAS_WIDTH) / 20
    MIN_COUNTY_SIZE = (CANVAS_HEIGHT * CANVAS_WIDTH) / 50

    # Class variables
    created_countries = 0
    canvas_map = None

    def get_unassigned_dot(self) -> MapDot:
        return self.canvas_map.map_dots.filter(county__isnull=True).order_by('?').first()

    def get_left_dots(self):
        return self.canvas_map.map_dots.filter(county__isnull=True)

    @staticmethod
    def set_capital(county, dot):
        dot.is_capital = True
        dot.county = county
        dot.save()

    def get_adjacent_dots(self, dot: MapDot):
        return MapDot.objects.filter(map=self.canvas_map,
                                     coordinate_x__range=[dot.coordinate_x - 1, dot.coordinate_x + 1],
                                     coordinate_y__range=[dot.coordinate_y - 1, dot.coordinate_y + 1]) \
            .exclude(id=dot.id)

    def initialize_map(self):

        if self.canvas_map:
            return

        self.canvas_map = Map.objects.create()
        print(f'Created map {self.canvas_map.id}')

        print(f'Start creating {self.CANVAS_HEIGHT*self.CANVAS_WIDTH} map dots in database.')
        for x in range(self.CANVAS_WIDTH):
            for y in range(self.CANVAS_HEIGHT):
                MapDot.objects.create(map=self.canvas_map, coordinate_x=x, coordinate_y=y)

    def populate_map_with_countries(self):

        self.initialize_map()

        county_list = []

        while self.get_unassigned_dot():
            left_dots = self.get_left_dots()
            left_dot_amount = left_dots.count()
            if left_dot_amount < self.MIN_COUNTY_SIZE:
                left_dots.update(is_wasteland=True)
                print(f'{left_dot_amount} dot(s) turned to wasteland.')
                break
            county = self.draw_county()
            county_list.append(county)
            print(f'County {county} was created with {county.map_dots.count()} dots.')

        print(f'{len(county_list)} countries created.')

        return county_list

    def draw_county(self):
        county = CountyService.create_random_county()

        capital_dot = self.get_unassigned_dot()

        if capital_dot:
            self.set_capital(county, capital_dot)

            self.extend_county_area(county, [capital_dot])

            self.created_countries += 1

        return county

    def extend_county_area(self, county, dot_list):
        new_county_dots = []
        for county_dot in dot_list:
            adjacent_dots = self.get_adjacent_dots(county_dot)
            for dot in adjacent_dots:
                if not dot.county and self.decide_if_dot_belongs_to_county(county):
                    temp = MapDot.objects.filter(map=self.canvas_map, county=county).count()
                    print(f'Extending county {county.name} with dot {dot}. '
                          f'County size: {temp} dots.')
                    dot.county = county
                    dot.save()
                    new_county_dots.append(dot)

        if len(new_county_dots):
            self.extend_county_area(county, new_county_dots)

    def decide_if_dot_belongs_to_county(self, county):
        current_county_size = county.map_dots.count()
        target_size = numpy.random.normal(self.BASE_COUNTY_AFFILIATION_MU, self.BASE_COUNTY_AFFILIATION_SIGMA)
        return current_county_size < target_size
