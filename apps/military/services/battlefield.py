from django.db.models import Q


class BattlefieldService(object):
    BATTLEFIELD_SIZE = 10

    savegame = None
    battle = None
    battlefield = None

    def __init__(self, savegame):
        from apps.military.models import BattlefieldTile, Battle

        self.savegame = savegame
        self.battle = Battle.objects.get_current_battle(savegame=savegame)

        if not self.battle:
            raise Exception('No current battle found.')

        self.battlefield = BattlefieldTile.objects.get_visible(savegame=self.savegame)
        self.me_attacking = self.battle.attacker == self.savegame.current_county

    def is_battlefield_created(self):
        """
        Checks if battlefield has been set up
        :return:
        """
        return self.battlefield.exists()

    def create_battlefield_tiles(self):
        """
        Create battlefield tiles for savegame
        :return:
        """
        from apps.military.models import BattlefieldTile

        for x in range(0, BattlefieldService.BATTLEFIELD_SIZE):
            for y in range(0, BattlefieldService.BATTLEFIELD_SIZE):
                BattlefieldTile.objects.get_or_create(
                    coordinate_x=x,
                    coordinate_y=y,
                    savegame=self.savegame
                )

    def get_current_battlefield(self):

        from apps.military.models import Battle

        if not self.battle:
            return False

        if Battle.objects.get_visible(savegame=self.savegame).filter(done=False).count() > 1:
            raise Exception('Too many active battles found.')

        data = {
            'battle': self.battle,
            'battlefield_tiles': self.battlefield
        }

        return data

    def get_tile(self, x, y):
        qs = self.battlefield.filter(coordinate_x=x, coordinate_y=y).first()
        if not qs:
            raise Exception(f'Queried invalid battlefied tile {x}/{y}.')
        return qs

    def get_neighbours_in_distance(self, x: int, y: int, distance: int = 1):
        """
        Return all neighbouring tiles in the range of `distance`
        """
        min_x = max(x - distance, 0)
        min_y = max(y - distance, 0)
        max_x = min(x + distance, self.BATTLEFIELD_SIZE - 1)
        max_y = min(y + distance, self.BATTLEFIELD_SIZE - 1)
        return self.battlefield.filter(coordinate_x__range=[min_x, max_x], coordinate_y__range=[min_y, max_y]) \
            .exclude(coordinate_x=x, coordinate_y=y)

    def get_enemies_in_distance(self, regiment, distance: int = 1):
        """
        Returns all tiles where an enemy stands in the given `distance`
        """
        x, y = regiment.get_position()
        neighbour_tiles = self.get_neighbours_in_distance(x, y, distance)

        return neighbour_tiles.filter(regiment__isnull=False).exclude(regiment__county=regiment.county)

    def get_neighbours_in_direct_plus_range(self, x: int, y: int):
        """
        Get all direct neighbours which are not on a diagonal field (plus-shaped area)
        """
        return self.battlefield.filter(Q(coordinate_x=x - 1, coordinate_y=y) |
                                       Q(coordinate_x=x + 1, coordinate_y=y) |
                                       Q(coordinate_x=x, coordinate_y=y - 1) |
                                       Q(coordinate_x=x, coordinate_y=y + 1))

    def get_enemies_in_direct_plus_range(self, regiment):
        """
        Returns all tiles where an enemy stands in the plus-shaped area around `regiment`
        """
        x, y = regiment.get_position()
        neighbour_tiles = self.get_neighbours_in_direct_plus_range(x, y)

        return neighbour_tiles.filter(regiment__isnull=False).exclude(regiment__county=regiment.county)

    def get_allies_in_direct_plus_range(self, regiment):
        """
        Returns all tiles where an ally stands in the plus-shaped area around `regiment`
        """
        x, y = regiment.get_position()
        neighbour_tiles = self.get_neighbours_in_direct_plus_range(x, y)

        return neighbour_tiles.filter(regiment__isnull=False, regiment__county=regiment.county)

    def get_enemies_in_shooting_range(self, regiment):
        """
        Finds all tiles with enemies on them which can be shot at with a crossbow or bow
        """
        return self.get_enemies_in_distance(regiment, 2).exclude(id__in=self.get_enemies_in_distance(regiment))

    def _lineup_troops(self, regiment_list, distance_weight_attribute):
        # todo write test
        from apps.military.models import BattlefieldTile

        weighted_regiment_list = []
        for regiment in regiment_list:
            weighted_regiment_list.append({'regiment': regiment, 'weight': regiment.lineup_weight})

        weighted_regiment_list = sorted(weighted_regiment_list, key=lambda k: k['weight'])

        for data in weighted_regiment_list:
            tile = BattlefieldTile.objects.get_visible(savegame=self.savegame).filter(regiment__isnull=True) \
                .order_by(distance_weight_attribute).first()
            tile.regiment = data['regiment']
            tile.save()

    def initialize_battle(self, attacking_regiments, defending_regiments):

        # Log which regiments are fighting this battle
        self.battle.attacker_regiments.set(attacking_regiments)
        self.battle.defender_regiments.set(defending_regiments)
        self.battle.save()

        # Check if battlefield setup is correct
        if not self.is_battlefield_created():
            raise Exception('Battlefield tile setup not complete')

        # Clear battlefield
        self.battlefield.update(regiment=None)

        # Reset round action for all regiments
        attacking_regiments.update(last_action_in_round=0)
        defending_regiments.update(last_action_in_round=0)

        # Line up troops
        self._lineup_troops(attacking_regiments, 'distance_weight_attacker')
        self._lineup_troops(defending_regiments, 'distance_weight_defender')

        print('Battlefield setup.')

    def move_regiment(self, regiment, x: int, y: int):

        # Check if tile is taken
        if self.battlefield.filter(coordinate_x=x, coordinate_y=y, regiment__isnull=False) \
                .exclude(regiment=regiment).exists():
            raise Exception(f'Cannot move regiment to coordinates {x}/{y} because tile is already taken.')

        # Remove regiment from previous tile
        self.battlefield.filter(regiment=regiment).update(regiment=None)

        # Set regiment to new tile
        self.battlefield.filter(coordinate_x=x, coordinate_y=y).update(regiment=regiment)

    def switch_regiments(self, regiment_active, x: int, y: int):

        target_tile = self.battlefield.filter(coordinate_x=x, coordinate_y=y, regiment__isnull=False).first()

        # Check if tile is taken
        if not self.battlefield.filter(regiment=regiment_active).exists() or not target_tile:
            raise Exception('Cannot switch regiments because they are not both on the battlefield.')

        regiment_passive = target_tile.regiment

        # Remove regiment from previous tile
        self.battlefield.filter(regiment=regiment_passive).update(regiment=None)
        self.battlefield.filter(regiment=regiment_active).update(regiment=regiment_passive)

        # Set regiment to new tile
        self.battlefield.filter(coordinate_x=x, coordinate_y=y).update(regiment=regiment_active)
