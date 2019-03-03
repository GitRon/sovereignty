from apps.military.models import Battle, BattleLogEntry
from apps.military.services.battlefield import BattlefieldService


class KiService(object):
    savegame = None
    battle = None
    bs = None

    def __init__(self, savegame):
        self.savegame = savegame
        self.battle = Battle.objects.get_current_battle(savegame=savegame)
        self.bs = BattlefieldService(self.savegame)

    def _move_fleeing_regiment(self, regiment, movement_on_x: int):
        if regiment.is_fleeing:
            regiment_coordinate_x = regiment.on_battlefield_tile.coordinate_x
            # Move one tile on the x-axes towards the starting side
            if (regiment.county == self.battle.attacker and regiment_coordinate_x > 0) or \
                    (regiment.county == self.battle.defender and regiment_coordinate_x < self.bs.BATTLEFIELD_SIZE - 1):
                self.bs.move_regiment(regiment, regiment_coordinate_x + movement_on_x,
                                      regiment.on_battlefield_tile.coordinate_y)
            # Remove regiment from battle
            else:
                tile = regiment.on_battlefield_tile
                tile.regiment = None
                tile.save()
                BattleLogEntry.objects.create(battle=self.battle, text=f'{regiment} fled the battlefield!')

    def process_fleeing_regiments(self):

        for regiment in self.battle.attacker_regiments.filter(on_battlefield_tile__isnull=False):
            self._move_fleeing_regiment(regiment, -1)

        for regiment in self.battle.defender_regiments.filter(on_battlefield_tile__isnull=False):
            self._move_fleeing_regiment(regiment, 1)
