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

## Run the game

From the extracted project directory, inside the course container, run:

```bash
python3 main.py
```

The game must run in a terminal window. It does not accept piped or redirected
input.

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

## Testing and known limitations

This checkout includes a small automated unit test suite. Run it with:

```bash
python3 -m unittest discover -s tests -t .
```

The group should also extract the final ZIP into a separate copy of the starter
project, run it in a fresh course container, and manually check:

- Normal play through all three puzzles.
- An invalid command or malformed coordinate.
- Boundary coordinates, including the first and last grid cells, plus an
  out-of-range coordinate.
- Each puzzle's win condition and the mission report.
- Restarting, returning to the title screen, and quitting.

The videos should show this same submitted version.

The game requires a TTY and an 80 × 24 terminal area. It is intended to run in
the supplied course container; other environments have not been documented
here.

## Contributions and sources

The following code contributions are summarized from the project files and Git
history. Add any shared design, testing, documentation, or video work before
submission so the record reflects the whole group's contributions.

| Member | Main code contributions |
| --- | --- |
| Jain Shaurya Dileep | Adventure flow, terminal UI, story integration, puzzle adapters, and Lights Out logic |
| Ziyan Wang | Minesweeper / Shard Field implementation |
| Kwok Wang Kin | Story and ASCII-art contributions |
| SOU Cheng Hei | Klotski / Drive Bay implementation |
