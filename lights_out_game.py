import random


class LightsOutGame:
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
        return tuple(tuple(row) for row in self._board)

    @property
    def rows(self):
        return self._rows

    @property
    def cols(self):
        return self._cols

    @property
    def move_count(self):
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
        self._check_coordinate(row, col)
        self._toggle(row, col)
        self._move_count += 1
        return self.is_solved()

    def press_from_text(self, coordinates):
        if not isinstance(coordinates, str):
            raise TypeError("coordinates must be text")

        parts = coordinates.replace(",", " ").split()
        if len(parts) != 2:
            raise ValueError("enter a row and column, for example '1 2'")
        try:
            row, col = (int(part) for part in parts)
        except ValueError as error:
            raise ValueError("row and column must be integers") from error
        return self.press(row, col)

    def is_solved(self):
        return all(all(row) for row in self._board)

    def reset(self):
        self._board = [[True for _ in range(self.cols)] for _ in range(self.rows)]
        self._move_count = 0
        return self

    def shuffle(self, moves=None):
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
