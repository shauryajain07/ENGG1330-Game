# WORMHOLE

WORMHOLE is a single-player, turn-based terminal puzzle adventure. You pilot the
Odyssey-7 and work with TARS to repair three systems before the ship falls into
the black hole KRONOS. Story choices affect your battery, hints, and later
events. A full playthrough is designed to take about 5–10 minutes.

## Group

- Course: ENGG1330 Group Project, 2026–27
- Tutorial subclass: M05
- Members: Jain Shaurya Dileep, Ziyan Wang, Kwok Wang Kin, SOU Cheng Hei

## Requirements

- Python 3 in the course-provided Docker environment
- Container image: `engg1330-project:2026-v03`
- An interactive terminal at least 80 columns wide and 24 rows high
- No extra packages or downloads are required; the game uses Python's standard
  library

If the terminal is too small, the game pauses and asks you to resize it.

## Run in Docker

Build and extract the source-only submission ZIP:

```bash
python3 scripts/package_submission.py
mkdir -p dist/extracted
unzip -oq dist/WORMHOLE-submission.zip -d dist/extracted
```

From the project root, start the game in the provided course container:

```bash
cd dist/extracted
docker run --rm -it -v "$PWD:/workspace" -w /workspace \
  engg1330-project:2026-v03 python3 main.py
```

The ZIP contains the game at its root and excludes `.git`, so the submission
does not contain repository history. The original checkout keeps its `.git`
folder. Do not build or submit a custom Docker image; the game uses the course
image above. The game needs an interactive terminal and does not accept piped
or redirected input.

## Project layout

The game stays at the top level of the extracted folder, with `main.py` as its
entry point.

| File | Purpose |
| --- | --- |
| `main.py` | Curses input, terminal setup, and screen flow |
| `adventure.py` | Mission state, choices, battery, difficulty, and scoring |
| `screens.py`, `story.py`, `art.py` | Screen layouts, narrative data, and ASCII scenes |
| `adapters.py` | Connects the original puzzle engines to the adventure |
| `minesweeper_game.py` | Shard Field rules and original terminal game |
| `lights_out_game.py` | Reusable Lights Out rules and board state |
| `klotski.py` | Three-bay Drive Bay puzzle and piece movement |
| `tests/` | Automated rule, input, board-layout, and screen-size checks |
| `ACKNOWLEDGEMENTS.md`, `ai_use.md` | Sources, acknowledgements, and AI-use record |

`lights_out.py` is also retained as a standalone Lights Out entry point; the
WORMHOLE adventure uses the reusable rules in `lights_out_game.py`.

## Purpose, rules, and controls

Repair all three systems to complete the mission. Battery is shared across the
mission; shard hits, switches, and paid hints use it. Story choices can provide
battery or free hints. Puzzle performance affects the difficulty of later
systems, and your final score determines the landing outcome.

At the title screen, use **Up/Down** or **1–4** to choose an item and press
**Enter**. On the difficulty item, use **Left/Right** to change difficulty.
Enter a pilot name of up to 12 characters; leaving it blank uses “Rookie”. The
**How to Play** option shows the in-game instructions.

The mission has three connected puzzle chapters:

1. **The Shard Field (Minesweeper):** Open every safe square on the 9 × 9 grid.
   Coordinates start at 1. Use `t row col` to open a square, `f row col` to
   place or remove a flag, and `b row col` to open around a number when enough
   flags are marked. `hint` spends battery to suggest a square.
2. **Life Support Grid (Lights Out):** Turn every light on. Use `p row col` to
   press a switch; it flips that light and its up, down, left, and right
   neighbours. Coordinates start at 1. `hint` spends battery to suggest a
   switch.
3. **The Drive Bay (Klotski):** Move the 2 × 2 core marked `X` to the gap at the
   bottom of each of three bays. Enter a move such as `A up` to slide crate A.
   `hint` shows a blueprint, `reset` restarts the current bay, and `quit` gives
   up on it.

In story-choice scenes, enter **1**, **2**, or **3**. During the mission, enter
`help` for the current commands, `restart` to restart the mission, `skip` to
give up on that chapter, or `quit` to return to the title screen. Inside the
Drive Bay, `quit` gives up on that bay. On the mission report, press **R** to
replay, **M** for the title screen, or **Q** to quit.

## Design notes

The mission is a state machine: story choices lead into puzzles, and puzzle
results update shared battery, difficulty, score, and later story details.
`main.py` handles terminal input and drawing, `screens.py` builds fixed-size
layouts, and `adventure.py` owns mission state. `adapters.py` connects the
existing puzzle engines to that shared interface. The puzzle boards use nested
data structures; the Lights Out solver searches first-row switch patterns and
derives the remaining rows from them. Story choices, paid and free hints, and
performance-based difficulty make the three classic puzzle types part of one
mission.

## Testing and known limitations

Run the unit tests in the same course image using the extracted submission:

```bash
cd dist/extracted
docker run --rm -v "$PWD:/workspace" -w /workspace \
  engg1330-project:2026-v03 \
  python3 -m unittest discover -s tests -t . -v
```

The tests cover puzzle rules, seeded Lights Out scrambles, valid and invalid
commands, boundary coordinates, the shape and solvability of all twelve
Klotski starting layouts, and 80-by-24 screen limits. Before submitting,
extract the final ZIP into a clean folder and manually play the game in a fresh
course container. Check:

- Normal play through all three puzzles.
- An invalid command or malformed coordinate.
- Boundary coordinates, including the first and last grid cells, plus an
  out-of-range coordinate.
- Each puzzle's win condition and the mission report.
- Restarting, returning to the title screen, and quitting.

The videos should show this same submitted version.

The game requires a TTY and an 80 × 24 terminal area. The tests do not replace a
full manual playthrough, especially checking that the group can explain every
AI-assisted layout and the resulting puzzle.

## Contributions

The following contributions are summarized from project files and repository
history; this record describes work visible in the checkout.

| Member | Main code contributions |
| --- | --- |
| Jain Shaurya Dileep | Adventure flow, terminal UI, story integration, puzzle adapters, Lights Out logic, README, and unit tests |
| Ziyan Wang | Minesweeper / Shard Field implementation |
| Kwok Wang Kin | Story and ASCII-art contributions |
| SOU Cheng Hei | Klotski / Drive Bay implementation, difficulty and hint systems, and piece-layout configurations |

## Acknowledgements and sources

See [ACKNOWLEDGEMENTS.md](ACKNOWLEDGEMENTS.md) for source credits and
[ai_use.md](ai_use.md) for the team's AI-use disclosure.
