


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

    def initialize_battle(self):

        from apps.military.models import BattlefieldTile

        # Check if battlefield setup is correct
        if not self.is_battlefield_created():
            raise Exception('Battlefield tile setup not complete')

        # Clear battlefield
        self.battlefield.update(regiment=None)

        # Reset round action for all regiments
        self.battle.attacker.regiments.all().update(last_action_in_round=0)
        self.battle.defender.regiments.all().update(last_action_in_round=0)

        # Position troops
        # todo for now all armies of a country are fighting
        if self.me_attacking:
            armies = [
                {
                    'x': 0,
                    'regiments': self.battle.attacker.regiments.all(),
                    'role': 'attacker'
                },
                {
                    'x': BattlefieldService.BATTLEFIELD_SIZE - 1,
                    'regiments': self.battle.defender.regiments.all(),
                    'role': 'defender'
                }
            ]

        else:
            armies = [
                {
                    'x': 0,
                    'regiments': self.battle.defender.regiments.all(),
                    'role': 'defender'
                },
                {
                    'x': BattlefieldService.BATTLEFIELD_SIZE - 1,
                    'regiments': self.battle.attacker.regiments.all(),
                    'role': 'attacker'
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