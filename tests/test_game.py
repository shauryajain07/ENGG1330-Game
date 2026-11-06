import builtins
import contextlib
import io
import unittest
from unittest import mock

import adapters
import screens
from adapters import LifeSupportGrid, ShardField, solve_lights
from adventure import LEVELS, MAX_BATTERY, MINES, Adventure
from klotski import klotski
from main import main


class FakeBay:

    def __init__(self, moves=(10, 10, 10), energy=0, threshold=35, finished=True):
        self.klotski_gameCount = 0 if finished else 2
        self.klotski_moveCount = list(moves)
        self.klotski_energy = energy
        self.klotski_moveThreshold = threshold


def clear_field(game, hit_first=False):
    field = game.field
    for row in range(9):
        for col in range(9):
            if game.stage != "navigation":
                return
            if field.game.map[row][col] != "X" and field.game.board[row][col] == " ":
                game.handle("t {} {}".format(row + 1, col + 1))


def fix_grid(game):
    while game.stage == "power":
        row, col = solve_lights(game.grid.lights)[0]
        game.handle("p {} {}".format(row + 1, col + 1))


def finish_bay(game, bay=None, result=None):
    given = game.engine_energy()
    if bay is None:
        bay = FakeBay(energy=given, threshold=35)
        result = (game.level, given)
    game.finish_engine(bay, result, given)


def play_whole_game(difficulty, picks, seed=3):
    game = Adventure(difficulty, "Tester", seed)
    game.handle(picks[0])
    clear_field(game)
    game.handle(picks[1])
    fix_grid(game)
    game.handle(picks[2])
    finish_bay(game)
    return game


class ShardFieldTests(unittest.TestCase):
    def test_uses_the_original_minesweeper_map(self):
        for mines in MINES:
            field = ShardField(mines, seed=mines)
            flat = [cell for row in field.game.map for cell in row]
            self.assertEqual(flat.count("X"), mines)
            self.assertGreater(field.safe_found(), 0)

    def test_hit_costs_a_strike_but_does_not_end_the_game(self):
        field = ShardField(10, seed=2)
        row, col = next((r, c) for r in range(9) for c in range(9)
                        if field.game.map[r][c] == "X")
        self.assertEqual(field.tap(row, col), "hit")
        self.assertEqual(field.symbol(row, col), "@")
        self.assertEqual(field.tap(row, col), "already")
        self.assertEqual(field.strikes, 1)

    def test_flags_use_the_original_rules(self):
        field = ShardField(10, seed=3)
        row, col = next((r, c) for r in range(9) for c in range(9)
                        if field.game.board[r][c] == " ")
        self.assertEqual(field.flag(row, col), "placed")
        self.assertEqual(field.flags_left(), 9)
        self.assertEqual(field.tap(row, col), "flagged")
        self.assertEqual(field.flag(row, col), "removed")
        opened = next((r, c) for r in range(9) for c in range(9)
                      if field.game.board[r][c].isdigit())
        self.assertEqual(field.flag(*opened), "revealed")

    def test_break_needs_matching_flags(self):
        field = ShardField(10, seed=4)
        cell = next((r, c) for r in range(9) for c in range(9)
                    if field.game.board[r][c] in "12345678" and field.game.board[r][c] != " ")
        result, reason = field.break_area(*cell)
        self.assertEqual(result, "invalid")
        self.assertIn("flags", reason)

    def test_hint_uses_the_original_message(self):
        field = ShardField(12, seed=5)
        self.assertTrue(field.hint().startswith("Try tap block at"))
        self.assertEqual(field.hints_used, 1)


class LifeSupportGridTests(unittest.TestCase):
    def test_grids_start_unsolved_and_hints_solve_them_in_best_moves(self):
        for size, scramble in ((3, 3), (4, 4), (5, 6)):
            for seed in range(20):
                grid = LifeSupportGrid(size, scramble, seed)
                self.assertFalse(grid.game.is_solved())
                presses = 0
                while not grid.game.is_solved():
                    grid.press(*grid.hint())
                    presses += 1
                self.assertEqual(presses, grid.best_moves)

    def test_goal_is_every_light_on(self):
        grid = LifeSupportGrid(3, 3, seed=1)
        for row, col in solve_lights(grid.lights):
            result = grid.press(row, col)
        self.assertEqual(result, "solved")
        self.assertEqual(grid.lights_off(), 0)


class KlotskiHandoverTests(unittest.TestCase):
    def test_original_klotski_runs_and_can_be_quit(self):
        output = io.StringIO()
        with mock.patch.object(builtins, "input", return_value=":q"), \
                contextlib.redirect_stdout(output):
            bay, result = adapters.play_klotski(1, 3)
        self.assertIsNone(result)
        self.assertNotEqual(bay.klotski_gameCount, 0)
        self.assertIn("Klotski", output.getvalue())

    def run_bridge(self, typed_lines, game=None, energy=3):
        script = iter(typed_lines)
        seen = []

        def ask(bay, view):
            if game is not None:
                lines = screens.drive_bay_screen(game, bay, view, "x" * 20, energy)
                self.assertEqual(len(lines), screens.HEIGHT)
                for text, colour in lines:
                    self.assertLessEqual(len(text), screens.LINE_WIDTH)
            seen.append((view, [row[:] for row in bay.klotski_board], bay.klotski_energy))
            return next(script)

        real_input = builtins.input
        bay, result = adapters.play_klotski(1, energy, ask)
        self.assertIs(builtins.input, real_input)
        return bay, result, seen

    def test_bridge_runs_original_klotski_inside_our_screen(self):
        bay, result, seen = self.run_bridge(["quit"])
        self.assertIsNone(result)
        self.assertEqual(seen[0][0]["mode"], "move")
        self.assertIn("X", [cell for row in seen[0][1] for cell in row])

    def test_bridge_passes_moves_and_shows_original_messages(self):
        bay, result, seen = self.run_bridge(["banana", "quit"])
        self.assertIn("Invalid input. Please enter a valid move.", seen[1][0]["messages"])

    def test_bridge_hint_asks_then_shows_blueprint(self):
        game = Adventure("medium", seed=1)
        bay, result, seen = self.run_bridge(["hint", "y", "", "hint", "", "quit"], game)
        self.assertEqual(seen[1][0]["mode"], "confirm")
        self.assertEqual(seen[2][0]["mode"], "continue")
        self.assertEqual(len(seen[2][0]["blueprint"]), 5)
        self.assertEqual(seen[2][2], 2)
        self.assertEqual(len(seen[4][0]["blueprint"]), 5)
        self.assertEqual(bay.klotski_energy, 2)

    def test_closing_the_prompt_gives_up_safely(self):
        bay, result, seen = self.run_bridge([None])
        self.assertIsNone(result)
        self.assertNotEqual(bay.klotski_gameCount, 0)

    def test_quitting_the_bay_counts_as_skip(self):
        game = Adventure("medium", seed=1)
        for command in ["1", "skip", "1", "skip", "1"]:
            game.handle(command)
        game.finish_engine(klotski(), None, game.engine_energy())
        self.assertIn("engine", game.skipped)
        self.assertEqual(game.stage, "ending")


class AdaptiveDifficultyTests(unittest.TestCase):
    def test_clean_minesweeper_makes_lights_out_harder(self):
        game = Adventure("easy", seed=3)
        game.handle("1")
        clear_field(game)
        self.assertEqual(game.ratings["navigation"], 1)
        self.assertEqual(game.level_name(), "medium")
        game.handle("1")
        self.assertEqual(game.grid.size, 4)

    def test_skipping_makes_the_next_game_easier(self):
        game = Adventure("hard", seed=3)
        game.handle("1")
        game.handle("skip")
        self.assertEqual(game.level_name(), "medium")
        game.handle("1")
        game.handle("skip")
        self.assertEqual(game.level_name(), "easy")
        game.handle("1")
        game.handle("skip")
        self.assertEqual(game.level_name(), "easy")
        self.assertEqual(game.next_difficulty, "easy")

    def test_level_never_goes_above_hard(self):
        game = Adventure("hard", seed=3)
        game.handle("2")
        clear_field(game)
        self.assertEqual(game.level_name(), "hard")

    def test_sloppy_lights_out_makes_klotski_easier(self):
        game = Adventure("medium", seed=6)
        game.handle("1")
        game.handle("skip")
        game.handle("2")
        start_level = game.level
        for _ in range(12):
            game.handle("p 1 1")
        fix_grid(game)
        self.assertEqual(game.ratings["power"], -1)
        self.assertEqual(game.level, max(0, start_level - 1))

    def test_klotski_result_sets_the_next_mission(self):
        game = Adventure("medium", seed=1)
        for command in ["1", "skip", "1", "skip", "1"]:
            game.handle(command)
        game.finish_engine(FakeBay(), (2, 0), 0)
        self.assertEqual(game.next_difficulty, "hard")

    def test_klotski_fast_hard_win_returning_none_stays_hard(self):
        game = Adventure("hard", seed=1)
        game.handle("2")
        clear_field(game)
        game.handle("1")
        fix_grid(game)
        game.handle("1")
        game.finish_engine(FakeBay(moves=(5, 5, 5), threshold=45), None, 0)
        self.assertEqual(game.next_difficulty, "hard")


class AdventureTests(unittest.TestCase):
    def test_game_starts_with_the_prologue_and_first_choice(self):
        game = Adventure("medium", "Sam", seed=1)
        pages = game.take_story_pages()
        self.assertEqual(len(pages), 3)
        self.assertIn("Sam", pages[0]["text"])
        self.assertEqual(game.stage, "wakeup")

    def test_bad_input_never_crashes(self):
        game = Adventure("easy", seed=2)
        for text in ["", "   ", "7", "banana", "!!!", "1 2 3 4"]:
            game.handle(text)
        game.handle("1")
        for text in ["t", "t a b", "t 0 0", "t 99 99", "f 1", "jump", "t -1 2", "b 10 1"]:
            self.assertEqual(game.handle(text), "invalid")
        self.assertEqual(game.battery, MAX_BATTERY)

    def test_deflector_blocks_one_shard(self):
        game = Adventure("easy", seed=5)
        game.handle("1")
        shards = [(r, c) for r in range(9) for c in range(9)
                  if game.field.game.map[r][c] == "X"]
        game.handle("t {} {}".format(shards[0][0] + 1, shards[0][1] + 1))
        self.assertEqual(game.battery, 100)
        game.handle("t {} {}".format(shards[1][0] + 1, shards[1][1] + 1))
        self.assertEqual(game.battery, 90)

    def test_gravity_ping_gives_a_free_scanner_hint(self):
        game = Adventure("easy", seed=5)
        game.handle("2")
        game.handle("hint")
        self.assertEqual(game.battery, 100)
        game.handle("hint")
        self.assertEqual(game.battery, 92)

    def test_fixed_antenna_makes_kip_give_a_bay_hint(self):
        game = Adventure("easy", seed=5)
        game.handle("3")
        game.handle("skip")
        game.handle("2")
        game.handle("skip")
        game.handle("2")
        self.assertEqual(game.free_hints["engine"], 1)

    def test_lifting_a_stranger_drone_costs_battery(self):
        game = Adventure("easy", seed=5)
        game.handle("1")
        game.handle("skip")
        game.handle("2")
        game.handle("skip")
        before = game.battery
        game.handle("2")
        self.assertEqual(game.battery, before - 5)
        self.assertEqual(game.free_hints["engine"], 0)

    def test_paid_bay_hints_cost_battery(self):
        game = Adventure("easy", seed=5)
        for command in ["1", "skip", "2", "skip", "1"]:
            game.handle(command)
        given = game.engine_energy()
        before = game.battery
        game.finish_engine(FakeBay(energy=given - 3), (0, given - 3), given)
        self.assertEqual(game.battery, before - 2 * 6)

    def test_engine_stage_enter_opens_klotski(self):
        game = Adventure("easy", seed=5)
        for command in ["1", "skip", "2", "skip", "1"]:
            game.handle(command)
        self.assertEqual(game.handle(""), "klotski")
        self.assertEqual(game.handle("banana"), "invalid")

    def test_battery_never_goes_below_zero_or_above_max(self):
        game = Adventure("easy", seed=5)
        game.handle("1")
        game.battery = 3
        self.assertEqual(game.handle("hint"), "invalid")
        game.spend(50)
        self.assertEqual(game.battery, 0)
        game.gain(500)
        self.assertEqual(game.battery, MAX_BATTERY)

    def test_restart_needs_confirmation(self):
        game = Adventure("easy", seed=5)
        game.handle("restart")
        self.assertEqual(game.handle("n"), "ok")
        game.handle("restart")
        self.assertEqual(game.handle("y"), "restart")
        self.assertEqual(game.handle("quit"), "menu")

    def test_perfect_play_wins_the_best_ending(self):
        game = play_whole_game("medium", ["1", "2", "3"])
        self.assertEqual(game.stage, "ending")
        self.assertEqual(game.ending, "perfect")
        self.assertGreaterEqual(game.score, 80)

    def test_skipping_everything_is_a_time_slip(self):
        game = Adventure("hard", seed=8)
        for command in ["1", "skip", "2", "skip", "3", "skip"]:
            game.handle(command)
        self.assertEqual(game.stage, "ending")
        self.assertEqual(game.ending, "jelly")

    def test_empty_battery_always_means_time_slip(self):
        game = Adventure("easy", seed=8)
        game.handle("1")
        clear_field(game)
        game.handle("1")
        fix_grid(game)
        game.handle("1")
        game.battery = 0
        finish_bay(game)
        self.assertEqual(game.ending, "jelly")

    def test_every_choice_path_reaches_an_ending(self):
        for difficulty in LEVELS:
            for picks in (["1", "1", "1"], ["2", "2", "2"], ["3", "3", "3"]):
                game = play_whole_game(difficulty, picks)
                self.assertEqual(game.stage, "ending")
                self.assertIn(game.ending, ("perfect", "bumpy", "jelly"))


class ScreenTests(unittest.TestCase):
    def assert_fits(self, lines):
        self.assertEqual(len(lines), screens.HEIGHT)
        for text, colour in lines:
            self.assertLessEqual(len(text), screens.LINE_WIDTH)

    def test_menus_fit_80_by_24(self):
        for difficulty in LEVELS:
            for selected in range(4):
                self.assert_fits(screens.menu_screen(selected, difficulty))
        self.assert_fits(screens.name_screen("A" * 12))
        for page in range(3):
            self.assert_fits(screens.how_to_play_screen(page))

    def test_every_game_screen_fits_80_by_24(self):
        for difficulty in LEVELS:
            game = Adventure(difficulty, "LongNameHere", seed=4)
            for page in game.take_story_pages():
                self.assert_fits(screens.story_screen(page, 9999, True))
            for command in ["help", "1", "t 1 1", "skip", "3", "p 1 1", "skip", "2", "help"]:
                self.assert_fits(screens.game_screen(game, "x" * 40))
                game.handle(command)
                for page in game.take_story_pages():
                    self.assert_fits(screens.story_screen(page, 9999, True))
            self.assert_fits(screens.game_screen(game, ""))
            finish_bay(game)
            self.assert_fits(screens.report_screen(game))

    def test_every_puzzle_ends_with_a_tars_report_that_fits(self):
        game = play_whole_game("medium", ["1", "2", "3"])
        titles = [page["title"] for page in game.take_story_pages()]
        for number in ("1/3", "2/3", "3/3"):
            self.assertTrue(any("SYSTEM REPORT " + number in title for title in titles))
        for difficulty in LEVELS:
            game = Adventure(difficulty, "LongNameHere", seed=2)
            for command in ["1", "skip", "1", "skip", "1"]:
                game.handle(command)
            game.handle("skip")
            for page in game.take_story_pages():
                self.assert_fits(screens.story_screen(page, 9999, True))

    def test_tiny_terminal_message_fits(self):
        for line in screens.resize_lines(3, 20):
            self.assertLess(len(line), 20)
        self.assertEqual(len(screens.resize_lines(3, 20)), 3)


class StartupTests(unittest.TestCase):
    def test_non_terminal_start_explains_how_to_run(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            main()
        self.assertIn("python3 main.py", output.getvalue())


if __name__ == "__main__":
    unittest.main()
