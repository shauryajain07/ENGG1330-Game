import curses
import os
import random
import sys

MIN_WIDTH = 100
MIN_HEIGHT = 40

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

    def setup_colours_game_2(self):
        if not curses.has_colors():
            return
        try:
            curses.start_color()
            background = 0
            block = 238
            exploded = 196
            self.words = []
            self.words.append(("1", 17, background)), self.words.append(("2", 46, background)), self.words.append(("3", 196, background)), self.words.append(("4", 127, background)), self.words.append(("5", 124, background)), self.words.append(("6", 3, background)), self.words.append(("7", curses.COLOR_BLACK, background)), self.words.append(("8", 255, background)), self.words.append((" ", 238, block)), self.words.append(("0", 238, background))
            self.words.append(("title", 255, background)), self.words.append(("F", 12, block)), self.words.append(("X", 240, background)), self.words.append(("exploded_mine", 240, exploded)), self.words.append(("success", 46, background)), self.words.append(("warning", 196, background)), self.words.append(("muted", 255, background))
            for i, (name, fg, bg) in enumerate(self.words, start=1):
                curses.init_pair(i, fg, bg)
                self.STYLES[name] = curses.color_pair(i) | curses.A_BOLD
        except curses.error:
            pass

    def put(self, row, text, style):
        rows, columns = self.screen.getmaxyx()
        self.screen.addnstr(row, 0, text, max(0, columns - 1), style)

    def put_block(self, row, col, text, style):
        rows, columns = self.screen.getmaxyx()
        if text == "exploded_mine":
            text = "X"
        for i in range(3):
            for j in range(3):
                if i == 1 and j == 1:
                    self.screen.addnstr(row + i, col + j, text, max(0, columns - 1), style)
                else:
                    self.screen.addnstr(row + i, col + j, " ", max(0, columns - 1), style)

    def draw_screen(self):
        self.screen.erase()
        self.put(0, "This is a minesweeper game, you can do the following operations:", self.STYLES["title"])
        self.put(1, "\"tap\" or \"t\" to open a block, \"flag\" or \"f\" to mark/unmark a block", self.STYLES["title"])
        self.put(2, "\"break\" or \"b\" to break blocks within 3x3 area of a number if correct number of flags are marked", self.STYLES["title"])
        self.put(3, "\"quit\" or \"q\" to quit the game, \"help\" or \"h\" for more details for how to play", self.STYLES["title"])
        self.put(4, "Input the operation you want to perform with the coordinates x y: (except \"quit\" operation)", self.STYLES["title"])
        self.put(5, "For example: \"tap 1 2\" to open the block at row 1 column 2", self.STYLES["title"])
        self.put(6, "----------------------------------------------------------------------------------------------------", self.STYLES["title"])
        self.put(8, "    1  2  3  4  5  6  7  8  9 ", self.STYLES["title"])
        self.put(9, "                              ", self.STYLES["title"])
        for i in range(9):
            self.put_block(10 + i * 3, 0, str(i + 1), self.STYLES["title"])
            for j in range(9):
                self.put_block(10 + i * 3, 3 + j * 3, self.board[i][j], self.STYLES[self.board[i][j]])
        self.put(37, "mines left on the grid: " + str(self.mines_left), self.STYLES["title"])
        self.put(38, self.message, self.STYLES[self.typ])
        self.screen.refresh()

    def print_how_to_play(self, page, message, typ):
        self.screen.erase()
        self.put(0, "This is \"How to Play\" session", self.STYLES["title"])
        self.put(1, "Press \"l\" to go to previous page, \"r\" to go to the next page", self.STYLES["title"])
        if page == 0:
            self.put(2, "This is the \"tap\" operation, it can open a block", self.STYLES["title"])
            self.put(3, "To do the \"tap\" operation, input \"tap x y\" or \"t x y\"", self.STYLES["title"])
            self.put(4, "In which x,y are the coordinates (x is row and y is column) you want to do the operation", self.STYLES["title"])
            self.put(5, "For example:", self.STYLES["title"])
            self.put(7, "    1  2  3 ", self.STYLES["title"])
            self.put(8, "            ", self.STYLES["title"])
            for i in range(3):
                self.put_block(9 + i * 3, 0, str(i + 1), self.STYLES["title"])
                for j in range(3):
                    self.put_block(9 + i * 3, 3 + j * 3, " ", self.STYLES[" "])
            self.put(18, "After operation \"tap 2 2\":", self.STYLES["title"])
            self.put(20, "    1  2  3", self.STYLES["title"])
            self.put(21, "           ", self.STYLES["title"])
            for i in range(3):
                self.put_block(22 + i * 3, 0, str(i + 1), self.STYLES["title"])
                for j in range(3):
                    if i == 1 and j == 1:
                        self.put_block(22 + i * 3, 3 + j * 3, "1", self.STYLES["1"])
                    else:
                        self.put_block(22 + i * 3, 3 + j * 3, " ", self.STYLES[" "])
            self.put(31, "You cannot tap a flagged block", self.STYLES["title"])
            self.put(32, "If you tap a block with mines,", self.STYLES["title"])
            self.put(33, "You will LOSE", self.STYLES["warning"])
            self.put(34, message, self.STYLES[typ])
        elif page == 1:
            self.put(2, "This is the \"flag\" operation, it can flag or unflag a block", self.STYLES["title"])
            self.put(3, "To do the \"flag\" operation, input \"flag x y\" or \"f x y\"", self.STYLES["title"])
            self.put(4, "In which x,y are the coordinates (x is row and y is column) you want to do the operation", self.STYLES["title"])
            self.put(5, "For example:", self.STYLES["title"])
            self.put(7, "    1  2  3 ", self.STYLES["title"])
            self.put(8, "            ", self.STYLES["title"])
            for i in range(3):
                self.put_block(9 + i * 3, 0, str(i + 1), self.STYLES["title"])
                for j in range(3):
                    self.put_block(9 + i * 3, 3 + j * 3, " ", self.STYLES[" "])
            self.put(18, "After operation \"flag 2 2\":", self.STYLES["title"])
            self.put(20, "    1  2  3 ", self.STYLES["title"])
            self.put(21, "            ", self.STYLES["title"])
            for i in range(3):
                self.put_block(22 + i * 3, 0, str(i + 1), self.STYLES["title"])
                for j in range(3):
                    if i == 1 and j == 1:
                        self.put_block(22 + i * 3, 3 + j * 3, "F", self.STYLES["F"])
                    else:
                        self.put_block(22 + i * 3, 3 + j * 3, " ", self.STYLES[" "])
            self.put(31, "If you flag a block which is already flagged, the block will be unflagged", self.STYLES["title"])
            self.put(32, "You cannot flag a opened block", self.STYLES["title"])
            self.put(33, message, self.STYLES[typ])
        elif page == 2:
            self.put(2, "This is the \"break\" operation, it can open a series block", self.STYLES["title"])
            self.put(3, "To do the \"break\" operation, input \"break x y\" or \"break x y\"", self.STYLES["title"])
            self.put(4, "In which x,y are the coordinates (x is row and y is column) you want to do the operation", self.STYLES["title"])
            self.put(5, "For example:", self.STYLES["title"])
            self.put(7, "    1  2  3 ", self.STYLES["title"])
            self.put(8, "            ", self.STYLES["title"])
            for i in range(3):
                self.put_block(9 + i * 3, 0, str(i + 1), self.STYLES["title"])
                for j in range(3):
                    if i == 0 and j == 1:
                        self.put_block(9 + i * 3, 3 + j * 3, "F", self.STYLES["F"])
                    elif i == 1 and j == 1:
                        self.put_block(9 + i * 3, 3 + j * 3, "1", self.STYLES["1"])
                    else:
                        self.put_block(9 + i * 3, 3 + j * 3, " ", self.STYLES[" "])
            self.put(18, "After operation \"break 2 2\":", self.STYLES["title"])
            self.put(20, "    1  2  3 ", self.STYLES["title"])
            self.put(21, "            ", self.STYLES["title"])
            for i in range(3):
                self.put_block(22 + i * 3, 0, str(i + 1), self.STYLES["title"])
                for j in range(3):
                    if i == 0 and j == 1:
                        self.put_block(22 + i * 3, 3 + j * 3, "F", self.STYLES["F"])
                    elif (i, j) in ((0, 0), (0, 2), (1, 1), (1, 0), (1, 2)):
                        self.put_block(22 + i * 3, 3 + j * 3, "1", self.STYLES["1"])
                    else:
                        self.put_block(22 + i * 3, 3 + j * 3, "0", self.STYLES["0"])
            self.put(31, "You can only break a opened block with flag count around the block equal to the number in the block", self.STYLES["title"])
            self.put(32, "If there exists a unflagged block with mine around the opened block and you do the \"break\" operation", self.STYLES["title"])
            self.put(33, "You will LOSE", self.STYLES["warning"])
            self.put(34, message, self.STYLES[typ])
        else:
            self.put(2, "To win the game, you have to open all blocks except the blocks with mine", self.STYLES["title"])
            self.put(3, "Good Luck", self.STYLES["success"])
            self.put(4, message, self.STYLES[typ])
        self.screen.refresh()

    def how_to_play(self):
        now = 0
        message = ""
        typ = "warning"
        while True:
            while True:
                self.print_how_to_play(now, message, typ)
                try:
                    key = self.screen.get_wch()
                except curses.error:
                    continue
                if key not in ("l", "L", "r", "R", "q", "Q"):
                    message = "Invalid input"
                else:
                    message = ""
                    key = key.lower()
                    break
            if key == "q":
                break
            elif key == "l":
                now = (now + 3) % 4
            else:
                now = (now + 1) % 4

    def generate_map(self):
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

    def get_key_input_game_2(self):
        previous = None
        while True:
            size = self.screen.getmaxyx()
            if size != previous:
                previous = size
                if size[0] >= MIN_HEIGHT and size[1] >= MIN_WIDTH:
                    break
                else:
                    self.screen.erase()
                    for row, line in enumerate((f"Resize to {MIN_WIDTH} x {MIN_HEIGHT}", "Press q to quit", str(size[0]), str(size[1]))):
                        if row < size[0] and size[1] > 1:
                            self.screen.addnstr(row, 0, line, size[1] - 1)
                    self.screen.refresh()
            try:
                key = self.screen.get_wch()
            except curses.error:
                continue
            if key == curses.KEY_RESIZE:
                previous = None
                continue
            if key in ("q", "Q", "\x03"):
                return "q"
            else:
                continue
        while True:
            self.draw_screen()
            ret = ""
            try:
                self.screen.timeout(60000)
                curses.echo()
                while True:
                    ret = self.screen.getstr()
                    if ret == b"":
                        continue
                    else:
                        break
                curses.noecho()
                self.screen.timeout(100)
            except curses.error:
                continue
            return ret.decode('utf-8').strip().lower()

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

    def draw_difficulty(self, message):
        self.screen.erase()
        self.put(0, "This is a minesweeper game", self.STYLES["title"])
        self.put(1, "Please choose the difficulty you want to play", self.STYLES["title"])
        self.put(2, "Type \"easy\" or \"e\" for easy mode, you will be rewarded 1 navigation chip", self.STYLES["title"])
        self.put(3, "Type \"medium\" or \"m\" for medium mode, you will be rewarded 3 navigation chip", self.STYLES["title"])
        self.put(4, "Type \"hard\" or \"h\" for hard mode, you will be rewarded 5 navigation chip", self.STYLES["title"])
        self.put(5, "Type \"nightmare\" or \"n\" for nightmare mode, you will be rewarded 8 navigation chip", self.STYLES["title"])
        self.put(6, message, self.STYLES["warning"])
        self.screen.refresh()

    def difficulty_option(self):
        message = ""
        while True:
            self.draw_difficulty(message)
            ret = ""
            try:
                self.screen.timeout(60000)
                curses.echo()
                while True:
                    ret = self.screen.getstr()
                    if ret == b"":
                        continue
                    else:
                        break
                curses.noecho()
                self.screen.timeout(100)
            except curses.error:
                continue
            ret = ret.decode('utf-8').strip().lower()    
            if ret in ("easy", "e"):
                return (10, 1)
            elif ret in ("medium", "m"):
                return (12, 3)
            elif ret in ("hard", "h"):
                return (15, 5)
            elif ret in ("nightmare", "n"):
                return (20, 8)
            else:
                message = "Invalid input, please type again"

        

    def play_round(self):
        self.mines_left, self.reward = self.difficulty_option()
        self.map, self.board = self.generate_map()
        self.message = "Please input your operation and coordinates to perform the operation, or \"quit\" to quit the game."
        self.typ = "title"
        while True:
            input_str = self.get_key_input_game_2()
            input_arr = input_str.split()
            if len(input_arr) == 0:
                self.message = "Invalid input, please input your operation and coordinates to perform the operation, or \"quit\" to quit the game."
                self.typ = "warning"
                continue
            if input_arr[0] == "quit" or input_arr[0] == "q":
                return False
            if input_arr[0] == "help" or input_arr[0] == "h":
                self.how_to_play()
                continue
            if len(input_arr) != 3 or input_arr[0] not in ("tap", "t", "flag", "f", "break", "b") or input_arr[1].isdigit() == False or input_arr[2].isdigit() == False or int(input_arr[1]) < 1 or int(input_arr[1]) > 9 or int(input_arr[2]) < 1 or int(input_arr[2]) > 9:
                self.message = "Invalid input, please input your operation and coordinates to perform the operation, or \"quit\" to quit the game."
                self.typ = "warning"
                continue
            if input_arr[0] in ("tap", "t"):
                x, y = int(input_arr[1]) - 1, int(input_arr[2]) - 1
                (self.message, self.typ, game_status) = self.tap(x, y)
                if game_status == False:
                    if self.message == "y" or self.message == "Y":
                        return True
                    else:
                        return False
                if (self.message, self.typ) != ("", ""):
                    continue
            elif input_arr[0] in ("flag", "f"):
                x, y = int(input_arr[1]) - 1, int(input_arr[2]) - 1
                (self.message, self.typ, game_status) = self.flag(x, y)
                if (self.message, self.typ) != ("", ""):
                    continue
            elif input_arr[0] in ("break", "b"):
                x, y = int(input_arr[1]) - 1, int(input_arr[2]) - 1
                (self.message, self.typ, game_status) = self.break_blocks(x, y)
                if game_status == False:
                    if self.message == "y" or self.message == "Y":
                        return True
                    else:
                        return False
                if (self.message, self.typ) != ("", ""):
                    continue
            (self.message, self.typ, game_status) = self.check_win()
            if game_status == False:
                if self.message == "y" or self.message == "Y":
                    return True
                else:
                    return False
            self.message = "Please input your operation and coordinates to perform the operation, or \"quit\" to quit the game."
            self.typ = "title"


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