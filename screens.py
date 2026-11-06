import textwrap

import art
import story


WIDTH = 80
HEIGHT = 24
LINE_WIDTH = WIDTH - 1
BODY_ROWS = 17

CHAPTER_NAMES = {
    1: "THE SHARD FIELD",
    2: "LIFE SUPPORT GRID",
    3: "THE DRIVE BAY",
}

MENU_ITEMS = ["START MISSION", "HOW TO PLAY", "DIFFICULTY", "QUIT"]


def wrap(text, width=LINE_WIDTH):
    lines = []
    for paragraph in text.split("\n"):
        if paragraph == "":
            lines.append("")
        else:
            lines.extend(textwrap.wrap(paragraph, width))
    return lines


def center_block(lines):
    widest = 0
    for line in lines:
        widest = max(widest, len(line))
    padding = " " * max(0, (LINE_WIDTH - widest) // 2)
    result = []
    for line in lines:
        result.append(padding + line)
    return result


def center(text):
    return center_block([text])[0]


def side_by_side(left, right, left_width):
    result = []
    for index in range(max(len(left), len(right))):
        left_part = ""
        right_part = ""
        if index < len(left):
            left_part = left[index]
        if index < len(right):
            right_part = right[index]
        result.append(left_part.ljust(left_width) + right_part)
    return result


def add(lines, text, colour="normal"):
    lines.append((text, colour))


def add_many(lines, texts, colour="normal"):
    for text in texts:
        add(lines, text, colour)


def finish(lines):
    final = []
    for text, colour in lines[:HEIGHT]:
        final.append((text[:LINE_WIDTH], colour))
    while len(final) < HEIGHT:
        final.append(("", "normal"))
    return final


def battery_bar(battery):
    filled = battery // 10
    return "[" + "#" * filled + "." * (10 - filled) + "] " + str(battery) + "%"


def battery_colour(battery):
    if battery > 50:
        return "green"
    if battery > 20:
        return "yellow"
    return "red"


def menu_screen(selected, difficulty):
    lines = []
    add(lines, "")
    add_many(lines, art.TITLE_LOGO, "cyan")
    add(lines, "")
    add(lines, center("~ escape the black hole with TARS in three puzzles ~"), "yellow")
    add(lines, "")
    add_many(lines, center_block(art.TITLE_SHIP))
    add(lines, "")
    for index in range(len(MENU_ITEMS)):
        label = MENU_ITEMS[index]
        if label == "DIFFICULTY":
            label = "DIFFICULTY:  < " + art.DIFFICULTY_NAMES[difficulty] + " >"
        label = str(index + 1) + "  " + label
        if index == selected:
            add(lines, center(">>  " + label.ljust(30) + "  <<"), "selected")
        else:
            add(lines, center("    " + label.ljust(30) + "    "))
    add(lines, "")
    add(lines, "")
    add(lines, center("UP/DOWN or 1-4 to pick   ENTER to select   LEFT/RIGHT difficulty"), "dim")
    return finish(lines)


def name_screen(typed):
    lines = []
    add(lines, "")
    add(lines, center("NEW MISSION // CREW REGISTRATION"), "cyan")
    add(lines, "")
    add_many(lines, center_block(art.TARS), "green")
    add(lines, "")
    add(lines, center("TARS: \"New crew member detected. What do I call you? Humor: 75%.\""))
    add(lines, "")
    add(lines, center("(type a name, up to 12 letters, then press ENTER)"), "dim")
    while len(lines) < HEIGHT - 2:
        add(lines, "")
    add(lines, "NAME > " + typed, "yellow")
    add(lines, "Leave it empty to be called Rookie.", "dim")
    return finish(lines)


def how_to_play_screen(page_number):
    lines = []
    total = len(story.HOW_TO_PLAY)
    add(lines, "HOW TO PLAY  (page " + str(page_number + 1) + "/" + str(total) + ")", "cyan")
    add(lines, "-" * LINE_WIDTH, "dim")
    add(lines, "")
    page = story.HOW_TO_PLAY[page_number]
    add(lines, page[0], "yellow")
    add_many(lines, page[1:])
    while len(lines) < HEIGHT - 1:
        add(lines, "")
    add(lines, "ENTER or RIGHT = next page    LEFT = back    Q = title screen", "dim")
    return finish(lines)


def story_screen(page, letters_shown, finished):
    lines = []
    add(lines, page["title"], "cyan")
    add(lines, "-" * LINE_WIDTH, "dim")
    add(lines, "")
    add_many(lines, center_block(page["art"]), "green")
    add(lines, "")
    add_many(lines, wrap(page["text"][:letters_shown]))
    while len(lines) < HEIGHT - 1:
        add(lines, "")
    if finished:
        add(lines, "Press ENTER to continue        (Q = back to title screen)", "yellow")
    else:
        add(lines, "Press ENTER to show all", "dim")
    return finish(lines)


LEVEL_KEYS = ["easy", "medium", "hard"]


def level_label(level):
    return art.DIFFICULTY_NAMES[LEVEL_KEYS[level]]


def level_meter(level):
    parts = []
    for index in range(len(LEVEL_KEYS)):
        name = level_label(index)
        if index == level:
            parts.append("[" + name + "]")
        else:
            parts.append(" " + name.lower() + " ")
    return "LEVEL " + "".join(parts)


def header_lines(game):
    lines = []
    chapter = game.chapter()
    title = "WORMHOLE  |  CHAPTER " + str(chapter) + "/3: " + CHAPTER_NAMES[chapter]
    badge = level_label(game.level) + "  " + game.player_name.upper()
    add(lines, title + badge.rjust(LINE_WIDTH - len(title)), "cyan")
    status = "BATTERY " + battery_bar(game.battery)
    free = game.free_hints["navigation"] + game.free_hints["power"] + game.free_hints["engine"]
    if free > 0:
        status += "   FREE HINTS: " + str(free)
    if game.coffee_shield:
        status += "   DEFLECTOR: ON"
    add(lines, status, battery_colour(game.battery))
    add(lines, "-" * LINE_WIDTH, "dim")
    return lines


def footer_lines(game, typed):
    lines = []
    message = wrap(game.message)
    if game.showing_help:
        message = []
    while len(message) < 2:
        message.append("")
    colour = "yellow"
    if "CLANG" in game.message or "Not enough" in game.message:
        colour = "red"
    elif "EFFICIENT" in game.message:
        colour = "green"
    add_many(lines, message[-2:], colour)
    add(lines, "> " + typed, "yellow")
    add(lines, command_reminder(game), "dim")
    return lines


def command_reminder(game):
    if game.confirming_restart:
        return "y = yes, restart    n = no, keep going"
    if game.stage in story.CHOICES:
        return "1 / 2 / 3 = choose    help    restart    quit"
    if game.stage == "navigation":
        return "t r c = tap   f r c = flag   b r c = break   hint   skip   help   quit"
    if game.stage == "power":
        return "p row col = press   hint   skip   help   restart   quit"
    if game.stage == "engine":
        return "ENTER = open the drive bay    skip    help    quit"
    return "ENTER = mission report"


def navigation_body(game):
    field = game.field
    board = []
    numbers = "     "
    for col in range(field.cols):
        numbers += str(col + 1).center(3)
    board.append(numbers)
    board.append("    +" + "-" * (field.cols * 3) + "+")
    for row in range(field.rows):
        cells = ""
        for col in range(field.cols):
            cells += field.symbol(row, col).center(3)
        board.append(str(row + 1).rjust(3) + " |" + cells + "|")
    board.append("    +" + "-" * (field.cols * 3) + "+")

    found = field.safe_found()
    total = field.safe_total()
    filled = found * 12 // total
    panel = list(art.ASTEROIDS)
    panel.append("")
    panel.append(level_meter(game.level))
    panel.append("Route  [" + "=" * filled + " " * (12 - filled) + "] "
                 + str(found) + "/" + str(total))
    panel.append("Shards: " + str(field.mine_count) + "   flags left: "
                 + str(field.flags_left()) + "   hits: " + str(field.strikes))
    panel.append("")
    panel.append("#  not scanned    .  empty space")
    panel.append("F  your flag      @  shard hit")
    panel.append("1-8  shards touching this square")
    panel.append("Clean run = next system gets harder")
    return side_by_side(board, panel, 36)


def power_body(game):
    grid = game.grid
    board = []
    numbers = "      "
    for col in range(grid.size):
        numbers += str(col + 1).center(5)
    board.append(numbers)
    board.append("     +" + "-" * (grid.size * 5) + "+")
    for row in range(grid.size):
        cells = ""
        for col in range(grid.size):
            if grid.lights[row][col]:
                cells += " [#] "
            else:
                cells += " [ ] "
        board.append(str(row + 1).rjust(4) + " |" + cells + "|")
        if row < grid.size - 1:
            board.append("     |" + " " * (grid.size * 5) + "|")
    board.append("     +" + "-" * (grid.size * 5) + "+")

    if "goose_crew" in game.flags:
        panel = list(art.SIGNAL_FRIEND)
    elif "snacks" in game.flags:
        panel = list(art.TARS_SAD)
    else:
        panel = list(art.SIGNAL)
    panel.append("")
    panel.append(level_meter(game.level))
    total = grid.size * grid.size
    online = total - grid.lights_off()
    panel.append("Online [" + "#" * (online * 12 // total)
                 + " " * (12 - online * 12 // total) + "] " + str(online) + "/" + str(total))
    panel.append("[#] light ON     [ ] light OFF")
    panel.append("Switches pressed: " + str(grid.moves)
                 + "   best: " + str(grid.best_moves))
    panel.append("Goal: turn EVERY light ON")
    panel.append("Few presses = next system harder")
    return side_by_side(board, panel, 36)


def engine_body(game):
    left = ["   +----------+", "   |  ######  |", "   |  # XX #  |", "   |  ######  |",
            "   +----||----+", "    DRIVE CORE"]
    left.extend(["", "   +---------+", "   | A A B G |", "   | C X X D |",
                 "   | C X X D |", "   +---   ---+", "     cradle"])
    panel = [
        "DRIVE BAY BRIEFING",
        "",
        level_meter(game.level),
        "",
        "Free 3 drive cores, one bay at a time.",
        "Slide the big X into the gap at the",
        "bottom middle of each bay.",
        "",
        "  A up / B left     slide a crate",
        "  hint   halfway blueprint (1 energy)",
        "  reset  start this bay again",
        "  quit   give up on the bay",
        "",
        "Hint energy: " + str(game.engine_energy()) + "  (paid ones cost 6 battery)",
        "Fewer moves = harder next mission.",
    ]
    return side_by_side(left, panel, 28)


def crate_rows(rows, label_rows=True):
    picture = ["     1    2    3    4"] if label_rows else ["     BLUEPRINT"]
    picture.append("   +" + "-" * 20 + "+")
    for row_number in range(len(rows)):
        cells = ""
        for letter in rows[row_number]:
            if letter == " ":
                cells += "  .  "
            else:
                cells += " " + letter * 3 + " "
        label = "   "
        if label_rows:
            label = str(row_number + 1).rjust(2) + " "
        picture.append(label + "|" + cells + "|")
    picture.append("   +-----" + " " * 10 + "-----+")
    picture.append("         ^^ CRADLE ^^")
    return picture


def drive_bay_screen(game, bay, view, typed, energy_given):
    used = max(0, energy_given - (bay.klotski_energy or 0))
    paid = max(0, used - game.free_hints["engine"])
    battery = max(0, game.battery - paid * 6)
    lines = []
    title = "WORMHOLE  |  CHAPTER 3/3: THE DRIVE BAY"
    badge = level_label(game.level) + "  " + game.player_name.upper()
    add(lines, title + badge.rjust(LINE_WIDTH - len(title)), "cyan")
    add(lines, "BATTERY " + battery_bar(battery) + "   HINT ENERGY: "
        + str(bay.klotski_energy), battery_colour(battery))
    add(lines, "-" * LINE_WIDTH, "dim")

    left = crate_rows(bay.klotski_board)
    freed = 3 - bay.klotski_gameCount
    panel_width = LINE_WIDTH - 34
    if view["blueprint"]:
        panel = crate_rows(view["blueprint"], label_rows=False)
        panel.append("")
        panel.extend(wrap("TARS: \"This is the bay halfway solved. Copy it, "
                          "then finish the job.\"", panel_width))
    else:
        panel = [level_meter(game.level), ""]
        panel.append("Cores freed  [" + "X" * freed + "." * (3 - freed) + "]  "
                     + str(freed) + "/3")
        panel.append("Moves so far " + str(sum(bay.klotski_moveCount))
                     + "   par " + str(bay.klotski_moveThreshold))
        panel.append("")
        panel.append("XXX = drive core    AAA = crate")
        panel.append("Slide X into the gap at the bottom")
        panel.append("")
        notes = " ".join(view["messages"])
        panel.extend(wrap(notes, panel_width)[-6:])
    body = side_by_side(left, panel, 34)[:BODY_ROWS]
    while len(body) < BODY_ROWS:
        body.append("")
    add_many(lines, body)

    if view["mode"] == "confirm":
        message, reminder = "Use 1 hint energy to see the halfway blueprint?", "y = yes    n = no"
    elif view["mode"] == "continue":
        message, reminder = "", "ENTER = continue"
        if bay.klotski_gameCount == 0:
            message = "All three drive cores are free! TARS is impressed. Mostly."
        elif not view["blueprint"]:
            message = "Core freed! TARS loads the next bay."
    else:
        message = "Type a crate letter and a direction, like: A up"
        reminder = "A up / B left = slide   hint   reset   quit"
    add(lines, message, "yellow")
    add(lines, "")
    add(lines, "> " + typed, "yellow")
    add(lines, reminder, "dim")
    return finish(lines)


def choice_body(game):
    scene = game.current_choice()
    body = [scene["title"], ""]
    body.extend(center_block(scene["art"]))
    body.append("")
    body.extend(wrap(scene["text"]))
    body.append("")
    for index in range(len(scene["options"])):
        body.append("  " + str(index + 1) + "  " + scene["options"][index])
    return body


def game_screen(game, typed):
    lines = header_lines(game)
    if game.showing_help:
        body = ["TARS HELP DESK", ""] + art.TARS + [""]
        body.extend(wrap(game.help_text()))
        body.append("")
        body.append("Type any command to carry on.")
    elif game.stage in story.CHOICES:
        body = choice_body(game)
    elif game.stage == "navigation":
        body = navigation_body(game)
    elif game.stage == "power":
        body = power_body(game)
    elif game.stage == "engine":
        body = engine_body(game)
    else:
        body = ["The drive core is home. Press ENTER."]
    body = body[:BODY_ROWS]
    while len(body) < BODY_ROWS:
        body.append("")
    add_many(lines, body)
    lines.extend(footer_lines(game, typed))
    return finish(lines)


def level_path_text(game):
    names = []
    for level in game.level_path:
        names.append(level_label(level))
    return " > ".join(names)


def report_screen(game):
    lines = []
    ending = story.ENDINGS[game.ending]
    add(lines, "MISSION REPORT  //  PILOT " + game.player_name.upper(), "cyan")
    add(lines, "-" * LINE_WIDTH, "dim")
    add(lines, ending["title"], "yellow")
    add(lines, "")
    add(lines, "  SCORE  " + str(game.score) + "/100      RATING  " + game.stars()
        + "      STARTED AS  " + art.DIFFICULTY_NAMES[game.difficulty], "green")
    add(lines, "")
    scores = game.part_scores()
    add(lines, "  Battery left      {:>3}%                 {:>4.1f} / 40"
        .format(game.battery, scores["battery"]))
    add(lines, "  Shard Field       " + chapter_summary(game, "navigation").ljust(22)
        + "{:>4.1f} / 20".format(scores["navigation"]))
    add(lines, "  Life Support Grid " + chapter_summary(game, "power").ljust(22)
        + "{:>4.1f} / 20".format(scores["power"]))
    add(lines, "  Drive Bay         " + chapter_summary(game, "engine").ljust(22)
        + "{:>4.1f} / 20".format(scores["engine"]))
    add(lines, "  Level path        " + level_path_text(game), "cyan")
    add(lines, "  Next mission      " + art.DIFFICULTY_NAMES[game.next_difficulty]
        + "  (set by your drive bay run)", "cyan")
    add(lines, "")
    add(lines, "  WHAT HAPPENED NEXT", "yellow")
    epilogue = game.epilogue()
    if len(epilogue) == 0:
        epilogue = ["Nothing weird happened. TARS finds this suspicious."]
    for line in epilogue:
        add(lines, "  - " + line)
    add(lines, "")
    add_many(lines, center_block(art.SEED_VAULT), "green")
    while len(lines) < HEIGHT - 1:
        add(lines, "")
    lines = lines[:HEIGHT - 1]
    add(lines, "R = fly again     M = title screen     Q = quit game", "yellow")
    return finish(lines)


def chapter_summary(game, stage):
    if stage in game.skipped:
        return "skipped"
    if stage == "navigation":
        return str(game.field.strikes) + " hit(s), " + str(game.field.hints_used) + " hint(s)"
    if stage == "power":
        return str(game.grid.moves) + " presses (best " + str(game.grid.best_moves) + ")"
    return str(game.bay_moves) + " moves (par " + str(game.bay_threshold) + ")"


def resize_lines(rows, cols):
    message = [
        "Window too small!",
        "Please make it at least",
        str(WIDTH) + " x " + str(HEIGHT) + ".",
        "Now: " + str(cols) + " x " + str(rows),
        "(q quits)",
    ]
    result = []
    for line in message[:rows]:
        result.append(line[:max(0, cols - 1)])
    return result
