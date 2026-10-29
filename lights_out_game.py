"""Importable Lights Out game logic.

The game uses only Python's standard library. Coordinates passed to ``press``
are zero-based, with (0, 0) at the top-left corner.
"""

import random


class LightsOutGame:
    """A Lights Out puzzle with a configurable number of rows and columns.

    A new game starts with a randomly scrambled, solvable board. Call
    ``reset()`` to return to an all-on board, or ``shuffle()`` for a new
    puzzle. An optional seed makes the generated board reproducible.
    """

    def __init__(self, rows=4, cols=4, *, seed=None):
        self._rows = self._positive_integer(rows, "rows")
        self._cols = self._positive_integer(cols, "cols")
        self._random = random.Random(seed)
        self._board = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self._move_count = 0
        self.shuffle()

    @staticmethod
    def _positive_integer(value, name):
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise ValueError("{} must be a positive integer".format(name))
        return value

    @property
    def board(self):
        """Return an immutable snapshot; ``True`` means that a light is on."""
        return tuple(tuple(row) for row in self._board)

    @property
    def rows(self):
        """Number of rows in the board."""
        return self._rows

    @property
    def cols(self):
        """Number of columns in the board."""
        return self._cols

    @property
    def move_count(self):
        """Number of moves made by the player since the last shuffle/reset."""
        return self._move_count

    def _check_coordinate(self, row, col):
        if isinstance(row, bool) or not isinstance(row, int):
            raise TypeError("row must be an integer")
        if isinstance(col, bool) or not isinstance(col, int):
            raise TypeError("col must be an integer")
        if not 0 <= row < self.rows:
            raise IndexError("row is outside the board")
        if not 0 <= col < self.cols:
            raise IndexError("column is outside the board")

    def _toggle(self, row, col):
        for row_offset, col_offset in ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)):
            neighbor_row = row + row_offset
            neighbor_col = col + col_offset
            if 0 <= neighbor_row < self.rows and 0 <= neighbor_col < self.cols:
                self._board[neighbor_row][neighbor_col] = not self._board[neighbor_row][neighbor_col]

    def press(self, row, col):
        """Toggle a cell and its orthogonal neighbors.

        Return ``True`` if the board is solved after the move.
        """
        self._check_coordinate(row, col)
        self._toggle(row, col)
        self._move_count += 1
        return self.is_solved()

    def is_solved(self):
        """Return whether every light is on."""
        return all(all(row) for row in self._board)

    def reset(self):
        """Turn every light on and reset the move counter."""
        self._board = [[True for _ in range(self.cols)] for _ in range(self.rows)]
        self._move_count = 0
        return self

    def shuffle(self, moves=None):
        """Create a solvable puzzle by scrambling the all-on goal board.

        ``moves`` controls how many random presses are used to make the puzzle.
        The default is twice the number of cells. A positive scramble is kept
        away from the solved state, even if random presses cancel one another.
        """
        if moves is None:
            moves = self.rows * self.cols * 2
        if isinstance(moves, bool) or not isinstance(moves, int) or moves < 0:
            raise ValueError("moves must be a non-negative integer")

        self.reset()
        for _ in range(moves):
            self._toggle(
                self._random.randrange(self.rows),
                self._random.randrange(self.cols),
            )
        if moves > 0 and self.is_solved():
            self._toggle(0, 0)
        self._move_count = 0
        return self
