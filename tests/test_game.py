from collections import Counter, deque
from contextlib import redirect_stdout
from io import StringIO
import unittest
from unittest.mock import patch

from game import screens
from game.adapters import LifeSupportGrid, ShardField, solve_lights, to_klotski_command
from game.adventure import Adventure, efficiency_points, read_numbers
from game.klotski import is_klotski_won, klotski
from game.lights_out_game import LightsOutGame


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

    def test_text_input_rejects_malformed_and_out_of_range_coordinates(self):
        with self.assertRaises(ValueError):
            self.game.press_from_text("two 1")
        with self.assertRaises(IndexError):
            self.game.press_from_text("1 4")

    def test_solver_returns_moves_that_restore_a_solved_board(self):
        self.game.press(1, 1)
        solution = solve_lights(self.game.board)

        self.assertIsNotNone(solution)
        for row, col in solution:
            self.game.press(row, col)

        self.assertTrue(self.game.is_solved())


class LifeSupportGridTests(unittest.TestCase):
    def test_all_difficulty_scrambles_have_a_solution(self):
        for size, scramble in ((3, 3), (4, 4), (5, 6)):
            for seed in range(3):
                with self.subTest(size=size, seed=seed):
                    grid = LifeSupportGrid(size, scramble, seed=seed)
                    solution = solve_lights(grid.lights)

                    self.assertIsNotNone(solution)
                    self.assertEqual(grid.best_moves, len(solution))
                    self.assertGreater(grid.lights_off(), 0)


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
        self.assertEqual(to_klotski_command("help", "move"), ":?")
        self.assertEqual(to_klotski_command("A up", "move"), "A up")
        self.assertEqual(to_klotski_command("ignored", "continue"), "")

    def test_help_shows_a_move_example_for_each_puzzle(self):
        examples = (
            ("navigation", "t 3 4"),
            ("power", "p 2 3"),
            ("engine", "I down or X right"),
        )
        for stage, example in examples:
            with self.subTest(stage=stage):
                game = Adventure(difficulty="easy", player_name="Pilot", seed=1)
                game.start_puzzle(stage)
                game.handle("help")
                layout = screens.game_screen(game, "")
                visible_text = "\n".join(line for line, _ in layout)

                self.assertIn(example, visible_text)


class MissionInputTests(unittest.TestCase):
    def navigation_mission(self):
        game = Adventure(difficulty="easy", player_name="Pilot", seed=23)
        game.handle("2")
        return game

    def test_invalid_navigation_commands_preserve_battery_and_progress(self):
        game = self.navigation_mission()
        battery_before = game.battery
        safe_before = game.field.safe_found()

        for command in ("t 0 1", "t 10 9", "t one 2", "t 1"):
            with self.subTest(command=command):
                self.assertEqual(game.handle(command), "invalid")
                self.assertEqual(game.battery, battery_before)
                self.assertEqual(game.field.safe_found(), safe_before)

    def test_hitting_a_hidden_mine_costs_battery_and_records_a_strike(self):
        game = self.navigation_mission()
        row, col = next(
            (r, c)
            for r in range(game.field.rows)
            for c in range(game.field.cols)
            if game.field.game.map[r][c] == "X"
            and game.field.game.board[r][c] == " "
        )
        battery_before = game.battery

        self.assertEqual(game.handle("t {} {}".format(row + 1, col + 1)), "ok")

        self.assertEqual(game.battery, battery_before - 10)
        self.assertEqual(game.field.strikes, 1)

    def test_free_hint_is_used_before_a_paid_hint(self):
        game = self.navigation_mission()
        battery_before = game.battery

        self.assertEqual(game.handle("hint"), "ok")
        self.assertEqual(game.battery, battery_before)
        self.assertEqual(game.free_hints["navigation"], 0)

        self.assertEqual(game.handle("hint"), "ok")
        self.assertEqual(game.battery, battery_before - 8)

    def test_opening_every_safe_square_completes_navigation(self):
        game = self.navigation_mission()

        for row in range(game.field.rows):
            for col in range(game.field.cols):
                if (game.stage == "navigation"
                        and game.field.game.map[row][col] != "X"
                        and game.field.game.board[row][col] == " "):
                    game.handle("t {} {}".format(row + 1, col + 1))

        self.assertTrue(game.field.is_cleared())
        self.assertEqual(game.stage, "goose")

    def test_solving_lights_out_completes_the_power_chapter(self):
        game = Adventure(difficulty="easy", player_name="Pilot", seed=5)
        game.start_puzzle("power")
        solution = solve_lights(game.grid.lights)

        for row, col in solution:
            game.handle("p {} {}".format(row + 1, col + 1))

        self.assertEqual(game.stage, "cat")
        self.assertTrue(game.grid.game.is_solved())

    def test_power_grid_rejects_bad_coordinates_without_spending_battery(self):
        game = Adventure(difficulty="easy", player_name="Pilot", seed=5)
        game.start_puzzle("power")
        battery_before = game.battery
        moves_before = game.grid.moves

        for command in ("p 0 1", "p 4 1", "p x 2"):
            with self.subTest(command=command):
                self.assertEqual(game.handle(command), "invalid")
                self.assertEqual(game.battery, battery_before)
                self.assertEqual(game.grid.moves, moves_before)


class KlotskiTests(unittest.TestCase):
    BOARD_LEVELS = {
        0: 0, 1: 0, 2: 0, 3: 1, 4: 1, 5: 0,
        6: 1, 7: 1, 8: 2, 9: 2, 10: 2, 11: 0,
    }
    EXPECTED_PIECES = Counter({
        "X": 4, "A": 2, "B": 2, "C": 2, "D": 2, "E": 2,
        "F": 1, "G": 1, "H": 1, "I": 1, " ": 2,
    })

    def play_board(self, board_index, commands):
        game = klotski()
        output = StringIO()
        with patch("game.klotski.random.choice", return_value=board_index):
            with patch("builtins.input", side_effect=commands):
                with redirect_stdout(output):
                    game.play_klotski(
                        difficulty=self.BOARD_LEVELS[board_index], energy=0
                    )
        self.last_output = output.getvalue()
        return game

    def can_reach_exit(self, pieces):
        # Sort identical crates to avoid revisiting label-swapped states.
        start = (
            (pieces["X"]["row"], pieces["X"]["col"]),
            tuple(sorted((pieces[name]["row"], pieces[name]["col"])
                         for name in "ABCD")),
            (pieces["E"]["row"], pieces["E"]["col"]),
            tuple(sorted((pieces[name]["row"], pieces[name]["col"])
                         for name in "FGHI")),
        )
        pending = deque([start])
        visited = {start}
        steps = ((-1, 0), (1, 0), (0, -1), (0, 1))

        while pending:
            state = pending.popleft()
            if state[0] == (3, 1):
                return True

            board = [[" " for _ in range(4)] for _ in range(5)]
            groups = (
                ("X", (2, 2), (state[0],)),
                ("V", (2, 1), state[1]),
                ("H", (1, 2), (state[2],)),
                ("S", (1, 1), state[3]),
            )
            for label, (height, width), positions in groups:
                for index, (row, col) in enumerate(positions):
                    token = label + str(index)
                    for board_row in range(row, row + height):
                        for board_col in range(col, col + width):
                            board[board_row][board_col] = token

            for label, (height, width), positions in groups:
                for index, (row, col) in enumerate(positions):
                    token = label + str(index)
                    for row_step, col_step in steps:
                        next_row = row + row_step
                        next_col = col + col_step
                        if not (0 <= next_row and next_row + height <= 5
                                and 0 <= next_col and next_col + width <= 4):
                            continue
                        if not all(
                            board[r][c] in (" ", token)
                            for r in range(next_row, next_row + height)
                            for c in range(next_col, next_col + width)
                        ):
                            continue

                        next_state = list(state)
                        moved = list(positions)
                        moved[index] = (next_row, next_col)
                        if label == "X":
                            next_state[0] = moved[0]
                        elif label == "V":
                            next_state[1] = tuple(sorted(moved))
                        elif label == "H":
                            next_state[2] = moved[0]
                        else:
                            next_state[3] = tuple(sorted(moved))
                        next_state = tuple(next_state)
                        if next_state not in visited:
                            visited.add(next_state)
                            pending.append(next_state)

        return False

    def test_every_piece_layout_fills_a_valid_five_by_four_board(self):
        for board_index in self.BOARD_LEVELS:
            with self.subTest(board=board_index):
                game = self.play_board(board_index, [":q"])
                self.assertEqual(len(game.klotski_board), 5)
                self.assertTrue(all(len(row) == 4 for row in game.klotski_board))
                self.assertEqual(
                    Counter(cell for row in game.klotski_board for cell in row),
                    self.EXPECTED_PIECES,
                )
                self.assertTrue(self.can_reach_exit(game.klotski_currentPieces))

    def test_valid_move_updates_piece_position_and_move_count(self):
        game = self.play_board(0, ["B down", ":q"])

        self.assertEqual(game.klotski_currentPieces["B"]["row"], 1)
        self.assertEqual(game.klotski_moveCount, [1, 0, 0])

    def test_out_of_bounds_move_leaves_board_unchanged(self):
        game = self.play_board(0, ["B up", ":q"])

        self.assertEqual(game.klotski_currentPieces["B"]["row"], 0)
        self.assertEqual(game.klotski_moveCount, [0, 0, 0])

    def test_unknown_piece_is_rejected_without_a_move(self):
        game = self.play_board(0, ["Z up", ":q"])

        self.assertEqual(game.klotski_moveCount, [0, 0, 0])

    def test_help_displays_drive_bay_move_examples(self):
        self.play_board(0, ["help", ":q"])

        self.assertIn("I down or X right", self.last_output)

    def test_reset_restores_the_selected_layout_and_clears_moves(self):
        game = self.play_board(0, ["B down", ":r", ":q"])

        self.assertEqual(game.klotski_currentPieces["B"]["row"], 0)
        self.assertEqual(game.klotski_moveCount, [0, 0, 0])

    def test_core_at_bottom_exit_is_the_win_condition(self):
        board = [[" " for _ in range(4)] for _ in range(5)]
        for row in range(3, 5):
            for col in range(1, 3):
                board[row][col] = "X"

        self.assertTrue(is_klotski_won(board))
        board[4][2] = " "
        self.assertFalse(is_klotski_won(board))


class ScreenLayoutTests(unittest.TestCase):
    def test_menu_and_instructions_stay_inside_the_terminal_area(self):
        for layout in (screens.menu_screen(0, "medium"), screens.how_to_play_screen(0)):
            with self.subTest(rows=len(layout)):
                self.assertEqual(len(layout), screens.HEIGHT)
                self.assertTrue(all(len(line) <= screens.LINE_WIDTH for line, _ in layout))

    def test_small_terminal_message_fits_available_size(self):
        for rows, cols in ((1, 1), (3, 10), (10, 50)):
            with self.subTest(rows=rows, cols=cols):
                lines = screens.resize_lines(rows, cols)
                self.assertLessEqual(len(lines), rows)
                self.assertTrue(all(len(line) < cols for line in lines))

    def test_finish_clips_long_lines_and_pads_to_fixed_height(self):
        layout = screens.finish([("x" * 100, "normal")])

        self.assertEqual(len(layout), screens.HEIGHT)
        self.assertEqual(len(layout[0][0]), screens.LINE_WIDTH)
        self.assertTrue(all(len(line) <= screens.LINE_WIDTH for line, _ in layout))


if __name__ == "__main__":
    unittest.main()
