import curses
import os
import sys
import time

from game import adapters, screens
from game.adventure import Adventure


# This module owns terminal input and drawing; Adventure owns mission state.
DIFFICULTIES = ["easy", "medium", "hard"]
ENTER_KEYS = [10, 13, curses.KEY_ENTER]
BACKSPACE_KEYS = [8, 127, curses.KEY_BACKSPACE]
COLOURS = {}


def set_cursor(visible):
    try:
        curses.curs_set(visible)
    except curses.error:
        pass


def setup_colours():
    if not curses.has_colors():
        return
    curses.start_color()
    try:
        curses.use_default_colors()
        background = -1
    except curses.error:
        background = curses.COLOR_BLACK
    names = [
        ("cyan", curses.COLOR_CYAN),
        ("yellow", curses.COLOR_YELLOW),
        ("green", curses.COLOR_GREEN),
        ("red", curses.COLOR_RED),
    ]
    number = 1
    for name, colour in names:
        curses.init_pair(number, colour, background)
        COLOURS[name] = number
        number += 1


def style_for(colour):
    if colour == "selected":
        return curses.A_REVERSE | curses.A_BOLD
    if colour == "dim":
        return curses.A_DIM
    if colour in COLOURS:
        return curses.color_pair(COLOURS[colour]) | curses.A_BOLD
    return curses.A_NORMAL


def sync_size(screen):
    try:
        actual = os.get_terminal_size(sys.stdout.fileno())
    except OSError:
        return
    size = (max(1, actual.lines), max(1, actual.columns))
    if size != screen.getmaxyx():
        curses.resizeterm(*size)


def is_too_small(screen):
    sync_size(screen)
    rows, cols = screen.getmaxyx()
    return rows < screens.HEIGHT or cols < screens.WIDTH


def show_resize_message(screen):
    rows, cols = screen.getmaxyx()
    screen.erase()
    row = 0
    for line in screens.resize_lines(rows, cols):
        try:
            screen.addstr(row, 0, line)
        except curses.error:
            pass
        row += 1
    screen.refresh()


def draw(screen, lines):
    screen.erase()
    row = 0
    for text, colour in lines:
        try:
            screen.addstr(row, 0, text, style_for(colour))
        except curses.error:
            pass
        row += 1
    screen.refresh()


def wait_for_key(screen):
    while True:
        key = screen.getch()
        if key == curses.KEY_RESIZE:
            return "resize"
        if is_too_small(screen):
            show_resize_message(screen)
            if key in (ord("q"), ord("Q")):
                return "quit"
            continue
        return key


def type_text(screen, build_lines, max_length):
    typed = ""
    set_cursor(1)
    while True:
        if is_too_small(screen):
            show_resize_message(screen)
        else:
            lines = build_lines(typed)
            draw(screen, lines)
            screen.move(screens.HEIGHT - 2, min(len(lines[-2][0]), screens.LINE_WIDTH - 1))
        key = wait_for_key(screen)
        if key == "resize":
            continue
        if key == "quit":
            set_cursor(0)
            return None
        if key in ENTER_KEYS:
            set_cursor(0)
            return typed
        if key in BACKSPACE_KEYS:
            typed = typed[:-1]
        elif 32 <= key <= 126 and len(typed) < max_length:
            typed += chr(key)


def show_story_page(screen, page):
    screen.nodelay(True)
    letters = 0
    total = len(page["text"])
    while letters < total:
        key = screen.getch()
        if key in ENTER_KEYS or key == ord(" "):
            break
        if is_too_small(screen):
            show_resize_message(screen)
        else:
            draw(screen, screens.story_screen(page, letters, False))
            letters += 2
        time.sleep(0.015)
    screen.nodelay(False)
    while True:
        if is_too_small(screen):
            show_resize_message(screen)
        else:
            draw(screen, screens.story_screen(page, total, True))
        key = wait_for_key(screen)
        if key == "quit" or key in (ord("q"), ord("Q")):
            return False
        if key in ENTER_KEYS or key == ord(" "):
            return True


def show_story_queue(screen, game):
    for page in game.take_story_pages():
        if not show_story_page(screen, page):
            return False
    return True


def run_menu(screen, difficulty):
    selected = 0
    while True:
        if is_too_small(screen):
            show_resize_message(screen)
        else:
            draw(screen, screens.menu_screen(selected, difficulty))
        key = wait_for_key(screen)
        if key == "resize":
            continue
        if key == "quit" or key in (ord("q"), ord("Q")):
            return "QUIT", difficulty
        if key == curses.KEY_UP:
            selected = (selected - 1) % len(screens.MENU_ITEMS)
        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % len(screens.MENU_ITEMS)
        elif key in (ord("1"), ord("2"), ord("3"), ord("4")):
            selected = key - ord("1")
            if selected != 2:
                return screens.MENU_ITEMS[selected], difficulty
        # Difficulty is edited in place; other selections return to play().
        elif key in (curses.KEY_LEFT, curses.KEY_RIGHT) and selected == 2:
            step = 1
            if key == curses.KEY_LEFT:
                step = -1
            position = (DIFFICULTIES.index(difficulty) + step) % 3
            difficulty = DIFFICULTIES[position]
        elif key in ENTER_KEYS:
            if selected == 2:
                position = (DIFFICULTIES.index(difficulty) + 1) % 3
                difficulty = DIFFICULTIES[position]
            else:
                return screens.MENU_ITEMS[selected], difficulty


def run_how_to_play(screen):
    page = 0
    total = len(screens.story.HOW_TO_PLAY)
    while True:
        if is_too_small(screen):
            show_resize_message(screen)
        else:
            draw(screen, screens.how_to_play_screen(page))
        key = wait_for_key(screen)
        if key == "quit" or key in (ord("q"), ord("Q")):
            return
        if key in ENTER_KEYS or key == curses.KEY_RIGHT:
            page += 1
            if page == total:
                return
        elif key == curses.KEY_LEFT and page > 0:
            page -= 1


def ask_name(screen):
    name = type_text(screen, screens.name_screen, 12)
    if name is None:
        return None
    name = name.strip()
    if name == "":
        name = "Rookie"
    return name


def run_drive_bay(screen, game):
    energy = game.engine_energy()

    def ask(bay, view):
        return type_text(
            screen,
            lambda typed: screens.drive_bay_screen(game, bay, view, typed, energy),
            20,
        )

    bay, result = adapters.play_klotski(game.level, energy, ask)
    game.finish_engine(bay, result, energy)


def run_mission(screen, game):
    if not show_story_queue(screen, game):
        return "menu"
    # The model returns transition names; this loop renders their next screen.
    while True:
        if game.stage == "ending":
            if not show_story_queue(screen, game):
                return "menu"
            return show_report(screen, game)
        command = type_text(screen, lambda typed: screens.game_screen(game, typed), 40)
        if command is None:
            return "menu"
        result = game.handle(command)
        if result == "menu":
            return "menu"
        if result == "restart":
            return "restart"
        if result == "klotski":
            run_drive_bay(screen, game)
        if not show_story_queue(screen, game):
            return "menu"


def show_report(screen, game):
    while True:
        if is_too_small(screen):
            show_resize_message(screen)
        else:
            draw(screen, screens.report_screen(game))
        key = wait_for_key(screen)
        if key == "quit" or key in (ord("q"), ord("Q")):
            return "quit"
        if key in (ord("r"), ord("R")):
            return "restart"
        if key in (ord("m"), ord("M")):
            return "menu"


def play(screen):
    set_cursor(0)
    screen.keypad(True)
    setup_colours()
    difficulty = "medium"
    while True:
        choice, difficulty = run_menu(screen, difficulty)
        if choice == "QUIT":
            return
        if choice == "HOW TO PLAY":
            run_how_to_play(screen)
            continue
        name = ask_name(screen)
        if name is None:
            continue
        result = "restart"
        # Rebuild mission state on restart while keeping the chosen pilot/level.
        while result == "restart":
            game = Adventure(difficulty, name)
            result = run_mission(screen, game)
            if game.stage == "ending":
                difficulty = game.next_difficulty
        if result == "quit":
            return


def main():
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print("Please run this game in a terminal window: python3 main.py")
        return
    curses.use_env(False)
    try:
        curses.wrapper(play)
    except KeyboardInterrupt:
        pass
    print("Thanks for playing WORMHOLE! TARS out.")


if __name__ == "__main__":
    main()
