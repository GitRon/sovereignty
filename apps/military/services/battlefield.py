from apps.military.models import BattlefieldTile, Battle


class BattlefieldService(object):
    BATTLEFIELD_SIZE = 10

    savegame = None
    battle = None

    def __init__(self, savegame):
        self.savegame = savegame
        self.battle = Battle.objects.get_visible(savegame=self.savegame).filter(done=False).first()
        self.me_attacking = self.battle.attacker == self.savegame.current_county

    def is_battlefield_created(self):
        """
        Checks if battlefield has been set up
        :return:
        """
        return BattlefieldTile.objects.get_visible(savegame=self.savegame).exists()

    def create_battlefield_tiles(self):
        """
        Create battlefield tiles for savegame
        :return:
        """
        for x in range(0, BattlefieldService.BATTLEFIELD_SIZE):
            for y in range(0, BattlefieldService.BATTLEFIELD_SIZE):
                BattlefieldTile.objects.get_or_create(
                    coordinate_x=x,
                    coordinate_y=y,
                    savegame=self.savegame
                )

    def get_current_battlefield(self):

        if not self.battle:
            return False

        if Battle.objects.get_visible(savegame=self.savegame).filter(done=False).count() > 1:
            raise Exception('Too many active battles found.')

        data = {
            'battle': self.battle,
            'battlefield_tiles': BattlefieldTile.objects.get_visible(savegame=self.savegame)
        }

        return data

    def initialize_battle(self):

        # Clear battlefield
        BattlefieldTile.objects.get_visible(savegame=self.savegame).update(regiment=None)

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
            first_position = int(self.BATTLEFIELD_SIZE / army['regiments'].count())

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
