import random

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver


def upload_location(instance, filename):
    return '%s/%s.png' % (instance.content_type, instance.id)


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

    class Meta:
        verbose_name_plural = 'Counties'

    def __str__(self):
        return self.name

    def get_primary_color_as_rgb(self):
        # todo könnte ich hier nicht direkt list() statt tuple() zurückgeben?
        return tuple(int(self.primary_color.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))


@receiver(pre_save, sender=County, dispatch_uid="county.set_primary_color")
def set_primary_color(sender, instance, **kwargs):
    if not instance.primary_color:
        instance.primary_color = "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])


class Map(models.Model):
    political_map = models.ImageField(upload_to=upload_location, null=True, blank=True)

    def __str__(self):
        return f'Map {self.id}'

    def is_fully_processed(self):
        return not self.map_dots.filter(county__isnull=True).exists()


class MapDot(models.Model):
    # TODO terrain types
    map = models.ForeignKey(Map, related_name='map_dots', on_delete=models.CASCADE)
    county = models.ForeignKey(County, related_name='map_dots', null=True, blank=True, on_delete=models.CASCADE)
    is_border = models.BooleanField(default=False)
    is_capital = models.BooleanField(default=False)
    coordinate_x = models.IntegerField()
    coordinate_y = models.IntegerField()

    def __str__(self):
        return f'Map-Dot {self.coordinate_x}/{self.coordinate_y} (Map {self.map.id})'

    def get_as_json(self):
        if self.is_capital:
            county_color = '#FFFFFF'
        else:
            county_color = self.county.primary_color if self.county else '#000000'
        json_str = f'"x": {self.coordinate_x}, "y": {self.coordinate_y}, "county": "{county_color}"'
        return '{' + json_str + '}'
