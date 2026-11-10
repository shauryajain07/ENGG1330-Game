import builtins
import contextlib
import io
import random

from klotski import klotski
from lights_out_game import LightsOutGame
from minesweeper_game import MinesweeperGame


NEIGHBOURS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


class ShardField:

    SIZE = 9

    def __init__(self, mine_count, seed=None):
        if seed is not None:
            random.seed(seed)
        game = MinesweeperGame.__new__(MinesweeperGame)
        game.screen = None
        game.STYLES = {}
        game.words = []
        game.mines_left = mine_count
        game.message = ""
        game.typ = "title"
        game.reward = 0
        game.navigation_chip_count = 0
        self.game = game
        self.mine_count = mine_count
        self.rows = self.SIZE
        self.cols = self.SIZE
        self.strikes = 0
        self.hints_used = 0
        game.map, game.board = game.generate_map()
        while self.is_cleared():
            game.map, game.board = game.generate_map()

    def is_inside(self, row, col):
        return 0 <= row < self.rows and 0 <= col < self.cols

    def symbol(self, row, col):
        cell = self.game.board[row][col]
        if cell == " ":
            return "#"
        if cell == "0":
            return "."
        if cell == "exploded_mine":
            return "@"
        return cell

    def safe_total(self):
        return self.rows * self.cols - self.mine_count

    def safe_found(self):
        count = 0
        for row in range(self.rows):
            for col in range(self.cols):
                if self.game.map[row][col] != "X" and self.game.board[row][col] == self.game.map[row][col]:
                    count += 1
        return count

    def is_cleared(self):
        return self.safe_found() == self.safe_total()

    def flags_left(self):
        return self.game.mines_left

    def wrong_flags(self):
        count = 0
        for row in range(self.rows):
            for col in range(self.cols):
                if self.game.board[row][col] == "F" and self.game.map[row][col] != "X":
                    count += 1
        return count

    def hit(self, row, col):
        self.game.board[row][col] = "exploded_mine"
        self.strikes += 1

    def tap(self, row, col):
        cell = self.game.board[row][col]
        if cell == "F":
            return "flagged"
        if cell != " ":
            return "already"
        if self.game.map[row][col] == "X":
            self.hit(row, col)
            return "hit"
        self.game.tap(row, col)
        if self.is_cleared():
            return "cleared"
        return "ok"

    def flag(self, row, col):
        before = self.game.board[row][col]
        message, kind, _ = self.game.flag(row, col)
        if message != "":
            return "revealed"
        if before == " ":
            return "placed"
        return "removed"

    def break_area(self, row, col):
        cell = self.game.board[row][col]
        flags = 0
        for row_step, col_step in NEIGHBOURS:
            r, c = row + row_step, col + col_step
            if self.is_inside(r, c) and self.game.board[r][c] == "F":
                flags += 1
        ready = cell.isdigit() and cell != "0" and flags == int(cell)
        if not ready:
            message, kind, _ = self.game.break_blocks(row, col)
            return "invalid", message
        hits = 0
        for row_step, col_step in NEIGHBOURS:
            r, c = row + row_step, col + col_step
            if (self.is_inside(r, c) and self.game.board[r][c] == " "
                    and self.game.map[r][c] == "X"):
                self.hit(r, c)
                hits += 1
        self.game.break_blocks(row, col)
        if hits > 0:
            return "hit", ""
        if self.is_cleared():
            return "cleared", ""
        return "ok", ""

    def hint(self):
        self.hints_used += 1
        message, kind = self.game.provide_hint()
        return message


def solve_lights(board):
    rows = len(board)
    cols = len(board[0])
    best = None
    # Each first-row pattern forces every press below it.
    for mask in range(2 ** cols):
        lights = [list(row) for row in board]
        presses = []
        for col in range(cols):
            if mask & (1 << col):
                flip(lights, presses, 0, col)
        for row in range(1, rows):
            for col in range(cols):
                if not lights[row - 1][col]:
                    flip(lights, presses, row, col)
        if all(lights[rows - 1]) and (best is None or len(presses) < len(best)):
            best = presses
    return best


def flip(lights, presses, row, col):
    presses.append((row, col))
    for row_step, col_step in ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)):
        r, c = row + row_step, col + col_step
        if 0 <= r < len(lights) and 0 <= c < len(lights[0]):
            lights[r][c] = not lights[r][c]


class LifeSupportGrid:

    def __init__(self, size, scramble, seed=None):
        self.game = LightsOutGame(size, size, seed=seed)
        self.game.shuffle(scramble)
        self.size = size
        self.hints_used = 0
        self.best_moves = len(solve_lights(self.game.board))

    @property
    def lights(self):
        return self.game.board

    @property
    def moves(self):
        return self.game.move_count

    def is_inside(self, row, col):
        return 0 <= row < self.size and 0 <= col < self.size

    def lights_off(self):
        count = 0
        for row in self.game.board:
            count += list(row).count(False)
        return count

    def press(self, row, col):
        if self.game.press(row, col):
            return "solved"
        return "ok"

    def hint(self):
        self.hints_used += 1
        return solve_lights(self.game.board)[0]


KLOTSKI_SKIP = ("[Mini-game", "Difficulty:", "Total moves made", "Energy left",
                "Enter move", "Hint: This is an intermediate", "Game exited")

PLAYER_WORDS = {"quit": ":q", "skip": ":q", "q": ":q", "giveup": ":q",
                "hint": ":h", "h": ":h", "reset": ":r", "r": ":r"}


def read_klotski_output(text, prompt):
    lines = text.split("\n")
    blueprint = []
    inside = False
    for line in lines:
        if line.startswith("+---------+"):
            inside = True
            blueprint = []
            continue
        if line.startswith("+---   ---+"):
            inside = False
            continue
        if inside and line.startswith("|"):
            blueprint.append([line[2 + 2 * k] for k in range(4)])
    messages = []
    for line in lines:
        line = line.strip()
        if line == "" or line.startswith("|") or line.startswith("+"):
            continue
        if line.startswith(KLOTSKI_SKIP):
            continue
        messages.append(line)
    hint_screen = "Hint: This is an intermediate" in text
    mode = "move"
    if "(y/n)" in text:
        mode = "confirm"
    elif "Press Enter" in prompt or "Press Enter" in text:
        mode = "continue"
    return {
        "messages": messages,
        "blueprint": blueprint if hint_screen else [],
        "mode": mode,
    }


def to_klotski_command(typed, mode):
    if mode == "continue":
        return ""
    words = typed.strip().lower().split()
    if mode == "move" and len(words) == 1 and words[0] in PLAYER_WORDS:
        return PLAYER_WORDS[words[0]]
    return typed.strip()


def play_klotski(difficulty, energy, ask=None):
    bay = klotski()
    if ask is None:
        try:
            result = bay.play_klotski(difficulty=difficulty, energy=energy)
        except (KeyboardInterrupt, EOFError):
            result = None
        return bay, result

    captured = io.StringIO()

    def bridge_input(prompt=""):
        text = captured.getvalue()
        captured.seek(0)
        captured.truncate()
        view = read_klotski_output(text + str(prompt), str(prompt))
        typed = ask(bay, view)
        if typed is None:
            return ":q"
        return to_klotski_command(typed, view["mode"])

    real_input = builtins.input
    builtins.input = bridge_input
    try:
        with contextlib.redirect_stdout(captured):
            result = bay.play_klotski(difficulty=difficulty, energy=energy)
    except (KeyboardInterrupt, EOFError):
        result = None
    finally:
        builtins.input = real_input
    return bay, result
