import unittest

from tiamat.game import (
    ENCOUNTER_RATE,
    MAPS,
    STARTERS,
    TiamatGame,
    apply_move,
    calculate_damage,
    validate_maps,
)


class ScriptedRng:
    def __init__(self, random_values=None, choices=None):
        self.random_values = list(random_values or [])
        self.choices = list(choices or [])

    def random(self):
        if self.random_values:
            return self.random_values.pop(0)
        return 1.0

    def choice(self, values):
        if self.choices:
            return self.choices.pop(0)
        return list(values)[0]


class TiamatGameTests(unittest.TestCase):
    def test_all_maps_are_rectangular(self):
        validate_maps()

    def test_rootmere_is_larger_than_original_spawn_area(self):
        self.assertEqual(len(MAPS["rootmere"].tiles), 18)
        self.assertEqual(len(MAPS["rootmere"].tiles[0]), 40)

    def test_damage_formula_has_minimum_one_damage(self):
        attacker = STARTERS["drizzle"].fresh_copy()
        defender = STARTERS["drizzle"].fresh_copy()
        defender.defense_modifier = 6

        damage = calculate_damage(attacker, attacker.moves[0], defender)

        self.assertEqual(damage, 1)

    def test_defensive_move_raises_battle_defense(self):
        spriglet = STARTERS["spriglet"].fresh_copy()
        drizzle = STARTERS["drizzle"].fresh_copy()

        message = apply_move(spriglet, drizzle, spriglet.moves[1])

        self.assertIn("Defense rose", message)
        self.assertEqual(spriglet.current_defense, 6)

    def test_collision_blocks_walls_water_and_furniture(self):
        game = TiamatGame(output_func=lambda _: None)

        game.player_x, game.player_y = 1, 1
        self.assertFalse(game.try_move(-1, 0))
        game.player_x, game.player_y = 21, 5
        self.assertFalse(game.try_move(0, -1))
        game.current_map = "player_home"
        game.player_x, game.player_y = 3, 2
        self.assertFalse(game.try_move(0, 0))

    def test_player_can_enter_and_exit_home(self):
        game = TiamatGame(output_func=lambda _: None)
        game.player_x, game.player_y = 9, 4

        game.interact()

        self.assertEqual(game.current_map, "player_home")
        self.assertEqual(game.player_position, (4, 5))

        game.interact()

        self.assertEqual(game.current_map, "rootmere")
        self.assertEqual(game.player_position, (9, 5))

    def test_player_can_enter_supply_hut(self):
        game = TiamatGame(output_func=lambda _: None)
        game.player_x, game.player_y = 10, 12

        game.interact()

        self.assertEqual(game.current_map, "supply_hut")
        self.assertIn("Supply Hut", game.message)

    def test_lab_choice_sets_starter_only_inside_lab(self):
        inputs = iter(["1"])
        game = TiamatGame(
            input_func=lambda _: next(inputs),
            output_func=lambda _: None,
        )

        game.choose_starter()
        self.assertIsNone(game.starter)

        game.current_map = "morph_lab"
        game.choose_starter()

        self.assertEqual(game.starter.name, "Spriglet")

    def test_interacting_with_lab_console_after_choice_is_blocked(self):
        game = TiamatGame(output_func=lambda _: None)
        game.current_map = "morph_lab"
        game.starter = STARTERS["spriglet"].fresh_copy()
        game.player_x, game.player_y = 4, 5

        game.interact()

        self.assertIn("already chose", game.message)

    def test_grass_requires_starter_then_can_skip_encounter(self):
        game = TiamatGame(
            output_func=lambda _: None,
            rng=ScriptedRng(random_values=[ENCOUNTER_RATE + 0.01]),
        )
        game.player_x, game.player_y = 14, 1

        self.assertTrue(game.try_move(1, 0))
        self.assertIn("visit the Morph Lab", game.message)

        game.starter = STARTERS["spriglet"].fresh_copy()
        self.assertTrue(game.try_move(1, 0))
        self.assertIn("Nothing stirs", game.message)

    def test_no_encounters_inside_buildings(self):
        game = TiamatGame(output_func=lambda _: None, rng=ScriptedRng(random_values=[0.0]))
        game.current_map = "player_home"
        game.player_x, game.player_y = 1, 1

        self.assertTrue(game.try_move(1, 0))
        self.assertNotIn("wild", game.message.lower())

    def test_trial_gate_has_locked_message(self):
        game = TiamatGame(output_func=lambda _: None)
        game.player_x, game.player_y = 37, 1

        game.interact()
        self.assertIn("Trial Gate is locked", game.message)

    def test_rootmere_exit_leads_to_route_01(self):
        game = TiamatGame(output_func=lambda _: None)
        game.player_x, game.player_y = 38, 15

        game.interact()

        self.assertEqual(game.current_map, "route_01")
        self.assertEqual(game.player_position, (1, 1))
        self.assertIn("Route 01", game.message)

    def test_route_01_connects_rootmere_and_thornwild(self):
        game = TiamatGame(output_func=lambda _: None)
        game.current_map = "route_01"
        game.player_x, game.player_y = 34, 15

        game.interact()
        self.assertEqual(game.current_map, "thornwild")
        self.assertEqual(game.player_position, (36, 15))

        game.interact()
        self.assertEqual(game.current_map, "route_01")
        self.assertEqual(game.player_position, (33, 15))

    def test_route_01_grass_can_warn_before_starter(self):
        game = TiamatGame(output_func=lambda _: None)
        game.current_map = "route_01"
        game.player_x, game.player_y = 7, 1

        self.assertTrue(game.try_move(1, 0))
        self.assertIn("visit the Morph Lab", game.message)

    def test_route_01_npc_has_dialogue(self):
        game = TiamatGame(output_func=lambda _: None)
        game.current_map = "route_01"
        game.player_x, game.player_y = 31, 2

        game.interact()

        self.assertIn("Thornwild is just ahead", game.message)

    def test_battle_can_complete_with_player_win(self):
        inputs = iter(["1", "1", "1", "1"])
        game = TiamatGame(
            input_func=lambda _: next(inputs),
            output_func=lambda _: None,
            rng=ScriptedRng(),
        )
        game.clear_screen = lambda: None
        game.starter = STARTERS["cindlet"].fresh_copy()

        game.start_battle(STARTERS["spriglet"].fresh_copy())

        self.assertIn("Wild Spriglet is worn out", game.message)


if __name__ == "__main__":
    unittest.main()
