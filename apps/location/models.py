from django.db import models


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

    def __str__(self):
        return self.name
