# Standalone Lights Out interface; WORMHOLE reuses its rules from lights_out_game.py.
import argparse
import curses
import os
import sys

from .lights_out_game import LightsOutGame


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
    column_width = max(3, len(str(cols - 1)))
    board_line_width = row_label_width + 3 + cols * column_width + cols - 1
    return rows + 5 <= HEIGHT and board_line_width <= WIDTH - 1


def _put(screen, row, text, style=0):
    screen.addnstr(row, 0, text, WIDTH - 1, style)


def _draw_screen(screen, game, message, input_text):
    move_text = str(game.move_count)
    if len(move_text) > 16:
        move_text = "..." + move_text[-16:]

    if game.is_solved():
        status = "*** VICTORY! ***  Solved in {} moves.".format(move_text)
        help_text = "Press n to play again or q to quit."
    else:
        status = "ON [#]   OFF [ ]   Moves: {}".format(move_text)
        help_text = message or (
            "Goal: all lights ON. Type row col + Enter (0-based); n=new; q=quit."
        )

    screen.erase()
    _put(screen, 0, "LIGHTS OUT", curses.A_BOLD)
    _put(screen, 1, status)
    _put(screen, 2, help_text)

    row_label_width = len(str(game.rows - 1))
    column_width = max(3, len(str(game.cols - 1)))
    board_prefix = " " * (row_label_width + 3)
    column_labels = board_prefix + " ".join(
        "{:^{width}}".format(col_index, width=column_width)
        for col_index in range(game.cols)
    )
    _put(screen, 3, column_labels)

    for row_index, row in enumerate(game.board):
        screen_row = row_index + 4
        prefix = "{:>{width}} | ".format(row_index, width=row_label_width)
        _put(screen, screen_row, prefix)
        column = len(prefix)
        for col_index, is_on in enumerate(row):
            cell = "[#]" if is_on else "[ ]"
            screen.addnstr(
                screen_row, column, cell.center(column_width), column_width
            )
            column += column_width
            if col_index < game.cols - 1:
                screen.addnstr(screen_row, column, " ", 1)
                column += 1

    _put(screen, game.rows + 4, "Move (row col): {}".format(input_text))

    screen.refresh()


def _draw_resize_message(screen, rows, cols):
    screen.erase()
    if cols > 1:
        for row, text in enumerate(("Resize to 80 x 24", "Press q to quit")):
            if row < rows:
                screen.addnstr(row, 0, text, min(cols - 1, WIDTH - 1))
    screen.refresh()


def _read_move(screen, game, message):
    previous_size = None
    input_text = ""

    while True:
        actual_size = os.get_terminal_size(sys.stdin.fileno())
        size = (max(1, actual_size.lines), max(1, actual_size.columns))
        if size != screen.getmaxyx():
            curses.resizeterm(*size)

        if size != previous_size:
            previous_size = size
            if size[0] >= HEIGHT and size[1] >= WIDTH:
                _draw_screen(screen, game, message, input_text)
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
            return "quit", ""
        if size[0] < HEIGHT or size[1] < WIDTH:
            continue
        if key in ("n", "N"):
            return "new", ""
        if key in (curses.KEY_ENTER, "\r", "\n"):
            if input_text.strip():
                return "coordinates", input_text
            continue
        if key in (curses.KEY_BACKSPACE, "\b", "\x7f"):
            input_text = input_text[:-1]
            _draw_screen(screen, game, message, input_text)
            continue
        if isinstance(key, str):
            if key.isprintable() and len(input_text) < 24:
                input_text += key
                _draw_screen(screen, game, message, input_text)


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

    while True:
        command, coordinates = _read_move(screen, game, message)
        if command == "quit":
            return
        if command == "new":
            game.shuffle()
            message = "New puzzle. Enter a row and column to toggle a cell."
            continue
        if game.is_solved():
            message = "Already solved. Press n for a new puzzle or q to quit."
            continue

        try:
            game.press_from_text(coordinates)
        except (ValueError, IndexError):
            message = "Enter row col: row 0-{}, column 0-{}.".format(
                game.rows - 1, game.cols - 1
            )
            continue
        message = ""


def main(argv=None):
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
