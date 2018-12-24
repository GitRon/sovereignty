import os
import tempfile
from random import randrange
from shutil import copyfile

import numpy
from PIL import Image
from django.conf import settings

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
    CANVAS_HEIGHT = 200
    CANVAS_WIDTH = 200
    MIN_COUNTY_SIZE_DIVISOR = 50
    BASE_COUNTY_AFFILIATION_MU_DIVISOR = 10
    BASE_COUNTY_AFFILIATION_SIGMA_DIVISOR = 20

    # Class variables
    created_countries = 0
    canvas_map = None

    """
    Base constant calculators
    """

    def get_min_county_size(self):
        return (self.CANVAS_HEIGHT * self.CANVAS_WIDTH) / self.MIN_COUNTY_SIZE_DIVISOR

    def get_base_county_affiliation_mu(self):
        return (self.CANVAS_HEIGHT * self.CANVAS_WIDTH) / self.BASE_COUNTY_AFFILIATION_MU_DIVISOR

    def get_base_county_affiliation_sigma(self):
        return (self.CANVAS_HEIGHT * self.CANVAS_WIDTH) / self.BASE_COUNTY_AFFILIATION_SIGMA_DIVISOR

    """
    Helper functions
    """

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

        target_dot_amount = self.CANVAS_HEIGHT * self.CANVAS_WIDTH

        if self.canvas_map:
            return

        self.canvas_map = Map.objects.create()
        print(f'Created map {self.canvas_map.id}.')

        print(f'Start creating {target_dot_amount} map dots in database.')
        created_dots = 0
        for x in range(self.CANVAS_WIDTH):
            for y in range(self.CANVAS_HEIGHT):
                if created_dots % int(target_dot_amount / 50) == 0 and created_dots > 0:
                    print(f'{created_dots}/{target_dot_amount} MapDots created.')
                MapDot.objects.create(map=self.canvas_map, coordinate_x=x, coordinate_y=y)
                created_dots += 1

        print('MapDot creation completed.')

    def populate_map_with_countries(self):

        self.initialize_map()

        county_list = []

        while self.get_unassigned_dot():
            left_dots = self.get_left_dots()
            left_dot_amount = left_dots.count()
            if left_dot_amount < self.get_min_county_size():
                self.assign_leftover_dots()

                break
            county = self.draw_county()
            county_list.append(county)
            print(f'County {county} was created with {county.map_dots.count()} dots.')

        print(f'{len(county_list)} countries created.')

        # Create and save PNG map file
        self.save_image_in_map()

        return county_list

    def save_image_in_map(self):
        if not settings.IS_TESTING:
            tmp_image_path = self.create_map_image()
            target_path = f'/maps/{self.canvas_map.id}.png'
            absolute_target_path = os.path.join(str(settings.APPS_DIR), f'media{target_path}')
            try:
                os.makedirs(os.path.dirname(absolute_target_path))
            except FileExistsError:
                pass
            copyfile(tmp_image_path, absolute_target_path)
            self.canvas_map.political_map = target_path
            self.canvas_map.save()
            try:
                os.unlink(tmp_image_path)
            except Exception:
                pass
            print(f'Map created as PNG file.')
        else:
            print('Map PNG creation skipped for unittests.')

    def assign_leftover_dots(self):
        left_dots = self.get_left_dots()
        left_dot_amount = left_dots.count()

        left_dots = list(left_dots)
        while len(left_dots):
            for dot in left_dots:
                neighbor = self.get_adjacent_dots(dot).filter(county__isnull=False).order_by('?').first()
                if neighbor:
                    dot.county = neighbor.county
                    dot.save()
                    left_dots.remove(dot)

        print(f'{left_dot_amount} leftover dot(s) assigned to neighboring counties.')

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
        target_size = numpy.random.normal(self.get_base_county_affiliation_mu(),
                                          self.get_base_county_affiliation_sigma())
        return current_county_size < target_size

    def create_map_image(self):

        data = numpy.zeros((self.CANVAS_WIDTH, self.CANVAS_HEIGHT, 3), dtype=numpy.uint8)

        for dot in self.canvas_map.map_dots.all():
            if dot.is_capital:
                color = [255, 255, 255]
            elif dot.county:
                color = list(dot.county.get_primary_color_as_rgb())
            else:
                color = [0, 0, 0]
            data[dot.coordinate_x, dot.coordinate_y] = color

        image = Image.fromarray(data)

        tmp = tempfile.NamedTemporaryFile()
        tmp_path = f'{tmp.name}.png'
        image.save(tmp_path)

        return tmp_path
