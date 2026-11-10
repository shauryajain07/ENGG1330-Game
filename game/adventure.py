# Mission state machine: story choices lead into the three puzzle stages.
import random

from . import art, story
from .adapters import LifeSupportGrid, ShardField


LEVELS = ["easy", "medium", "hard"]

MINES = [10, 12, 15]
GRIDS = [(3, 3), (4, 4), (5, 6)]

COSTS = {
    "shard_hit": 10,
    "scan_hint": 8,
    "switch": 1,
    "grid_hint": 4,
    "bay_hint": 6,
}

MAX_BATTERY = 100

CHOICE_ORDER = {
    "wakeup": ["coffee", "poem", "belly_rub"],
    "goose": ["frosting", "snacks", "staring"],
    "cat": ["laser", "lift", "lullaby"],
}

NEXT_STAGE = {
    "wakeup": "navigation",
    "goose": "power",
    "cat": "engine",
}

CHAPTER_NUMBERS = {
    "wakeup": 1, "navigation": 1,
    "goose": 2, "power": 2,
    "cat": 3, "engine": 3,
    "ending": 3,
}

RATING_WORDS = {1: "EFFICIENT", 0: "STEADY", -1: "SLOPPY"}


def read_numbers(words):
    # Players enter one-based coordinates; puzzle models use zero-based indexes.
    if len(words) != 3:
        return None
    if not words[1].isdigit() or not words[2].isdigit():
        return None
    return int(words[1]) - 1, int(words[2]) - 1


def efficiency_points(best_moves, moves, paid_hints, worth):
    if moves == 0:
        return 0
    # Score against par, counting each paid hint as two extra moves.
    effort = moves + 2 * paid_hints
    if effort < best_moves:
        effort = best_moves
    return worth * best_moves / effort


def clamp_level(level):
    return max(0, min(len(LEVELS) - 1, level))


class Adventure:
    def __init__(self, difficulty="medium", player_name="Rookie", seed=None):
        self.difficulty = difficulty
        self.player_name = player_name
        self.random = random.Random(seed)
        self.level = LEVELS.index(difficulty)
        self.level_path = [self.level]
        self.ratings = {}
        self.next_difficulty = difficulty
        self.battery = MAX_BATTERY
        self.stage = "wakeup"
        self.flags = []
        self.free_hints = {"navigation": 0, "power": 0, "engine": 0}
        self.free_hints_used = {"navigation": 0, "power": 0, "engine": 0}
        self.coffee_shield = False
        self.skipped = []
        self.confirming_restart = False
        self.showing_help = False
        self.message = ""
        self.story_queue = []
        self.score = 0
        self.ending = ""
        self.field = None
        self.grid = None
        self.bay_moves = 0
        self.bay_threshold = 0
        self.bay_hints_paid = 0
        self.bay_hints_used = 0
        for page in story.PROLOGUE:
            self.add_page(page["title"], page["art"], page["text"])

    def add_page(self, title, picture, text):
        page = {
            "title": title,
            "art": picture,
            "text": text.replace("{name}", self.player_name),
        }
        self.story_queue.append(page)

    def take_story_pages(self):
        pages = self.story_queue
        self.story_queue = []
        return pages

    def chapter(self):
        return CHAPTER_NUMBERS[self.stage]

    def level_name(self):
        return LEVELS[self.level]

    def current_choice(self):
        if self.stage not in story.CHOICES:
            return None
        scene = story.CHOICES[self.stage]
        return {
            "title": scene["title"],
            "art": scene["art"],
            "text": scene["text"].replace("{name}", self.player_name),
            "options": scene["options"],
        }

    def spend(self, amount):
        paid = min(amount, self.battery)
        self.battery -= paid
        return paid

    def gain(self, amount):
        self.battery = min(MAX_BATTERY, self.battery + amount)

    def handle(self, text):
        words = text.strip().lower().split()
        if len(words) == 0:
            if self.stage == "engine" and not self.confirming_restart:
                return "klotski"
            self.message = "Type a command, or 'help' to see the controls."
            return "invalid"
        command = words[0]
        self.showing_help = False

        if self.confirming_restart:
            self.confirming_restart = False
            if command in ("y", "yes"):
                return "restart"
            self.message = "Phew. Mission continues."
            return "ok"

        if command in ("quit", "q", "menu"):
            return "menu"
        if command in ("help", "?"):
            self.showing_help = True
            self.message = self.help_text()
            return "ok"
        if command == "restart":
            self.confirming_restart = True
            self.message = "Restart the whole mission? Type y for yes, n for no."
            return "ok"
        if command == "tars":
            self.message = "TARS: \"Humor setting 75%. I know a black hole joke, but it sucks.\""
            return "ok"
        if command == "knock":
            self.message = "Somewhere beyond the wormhole, something knocks back."
            return "ok"

        if self.stage == "ending":
            self.message = "The mission is over! Press ENTER to see the report."
            return "invalid"
        if command == "skip" and self.stage in ("navigation", "power", "engine"):
            self.skipped.append(self.stage)
            self.finish_puzzle()
            return "ok"
        if self.stage in story.CHOICES:
            return self.make_choice(command)
        if self.stage == "navigation":
            return self.navigation_command(command, words)
        if self.stage == "power":
            return self.power_command(command, words)
        if self.stage == "engine":
            if command in ("go", "start", "open"):
                return "klotski"
            self.message = "Press ENTER to open the drive bay (or type skip)."
            return "invalid"
        return "invalid"

    def help_text(self):
        if self.stage in story.CHOICES:
            return "Type 1, 2 or 3 to choose. Every choice changes something later!"
        if self.stage == "navigation":
            return ("Shard Field: t 3 4 = open row 3, column 4; f 3 4 = flag; "
                    "b 3 4 = break around a clue. hint = safe square (8 battery); "
                    "skip = give up.")
        if self.stage == "power":
            return ("Life Support: p 2 3 = press row 2, column 3 (1 battery). "
                    "hint = switch (4 battery); skip = give up.")
        if self.stage == "engine":
            return ("Drive Bay move examples: I down or X right (when the path is "
                    "clear). Press ENTER to start. hint = blueprint, reset = "
                    "restart, quit = give up.")
        return "Press ENTER to see your mission report."

    def make_choice(self, command):
        if command not in ("1", "2", "3"):
            self.message = "Please type 1, 2 or 3."
            return "invalid"
        choice = CHOICE_ORDER[self.stage][int(command) - 1]
        result = choice

        if choice == "coffee":
            self.coffee_shield = True
        elif choice == "poem":
            self.free_hints["navigation"] += 1
        elif choice == "frosting":
            self.free_hints["power"] += 1
        elif choice == "snacks":
            self.gain(10)
        elif choice == "staring":
            if self.random.random() < 0.5:
                result = "goose_win"
                self.gain(5)
                self.flags.append("goose_crew")
            else:
                result = "goose_lose"
                self.spend(5)
        elif choice == "laser":
            self.free_hints["engine"] += 1
        elif choice == "lift":
            if "belly_rub" in self.flags:
                result = "lift_friend"
                self.free_hints["engine"] += 1
            else:
                result = "lift_angry"
                self.spend(5)
        elif choice == "lullaby":
            self.gain(5)

        if choice != "staring" and choice != "lift":
            self.flags.append(choice)
        picture, text = story.CHOICE_RESULTS[result]
        self.add_page("YOU CHOSE " + command, picture, text)
        self.start_puzzle(NEXT_STAGE[self.stage])
        return "ok"

    def start_puzzle(self, stage):
        self.stage = stage
        self.message = (story.CHAPTER_INTROS[stage] + " Level: "
                        + art.DIFFICULTY_NAMES[self.level_name()] + ".")
        # Derive each board seed from the mission RNG for reproducible missions.
        seed = self.random.randrange(1000000)
        if stage == "navigation":
            self.field = ShardField(MINES[self.level], seed)
        elif stage == "power":
            size, scramble = GRIDS[self.level]
            self.grid = LifeSupportGrid(size, scramble, seed)

    def use_hint(self, puzzle, cost):
        # Use earned hints first; only a paid hint reduces the shared battery.
        if self.free_hints[puzzle] > 0:
            self.free_hints[puzzle] -= 1
            self.free_hints_used[puzzle] += 1
            return "free"
        if self.battery < cost:
            return "no battery"
        self.spend(cost)
        return "paid"

    def hint_label(self, status, cost_name):
        if status == "free":
            return "free hint"
        return "-" + str(COSTS[cost_name]) + " battery"

    def shard_hit_message(self):
        if self.coffee_shield:
            self.coffee_shield = False
            return "CLANG! An ice shard! The deflector takes the hit. No battery lost."
        self.spend(COSTS["shard_hit"])
        return "CLANG! An ice shard hits the hull! -10 battery. The seed vault holds."

    def navigation_command(self, command, words):
        if command in ("t", "tap", "s", "scan", "f", "flag", "b", "break"):
            spot = read_numbers(words)
            if spot is None:
                self.message = "Type it like this: t 3 4  (row 3, column 4)."
                return "invalid"
            row, col = spot
            if not self.field.is_inside(row, col):
                self.message = "Rows and columns go from 1 to " + str(self.field.rows) + "."
                return "invalid"
            if command in ("f", "flag"):
                return self.flag_square(row, col)
            if command in ("b", "break"):
                return self.break_square(row, col)
            return self.tap_square(row, col)

        if command in ("h", "hint"):
            status = self.use_hint("navigation", COSTS["scan_hint"])
            if status == "no battery":
                self.message = "Not enough battery for a hint. Trust the numbers!"
                return "invalid"
            self.message = ("Scanner: " + self.field.hint() + " ("
                            + self.hint_label(status, "scan_hint") + ")")
            return "ok"

        self.message = "Unknown command. Try: t 3 4   f 3 4   b 3 4   hint   help"
        return "invalid"

    def tap_square(self, row, col):
        result = self.field.tap(row, col)
        if result == "already":
            self.message = "That square is already open."
            return "invalid"
        if result == "flagged":
            self.message = "That square has a flag. Type f again to remove it first."
            return "invalid"
        if result == "hit":
            self.message = self.shard_hit_message()
            return "ok"
        if result == "cleared":
            self.finish_puzzle()
            return "ok"
        self.message = "Clear! " + str(self.field.safe_found()) + " safe squares mapped."
        return "ok"

    def break_square(self, row, col):
        result, reason = self.field.break_area(row, col)
        if result == "invalid":
            self.message = reason
            return "invalid"
        if result == "hit":
            self.message = self.shard_hit_message()
            if self.field.is_cleared():
                self.finish_puzzle()
            return "ok"
        if result == "cleared":
            self.finish_puzzle()
            return "ok"
        self.message = "Broken open! " + str(self.field.safe_found()) + " safe squares mapped."
        return "ok"

    def flag_square(self, row, col):
        result = self.field.flag(row, col)
        if result == "revealed":
            self.message = "That square is already open."
            return "invalid"
        if result == "placed":
            self.message = "Flag placed. TARS marks it on the nav chart."
        else:
            self.message = "Flag removed."
        return "ok"

    def power_command(self, command, words):
        if command in ("h", "hint"):
            status = self.use_hint("power", COSTS["grid_hint"])
            if status == "no battery":
                self.message = "Not enough battery for a hint. Switches still work!"
                return "invalid"
            spot = self.grid.hint()
            self.message = ("Try pressing row {}, column {}. ({})"
                            .format(spot[0] + 1, spot[1] + 1,
                                    self.hint_label(status, "grid_hint")))
            return "ok"

        if command.isdigit():
            words = ["p"] + words
            command = "p"
        if command in ("p", "press"):
            spot = read_numbers(words)
            if spot is None:
                self.message = "Type it like this: p 2 3  (row 2, column 3)."
                return "invalid"
            row, col = spot
            if not self.grid.is_inside(row, col):
                self.message = "Rows and columns go from 1 to " + str(self.grid.size) + "."
                return "invalid"
            result = self.grid.press(row, col)
            self.spend(COSTS["switch"])
            if result == "solved":
                self.finish_puzzle()
                return "ok"
            self.message = "Bzzt! " + str(self.grid.lights_off()) + " lights still off."
            return "ok"

        self.message = "Unknown command. Try: p 2 3   hint   help"
        return "invalid"

    def engine_energy(self):
        return self.free_hints["engine"] + self.battery // COSTS["bay_hint"]

    def finish_engine(self, bay, result, energy_given):
        if bay.klotski_gameCount != 0:
            self.skipped.append("engine")
            self.finish_puzzle()
            return
        used = max(0, energy_given - (bay.klotski_energy or 0))
        free = min(used, self.free_hints["engine"])
        self.free_hints["engine"] -= free
        self.free_hints_used["engine"] += free
        self.bay_hints_used = used
        self.bay_hints_paid = used - free
        self.spend(self.bay_hints_paid * COSTS["bay_hint"])
        self.bay_moves = sum(bay.klotski_moveCount)
        self.bay_threshold = bay.klotski_moveThreshold
        if result is None:
            result = (len(LEVELS) - 1, bay.klotski_energy)
        new_level = clamp_level(result[0])
        self.ratings["engine"] = new_level - self.level
        self.next_difficulty = LEVELS[new_level]
        self.finish_puzzle()

    def rate_navigation(self):
        paid = self.field.hints_used - self.free_hints_used["navigation"]
        mistakes = self.field.strikes + paid + self.field.wrong_flags()
        if mistakes == 0:
            return 1
        if mistakes <= 2:
            return 0
        return -1

    def rate_power(self):
        paid = self.grid.hints_used - self.free_hints_used["power"]
        effort = self.grid.moves + 2 * paid
        if effort <= self.grid.best_moves + 2:
            return 1
        if effort <= self.grid.best_moves * 2 + 2:
            return 0
        return -1

    def adjust_level(self, stage, rating):
        self.ratings[stage] = rating
        self.level = clamp_level(self.level + rating)
        self.level_path.append(self.level)
        return " TARS rates it {}: next system is {}.".format(
            RATING_WORDS[rating], art.DIFFICULTY_NAMES[self.level_name()])

    def add_report(self, title, facts, rating, next_line):
        picture = art.TARS if rating >= 0 else art.TARS_SAD
        text = (facts + "\n\nTARS: \"" + story.TARS_RATING_LINES[rating] + "\"\n\n"
                + "RATING: " + RATING_WORDS[rating] + "   //   " + next_line)
        self.add_page(title, picture, text)

    def finish_puzzle(self):
        # A cleared system reports its result, then advances to the next choice.
        if self.stage == "navigation":
            skipped = "navigation" in self.skipped
            rating = -1 if skipped else self.rate_navigation()
            self.stage = "goose"
            self.message = self.adjust_level("navigation", rating).strip()
            if skipped:
                facts = "You closed your eyes and flew straight through the Shard Field."
            else:
                paid = self.field.hints_used - self.free_hints_used["navigation"]
                facts = ("Route plotted through the Shard Field. Shard hits: {}. "
                         "Paid hints: {}. Wrong flags: {}."
                         .format(self.field.strikes, paid, self.field.wrong_flags()))
            self.add_report("SYSTEM REPORT 1/3  //  SHARD FIELD", facts, rating,
                            "Life Support Grid level: "
                            + art.DIFFICULTY_NAMES[self.level_name()])
        elif self.stage == "power":
            skipped = "power" in self.skipped
            rating = -1 if skipped else self.rate_power()
            self.stage = "cat"
            self.message = self.adjust_level("power", rating).strip()
            if skipped:
                facts = "You kicked the panel until the grid grumbled back to life."
            else:
                paid = self.grid.hints_used - self.free_hints_used["power"]
                facts = ("Life support is back online. Presses: {} (best possible: {}). "
                         "Paid hints: {}.".format(self.grid.moves, self.grid.best_moves, paid))
            self.add_report("SYSTEM REPORT 2/3  //  LIFE SUPPORT GRID", facts, rating,
                            "Drive Bay level: " + art.DIFFICULTY_NAMES[self.level_name()])
        elif self.stage == "engine":
            if "engine" in self.skipped:
                self.ratings["engine"] = -1
                self.next_difficulty = LEVELS[clamp_level(self.level - 1)]
                facts = ("You gave up on the drive bay. TARS jams the core in with "
                         "a crowbar and a lot of swearing in binary.")
            else:
                facts = ("All three drive cores freed in {} moves (par {}). "
                         "Hint energy used: {}."
                         .format(self.bay_moves, self.bay_threshold, self.bay_hints_used))
            rating = max(-1, min(1, self.ratings["engine"]))
            self.add_report("SYSTEM REPORT 3/3  //  DRIVE BAY", facts, rating,
                            "Next mission level: "
                            + art.DIFFICULTY_NAMES[self.next_difficulty])
            self.stage = "ending"
            self.calculate_ending()
            ending = story.ENDINGS[self.ending]
            self.add_page(ending["title"], ending["art"], ending["text"])
            self.message = "The drive core is home!"

    def part_scores(self):
        scores = {"battery": 40 * self.battery / MAX_BATTERY}

        if "navigation" in self.skipped:
            scores["navigation"] = 0
        else:
            paid = self.field.hints_used - self.free_hints_used["navigation"]
            penalty = 5 * self.field.strikes + 3 * paid + 2 * self.field.wrong_flags()
            scores["navigation"] = max(0, 20 - penalty)

        if "power" in self.skipped:
            scores["power"] = 0
        else:
            paid = self.grid.hints_used - self.free_hints_used["power"]
            scores["power"] = efficiency_points(self.grid.best_moves, self.grid.moves, paid, 20)

        if "engine" in self.skipped:
            scores["engine"] = 0
        else:
            scores["engine"] = efficiency_points(self.bay_threshold, self.bay_moves,
                                                 self.bay_hints_paid, 20)
        return scores

    def calculate_ending(self):
        total = 0
        for points in self.part_scores().values():
            total += points
        self.score = round(total)
        # Empty battery forces the lowest ending; otherwise total score sets it.
        if self.battery == 0 or self.score < 50:
            self.ending = "jelly"
        elif self.score >= 80:
            self.ending = "perfect"
        else:
            self.ending = "bumpy"

    def epilogue(self):
        lines = []
        for flag in self.flags:
            if flag in story.EPILOGUE_LINES:
                lines.append(story.EPILOGUE_LINES[flag])
        return lines[:3]

    def stars(self):
        count = min(5, self.score // 20)
        return "*" * count + "." * (5 - count)
