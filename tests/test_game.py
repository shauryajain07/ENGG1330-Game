import unittest

from adapters import ShardField, solve_lights, to_klotski_command
from adventure import Adventure, efficiency_points, read_numbers
from lights_out_game import LightsOutGame


class LightsOutTests(unittest.TestCase):
    def setUp(self):
        self.game = LightsOutGame(3, 3, seed=1)
        self.game.reset()

    def test_center_press_flips_only_the_cross(self):
        self.game.press(1, 1)

        self.assertEqual(
            self.game.board,
            (
                (True, False, True),
                (False, False, False),
                (True, False, True),
            ),
        )

    def test_corner_press_stays_inside_board(self):
        self.game.press(0, 0)

        self.assertFalse(self.game.board[0][0])
        self.assertFalse(self.game.board[0][1])
        self.assertFalse(self.game.board[1][0])
        self.assertTrue(self.game.board[1][1])
        self.assertTrue(self.game.board[2][0])

    def test_press_rejects_out_of_range_coordinates(self):
        with self.assertRaises(IndexError):
            self.game.press(-1, 0)
        with self.assertRaises(IndexError):
            self.game.press(0, 3)

    def test_solver_returns_moves_that_restore_a_solved_board(self):
        self.game.press(1, 1)
        solution = solve_lights(self.game.board)

        self.assertIsNotNone(solution)
        for row, col in solution:
            self.game.press(row, col)

        self.assertTrue(self.game.is_solved())


class ShardFieldTests(unittest.TestCase):
    def setUp(self):
        self.field = ShardField(mine_count=10, seed=23)

    def test_board_size_and_boundaries(self):
        self.assertEqual((self.field.rows, self.field.cols), (9, 9))
        self.assertEqual(self.field.safe_total(), 71)
        self.assertTrue(self.field.is_inside(0, 0))
        self.assertTrue(self.field.is_inside(8, 8))
        self.assertFalse(self.field.is_inside(-1, 0))
        self.assertFalse(self.field.is_inside(0, 9))

    def test_flag_can_be_added_and_removed(self):
        row, col = next(
            (r, c)
            for r in range(9)
            for c in range(9)
            if self.field.game.board[r][c] == " "
            and self.field.game.map[r][c] != "X"
        )

        self.assertEqual(self.field.flag(row, col), "placed")
        self.assertEqual(self.field.flags_left(), 9)
        self.assertEqual(self.field.wrong_flags(), 1)
        self.assertEqual(self.field.flag(row, col), "removed")
        self.assertEqual(self.field.flags_left(), 10)

    def test_opening_hidden_safe_cell_increases_progress(self):
        row, col = next(
            (r, c)
            for r in range(9)
            for c in range(9)
            if self.field.game.board[r][c] == " "
            and self.field.game.map[r][c] != "X"
        )
        safe_before = self.field.safe_found()

        result = self.field.tap(row, col)

        self.assertIn(result, ("ok", "cleared"))
        self.assertGreater(self.field.safe_found(), safe_before)


class MissionHelperTests(unittest.TestCase):
    def test_restart_requires_confirmation(self):
        game = Adventure(difficulty="easy", player_name="Pilot", seed=1)

        self.assertEqual(game.handle("restart"), "ok")
        self.assertTrue(game.confirming_restart)
        self.assertEqual(game.handle("n"), "ok")
        self.assertFalse(game.confirming_restart)

        self.assertEqual(game.handle("restart"), "ok")
        self.assertEqual(game.handle("yes"), "restart")

    def test_coordinates_are_converted_from_one_based_input(self):
        self.assertEqual(read_numbers(["p", "2", "3"]), (1, 2))
        self.assertIsNone(read_numbers(["p", "two", "3"]))

    def test_paid_hints_reduce_efficiency_score(self):
        no_hint = efficiency_points(10, 10, 0, 20)
        paid_hint = efficiency_points(10, 10, 1, 20)

        self.assertEqual(no_hint, 20)
        self.assertLess(paid_hint, no_hint)
        self.assertEqual(efficiency_points(10, 1, 0, 20), 20)

    def test_drive_bay_commands_are_translated(self):
        self.assertEqual(to_klotski_command("hint", "move"), ":h")
        self.assertEqual(to_klotski_command("quit", "move"), ":q")
        self.assertEqual(to_klotski_command("A up", "move"), "A up")
        self.assertEqual(to_klotski_command("ignored", "continue"), "")


if __name__ == "__main__":
    unittest.main()
