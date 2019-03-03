from apps.military.tests.test_regiment_actions_base_test import RegimentActionBaseTest


class RegimentActionBasicMovementTest(RegimentActionBaseTest):
    fixtures = ['initial_data']

    def test_det_basic_movement_all_directions_ok(self):
        # Move regiment to middle so we have space around
        self.battle_service.move_regiment(self.regiment_peasants_1, self.field_size / 2, self.field_size / 2)

        directions = self.regiment_action_service.det_basic_movement(self.regiment_peasants_1)

        self.assertEqual(len(directions), 4)

    def test_det_basic_movement_no_left_on_border(self):
        # Move other regiment out of the way
        self.battle_service.move_regiment(self.regiment_peasants_2, 0, 0)
        # Move regiment to middle so we have space around
        self.battle_service.move_regiment(self.regiment_peasants_1, 0, self.field_size / 2)

        directions = self.regiment_action_service.det_basic_movement(self.regiment_peasants_1)

        self.assertIn(self.regiment_action_service.ACTION_MOVE_UP, directions)
        self.assertIn(self.regiment_action_service.ACTION_MOVE_DOWN, directions)
        self.assertIn(self.regiment_action_service.ACTION_MOVE_RIGHT, directions)

    def test_det_basic_movement_no_right_on_border(self):
        # Move regiment to middle so we have space around
        self.battle_service.move_regiment(self.regiment_peasants_1, self.field_size, self.field_size / 2)

        directions = self.regiment_action_service.det_basic_movement(self.regiment_peasants_1)

        self.assertIn(self.regiment_action_service.ACTION_MOVE_UP, directions)
        self.assertIn(self.regiment_action_service.ACTION_MOVE_DOWN, directions)
        self.assertIn(self.regiment_action_service.ACTION_MOVE_LEFT, directions)

    def test_det_basic_movement_no_down_on_border(self):
        # Move regiment to middle so we have space around
        self.battle_service.move_regiment(self.regiment_peasants_1, self.field_size / 2, self.field_size)

        directions = self.regiment_action_service.det_basic_movement(self.regiment_peasants_1)

        self.assertIn(self.regiment_action_service.ACTION_MOVE_UP, directions)
        self.assertIn(self.regiment_action_service.ACTION_MOVE_LEFT, directions)
        self.assertIn(self.regiment_action_service.ACTION_MOVE_RIGHT, directions)
