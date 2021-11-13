from django.db import models

from apps.location.models import County
from apps.naming.services import LocationNameService


class CastleUpgrade(models.Model):
    name = models.CharField(max_length=75)
    building_cost = models.PositiveSmallIntegerField(default=0)
    maintenance_cost = models.PositiveSmallIntegerField(default=0)
    defense_bonus = models.SmallIntegerField(default=0)

    def __str__(self):
        return self.name


class Castle(models.Model):
    name = models.CharField(max_length=75)
    county = models.OneToOneField(County, related_name='castle', null=True, blank=True, on_delete=models.CASCADE)
    upgrades = models.ManyToManyField(CastleUpgrade, blank=True)

    # System attributes
    savegame = models.ForeignKey('account.Savegame', related_name='castles', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = LocationNameService.create_name(savegame=self.savegame)
        super().save(*args, **kwargs)


