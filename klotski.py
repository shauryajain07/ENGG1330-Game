import random
import copy
import time
import textwrap

#lowercase input is fine
#change the number of rounds in klotski_gameCount at the bottom (~line 300) and update the message in initialise_board (~line 180)
#other dimensions than 4*5 are not yet tested but should be fine; but the dimensions must be consistent since the dimensions of the board is fixed in initialise_board() (default 4*5)
#board and currentPieces can become async and is synced in move_piece() and reset_board() (using initialise_board); always update board, currentPieces from initialise_game() to avoid async between rounds
# ---- delete print_wrap(), clear_terminal() and MAX_WIDTH, MAX_HEIGHT when merging; but do import copy ----

def play_klotski():
    def initialise_pieces(last_board=None):
        pieceArrangements = [ #row and col coords are the top left corner of piece, size is (height, width)
            #board 0 below
            {
                'X': {'row': 2, 'col': 1, 'size': (2, 2)},
                'A': {'row': 1, 'col': 0, 'size': (2, 1)},
                'B': {'row': 0, 'col': 3, 'size': (2, 1)},
                'C': {'row': 3, 'col': 0, 'size': (2, 1)},
                'D': {'row': 3, 'col': 3, 'size': (2, 1)},
                'E': {'row': 0, 'col': 0, 'size': (1, 2)},
                'F': {'row': 1, 'col': 1, 'size': (1, 1)},
                'G': {'row': 0, 'col': 2, 'size': (1, 1)},
                'H': {'row': 4, 'col': 2, 'size': (1, 1)},
                'I': {'row': 1, 'col': 2, 'size': (1, 1)}
            },
            #board 1 below
            {
                'X': {'row': 2, 'col': 1, 'size': (2, 2)},
                'A': {'row': 1, 'col': 0, 'size': (2, 1)},
                'B': {'row': 1, 'col': 3, 'size': (2, 1)},
                'C': {'row': 3, 'col': 0, 'size': (2, 1)},
                'D': {'row': 3, 'col': 3, 'size': (2, 1)},
                'E': {'row': 0, 'col': 0, 'size': (1, 2)},
                'F': {'row': 1, 'col': 1, 'size': (1, 1)},
                'G': {'row': 0, 'col': 3, 'size': (1, 1)},
                'H': {'row': 4, 'col': 2, 'size': (1, 1)},
                'I': {'row': 1, 'col': 2, 'size': (1, 1)}
            },
            #board 2 below
            {
                'X': {'row': 2, 'col': 1, 'size': (2, 2)},
                'A': {'row': 0, 'col': 1, 'size': (2, 1)},
                'B': {'row': 1, 'col': 3, 'size': (2, 1)},
                'C': {'row': 1, 'col': 0, 'size': (2, 1)},
                'D': {'row': 3, 'col': 3, 'size': (2, 1)},
                'E': {'row': 0, 'col': 2, 'size': (1, 2)},
                'F': {'row': 4, 'col': 1, 'size': (1, 1)},
                'G': {'row': 1, 'col': 2, 'size': (1, 1)},
                'H': {'row': 4, 'col': 0, 'size': (1, 1)},
                'I': {'row': 4, 'col': 2, 'size': (1, 1)}
            },
            #board 3 below
            {
                'X': {'row': 1, 'col': 1, 'size': (2, 2)},
                'A': {'row': 1, 'col': 0, 'size': (2, 1)},
                'B': {'row': 3, 'col': 3, 'size': (2, 1)},
                'C': {'row': 3, 'col': 0, 'size': (2, 1)},
                'D': {'row': 1, 'col': 3, 'size': (2, 1)},
                'E': {'row': 0, 'col': 1, 'size': (1, 2)},
                'F': {'row': 0, 'col': 3, 'size': (1, 1)},
                'G': {'row': 0, 'col': 0, 'size': (1, 1)},
                'H': {'row': 4, 'col': 1, 'size': (1, 1)},
                'I': {'row': 4, 'col': 2, 'size': (1, 1)}
            },
            #board 4 below
            {
                'X': {'row': 2, 'col': 1, 'size': (2, 2)},
                'A': {'row': 0, 'col': 0, 'size': (2, 1)},
                'B': {'row': 0, 'col': 3, 'size': (2, 1)},
                'C': {'row': 3, 'col': 0, 'size': (2, 1)},
                'D': {'row': 2, 'col': 3, 'size': (2, 1)},
                'E': {'row': 0, 'col': 1, 'size': (1, 2)},
                'F': {'row': 4, 'col': 2, 'size': (1, 1)},
                'G': {'row': 1, 'col': 1, 'size': (1, 1)},
                'H': {'row': 4, 'col': 1, 'size': (1, 1)},
                'I': {'row': 4, 'col': 3, 'size': (1, 1)}
            },
            #board 5 below
            {
                'X': {'row': 2, 'col': 1, 'size': (2, 2)},
                'A': {'row': 1, 'col': 0, 'size': (2, 1)},
                'B': {'row': 3, 'col': 3, 'size': (2, 1)},
                'C': {'row': 3, 'col': 0, 'size': (2, 1)},
                'D': {'row': 0, 'col': 3, 'size': (2, 1)},
                'E': {'row': 1, 'col': 1, 'size': (1, 2)},
                'F': {'row': 0, 'col': 2, 'size': (1, 1)},
                'G': {'row': 0, 'col': 1, 'size': (1, 1)},
                'H': {'row': 4, 'col': 2, 'size': (1, 1)},
                'I': {'row': 4, 'col': 1, 'size': (1, 1)}
            },
            #board 6 below
            {
                'X': {'row': 2, 'col': 1, 'size': (2, 2)},
                'A': {'row': 0, 'col': 0, 'size': (2, 1)},
                'B': {'row': 3, 'col': 3, 'size': (2, 1)},
                'C': {'row': 3, 'col': 0, 'size': (2, 1)},
                'D': {'row': 1, 'col': 3, 'size': (2, 1)},
                'E': {'row': 1, 'col': 1, 'size': (1, 2)},
                'F': {'row': 0, 'col': 3, 'size': (1, 1)},
                'G': {'row': 0, 'col': 2, 'size': (1, 1)},
                'H': {'row': 4, 'col': 1, 'size': (1, 1)},
                'I': {'row': 4, 'col': 2, 'size': (1, 1)}
            },
            #board 7 below
            {
                'X': {'row': 2, 'col': 2, 'size': (2, 2)},
                'A': {'row': 1, 'col': 0, 'size': (2, 1)},
                'B': {'row': 0, 'col': 2, 'size': (2, 1)},
                'C': {'row': 3, 'col': 0, 'size': (2, 1)},
                'D': {'row': 0, 'col': 3, 'size': (2, 1)},
                'E': {'row': 0, 'col': 0, 'size': (1, 2)},
                'F': {'row': 4, 'col': 1, 'size': (1, 1)},
                'G': {'row': 1, 'col': 1, 'size': (1, 1)},
                'H': {'row': 3, 'col': 1, 'size': (1, 1)},
                'I': {'row': 4, 'col': 3, 'size': (1, 1)}
            },
            #board 8 below
            {
                'X': {'row': 2, 'col': 1, 'size': (2, 2)},
                'A': {'row': 0, 'col': 0, 'size': (2, 1)},
                'B': {'row': 1, 'col': 3, 'size': (2, 1)},
                'C': {'row': 2, 'col': 0, 'size': (2, 1)},
                'D': {'row': 3, 'col': 3, 'size': (2, 1)},
                'E': {'row': 0, 'col': 1, 'size': (1, 2)},
                'F': {'row': 4, 'col': 1, 'size': (1, 1)},
                'G': {'row': 1, 'col': 1, 'size': (1, 1)},
                'H': {'row': 4, 'col': 0, 'size': (1, 1)},
                'I': {'row': 4, 'col': 2, 'size': (1, 1)}
            },
            #board 9 below
            {
                'X': {'row': 2, 'col': 1, 'size': (2, 2)},
                'A': {'row': 0, 'col': 0, 'size': (2, 1)},
                'B': {'row': 0, 'col': 3, 'size': (2, 1)},
                'C': {'row': 2, 'col': 0, 'size': (2, 1)},
                'D': {'row': 2, 'col': 3, 'size': (2, 1)},
                'E': {'row': 0, 'col': 1, 'size': (1, 2)},
                'F': {'row': 4, 'col': 1, 'size': (1, 1)},
                'G': {'row': 1, 'col': 2, 'size': (1, 1)},
                'H': {'row': 4, 'col': 0, 'size': (1, 1)},
                'I': {'row': 4, 'col': 3, 'size': (1, 1)}
            }
        ]

        #return copy.deepcopy(pieceArrangements[board_index]) #specify board here if needed

        if last_board is not None:
            piece = copy.deepcopy(pieceArrangements[last_board])
            return piece

        index = random.randrange(len(pieceArrangements))
        if index not in usedBoards:
            piece = copy.deepcopy(pieceArrangements[index])
            usedBoards.append(index)
        else:
            return initialise_pieces()
        
        return piece

    def initialise_board(klotski_gameCount, currentPieces):
        global klotski_errorMessage

        board = [[' ' for _ in range(4)] for _ in range(5)] #create a list of 5 lists (rows), each with 4 elements (columns); change here also if dimension changes
        
        for piece, info in currentPieces.items():
            row, col = info['row'], info['col']
            height, width = info['size']
            for r in range(row, row + height):
                for c in range(col, col + width):
                    board[r][c] = piece

        #change also the no of rounds here!!
        klotski_errorMessage = f"Your goal is to retrieve the engine part 'X' by moving the obstacles around.\nMove 'X' to the bottom middle of the board to retrieve it! \nYou have retrieved {3 - klotski_gameCount}/3 of the engine parts."
        
        return board

    def initialise_game(klotski_gameCount, last_board=None): #run this instead of individually
        currentPieces = initialise_pieces(last_board)
        board = initialise_board(klotski_gameCount, currentPieces)
        display_board(board)
        
        return board, currentPieces

    def print_wrap(text, delay=0.02): #directly copied from main code; delete when merge
        """Prints text wrapped to the 80-column terminal constraint."""
        paragraphs = text.split('\n')
        for p in paragraphs:
            if p.strip() == "":
                print("")
            else:
                wrapped = textwrap.fill(p, width=MAX_WIDTH)
                print(wrapped)
                time.sleep(delay)

    def clear_terminal(): #delete this when merging
        """Simulates clearing the terminal by printing newlines, staying within 24 rows."""
        print("\n" * MAX_HEIGHT)
    
    def display_board(board):
        global klotski_errorMessage

        clear_terminal()
        print("[Mini-game 4: Klotski]")
        for index,row in enumerate(board):
            if index == 0:
                print('+---------+')
            for rowIndex,item in enumerate(row):
                if rowIndex == 0:
                    print('|', end=' ')
                print(item, end=' ')
                if rowIndex == len(row) - 1:
                    print('|', end=' ')
            print()
            if index == len(board) - 1:
                print('+---   ---+')  
        if klotski_errorMessage != "":
            print_wrap(klotski_errorMessage)
            klotski_errorMessage = ""

    def get_user_input():
        global klotski_errorMessage

        while True:
            print_wrap("Enter move (e.g., A up, B down, etc.), ':r' to reset board, or ':q' to exit: ")
            user_input = input("")
            if user_input.lower() == ':q':
                return 'quit'
            if user_input.lower() == ':r':
                return 'reset'

            parts = user_input.split()
            if len(parts) == 2 and parts[0].isalpha() and parts[1] in ['up', 'down', 'left', 'right']:
                parts[0] = parts[0].upper()
                return parts
            else:
                klotski_errorMessage = "Invalid input. Please enter a valid move."
                display_board(board)

    def move_piece(board, currentPieces, piece, direction):
        global klotski_errorMessage
        global lastResetBoard
        klotski_errorMessage = ""

        if piece not in currentPieces:
            klotski_errorMessage = f"Piece {piece} does not exist on the board."
            return

        row, col = currentPieces[piece]['row'], currentPieces[piece]['col']
        height, width = currentPieces[piece]['size']

        if direction == 'up':
            newRow, newCol = row - 1, col #counts from top to bottom
        elif direction == 'down':
            newRow, newCol = row + 1, col
        elif direction == 'left':
            newRow, newCol = row, col - 1
        elif direction == 'right':
            newRow, newCol = row, col + 1
        else:
            klotski_errorMessage = "Invalid direction."
            return

        #checks if 1) the new position is within the board boundaries and 2) if the new position is empty or occupied by the same piece, i.e. (' ' or piece)
        if (0 <= newRow and newRow + height <= 5 and 0 <= newCol and newCol + width <= 4 and all(board[r][c] in (' ', piece) for r in range(newRow, newRow + height) for c in range(newCol, newCol + width))):
            for r in range(row, row + height):
                for c in range(col, col + width):
                    board[r][c] = ' '

            currentPieces[piece]['row'], currentPieces[piece]['col'] = newRow, newCol

            for r in range(newRow, newRow + height):
                for c in range(newCol, newCol + width):
                    board[r][c] = piece

            klotski_errorMessage = ""
        else:
            klotski_errorMessage = "Invalid move. The piece cannot be moved in that direction."

    def determine_win(board):
        #both for debugging
        #return False

        #while klotski_gameCount > 0:
           #return True
        return (board[3][1] == 'X' and board[4][2] == 'X')

    def reset_board(last_board):
        global klotski_errorMessage

        currentPieces = initialise_pieces(last_board)
        board = initialise_board(klotski_gameCount, currentPieces)

        klotski_errorMessage = "Board has been reset to the initial state."

        return board, currentPieces

    global klotski_errorMessage
    global klotski_gameCount
    global board
    global currentPieces
    MAX_WIDTH = 80 #delete when merge
    MAX_HEIGHT = 24 #delete when merge
    klotski_gameCount = 3 #change here to change no of rounds and dont forget to update the message in initialise_board
    usedBoards = []
    klotski_errorMessage = ""
    board, currentPieces = initialise_game(klotski_gameCount)

    while not klotski_gameCount == 0:
        if not determine_win(board):
            user_input = get_user_input()
            if user_input == 'quit': 
                print_wrap("Game exited.")
                return
            if user_input == 'reset':
                board, currentPieces = reset_board(usedBoards[-1])
                display_board(board)
                continue

            piece, direction = user_input
            move_piece(board, currentPieces, piece, direction)
            display_board(board)
        elif not klotski_gameCount == 0:
            klotski_gameCount -= 1
            print_wrap("Congratulations! You've retrieved the engine part! Press Enter to continue...")
            input()
            board, currentPieces = initialise_game(klotski_gameCount)
    else:
        clear_terminal()
        print_wrap("\nCongratulations! You've retrieved all the engine parts!\n")
        input()

    return True

if __name__ == "__main__":
    play_klotski()