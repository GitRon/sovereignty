from django.db import models

from apps.location.models import County
from apps.military.managers import BattleManager, BattlefieldTileManager
from apps.military.services.regiment_actions import RegimentActionService


class Battle(models.Model):
    year = models.PositiveIntegerField()
    done = models.BooleanField(default=False)
    round = models.PositiveIntegerField(default=1)
    attacker = models.ForeignKey(County, related_name='attacker_in_battles', on_delete=models.CASCADE)
    defender = models.ForeignKey(County, related_name='defender_in_battles', on_delete=models.CASCADE)
    losses_attacker = models.PositiveIntegerField(default=0)
    losses_defender = models.PositiveIntegerField(default=0)

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

    last_action_in_round = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.name} of {self.county}'

    @property
    def battlefield_actions(self):
        ras = RegimentActionService(self.county.savegame)
        available_actions = []

        if not self.turn_done:
            available_actions += ras.det_basic_movement(self)

        return available_actions

    @property
    def turn_done(self):
        current_battle = Battle.objects.get_current_battle(savegame=self.county.savegame)
        return True if current_battle.round <= self.last_action_in_round else False


class BattlefieldTile(models.Model):
    coordinate_x = models.IntegerField(db_index=True)
    coordinate_y = models.IntegerField(db_index=True)
    savegame = models.ForeignKey('account.Savegame', related_name='battlefield_tiles', on_delete=models.CASCADE)

    regiment = models.OneToOneField(Regiment, null=True, blank=True, related_name='on_battlefield_tile',
                                    on_delete=models.SET_NULL)

    objects = BattlefieldTileManager()

    def __str__(self):
        return f'Tile {self.coordinate_x}/{self.coordinate_y} (#{self.savegame.id})'

    @property
    def left_neighbour(self):
        return self.coordinate_x - 1, self.coordinate_y

    @property
    def right_neighbour(self):
        return self.coordinate_x + 1, self.coordinate_y

    @property
    def up_neighbour(self):
        return self.coordinate_x, self.coordinate_y - 1

    @property
    def down_neighbour(self):
        return self.coordinate_x, self.coordinate_y + 1
