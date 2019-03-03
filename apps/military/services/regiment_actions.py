import random

from apps.military.services.battlefield import BattlefieldService


class RegimentActionService(object):
    # Basic movement
    ACTION_MOVE_LEFT = 1
    ACTION_MOVE_UP = 2
    ACTION_MOVE_RIGHT = 3
    ACTION_MOVE_DOWN = 4
    # Attack
    ACTION_MELEE = 5
    ACTION_LONG_RANGE = 6

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
        elif action == self.ACTION_MELEE:
            self._execute_melee(regiment)
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

    def calculate_melee_damage(self, attacker, target_list):
        """
        # TODO morale can go up as well
        # TODO build functions for calculating men, morale etc.
        # TODO moral check before any action is required
        # TODO write tests
        """
        from apps.military.models import BattleLogEntry

        # Variables
        losses_attacker = losses_defender = 0

        # If attacker has multiple targets, for each enemy the attack value is reduced
        corrected_attack_value = attacker.type.attack_value / target_list.count()

        for tile in target_list:
            target = tile.regiment
            dice_roll_attack = max(random.gauss(5, 5), 0)

            # If defender is flanked by multiple targets, defense value is reduced
            flanking_opponents = self.battle_service.get_enemies_in_distance(target)
            target_corrected_defense_value = target.type.defense_value / max(flanking_opponents.count() - 1, 1)

            # Effect on target
            killed_target_men = round((corrected_attack_value / target_corrected_defense_value) * 10 * dice_roll_attack)
            lost_target_morale = round(pow(dice_roll_attack, 2) / 2)
            target.current_men -= min(max(killed_target_men, 0), target.current_men)
            target.current_morale -= lost_target_morale
            target.save()

            losses_defender += killed_target_men

            # Effect on attacker
            dice_roll_defense = max(random.gauss(5, 5), 0)
            target_corrected_attack_value = target.type.attack_value / flanking_opponents.count()
            killed_attacker_men = round((corrected_attack_value / target_corrected_attack_value) * 2 * dice_roll_defense)
            lost_attacker_morale = round(pow(dice_roll_defense, 2) / 2)
            attacker.current_men -= min(max(killed_attacker_men, 0), target.current_men)
            attacker.current_morale -= lost_attacker_morale
            attacker.save()

            losses_attacker += killed_attacker_men

            BattleLogEntry.objects.create(
                battle=self.battle,
                text=f'{attacker} attacked {target} with {round(corrected_attack_value, 2)} of their men. '
                f'They killed {killed_target_men} men and lost {killed_attacker_men}.')

        self.battle.losses_attacker = losses_attacker
        self.battle.losses_defender = losses_defender
        self.battle.save()

    def _execute_melee(self, regiment):
        enemies = self.battle_service.get_enemies_in_distance(regiment)
        self.calculate_melee_damage(regiment, enemies)
        # todo

    def det_fight_melee(self, regiment):

        # Only for melee regiments
        if regiment.type.is_long_range:
            return []

        # If a tile exists where there is a regiment from the other side...
        tiles_with_enemies = self.battle_service.get_enemies_in_distance(regiment)
        if not tiles_with_enemies.exists():
            return []

        return [self.ACTION_MELEE]

    def det_fight_long_range(self, regiment):
        # Only for long range regiments
        if not regiment.type.is_long_range:
            return []

        # They can shoot only when no enemy is next to them
        tiles_with_enemies = self.battle_service.get_enemies_in_distance(regiment)
        if tiles_with_enemies.exists():
            return []

        # If there are enemies in range we can shoot at them
        enemies_in_range = self.battle_service.get_enemies_in_shooting_range(regiment)
        if not enemies_in_range.exists():
            return []

        return [self.ACTION_LONG_RANGE]
