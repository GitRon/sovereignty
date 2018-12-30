import os
import tempfile
import time
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
        )

        return person


class MapService(object):
    # Constants
    CANVAS_HEIGHT = 25
    CANVAS_WIDTH = 25
    LAND_WATER_RATIO = 0.65
    MIN_COUNTY_SIZE_DIVISOR = 50
    MIN_COUNTY_START_SPACE = 5
    BASE_COUNTY_SIZE_DIVISOR = 20
    BASE_COUNTY_SIZE_TYPES = 4

    # Class variables
    created_countries = 0
    canvas_map = None
    start_time = None

    """
    Base constant calculators
    """

    def get_map_size(self):
        return self.CANVAS_HEIGHT * self.CANVAS_WIDTH

    def get_min_county_size(self):
        return int((self.get_map_size() * self.LAND_WATER_RATIO) / self.MIN_COUNTY_SIZE_DIVISOR)

    def calculate_county_target_size(self):
        # Base size times big or small factor to shuffle county sizes
        return int((self.get_map_size() / self.BASE_COUNTY_SIZE_DIVISOR) *
                   (randrange(1, self.BASE_COUNTY_SIZE_TYPES * 2) / self.BASE_COUNTY_SIZE_TYPES))

    def get_max_iterations(self):
        return max(self.get_map_size() / 1000, 100)

    """
    Helper functions
    """

    def get_unassigned_dot(self) -> MapDot:
        return self.canvas_map.map_dots.filter(county__isnull=True).exclude(terrain=MapDot.TERRAIN_WATER) \
            .get_random()

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

        target_dot_amount = self.get_map_size()

        if self.canvas_map:
            return

        self.canvas_map = Map.objects.create()
        print(f'Created map {self.canvas_map.id}.')

        print(f'Start creating {target_dot_amount} map dots in database.')
        created_dots = 0
        bulk_insert_list = []
        for x in range(self.CANVAS_WIDTH):
            for y in range(self.CANVAS_HEIGHT):
                bulk_insert_list.append(MapDot(map=self.canvas_map, coordinate_x=x, coordinate_y=y))
                if created_dots % int(target_dot_amount / 50) == 0 and created_dots > 0:
                    MapDot.objects.bulk_create(bulk_insert_list)
                    bulk_insert_list = []
                    print(f'{created_dots}/{target_dot_amount} MapDots created.')

                created_dots += 1

        MapDot.objects.bulk_create(bulk_insert_list)
        print(f'{created_dots}/{target_dot_amount} MapDots created.')

        print('MapDot creation completed.')

    def populate_map_with_countries(self):

        county_list = []

        while self.get_unassigned_dot():
            left_dots = self.get_left_dots()
            left_dot_amount = left_dots.count()
            if left_dot_amount < self.get_min_county_size():
                self.assign_leftover_dots()

                break
            county = self.draw_county()
            if not county:
                print(f'No suitable space found for county capital. Stopping county creation.')
                self.assign_leftover_dots()
                break
            county_list.append(county)
            print(f'County {county} was created with {county.map_dots.count()} dots.')

        print(f'{len(county_list)} countries created.')

        # Logging
        for county in county_list:
            print(f'County {county.name}: {county.map_dots.count()} dots.')

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
            except OSError:
                pass
            print(f'Map #{self.canvas_map.id} created as PNG file.')
        else:
            print('Map PNG creation skipped for unittests.')

    def assign_leftover_dots(self):
        left_dots = self.get_left_dots()
        left_dot_amount = left_dots.count()

        left_dots = list(left_dots)

        print(f'Assigning {len(left_dots)} to neighboring counties.')

        while len(left_dots):
            for dot in left_dots:
                neighbor = self.get_adjacent_dots(dot).filter(county__isnull=False).get_random()
                if neighbor:
                    dot.county = neighbor.county
                    dot.save()
                    left_dots.remove(dot)
                    print(f'Leftover dot assigned. Still {len(left_dots)} dots to go.')

        print(f'{left_dot_amount} leftover dot(s) assigned to neighboring counties.')

    def draw_main_island(self):

        # Create dummy county for landmass
        land_county = County.objects.create(name='Main island')
        # Needs to be after the creation to override the pre-save-signal
        land_county.target_size = int(self.get_map_size() * self.LAND_WATER_RATIO)

        capital_dot = self.canvas_map.map_dots.filter(coordinate_x=self.CANVAS_WIDTH / 2,
                                                      coordinate_y=self.CANVAS_HEIGHT / 2).first()

        # Set capital and create county
        self.set_capital(land_county, capital_dot)
        self.extend_county_area(land_county, [capital_dot])

        created_dots = self.canvas_map.map_dots.filter(county=land_county)

        # Log island size
        print(f'Main island created with a size of {created_dots.count()}/{self.get_map_size()}.')

        # Remove dummy county and turn dots to terrain 'land'
        created_dots.update(terrain=MapDot.TERRAIN_LAND, county=None, is_capital=False)
        land_county.delete()

    def draw_county(self):
        county = CountyService.create_random_county()
        while County.objects.filter(map_dots__map=self.canvas_map, name=county.name).count() > 1:
            # todo make this more fancy
            county.name = LocationNameService.create_name()
            county.save()

        # Check if there is enough 'space' around the chosen capital dot
        current_iteration = 1
        max_iterations = self.get_max_iterations()
        free_surrounding_dots = 0
        capital_dot = None
        while current_iteration < max_iterations:
            capital_dot = self.get_unassigned_dot()
            if capital_dot:
                free_surrounding_dots = 0
                for dot in self.get_adjacent_dots(capital_dot):
                    if dot.county is None:
                        free_surrounding_dots += 1
            current_iteration += 1

        # If not enough space was found, indicate that map is 'full'
        if free_surrounding_dots < self.MIN_COUNTY_START_SPACE:
            return None

        self.set_capital(county, capital_dot)

        self.extend_county_area(county, [capital_dot])

        self.created_countries += 1

        return county

    def extend_county_area(self, county, dot_list):
        new_county_dots = []
        county_size = MapDot.objects.filter(map=self.canvas_map, county=county).count()

        # For each dot in the given list...
        for county_dot in dot_list:
            adjacent_dots = self.get_adjacent_dots(county_dot)
            # For each adjacent dot...
            for dot in adjacent_dots:
                # Determine if dot can become a new county dot...
                if not dot.county and county_size < self.determine_random_county_size(county):
                    # If so, set county in dot and add to newly added dot list
                    print(f'Extending county {county.name} with dot {dot}. '
                          f'County size: {county_size} dots for target size {county.target_size}.')
                    dot.county = county
                    dot.save()
                    county_size += 1
                    new_county_dots.append(dot)

        if len(new_county_dots):
            self.extend_county_area(county, new_county_dots)

    def determine_random_county_size(self, county):
        return randrange(0, max(self.get_min_county_size(), county.target_size))

    def create_map_image(self):

        data = numpy.zeros((self.CANVAS_WIDTH, self.CANVAS_HEIGHT, 3), dtype=numpy.uint8)

        for dot in self.canvas_map.map_dots.all():
            data[dot.coordinate_x, dot.coordinate_y] = dot.get_color()

        image = Image.fromarray(data)

        tmp = tempfile.NamedTemporaryFile()
        tmp_path = f'{tmp.name}.png'
        image.save(tmp_path)

        return tmp_path

    def create_world(self):

        # Set start time
        self.start_time = time.time()

        # Initialize map
        self.initialize_map()

        # Create main land island
        self.draw_main_island()

        # Create counties
        self.populate_map_with_countries()

        # Create and save PNG map file
        self.save_image_in_map()

        # Final logging
        duration_seconds = f'{(time.time() - self.start_time):.2f}'
        print(f'Map of size {self.get_map_size()} created in {duration_seconds}s.')
