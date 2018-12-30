import random

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from apps.location.managers import MapDotManager


def upload_location(instance, filename):
    return '%s/%s.png' % (instance.content_type, instance.id)


class County(models.Model):
    name = models.CharField(max_length=50)
    primary_color = models.CharField(max_length=10, null=True, blank=True)
    target_size = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Counties'

    def __str__(self):
        return self.name

    def get_primary_color_as_rgb(self):
        return list(int(self.primary_color.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))


@receiver(pre_save, sender=County, dispatch_uid="county.set_primary_color")
def set_primary_color(sender, instance, **kwargs):
    if not instance.primary_color:
        instance.primary_color = "#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)])


@receiver(pre_save, sender=County, dispatch_uid="county.calculate_target_size")
def calculate_target_size(sender, instance, **kwargs):
    if not instance.target_size:
        from apps.location.services import MapService
        ms = MapService()
        while instance.target_size < MapService.MIN_COUNTY_START_SPACE:
            instance.target_size = ms.calculate_county_target_size()


class Map(models.Model):
    political_map = models.ImageField(upload_to=upload_location, null=True, blank=True)

    def __str__(self):
        return f'Map {self.id}'

    def is_fully_processed(self):
        return not self.map_dots.filter(county__isnull=True).exists()


class MapDot(models.Model):
    TERRAIN_WATER = 1
    TERRAIN_LAND = 2
    TERRAIN_CHOICES = (
        (TERRAIN_WATER, 'Water'),
        (TERRAIN_LAND, 'Land')
    )

    # AREA_TYPE_FIELDS = 1
    # AREA_TYPE_MOUNTAINS = 2
    # AREA_TYPE_SWAMP = 3
    # AREA_TYPE_WOODS = 4
    # AREA_TYPE_CHOICES = (
    #     (AREA_TYPE_FIELDS, 'Fields'),
    #     (AREA_TYPE_MOUNTAINS, 'Montains'),
    #     (AREA_TYPE_SWAMP, 'Swamp'),
    #     (AREA_TYPE_WOODS, 'Woods')
    # )

    map = models.ForeignKey(Map, related_name='map_dots', db_index=True, on_delete=models.CASCADE)
    county = models.ForeignKey(County, related_name='map_dots', null=True, blank=True, db_index=True,
                               on_delete=models.CASCADE)
    terrain = models.PositiveIntegerField(choices=TERRAIN_CHOICES, default=TERRAIN_WATER, db_index=True)
    is_border = models.BooleanField(default=False)
    is_capital = models.BooleanField(default=False)
    coordinate_x = models.IntegerField(db_index=True)
    coordinate_y = models.IntegerField(db_index=True)

    objects = MapDotManager()

    def __str__(self):
        return f'Map-Dot {self.coordinate_x}/{self.coordinate_y} (Map {self.map.id})'

    def get_color(self):
        if self.terrain == MapDot.TERRAIN_WATER:
            color = [66, 134, 244]
        elif self.is_capital:
            color = [255, 255, 255]
        elif self.county:
            color = self.county.get_primary_color_as_rgb()
        else:
            color = [0, 0, 0]

        return color
