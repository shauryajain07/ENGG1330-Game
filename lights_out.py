"""Importable Lights Out game logic with a small terminal interface.

The game uses only Python's standard library. Coordinates passed to ``press``
are zero-based, with (0, 0) at the top-left corner.
"""

import argparse
import os
import select
import shutil
import sys

from lights_out_game import LightsOutGame

try:
    import termios
    import tty
except ImportError:  # The bounded character input is used on POSIX terminals.
    termios = None
    tty = None


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
    return rows + 4 <= 24 and board_line_width <= 80


def _terminal_size():
    size = shutil.get_terminal_size(fallback=(80, 24))
    return size.columns, size.lines


def _read_key_without_echo():
    if sys.stdin.isatty() and sys.stdout.isatty() and os.name == "posix" and tty:
        file_descriptor = sys.stdin.fileno()
        old_settings = termios.tcgetattr(file_descriptor)
        try:
            tty.setraw(file_descriptor)
            key = sys.stdin.read(1)
            if key == "\x03":
                raise KeyboardInterrupt
            return key
        finally:
            termios.tcsetattr(file_descriptor, termios.TCSADRAIN, old_settings)
    line = sys.stdin.readline()
    if line == "":
        raise EOFError
    return line[:1]


def _wrapped_lines(message, width):
    words = message.split()
    lines = []
    current = ""
    for word in words:
        while len(word) > width:
            if current:
                lines.append(current)
                current = ""
            lines.append(word[:width])
            word = word[width:]
        if not word:
            continue
        if current and len(current) + 1 + len(word) > width:
            lines.append(current)
            current = word
        elif current:
            current += " " + word
        else:
            current = word
    if current:
        lines.append(current)
    return lines


def _pause_for_resize(width, height):
    message = "Resize to 80x24" if width >= 15 else "80x24 needed"
    lines = _wrapped_lines(message, max(1, width))[:max(1, height)]
    screen = "\033[?25h\033[2J\033[H" + "\r\n".join(
        line[:width] for line in lines
    )
    sys.stdout.write(screen)
    sys.stdout.flush()
    _read_key_without_echo()


def _wait_for_playable_terminal():
    while True:
        width, height = _terminal_size()
        if width >= 80 and height >= 24:
            return
        _pause_for_resize(width, height)


def _read_key():
    """Read one key without echoing it or requiring the user to press Enter."""
    if not (sys.stdin.isatty() and sys.stdout.isatty() and os.name == "posix" and tty):
        line = sys.stdin.readline()
        if line == "":
            raise EOFError
        key = line[:1]
        return "enter" if key in ("\r", "\n") else key.lower()

    file_descriptor = sys.stdin.fileno()
    old_settings = termios.tcgetattr(file_descriptor)
    try:
        tty.setraw(file_descriptor)
        key = sys.stdin.read(1)
        if key == "":
            raise EOFError
        if key == "\x03":
            raise KeyboardInterrupt
        if key == "\x04":
            raise EOFError
        if key == "\x1b":
            if not select.select([file_descriptor], [], [], 0.05)[0]:
                return "escape"
            sequence_start = sys.stdin.read(1)
            if sequence_start not in ("[", "O"):
                return "escape"
            if not select.select([file_descriptor], [], [], 0.05)[0]:
                return "escape"
            direction = sys.stdin.read(1)
            return {"A": "up", "B": "down", "C": "right", "D": "left"}.get(
                direction, "escape"
            )
        if key in ("\r", "\n"):
            return "enter"
        return key.lower()
    finally:
        termios.tcsetattr(file_descriptor, termios.TCSADRAIN, old_settings)


def _draw_screen(game, message, selected_row, selected_col):
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

    row_label_width = len(str(game.rows - 1))
    lines = ["LIGHTS OUT", status, help_text]
    for row_index, row in enumerate(game.board):
        cells = []
        for col_index, is_on in enumerate(row):
            cell = "[#]" if is_on else "[ ]"
            if row_index == selected_row and col_index == selected_col:
                cell = "\033[7m{}\033[0m".format(cell)
            cells.append(cell)
        lines.append(
            "{:>{width}} | {}".format(
                row_index, " ".join(cells), width=row_label_width
            )
        )

    screen = "\033[?25l\033[2J\033[H" + "\r\n".join(lines)
    sys.stdout.write(screen)
    sys.stdout.flush()


def main(argv=None):
    """Run the terminal game. Defaults to a 4x4 board."""
    parser = argparse.ArgumentParser(
        description="Play a configurable Lights Out puzzle in the terminal.",
        formatter_class=lambda prog: argparse.HelpFormatter(prog, width=80),
    )
    parser.add_argument("--rows", type=_positive_dimension, default=4, help="number of rows (default: 4)")
    parser.add_argument("--cols", type=_positive_dimension, default=4, help="number of columns (default: 4)")
    arguments = parser.parse_args(argv)

    if not _board_fits_play_area(arguments.rows, arguments.cols):
        print("Board is too large for the 80x24 display; reduce rows or columns.", file=sys.stderr)
        return 2

    try:
        _wait_for_playable_terminal()
        game = LightsOutGame(rows=arguments.rows, cols=arguments.cols)
        message = ""
        selected_row = 0
        selected_col = 0
        while True:
            _wait_for_playable_terminal()
            _draw_screen(game, message, selected_row, selected_col)

            key = _read_key()
            if key == "q":
                return 0
            if key == "n":
                game.shuffle()
                message = "New puzzle. Move the highlighted cell."
                selected_row = 0
                selected_col = 0
                continue
            if game.is_solved():
                continue

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
            if key in movements:
                row_delta, col_delta = movements[key]
                selected_row = min(max(selected_row + row_delta, 0), game.rows - 1)
                selected_col = min(max(selected_col + col_delta, 0), game.cols - 1)
                message = ""
            elif key in (" ", "enter"):
                game.press(selected_row, selected_col)
                message = ""
    except (EOFError, KeyboardInterrupt):
        return 0
    finally:
        sys.stdout.write("\033[?25h\r\n")
        sys.stdout.flush()


if __name__ == "__main__":
    raise SystemExit(main())
