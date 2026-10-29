"""Curses terminal interface for the importable Lights Out game."""

import argparse
import curses
import os
import sys

from lights_out_game import LightsOutGame


WIDTH = 80
HEIGHT = 24


def _positive_dimension(text):
    try:
        value = int(text)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be a positive integer") from error
    if value < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return value


def _board_fits_play_area(rows, cols):
    row_label_width = len(str(rows - 1))
    board_line_width = row_label_width + 2 + 4 * cols
    return rows + 4 <= HEIGHT and board_line_width <= WIDTH - 1


def _put(screen, row, text, style=0):
    """Draw a line without writing into the terminal's final column."""
    screen.addnstr(row, 0, text, WIDTH - 1, style)


def _draw_screen(screen, game, message, selected_row, selected_col):
    move_text = str(game.move_count)
    if len(move_text) > 16:
        move_text = "..." + move_text[-16:]

    if game.is_solved():
        status = "*** VICTORY! ***  Solved in {} moves.".format(move_text)
        help_text = "Press n to play again or q to quit."
    else:
        status = "ON [#]   OFF [ ]   Moves: {}".format(move_text)
        help_text = message or (
            "Goal: all lights ON. Arrows/WASD move; Space/Enter toggles; "
            "n=new; q=quit."
        )

    screen.erase()
    _put(screen, 0, "LIGHTS OUT", curses.A_BOLD)
    _put(screen, 1, status)
    _put(screen, 2, help_text)

    row_label_width = len(str(game.rows - 1))
    for row_index, row in enumerate(game.board):
        screen_row = row_index + 3
        prefix = "{:>{width}} | ".format(row_index, width=row_label_width)
        _put(screen, screen_row, prefix)
        column = len(prefix)
        for col_index, is_on in enumerate(row):
            cell = "[#]" if is_on else "[ ]"
            style = (
                curses.A_REVERSE
                if row_index == selected_row and col_index == selected_col
                else curses.A_NORMAL
            )
            screen.addnstr(screen_row, column, cell, len(cell), style)
            column += len(cell)
            if col_index < game.cols - 1:
                screen.addnstr(screen_row, column, " ", 1)
                column += 1

    screen.refresh()


def _draw_resize_message(screen, rows, cols):
    screen.erase()
    if cols > 1:
        for row, text in enumerate(("Resize to 80 x 24", "Press q to quit")):
            if row < rows:
                screen.addnstr(row, 0, text, min(cols - 1, WIDTH - 1))
    screen.refresh()


def _read_key(screen, game, message, selected_row, selected_col):
    """Read a key while pausing play if the terminal is too small."""
    previous_size = None
    movement_keys = {
        curses.KEY_UP: "up",
        curses.KEY_DOWN: "down",
        curses.KEY_LEFT: "left",
        curses.KEY_RIGHT: "right",
    }

    while True:
        actual_size = os.get_terminal_size(sys.stdin.fileno())
        size = (max(1, actual_size.lines), max(1, actual_size.columns))
        if size != screen.getmaxyx():
            curses.resizeterm(*size)

        if size != previous_size:
            previous_size = size
            if size[0] >= HEIGHT and size[1] >= WIDTH:
                _draw_screen(screen, game, message, selected_row, selected_col)
            else:
                _draw_resize_message(screen, *size)

        try:
            key = screen.get_wch()
        except curses.error:
            continue

        if key == curses.KEY_RESIZE:
            previous_size = None
            continue
        if key in ("q", "Q", "\x03"):
            return "q"
        if size[0] < HEIGHT or size[1] < WIDTH:
            continue
        if key in movement_keys:
            return movement_keys[key]
        if isinstance(key, str):
            if key in ("\r", "\n"):
                return "enter"
            return key.lower()


def _run_game(screen, rows, cols):
    curses.noecho()
    screen.keypad(True)
    screen.timeout(100)
    try:
        curses.curs_set(0)
    except curses.error:
        pass

    game = LightsOutGame(rows=rows, cols=cols)
    message = ""
    selected_row = 0
    selected_col = 0
    movements = {
        "up": (-1, 0),
        "w": (-1, 0),
        "down": (1, 0),
        "s": (1, 0),
        "left": (0, -1),
        "a": (0, -1),
        "right": (0, 1),
        "d": (0, 1),
    }

    while True:
        key = _read_key(screen, game, message, selected_row, selected_col)
        if key == "q":
            return
        if key == "n":
            game.shuffle()
            message = "New puzzle. Move the highlighted cell."
            selected_row = 0
            selected_col = 0
            continue
        if game.is_solved():
            continue

        if key in movements:
            row_delta, col_delta = movements[key]
            selected_row = min(max(selected_row + row_delta, 0), game.rows - 1)
            selected_col = min(max(selected_col + col_delta, 0), game.cols - 1)
            message = ""
        elif key in (" ", "enter"):
            game.press(selected_row, selected_col)
            message = ""


def main(argv=None):
    """Run the terminal game. Defaults to a 4x4 board."""
    parser = argparse.ArgumentParser(
        description="Play a configurable Lights Out puzzle in the terminal.",
        formatter_class=lambda prog: argparse.HelpFormatter(prog, width=80),
    )
    parser.add_argument(
        "--rows", type=_positive_dimension, default=4,
        help="number of rows (default: 4)",
    )
    parser.add_argument(
        "--cols", type=_positive_dimension, default=4,
        help="number of columns (default: 4)",
    )
    arguments = parser.parse_args(argv)

    if not _board_fits_play_area(arguments.rows, arguments.cols):
        print(
            "Board is too large for the 80x24 display; reduce rows or columns.",
            file=sys.stderr,
        )
        return 2
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print("Run this game in an interactive terminal (without -T).")
        return 0

    os.environ.pop("COLUMNS", None)
    os.environ.pop("LINES", None)
    curses.use_env(False)
    try:
        curses.wrapper(_run_game, arguments.rows, arguments.cols)
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
