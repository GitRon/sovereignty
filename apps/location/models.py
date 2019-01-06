import random

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from apps.location.managers import MapDotManager, CountyManager


def upload_location(instance, filename):
    return '%s/%s.png' % (instance.content_type, instance.id)


class County(models.Model):
    NAME_LENGTH = 50

    name = models.CharField(max_length=NAME_LENGTH)
    primary_color = models.CharField(max_length=10, null=True, blank=True)
    target_size = models.PositiveIntegerField(default=0)
    savegame = models.ForeignKey('account.Savegame', related_name='counties', on_delete=models.CASCADE)

    objects = CountyManager()

    class Meta:
        verbose_name_plural = 'Counties'

    def __str__(self):
        return self.name

    def size(self):
        return self.map_dots.count()

    def get_primary_color_as_rgb(self):
        return list(int(self.primary_color.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))


@receiver(pre_save, sender=County, dispatch_uid="county.set_primary_color")
def set_primary_color(sender, instance, **kwargs):
    if not instance.primary_color:
        instance.primary_color = "#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)])


@receiver(pre_save, sender=County, dispatch_uid="county.calculate_target_size")
def calculate_target_size(sender, instance, **kwargs):
    if not instance.target_size:
        from apps.location.services.map import MapService
        ms = MapService()
        while instance.target_size < MapService.MIN_COUNTY_START_SPACE:
            instance.target_size = ms.calculate_county_target_size()


class Map(models.Model):
    DISPLAY_FACTOR = 4

    dimension = models.PositiveIntegerField(default=0, help_text='Height/Width of the map')
    political_map = models.ImageField(upload_to=upload_location, null=True, blank=True)
    savegame = models.OneToOneField('account.Savegame', related_name='map', on_delete=models.CASCADE)

    def __str__(self):
        return f'Map {self.id}'

    def is_fully_processed(self):
        return not self.map_dots.filter(county__isnull=True).exclude(is_water=True).exists() and self.political_map.name

    @property
    def display_size(self):
        return self.dimension * self.DISPLAY_FACTOR


class MapDot(models.Model):
    TERRAIN_FIELDS = 1
    TERRAIN_PLAINS = 2
    TERRAIN_SWAMP = 3
    TERRAIN_STEPPE = 4
    TERRAIN_WOODS = 5
    TERRAIN_HILLS = 6
    TERRAIN_MOUNTAINS = 7
    TERRAIN_CHOICES = (
        (TERRAIN_FIELDS, 'Fields'),
        (TERRAIN_PLAINS, 'Plains'),
        (TERRAIN_SWAMP, 'Swamp'),
        (TERRAIN_STEPPE, 'Steppe'),
        (TERRAIN_WOODS, 'Woods'),
        (TERRAIN_HILLS, 'Hills'),
        (TERRAIN_MOUNTAINS, 'Mountains'),
    )

    map = models.ForeignKey(Map, related_name='map_dots', db_index=True, on_delete=models.CASCADE)
    county = models.ForeignKey(County, related_name='map_dots', null=True, blank=True, db_index=True,
                               on_delete=models.CASCADE)
    is_water = models.BooleanField(default=True, db_index=True)
    terrain = models.PositiveIntegerField(choices=TERRAIN_CHOICES, null=True, blank=True, db_index=True)
    is_border = models.BooleanField(default=False)
    is_capital = models.BooleanField(default=False)
    coordinate_x = models.IntegerField(db_index=True)
    coordinate_y = models.IntegerField(db_index=True)

    objects = MapDotManager()

    def __str__(self):
        return f'Map-Dot {self.coordinate_x}/{self.coordinate_y} (Map {self.map.id})'

    def get_color(self):
        if self.is_water:
            color = [66, 134, 244]
        elif self.is_capital:
            color = [255, 255, 255]
        elif self.county:
            color = self.county.get_primary_color_as_rgb()
        else:
            color = [0, 0, 0]

        return color
