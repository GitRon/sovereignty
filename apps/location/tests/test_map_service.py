from django.test import TestCase

from apps.location.models import MapDot, Map
from apps.location.services import MapService, CountyService


class MapServiceTest(TestCase):
    fixtures = ['initial_data']

    def setUp(self):
        self.ms = MapService()
        self.ms.initialize_map()

        self.cs = CountyService()

    def test_initialize_map(self):
        self.assertEqual(Map.objects.count(), 1)
        self.assertEqual(MapDot.objects.count(), self.ms.CANVAS_WIDTH * self.ms.CANVAS_HEIGHT)

    def test_get_adjacent_dots_in_the_middle(self):
        dot = MapDot.objects.filter(coordinate_x=int(self.ms.CANVAS_WIDTH / 2),
                                    coordinate_y=int(self.ms.CANVAS_HEIGHT / 2)).first()
        self.assertEquals(self.ms.get_adjacent_dots(dot).count(), 8)

    def test_get_adjacent_dots_at_the_side(self):
        dot = MapDot.objects.filter(coordinate_x=int(self.ms.CANVAS_WIDTH / 2),
                                    coordinate_y=0).first()
        self.assertEquals(self.ms.get_adjacent_dots(dot).count(), 5)

    def test_get_adjacent_dots_in_the_corner(self):
        dot = MapDot.objects.filter(coordinate_x=self.ms.CANVAS_WIDTH - 1,
                                    coordinate_y=self.ms.CANVAS_WIDTH - 1).first()
        self.assertEquals(self.ms.get_adjacent_dots(dot).count(), 3)

    def test_get_unassigned_dot_regular(self):
        self.assertIsInstance(self.ms.get_unassigned_dot(), MapDot)

    def test_get_unassigned_dot_all_gone(self):
        county = self.cs.create_random_county()
        MapDot.objects.filter(map=self.ms.canvas_map).update(county=county)
        self.assertEquals(self.ms.get_unassigned_dot(), None)

    def test_draw_county(self):
        county = self.ms.draw_county()
        self.assertEquals(self.ms.created_countries, 1)
        self.assertGreaterEqual(MapDot.objects.filter(map=self.ms.canvas_map, county=county).count(), 1)

    def test_populate_map_with_countries(self):
        county_list = self.ms.populate_map_with_countries()
        self.assertGreaterEqual(len(county_list), 1)
        for county in county_list:
            self.assertGreaterEqual(MapDot.objects.filter(map=self.ms.canvas_map, county=county).count(), 1)
