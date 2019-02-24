from apps.military.services.battlefield import BattlefieldService


class RegimentActionService(object):
    ACTION_MOVE_LEFT = 1
    ACTION_MOVE_UP = 2
    ACTION_MOVE_RIGHT = 3
    ACTION_MOVE_DOWN = 4

    battle = None
    battlefield = None

    def __init__(self, savegame):
        from apps.military.models import Battle, BattlefieldTile
        self.battle = Battle.objects.get_current_battle(savegame=savegame)
        self.battlefield = BattlefieldTile.objects.get_visible(savegame=savegame)
        self.battle_service = BattlefieldService(savegame=savegame)

    def execute_action(self, regiment, action):

        if regiment.turn_done:
            raise Exception('Regiment already moved in this round.')

        if action == self.ACTION_MOVE_LEFT:
            self._execute_move_left_basic(regiment)
        elif action == self.ACTION_MOVE_RIGHT:
            self._execute_move_right_basic(regiment)
        elif action == self.ACTION_MOVE_UP:
            self._execute_move_up_basic(regiment)
        elif action == self.ACTION_MOVE_DOWN:
            self._execute_move_down_basic(regiment)
        else:
            raise Exception(f'Tried to execute unknown action {action}.')

        regiment.last_action_in_round += 1
        regiment.save()

    def det_basic_movement(self, regiment):

        allowed_actions = []

        current_position = self.battlefield.filter(regiment=regiment).first()

        if not current_position:
            return allowed_actions

        left_neighbour_x, left_neighbour_y = current_position.left_neighbour
        right_neighbour_x, right_neighbour_y = current_position.right_neighbour
        up_neighbour_x, up_neighbour_y = current_position.up_neighbour
        down_neighbour_x, down_neighbour_y = current_position.down_neighbour

        # Step left
        if left_neighbour_x > 0 and \
                not self.battle_service.get_tile(left_neighbour_x, left_neighbour_y).regiment:
            allowed_actions.append(self.ACTION_MOVE_LEFT)

        # Step right
        if right_neighbour_x < BattlefieldService.BATTLEFIELD_SIZE and \
                not self.battle_service.get_tile(right_neighbour_x, right_neighbour_y).regiment:
            allowed_actions.append(self.ACTION_MOVE_RIGHT)

        # Step up
        if up_neighbour_y > 0 and \
                not self.battle_service.get_tile(up_neighbour_x, up_neighbour_y).regiment:
            allowed_actions.append(self.ACTION_MOVE_UP)

        # Step down
        if down_neighbour_y < BattlefieldService.BATTLEFIELD_SIZE and \
                not self.battle_service.get_tile(down_neighbour_x, down_neighbour_y).regiment:
            allowed_actions.append(self.ACTION_MOVE_DOWN)

        return allowed_actions

    def _execute_move_basic(self, regiment, action, x, y):
        if action not in self.det_basic_movement(regiment):
            raise Exception('Tried to execute invalid basic move action for regiment.')
        self.battle_service.move_regiment(regiment, x, y)

    def _execute_move_left_basic(self, regiment):
        x, y = regiment.on_battlefield_tile.left_neighbour
        self._execute_move_basic(regiment, self.ACTION_MOVE_LEFT, x, y)

    def _execute_move_right_basic(self, regiment):
        x, y = regiment.on_battlefield_tile.right_neighbour
        self._execute_move_basic(regiment, self.ACTION_MOVE_RIGHT, x, y)

    def _execute_move_up_basic(self, regiment):
        x, y = regiment.on_battlefield_tile.up_neighbour
        self._execute_move_basic(regiment, self.ACTION_MOVE_UP, x, y)

    def _execute_move_down_basic(self, regiment):
        x, y = regiment.on_battlefield_tile.down_neighbour
        self._execute_move_basic(regiment, self.ACTION_MOVE_DOWN, x, y)
