from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from apps.location.models import County
from apps.military.managers import BattleManager, BattlefieldTileManager
from apps.military.services.regiment_actions import RegimentActionService


class Battle(models.Model):
    year = models.PositiveIntegerField()
    done = models.BooleanField(default=False)
    round = models.PositiveIntegerField(default=1)
    attacker = models.ForeignKey(County, related_name='attacker_in_battles', on_delete=models.CASCADE)
    attacker_regiments = models.ManyToManyField("Regiment", related_name='attacker_in_battles')
    defender = models.ForeignKey(County, related_name='defender_in_battles', on_delete=models.CASCADE)
    defender_regiments = models.ManyToManyField("Regiment", related_name='defender_in_battles')
    # todo do i need this or can i extend the battle log to get the value from there?
    losses_attacker = models.PositiveIntegerField(default=0)
    losses_defender = models.PositiveIntegerField(default=0)

    savegame = models.ForeignKey('account.Savegame', related_name='battles', on_delete=models.CASCADE)

    objects = BattleManager()

    def __str__(self):
        return f'{self.year} - {self.attacker} vs {self.defender}'


class BattleLogEntry(models.Model):
    battle = models.ForeignKey(Battle, related_name='logs', on_delete=models.CASCADE)
    text = models.TextField()

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.text


class RegimentType(models.Model):
    name = models.CharField(max_length=75)
    attack_value = models.PositiveSmallIntegerField()
    defense_value = models.PositiveSmallIntegerField()
    costs = models.PositiveSmallIntegerField()
    morale = models.PositiveSmallIntegerField()
    steps_per_turn = models.PositiveSmallIntegerField()
    is_long_range = models.BooleanField()
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
    BORDER_MORALE = 10

    name = models.CharField(max_length=100)
    county = models.ForeignKey(County, related_name='regiments', on_delete=models.CASCADE)
    type = models.ForeignKey(RegimentType, related_name='regiments', on_delete=models.CASCADE)
    upgrades = models.ManyToManyField(RegimentUpgrade, related_name='regiments', blank=True)
    current_men = models.PositiveIntegerField(default=DEFAULT_REGIMENT_SIZE)
    current_morale = models.SmallIntegerField(default=0)

    last_action_in_round = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.name} of {self.county}'

    @property
    def attack_value(self):
        attack_value = self.type.attack_value
        for upgrade in self.upgrades.all():
            attack_value += upgrade.bonus_attack
        return attack_value

    @property
    def defense_value(self):
        defense_value = self.type.defense_value
        for upgrade in self.upgrades.all():
            defense_value += upgrade.bonus_attack
        return defense_value

    @property
    def battlefield_actions(self):
        ras = RegimentActionService(self.county.savegame)
        available_actions = []

        if not (self.turn_done or self.is_fleeing):
            # Movement
            available_actions += ras.det_basic_movement(self)
            available_actions += ras.det_switch(self)
            # Fighting
            available_actions += ras.det_fight_melee(self)
            available_actions += ras.det_fight_long_range(self)

        return available_actions

    @property
    def turn_done(self):
        current_battle = Battle.objects.get_current_battle(savegame=self.county.savegame)
        return True if current_battle.round <= self.last_action_in_round else False

    @property
    def is_fleeing(self):
        return self.current_morale < self.BORDER_MORALE

    @property
    def on_battlefield(self):
        return self.on_battlefield_tile

    @property
    def lineup_weight(self):
        return pow((self.defense_value * 0.1 + self.attack_value) * pow(self.type.steps_per_turn, 0.25), -1)

    def get_position(self):
        if self.on_battlefield_tile:
            x = self.on_battlefield_tile.coordinate_x
            y = self.on_battlefield_tile.coordinate_y
            return x, y


@receiver(post_save, sender=Regiment, dispatch_uid="regiment.set_initial_morale_from_type")
def set_initial_morale_from_type(sender, instance, created, **kwargs):
    if created:
        instance.morale = instance.type.morale
        instance.save()


class BattlefieldTile(models.Model):
    coordinate_x = models.IntegerField(db_index=True)
    coordinate_y = models.IntegerField(db_index=True)
    savegame = models.ForeignKey('account.Savegame', related_name='battlefield_tiles', on_delete=models.CASCADE)

    regiment = models.OneToOneField(Regiment, null=True, blank=True, related_name='on_battlefield_tile',
                                    on_delete=models.SET_NULL)
    distance_weight_attacker = models.FloatField('Distance weight', default=0,
                                                 help_text='Weighted distance on attacker side')
    distance_weight_defender = models.FloatField('Distance weight', default=0,
                                                 help_text='Weighted distance on defender side')

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

    def _calculate_distance_weight_attacker(self):
        from apps.military.services.battlefield import BattlefieldService
        return abs(((BattlefieldService.BATTLEFIELD_SIZE - 1) / 2) - self.coordinate_y) + pow(self.coordinate_x, 2)

    def _calculate_distance_weight_defender(self):
        from apps.military.services.battlefield import BattlefieldService
        return abs(((BattlefieldService.BATTLEFIELD_SIZE - 1) / 2) - self.coordinate_y) + \
               pow(BattlefieldService.BATTLEFIELD_SIZE - 1 - self.coordinate_x, 2)


@receiver(pre_save, sender=BattlefieldTile, dispatch_uid="battlefieldtile.set_base_distance_weight")
def set_base_distance_weight(sender, instance, **kwargs):
    if not instance.distance_weight_attacker:
        instance.distance_weight_attacker = instance._calculate_distance_weight_attacker()
        instance.distance_weight_defender = instance._calculate_distance_weight_defender()
