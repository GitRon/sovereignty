import os

from django.db.models import Count
from django.test import TestCase

from apps.account.models import Savegame
from apps.location.models import MapDot, Map
from apps.location.services.country import CreateCountyService
from apps.location.services.map import MapService


class MapServiceTest(TestCase):
    fixtures = ['initial_data']
    TEST_CANVAS_HEIGHT = 10
    TEST_CANVAS_WIDTH = 10

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.ms = MapService()
        cls.ms.CANVAS_HEIGHT = cls.TEST_CANVAS_HEIGHT
        cls.ms.CANVAS_WIDTH = cls.TEST_CANVAS_WIDTH
        cls.ms.initialize_map()

        # Create main island
        cls.ms.draw_main_island()

        # Additional services and objects
        cls.cs = CreateCountyService()

    def setUp(self):
        pass

    def test_initialize_map(self):
        self.assertEqual(Map.objects.count(), 1)
        self.assertEqual(MapDot.objects.count(), self.ms.CANVAS_WIDTH * self.ms.CANVAS_HEIGHT)

    def tet_created_main_island(self):
        self.assertGreaterEqual(MapDot.objects.filter(is_water=False).count(), 1)

    def test_get_adjacent_dots_in_the_middle(self):
        dot = MapDot.objects.filter(coordinate_x=int(self.ms.CANVAS_WIDTH / 2),
                                    coordinate_y=int(self.ms.CANVAS_HEIGHT / 2)).first()
        self.assertEquals(self.ms.get_adjacent_dots(dot, False).count(), 8)

    def test_get_adjacent_dots_at_the_side(self):
        dot = MapDot.objects.filter(coordinate_x=int(self.ms.CANVAS_WIDTH / 2),
                                    coordinate_y=0).first()
        self.assertEquals(self.ms.get_adjacent_dots(dot, False).count(), 5)

    def test_get_adjacent_dots_in_the_corner(self):
        dot = MapDot.objects.filter(coordinate_x=self.ms.CANVAS_WIDTH - 1,
                                    coordinate_y=self.ms.CANVAS_WIDTH - 1).first()
        self.assertEquals(self.ms.get_adjacent_dots(dot, False).count(), 3)

    def test_get_unassigned_dot_regular(self):
        self.assertIsInstance(self.ms.get_unassigned_dot(), MapDot)

    def test_get_unassigned_dot_with_water(self):
        county = self.cs.create_random_county(self.ms.canvas_map.savegame)
        self.ms.canvas_map.map_dots.update(county=county)
        self.assertEqual(self.ms.get_unassigned_dot(), None)

    def test_get_unassigned_dot_all_gone(self):
        county = self.cs.create_random_county(self.ms.canvas_map.savegame)
        MapDot.objects.filter(map=self.ms.canvas_map).update(county=county)
        self.assertEquals(self.ms.get_unassigned_dot(), None)

    def test_assign_leftover_dots(self):
        county = self.cs.create_random_county(self.ms.canvas_map.savegame)
        self.ms.canvas_map.map_dots.filter(coordinate_x=0).update(county=county)
        self.ms.assign_leftover_dots()
        self.assertEquals(self.ms.get_left_dots().count(), 0)

    def test_draw_county(self):
        self.ms.created_countries = 0
        county = self.ms.draw_county()
        self.assertEquals(self.ms.created_countries, 1)
        self.assertGreaterEqual(MapDot.objects.filter(map=self.ms.canvas_map, county=county).count(), 1)

    def test_not_single_dot_counties(self):
        self.ms.populate_map_with_countries()
        self.assertEqual(
            MapDot.objects.filter(map=self.ms.canvas_map).values('county').annotate(Count('id')).order_by().filter(
                county__isnull=False, id__count=0).count(), 0)

    def test_populate_map_with_countries(self):
        county_list = self.ms.populate_map_with_countries()
        self.assertGreaterEqual(len(county_list), 1)
        for county in county_list:
            self.assertGreaterEqual(MapDot.objects.filter(map=self.ms.canvas_map, county=county).count(), 1)

    def test_create_map_image_as_tmp_file(self):
        self.ms.draw_county()
        tmp_image_path = self.ms.create_map_image()
        self.assertTrue(os.path.isfile(tmp_image_path), True)

    def test_no_leftover_dots(self):
        self.ms.create_world()
        self.assertEqual(self.ms.canvas_map.map_dots.filter(county__isnull=True, is_water=False).count(), 0)

    def test_single_capital_per_county(self):
        self.ms.populate_map_with_countries()
        self.assertEqual(
            MapDot.objects.filter(map=self.ms.canvas_map, is_capital=True).annotate(
                Count('id')).values('county').order_by().filter(
                county__isnull=False, id__count=0).count(), 0)

    def test_water_has_no_country(self):
        self.assertEqual(MapDot.objects.filter(is_water=True, county__isnull=False).count(), 0)
