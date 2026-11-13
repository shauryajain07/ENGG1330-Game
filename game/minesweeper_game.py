
import curses
import os
import random
import sys

class MinesweeperGame:
    def __init__(self, screen, navigation_chip_count):
        self.screen = screen
        self.STYLES = {}
        self.words = []
        self.mines_left = 10
        self.map = []
        self.board = []
        self.message = ""
        self.typ = "title"
        self.reward = 0
        self.navigation_chip_count = navigation_chip_count
        
        self.setup_colours_game_2()

    def generate_map(self):
        # Choose each mine using the remaining-mine ratio to end with an exact count.
        map = [[" " for _ in range(9)] for _ in range(9)]
        blocks = 81
        mines = self.mines_left
        for i in range(9):
            for j in range(9):
                if random.random() <= mines / blocks:
                    map[i][j] = "X"
                    mines -= 1
                blocks -= 1
        target = []
        dx = [-1, -1, -1, 0, 0, 1, 1, 1]
        dy = [-1, 0, 1, -1, 1, -1, 0, 1]
        for i in range(9):
            for j in range(9):
                if map[i][j] == "X":
                    continue
                # Count adjacent mines once, then use the number during play.
                cnt = 0
                for k in range(8):
                    ni, nj = i + dx[k], j + dy[k]
                    if 0 <= ni < 9 and 0 <= nj < 9 and map[ni][nj] == "X":
                        cnt += 1
                map[i][j] = str(cnt)
                if cnt == 0:
                    target.append((i, j))
        (x, y) = random.choice(target)
        board = [[" " for _ in range(9)] for _ in range(9)]
        # Reveal from a zero using a queue so its safe numbered border opens too.
        queue = [(x, y)]
        board[x][y] = map[x][y]
        pos = 0
        while pos < len(queue):
            (i, j) = queue[pos]
            pos += 1
            for k in range(8):
                ni, nj = i + dx[k], j + dy[k]
                if 0 <= ni < 9 and 0 <= nj < 9 and board[ni][nj] == " " and map[ni][nj].isdigit() == True:
                    board[ni][nj] = map[ni][nj]
                    if map[ni][nj] == "0":
                        queue.append((ni, nj))
        return map, board
    
    def tap(self, x, y):
        if self.board[x][y] != " ":
            return ("This block has already been opened or flagged, please choose another block.", "warning", True)
        if self.map[x][y] == "X":
            self.board[x][y] = "exploded_mine"
            for i in range(9):
                for j in range(9):
                    if self.map[i][j] == "X" and self.board[i][j] != "exploded_mine":
                        self.board[i][j] = "X"
            self.draw_screen()
            self.put(39, "You hit a mine! Game over. Current navigation chip count is " + str(self.navigation_chip_count), self.STYLES["warning"])
            self.put(40, "Do you want to continue? Press y to continue and n / q to quit", self.STYLES["title"])
            self.screen.refresh()
            c = ""
            while True:
                try:
                    c = self.screen.get_wch()
                except curses.error:
                    continue
                if c == -1:
                    continue
                elif c not in ("y", "Y", "n", "N", "q", "Q"):
                    self.draw_screen()
                    self.put(39, "You hit a mine! Game over. Current navigation chip count is " + str(self.navigation_chip_count), self.STYLES["warning"])
                    self.put(40, "Invalid input, please press y to continue and n / q to quit", self.STYLES["warning"])
                    self.screen.refresh()
                    continue
                else:
                    break
            return (c, "", False)
        else:
            self.board[x][y] = self.map[x][y]
            if self.map[x][y] == "0":
                # A zero flood-fills connected safe cells and stops at numbered cells.
                dx = [-1, -1, -1, 0, 0, 1, 1, 1]
                dy = [-1, 0, 1, -1, 1, -1, 0, 1]
                queue = [(x, y)]
                pos = 0
                while pos < len(queue):
                    (i, j) = queue[pos]
                    pos += 1
                    for k in range(8):
                        ni, nj = i + dx[k], j + dy[k]
                        if 0 <= ni < 9 and 0 <= nj < 9 and self.board[ni][nj] == " " and self.map[ni][nj].isdigit() == True:
                            self.board[ni][nj] = self.map[ni][nj]
                            if self.map[ni][nj] == "0":
                                queue.append((ni, nj))
            return ("", "", True)

    def flag(self, x, y):
        if self.board[x][y] == " ":
            self.board[x][y] = "F"
            self.mines_left -= 1
        elif self.board[x][y] == "F":
            self.board[x][y] = " "
            self.mines_left += 1
        else:
            return ("This block has already been opened, please choose another block.", "warning", True)
        return ("", "", True)

    def break_blocks(self, x, y):
        if self.board[x][y] == " " or self.board[x][y] == "F":
            return ("This block has not been opened, please choose another block.", "warning", True)
        if self.board[x][y] == "0":
            return ("This block is a 0 block, please choose another block.", "warning", True)
        dx = [-1, -1, -1, 0, 0, 1, 1, 1]
        dy = [-1, 0, 1, -1, 1, -1, 0, 1]
        flag_count = 0
        for k in range(8):
            ni, nj = x + dx[k], y + dy[k]
            if 0 <= ni < 9 and 0 <= nj < 9 and self.board[ni][nj] == "F":
                flag_count += 1
        # Chording only opens neighbours when the marked count matches the clue.
        if flag_count != int(self.board[x][y]):
            return ("The number of flags around this block is not equal to the number on this block.", "warning", True)
        for k in range(8):
            ni, nj = x + dx[k], y + dy[k]
            if 0 <= ni < 9 and 0 <= nj < 9 and self.board[ni][nj] == " ":
                if self.map[ni][nj] == "X" and self.board[ni][nj] != "F":
                    self.board[ni][nj] = "exploded_mine"
                    for i in range(9):
                        for j in range(9):
                            if self.map[i][j] == "X" and self.board[i][j] != "exploded_mine":
                                self.board[i][j] = "X"
                    self.draw_screen()
                    self.put(39, "You hit a mine! Game over. Current navigation chip count is " + str(self.navigation_chip_count), self.STYLES["warning"])
                    self.put(40, "Do you want to continue? Press y to continue and n / q to quit", self.STYLES["title"])
                    self.screen.refresh()
                    c = ""
                    while True:
                        try:
                            c = self.screen.get_wch()
                        except curses.error:
                            continue
                        if c == -1:
                            continue
                        elif c not in ("y", "Y", "n", "N", "q", "Q"):
                            self.draw_screen()
                            self.put(39, "You hit a mine! Game over. Current navigation chip count is " + str(self.navigation_chip_count), self.STYLES["warning"])
                            self.put(40, "Invalid input, please press y to continue and n / q to quit", self.STYLES["warning"])
                            self.screen.refresh()
                            continue
                        else:
                            break
                    return (c, "", False)
        for k in range(8):
            ni, nj = x + dx[k], y + dy[k]
            if 0 <= ni < 9 and 0 <= nj < 9 and self.board[ni][nj] == " ":
                self.board[ni][nj] = self.map[ni][nj]
                if self.map[ni][nj] == "0":
                    queue = [(ni, nj)]
                    pos = 0
                    while pos < len(queue):
                        (i, j) = queue[pos]
                        pos += 1
                        for k in range(8):
                            nni, nnj = i + dx[k], j + dy[k]
                            if 0 <= nni < 9 and 0 <= nnj < 9 and self.board[nni][nnj] == " " and self.map[nni][nnj].isdigit() == True:
                                self.board[nni][nnj] = self.map[nni][nnj]
                                if self.map[nni][nnj] == "0":
                                    queue.append((nni, nnj))
        return ("", "", True)

    def check_win(self):
        # The player wins by revealing every safe cell; mines need not be flagged.
        win = True
        for i in range(9):
            for j in range(9):
                if self.map[i][j] != "X" and self.board[i][j] != self.map[i][j]:
                    win = False
        if win == False:
            return ("", "", True)
        self.mines_left = 0
        self.navigation_chip_count += self.reward
        for i in range(9):
            for j in range(9):
                if self.map[i][j] == "X":
                    self.board[i][j] = "F"
        self.typ = "success"
        self.draw_screen()
        self.put(39, "You won! Current navigation chip count is " + str(self.navigation_chip_count), self.STYLES["success"])
        self.put(40, "Do you want to continue? Press y to continue and n / q to quit", self.STYLES["title"])
        self.screen.refresh()
        c = ""
        while True:
            try:
                c = self.screen.get_wch()
            except curses.error:
                continue
            if c == -1:
                continue
            elif c not in ("y", "Y", "n", "N", "q", "Q"):
                self.draw_screen()
                self.put(39, "You won! Current navigation chip count is " + str(self.navigation_chip_count), self.STYLES["success"])
                self.put(40, "Invalid input, please press y to continue and n / q to quit", self.STYLES["warning"])
                self.screen.refresh()
                continue
            else:
                break
        return (c, "", False)
    
    def check_hint(self, x, y):
        if self.map[x][y] == "X" or self.board[x][y].isdigit() == True:
            return 4
        dx4 = [-1, 0, 0, 1]
        dy4 = [0, -1, 1, 0]
        for k in range(4):
            ni, nj = x + dx4[k], y + dy4[k]
            if 0 <= ni < 9 and 0 <= nj < 9 and self.board[ni][nj].isdigit() == True:
                if self.map[x][y] == "0":
                    return 0
                else:
                    return 1
        dx8 = [-1, -1, -1, 0, 0, 1, 1, 1]
        dy8 = [-1, 0, 1, -1, 1, -1, 0, 1]
        for k in range(8):
            ni, nj = x + dx8[k], y + dy8[k]
            if 0 <= ni < 9 and 0 <= nj < 9 and self.board[ni][nj].isdigit() == True:
                if self.map[x][y] == "0":
                    return 0
                else:
                    return 2
        return 3
    

    def provide_hint(self):
        for x in range(4):
            target_blocks = [(i, j) for i in range(9) for j in range(9) if self.check_hint(i, j) == x]
            if len(target_blocks) > 0:
                hint_block = random.choice(target_blocks)
                return ("Try tap block at (" + str(hint_block[0] + 1) + ", " + str(hint_block[1] + 1) + ")", "success")
        return ("No hints available at the moment.", "warning")


def run_game_2(screen):
    navigation_chip_count = 0
    game = MinesweeperGame(screen, navigation_chip_count)
    curses.noecho()
    screen.keypad(True)
    screen.timeout(100)
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    while game.play_round():
        continue

def main():
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print("Please run this game in a interactive terminal.")
        return
    os.environ.pop("COLUMNS", None)
    os.environ.pop("LINES", None)
    curses.use_env(False)
    try:
        curses.wrapper(run_game_2)
    except KeyboardInterrupt:
        pass
    print("Thank you for playing!")

if __name__ == "__main__":
    main()
