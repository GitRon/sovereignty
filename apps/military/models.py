from django.db import models

from apps.location.models import County
from apps.military.managers import BattleManager, BattlefieldTileManager


class Battle(models.Model):
    year = models.PositiveIntegerField()
    done = models.BooleanField(default=False)
    attacker = models.ForeignKey(County, related_name='attacker_in_battles', on_delete=models.CASCADE)
    defender = models.ForeignKey(County, related_name='defender_in_battles', on_delete=models.CASCADE)
    losses_attacker = models.PositiveIntegerField()
    losses_defender = models.PositiveIntegerField()

    savegame = models.ForeignKey('account.Savegame', related_name='battles', on_delete=models.CASCADE)

    objects = BattleManager()

    def __str__(self):
        return f'{self.year} - {self.attacker} vs {self.defender}'


class RegimentType(models.Model):
    name = models.CharField(max_length=75)
    attack_value = models.PositiveSmallIntegerField()
    defense_value = models.PositiveSmallIntegerField()
    costs = models.PositiveSmallIntegerField()
    morale = models.PositiveSmallIntegerField()
    steps_per_turn = models.PositiveSmallIntegerField()
    is_long_range = models.BooleanField()
    long_range_tile_distance = models.PositiveSmallIntegerField(null=True, blank=True)
    default_type = models.BooleanField(default=False, help_text='There can only be one default type.')
    icon_path = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.name


class RegimentUpgrade(models.Model):
    name = models.CharField(max_length=75)
    bonus_attack = models.PositiveSmallIntegerField()
    bonus_defense = models.PositiveSmallIntegerField()
    bonus_morale = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.name


class Regiment(models.Model):
    DEFAULT_REGIMENT_SIZE = 100

    name = models.CharField(max_length=100)
    county = models.ForeignKey(County, related_name='regiments', on_delete=models.CASCADE)
    type = models.ForeignKey(RegimentType, related_name='regiments', on_delete=models.CASCADE)
    upgrades = models.ManyToManyField(RegimentUpgrade, related_name='regiments', blank=True)
    current_men = models.PositiveIntegerField(default=DEFAULT_REGIMENT_SIZE)

    def __str__(self):
        return f'{self.name} of {self.county}'


class BattlefieldTile(models.Model):
    coordinate_x = models.IntegerField(db_index=True)
    coordinate_y = models.IntegerField(db_index=True)
    savegame = models.ForeignKey('account.Savegame', related_name='battlefield_tiles', on_delete=models.CASCADE)

    regiment = models.ForeignKey(Regiment, null=True, blank=True, related_name='on_battlefield_tile',
                                 on_delete=models.SET_NULL)

    objects = BattlefieldTileManager()

    def __str__(self):
        return f'Tile {self.coordinate_x}/{self.coordinate_y} (#{self.savegame.id})'
