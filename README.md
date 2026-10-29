# ENGG1330-Game

Lights Out is a terminal puzzle game written in Python. Turn every light on to
win. It uses only the standard library and can also be imported as a small
game library.

## Play in the terminal

Start a 4x4 game:

```bash
python lights_out.py
```

Move the highlighted cell with the arrow keys or `W`, `A`, `S`, `D`. Press
Space or Enter to toggle that light and its up, down, left, and right
neighbors. Solving the board displays a victory message and move count. Press
`n` for a new puzzle or `q` to quit. The terminal game requires an 80x24
terminal.

Set a custom rectangular board size with command-line options:

```bash
python lights_out.py --rows 5 --cols 6
```

## Import the game

The game logic is isolated from the terminal interface in `lights_out_game.py`,
so the main game can import it without starting the terminal UI.

```python
from lights_out_game import LightsOutGame

game = LightsOutGame(rows=5, cols=6, seed=42)
game.press(1, 2)

print(game.board)
print(game.move_count)
print(game.is_solved())
```

`LightsOutGame()` defaults to a randomized, solvable 4x4 puzzle. Pass `seed`
to reproduce a board. Use `game.reset()` to turn all lights on or
`game.shuffle()` to create a new solvable puzzle. `game.shuffle(moves=10)` sets
the number of random presses used to make the puzzle.
