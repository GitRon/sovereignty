from apps.military.services.regiment_actions import RegimentActionService
from apps.military.tests.test_regiment_actions_base_test import RegimentActionBaseTest


class RegimentActionFightingTest(RegimentActionBaseTest):

    def test_bs_get_neighbours_in_distance_regular(self):
        tiles = self.battle_service.get_neighbours_in_distance(4, 4, 1)
        self.assertEqual(tiles.count(), 8)

    def test_bs_get_neighbours_in_distance_distance_2(self):
        tiles = self.battle_service.get_neighbours_in_distance(5, 5, 2)
        self.assertEqual(tiles.count(), 24)

    def test_bs_get_enemies_in_distance_no_enemy(self):
        # Move two opposing regiments next to each other
        self.battle_service.move_regiment(self.regiment_peasants_1, 4, 4)
        self.battle_service.move_regiment(self.regiment_peasants_3, 4, 6)

        tiles = self.battle_service.get_enemies_in_distance(self.regiment_peasants_1, 1)
        self.assertEqual(tiles.count(), 0)

    def test_bs_get_enemies_in_distance_one_enemy(self):
        # Move two opposing regiments next to each other
        self.battle_service.move_regiment(self.regiment_peasants_1, 4, 4)
        self.battle_service.move_regiment(self.regiment_peasants_3, 4, 5)

        tiles = self.battle_service.get_enemies_in_distance(self.regiment_peasants_1, 1)
        self.assertEqual(tiles.count(), 1)

    def test_bs_get_enemies_in_distance_two_enemies(self):
        # Move two opposing regiments next to each other
        self.battle_service.move_regiment(self.regiment_peasants_1, 4, 4)
        self.battle_service.move_regiment(self.regiment_peasants_3, 4, 5)
        self.battle_service.move_regiment(self.regiment_peasants_4, 4, 3)

        tiles = self.battle_service.get_enemies_in_distance(self.regiment_peasants_1, 1)
        self.assertEqual(tiles.count(), 2)

    def test_bs_get_enemies_in_distance_one_enemy_distance_2(self):
        # Move two opposing regiments close to each other
        self.battle_service.move_regiment(self.regiment_peasants_1, 4, 4)
        self.battle_service.move_regiment(self.regiment_peasants_3, 4, 6)

        tiles = self.battle_service.get_enemies_in_distance(self.regiment_peasants_1, 2)
        self.assertEqual(tiles.count(), 1)

    def test_bs_get_enemies_in_shooting_range(self):
        # Move two opposing regiments close to each other
        self.battle_service.move_regiment(self.regiment_peasants_1, 4, 4)
        self.battle_service.move_regiment(self.regiment_peasants_3, 4, 6)

        tiles = self.battle_service.get_enemies_in_shooting_range(self.regiment_peasants_1)
        self.assertEqual(tiles.count(), 1)

    def test_bs_get_enemies_in_shooting_range_no_enemies(self):
        # Move two opposing regiments close to each other
        self.battle_service.move_regiment(self.regiment_peasants_1, 4, 4)
        self.battle_service.move_regiment(self.regiment_peasants_3, 4, 7)

        tiles = self.battle_service.get_enemies_in_shooting_range(self.regiment_peasants_1)
        self.assertEqual(tiles.count(), 0)

    def test_det_melee(self):
        # Move two opposing regiments next to each other
        self.battle_service.move_regiment(self.regiment_peasants_1, 4, 4)
        self.battle_service.move_regiment(self.regiment_peasants_3, 4, 5)

        action_list = self.regiment_action_service.det_fight_melee(self.regiment_peasants_1)

        self.assertEqual(action_list, [RegimentActionService.ACTION_MELEE])

    def test_det_no_melee(self):
        # Move two opposing regiments next to each other
        self.battle_service.move_regiment(self.regiment_peasants_1, 4, 4)
        self.battle_service.move_regiment(self.regiment_peasants_3, 4, 6)

        action_list = self.regiment_action_service.det_fight_melee(self.regiment_peasants_1)

        self.assertEqual(action_list, [])

    def test_det_long_range_in_range(self):
        # Move two opposing regiments next to each other
        self.battle_service.move_regiment(self.regiment_long_range_1, 4, 4)
        self.battle_service.move_regiment(self.regiment_peasants_3, 4, 6)

        action_list = self.regiment_action_service.det_fight_long_range(self.regiment_long_range_1)

        self.assertEqual(action_list, [RegimentActionService.ACTION_LONG_RANGE])

    def test_det_long_range_blocked_by_adjacent_enemy(self):
        # Move two opposing regiments next to each other
        self.battle_service.move_regiment(self.regiment_long_range_1, 4, 4)
        self.battle_service.move_regiment(self.regiment_peasants_3, 4, 5)

        action_list = self.regiment_action_service.det_fight_long_range(self.regiment_long_range_1)

        self.assertEqual(action_list, [])
