import random

from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save
from django.dispatch import receiver


class County(models.Model):
    AREA_TYPE_FIELDS = 1
    AREA_TYPE_MOUNTAINS = 2
    AREA_TYPE_SWAMP = 3
    AREA_TYPE_WOODS = 4
    AREA_TYPE_CHOICES = (
        (AREA_TYPE_FIELDS, 'Fields'),
        (AREA_TYPE_MOUNTAINS, 'Montains'),
        (AREA_TYPE_SWAMP, 'Swamp'),
        (AREA_TYPE_WOODS, 'Woods')
    )

    name = models.CharField(max_length=50)
    area_type = models.PositiveSmallIntegerField(choices=AREA_TYPE_CHOICES)
    primary_color = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return self.name


@receiver(pre_save, sender=County, dispatch_uid="county.set_primary_color")
def set_primary_color(sender, instance, **kwargs):
    if not instance.primary_color:
        instance.primary_color = "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])


class Map(models.Model):

    def __str__(self):
        return f'Map {self.id}'

    def is_fully_processed(self):
        return self.map_dots.filter(Q(county__isnull=True) | Q(is_wasteland=False)).exists()


class MapDot(models.Model):
    map = models.ForeignKey(Map, related_name='map_dots', on_delete=models.CASCADE)
    county = models.ForeignKey(County, related_name='map_dots', null=True, blank=True, on_delete=models.CASCADE)
    is_border = models.BooleanField(default=False)
    is_capital = models.BooleanField(default=False)
    is_wasteland = models.BooleanField(default=False)
    coordinate_x = models.IntegerField()
    coordinate_y = models.IntegerField()

    def __str__(self):
        return f'Map-Dot {self.coordinate_x}/{self.coordinate_y} (Map {self.map.id})'

    def get_as_json(self):
        county_color = self.county.primary_color if self.county else '#000000'
        json_str = f'"x": {self.coordinate_x}, "y": {self.coordinate_y}, "county": "{county_color}"'
        return '{' + json_str + '}'
