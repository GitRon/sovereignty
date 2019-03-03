

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

    def get_enemies_in_shooting_range(self, regiment):
        """
        Finds all tiles with enemies on them which can be shot at with a crossbow or bow
        """
        return self.get_enemies_in_distance(regiment, 2).exclude(id__in=self.get_enemies_in_distance(regiment))

    def initialize_battle(self, attacking_regiments, defending_regiments):

        from apps.military.models import BattlefieldTile

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

        # Position troops
        armies = [
            {
                'x': 0,
                'regiments': attacking_regiments,
                'role': 'attacker'
            },
            {
                'x': BattlefieldService.BATTLEFIELD_SIZE - 1,
                'regiments': defending_regiments,
                'role': 'defender'
            }
        ]

        for army in armies:
            # todo build a test for this! kind of fragile...
            first_position = int((self.BATTLEFIELD_SIZE - 1) / army['regiments'].count())

            counter = 0
            for regiment in army['regiments']:
                tile = None
                tile_counter = 0
                y = first_position + counter
                while not tile:
                    if self.me_attacking and army['role'] == 'attacker':
                        x = army['x'] + tile_counter
                    else:
                        x = army['x'] - tile_counter

                    tile = BattlefieldTile.objects.get_visible(
                        savegame=self.savegame).filter(coordinate_x=x,
                                                       coordinate_y=y).exclude(regiment__isnull=False).first()

                    tile_counter += 1

                tile.regiment = regiment
                tile.save()

                if counter < BattlefieldService.BATTLEFIELD_SIZE - 1:
                    counter += 1
                else:
                    counter = 0

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
