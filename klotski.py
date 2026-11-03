import random
import copy
import time
import textwrap

#lowercase input is fine
#change the number of rounds in klotski_gameCount at the bottom (~line 360), klotski_moveCount (~line 360) and update the message in initialise_board (~line 220)
#other dimensions than 4*5 are not yet tested but should be fine; but the dimensions must be consistent since the dimensions of the board is fixed in initialise_board() (default 4*5)
#klotski_board and klotski_currentPieces can become async and is synced in move_piece() and reset_board() (using initialise_board); always update klotski_board, klotski_currentPieces from initialise_game() to avoid async between rounds
#returns new difficulty as numbers 0,1,2 directly
# ---- delete print_wrap(), clear_terminal() and MAX_WIDTH, MAX_HEIGHT when merging; but do import copy ----

class klotski:
    def play_klotski(self, difficulty=None):
        def initialise_pieces(last_board=None):
            global klotski_moveThreshold
            global klotski_difficultyRate
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
                    'D': {'row': 0, 'col': 0, 'size': (2, 1)},
                    'A': {'row': 0, 'col': 3, 'size': (2, 1)},
                    'C': {'row': 2, 'col': 0, 'size': (2, 1)},
                    'B': {'row': 2, 'col': 3, 'size': (2, 1)},
                    'E': {'row': 0, 'col': 1, 'size': (1, 2)},
                    'F': {'row': 4, 'col': 1, 'size': (1, 1)},
                    'G': {'row': 1, 'col': 2, 'size': (1, 1)},
                    'I': {'row': 4, 'col': 0, 'size': (1, 1)},
                    'H': {'row': 4, 'col': 3, 'size': (1, 1)}
                },
                #board 10 below
                {
                    'X': {'row': 1, 'col': 1, 'size': (2, 2)},
                    'A': {'row': 0, 'col': 0, 'size': (2, 1)},
                    'B': {'row': 1, 'col': 3, 'size': (2, 1)},
                    'C': {'row': 2, 'col': 0, 'size': (2, 1)},
                    'D': {'row': 3, 'col': 3, 'size': (2, 1)},
                    'E': {'row': 0, 'col': 2, 'size': (1, 2)},
                    'F': {'row': 3, 'col': 2, 'size': (1, 1)},
                    'G': {'row': 0, 'col': 1, 'size': (1, 1)},
                    'H': {'row': 4, 'col': 0, 'size': (1, 1)},
                    'I': {'row': 4, 'col': 2, 'size': (1, 1)}
                },
                #board 11 below
                {
                    'X': {'row': 2, 'col': 1, 'size': (2, 2)},
                    'A': {'row': 0, 'col': 1, 'size': (2, 1)},
                    'B': {'row': 1, 'col': 3, 'size': (2, 1)},
                    'C': {'row': 0, 'col': 0, 'size': (2, 1)},
                    'D': {'row': 3, 'col': 3, 'size': (2, 1)},
                    'E': {'row': 0, 'col': 2, 'size': (1, 2)},
                    'F': {'row': 4, 'col': 1, 'size': (1, 1)},
                    'G': {'row': 1, 'col': 2, 'size': (1, 1)},
                    'H': {'row': 4, 'col': 0, 'size': (1, 1)},
                    'I': {'row': 4, 'col': 2, 'size': (1, 1)}
                }
            ]

            '''
            ez: 0, 1, 2, 5, 11
            medium: 3, 4, 6, 7
            hard: 8, 9, 10
            '''

            #difficulty = 2 #specify difficulty here if needed

            if last_board is not None:
                piece = copy.deepcopy(pieceArrangements[last_board])
                return piece

            if difficulty == 0: #easy
                easyBoards = [0, 1, 2, 5, 11]
                klotski_moveThreshold = 25
                klotski_difficultyRate = "easy"
                index = random.choice(easyBoards)
            elif difficulty == 1: #medium   
                mediumBoards = [3, 4, 6, 7]
                klotski_moveThreshold = 35
                klotski_difficultyRate = "medium"
                index = random.choice(mediumBoards)
            elif difficulty == 2: #hard
                hardBoards = [8, 9, 10]
                klotski_moveThreshold = 45
                klotski_difficultyRate = "hard"
                index = random.choice(hardBoards)
            else:
                index = random.randrange(len(pieceArrangements))
                klotski_moveThreshold = 35
                klotski_difficultyRate = "randomised"

            #index = 6 #specify board here if needed

            if index not in usedBoards:
                piece = copy.deepcopy(pieceArrangements[index])
                usedBoards.append(index)
            else:
                return initialise_pieces()
            
            return piece

        def initialise_board(klotski_gameCount, klotski_currentPieces):
            global klotski_errorMessage

            klotski_board = [[' ' for _ in range(4)] for _ in range(5)] #create a list of 5 lists (rows), each with 4 elements (columns); change here also if dimension changes
            
            for piece, info in klotski_currentPieces.items():
                row, col = info['row'], info['col']
                height, width = info['size']
                for r in range(row, row + height):
                    for c in range(col, col + width):
                        klotski_board[r][c] = piece

            #change also the no of rounds here!!
            klotski_errorMessage = f"Your goal is to retrieve the engine part 'X' by moving the obstacles around.\nMove 'X' to the bottom middle of the board to retrieve it! \nYou have retrieved {3 - klotski_gameCount}/3 of the engine parts."
            
            return klotski_board

        def initialise_game(klotski_gameCount, last_board=None): #run this instead of individually
            klotski_currentPieces = initialise_pieces(last_board)
            klotski_board = initialise_board(klotski_gameCount, klotski_currentPieces)
            display_board(klotski_board)
            
            return klotski_board, klotski_currentPieces

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
        
        def display_board(klotski_board):
            global klotski_errorMessage
            global klotski_moveCount
            global klotski_gameCount
            global klotski_difficultyRate

            clear_terminal()
            #print(f"Boards used: {usedBoards}") #for debugging
            print("[Mini-game 3: Klotski]")
            print(f"Difficulty: {klotski_difficultyRate}")
            print(f"Total moves made: {sum(klotski_moveCount)}")
            for index,row in enumerate(klotski_board):
                if index == 0:
                    print('+---------+')
                for rowIndex,item in enumerate(row):
                    if rowIndex == 0:
                        print('|', end=' ')
                    print(item, end=' ')
                    if rowIndex == len(row) - 1:
                        print('|', end=' ')
                print()
                if index == len(klotski_board) - 1:
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
                    display_board(klotski_board)

        def move_piece(klotski_board, klotski_currentPieces, piece, direction):
            global klotski_errorMessage
            global klotski_lastResetBoard
            global klotski_moveCount
            global klotski_gameCount
            klotski_errorMessage = ""

            if piece not in klotski_currentPieces:
                klotski_errorMessage = f"Piece {piece} does not exist on the board."
                return

            row, col = klotski_currentPieces[piece]['row'], klotski_currentPieces[piece]['col']
            height, width = klotski_currentPieces[piece]['size']

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
            if (0 <= newRow and newRow + height <= 5 and 0 <= newCol and newCol + width <= 4 and all(klotski_board[r][c] in (' ', piece) for r in range(newRow, newRow + height) for c in range(newCol, newCol + width))):
                for r in range(row, row + height):
                    for c in range(col, col + width):
                        klotski_board[r][c] = ' '

                klotski_currentPieces[piece]['row'], klotski_currentPieces[piece]['col'] = newRow, newCol

                for r in range(newRow, newRow + height):
                    for c in range(newCol, newCol + width):
                        klotski_board[r][c] = piece

                klotski_errorMessage = ""
                klotski_moveCount[-(klotski_gameCount-3)] += 1
            else:
                klotski_errorMessage = "Invalid move. The piece cannot be moved in that direction."

        def determine_win(klotski_board):
            #both for debugging
            #return False

            #while klotski_gameCount > 0:
            #return True
            return (klotski_board[3][1] == 'X' and klotski_board[4][2] == 'X')

        def reset_board(last_board):
            global klotski_errorMessage
            global klotski_moveCount
            global klotski_gameCount

            klotski_currentPieces = initialise_pieces(last_board)
            klotski_board = initialise_board(klotski_gameCount, klotski_currentPieces)

            klotski_errorMessage = "Board has been reset to the initial state."
            klotski_moveCount[-(klotski_gameCount-3)] = 0

            return klotski_board, klotski_currentPieces

        global klotski_errorMessage
        global klotski_gameCount
        global klotski_moveCount
        global klotski_board
        global klotski_currentPieces
        MAX_WIDTH = 80 #delete when merge
        MAX_HEIGHT = 24 #delete when merge
        klotski_gameCount = 3 #change here to change no of rounds and dont forget to update the message in initialise_board
        klotski_moveCount = []
        usedBoards = []
        klotski_errorMessage = ""
        klotski_board, klotski_currentPieces = initialise_game(klotski_gameCount)

        for _ in range(klotski_gameCount):
            klotski_moveCount.append(0)

        while not klotski_gameCount == 0:
            if not determine_win(klotski_board):
                user_input = get_user_input()
                if user_input == 'quit': 
                    print_wrap("Game exited.")
                    return
                if user_input == 'reset':
                    klotski_board, klotski_currentPieces = reset_board(usedBoards[-1])
                    display_board(klotski_board)
                    continue

                piece, direction = user_input
                move_piece(klotski_board, klotski_currentPieces, piece, direction)
                display_board(klotski_board)
            elif not klotski_gameCount == 0:
                klotski_gameCount -= 1
                print_wrap("Congratulations! You've retrieved the engine part! Press Enter to continue...")
                input()
                klotski_board, klotski_currentPieces = initialise_game(klotski_gameCount)
        else:
            clear_terminal()
            print_wrap(f"\nCongratulations! You've retrieved all the engine parts with {sum(klotski_moveCount)} moves!\n")
            input()
            if sum(klotski_moveCount) < klotski_moveThreshold and difficulty != 0:
                return (difficulty-1)
            elif sum(klotski_moveCount) == klotski_moveThreshold or difficulty == 2 or difficulty == 0:
                return (difficulty)
            elif sum(klotski_moveCount) > klotski_moveThreshold:
                return (difficulty+1)

if __name__ == "__main__":
    game = klotski()
    game.play_klotski()