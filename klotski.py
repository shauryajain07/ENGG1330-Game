import random
import copy
import time
import textwrap

#lowercase input is fine
#change the number of rounds in klotski_gameCount, klotski_moveCount, win exception (~line 220) and update the message in initialise_board (~line 240)
#other dimensions than 4*5 are not yet tested but should be fine; but the dimensions must be consistent since the dimensions of the board is fixed in initialise_board() (default 4*5)
#klotski_board and klotski_currentPieces can become async and is synced in move_piece() and reset_board() (using initialise_board); always update klotski_board, klotski_currentPieces from initialise_game() to avoid async between rounds
#returns new difficulty as numbers 0,1,2 directly, and remaining energy after this minigame as tuple

class klotski:
    def __init__(self):
        self.klotski_errorMessage = ""
        self.klotski_gameCount = 3
        self.klotski_moveCount = []
        self.klotski_board = []
        self.klotski_currentPieces = {}
        self.klotski_moveThreshold = 35
        self.klotski_difficultyRate = "randomised"
        self.klotski_energy = 0
        self.klotski_hasHinted = False
        self.MAX_WIDTH = 80
        self.MAX_HEIGHT = 24
        self.klotski_usedBoards = []
        self.effectiveDifficulty = None

    def play_klotski(self, difficulty=None, energy=None):
        def initialise_pieces(last_board=None, difficulty=difficulty):
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

            if last_board is not None: #for reset
                piece = copy.deepcopy(pieceArrangements[last_board])
                return piece

            if difficulty is None:
                self.effectiveDifficulty = 1
                index = random.randrange(len(pieceArrangements))
            elif difficulty == 0: #easy
                easyBoards = [0, 1, 2, 5, 11]
                self.klotski_moveThreshold = 25
                self.klotski_difficultyRate = "easy"
                self.effectiveDifficulty = 0
                index = random.choice(easyBoards)
            elif difficulty == 1: #medium   
                mediumBoards = [3, 4, 6, 7]
                self.klotski_difficultyRate = "medium"
                self.effectiveDifficulty = 1
                index = random.choice(mediumBoards)
            elif difficulty == 2: #hard
                hardBoards = [8, 9, 10]
                self.klotski_moveThreshold = 45
                self.effectiveDifficulty = 2
                self.klotski_difficultyRate = "hard"
                index = random.choice(hardBoards)

            #index = 11 #specify board here if needed

            if not self.klotski_usedBoards or index not in self.klotski_usedBoards or len(self.klotski_usedBoards) != 3: #win condition
                piece = copy.deepcopy(pieceArrangements[index])
                self.klotski_usedBoards.append(index)
            else:
                #print(self.klotski_usedBoards)
                return initialise_pieces()
            
            return piece

        def initialise_board(klotski_gameCount,klotski_currentPieces):
            self.klotski_board = [[' ' for _ in range(4)] for _ in range(5)] #create a list of 5 lists (rows), each with 4 elements (columns); change here also if dimension changes
            
            for piece, info in klotski_currentPieces.items():
                row, col = info['row'], info['col']
                height, width = info['size']
                for r in range(row, row + height):
                    for c in range(col, col + width):
                        self.klotski_board[r][c] = piece

            #change also the no of rounds here!!
            self.klotski_errorMessage = f"Your goal is to retrieve the engine part 'X' by moving the obstacles around.\nMove 'X' to the bottom middle of the board to retrieve it! \nYou have retrieved {3 - klotski_gameCount}/3 of the engine parts."
            
            return self.klotski_board

        def initialise_game(klotski_gameCount, last_board=None, difficulty=difficulty): #run this instead of individually
            klotski_currentPieces = initialise_pieces(last_board, difficulty)
            klotski_board = initialise_board(klotski_gameCount, klotski_currentPieces)
            display_board(klotski_board)
            #print(self.effectiveDifficulty)

            return klotski_board, klotski_currentPieces

        def hint_arrangement(cuurentBoardIndex):
            hintArrangements = [
                # Board 0
                {
                    'X': {'row': 2, 'col': 1, 'size': (2, 2)},
                    'A': {'row': 1, 'col': 0, 'size': (2, 1)},
                    'B': {'row': 0, 'col': 3, 'size': (2, 1)},
                    'C': {'row': 3, 'col': 0, 'size': (2, 1)},
                    'D': {'row': 2, 'col': 3, 'size': (2, 1)},
                    'E': {'row': 0, 'col': 0, 'size': (1, 2)},
                    'F': {'row': 1, 'col': 1, 'size': (1, 1)},
                    'G': {'row': 0, 'col': 2, 'size': (1, 1)},
                    'H': {'row': 4, 'col': 3, 'size': (1, 1)},
                    'I': {'row': 1, 'col': 2, 'size': (1, 1)},
                },
                # Board 1
                {
                    'X': {'row': 2, 'col': 1, 'size': (2, 2)},
                    'A': {'row': 1, 'col': 0, 'size': (2, 1)},
                    'B': {'row': 0, 'col': 3, 'size': (2, 1)},
                    'C': {'row': 3, 'col': 0, 'size': (2, 1)},
                    'D': {'row': 2, 'col': 3, 'size': (2, 1)},
                    'E': {'row': 0, 'col': 0, 'size': (1, 2)},
                    'F': {'row': 1, 'col': 1, 'size': (1, 1)},
                    'G': {'row': 0, 'col': 2, 'size': (1, 1)},
                    'H': {'row': 4, 'col': 2, 'size': (1, 1)},
                    'I': {'row': 1, 'col': 2, 'size': (1, 1)},
                },
                # Board 2
                {
                    'X': {'row': 2, 'col': 1, 'size': (2, 2)},
                    'A': {'row': 0, 'col': 1, 'size': (2, 1)},
                    'B': {'row': 1, 'col': 3, 'size': (2, 1)},
                    'C': {'row': 0, 'col': 0, 'size': (2, 1)},
                    'D': {'row': 3, 'col': 3, 'size': (2, 1)},
                    'E': {'row': 0, 'col': 2, 'size': (1, 2)},
                    'F': {'row': 4, 'col': 0, 'size': (1, 1)},
                    'G': {'row': 1, 'col': 2, 'size': (1, 1)},
                    'H': {'row': 2, 'col': 0, 'size': (1, 1)},
                    'I': {'row': 4, 'col': 2, 'size': (1, 1)},
                },
                # Board 3
                {
                    'X': {'row': 2, 'col': 1, 'size': (2, 2)},
                    'A': {'row': 1, 'col': 0, 'size': (2, 1)},
                    'B': {'row': 2, 'col': 3, 'size': (2, 1)},
                    'C': {'row': 3, 'col': 0, 'size': (2, 1)},
                    'D': {'row': 0, 'col': 3, 'size': (2, 1)},
                    'E': {'row': 1, 'col': 1, 'size': (1, 2)},
                    'F': {'row': 0, 'col': 2, 'size': (1, 1)},
                    'G': {'row': 0, 'col': 1, 'size': (1, 1)},
                    'H': {'row': 4, 'col': 1, 'size': (1, 1)},
                    'I': {'row': 4, 'col': 2, 'size': (1, 1)},
                },
                # Board 4
                {
                    'X': {'row': 2, 'col': 1, 'size': (2, 2)},
                    'A': {'row': 1, 'col': 0, 'size': (2, 1)},
                    'B': {'row': 0, 'col': 2, 'size': (2, 1)},
                    'C': {'row': 3, 'col': 0, 'size': (2, 1)},
                    'D': {'row': 0, 'col': 3, 'size': (2, 1)},
                    'E': {'row': 0, 'col': 0, 'size': (1, 2)},
                    'F': {'row': 4, 'col': 2, 'size': (1, 1)},
                    'G': {'row': 1, 'col': 1, 'size': (1, 1)},
                    'H': {'row': 4, 'col': 1, 'size': (1, 1)},
                    'I': {'row': 3, 'col': 3, 'size': (1, 1)},
                },
                # Board 5
                {
                    'X': {'row': 2, 'col': 1, 'size': (2, 2)},
                    'A': {'row': 0, 'col': 0, 'size': (2, 1)},
                    'B': {'row': 2, 'col': 3, 'size': (2, 1)},
                    'C': {'row': 2, 'col': 0, 'size': (2, 1)},
                    'D': {'row': 0, 'col': 3, 'size': (2, 1)},
                    'E': {'row': 1, 'col': 1, 'size': (1, 2)},
                    'F': {'row': 0, 'col': 2, 'size': (1, 1)},
                    'G': {'row': 0, 'col': 1, 'size': (1, 1)},
                    'H': {'row': 4, 'col': 2, 'size': (1, 1)},
                    'I': {'row': 4, 'col': 1, 'size': (1, 1)},
                },
                # Board 6
                {
                    'X': {'row': 2, 'col': 1, 'size': (2, 2)},
                    'A': {'row': 0, 'col': 0, 'size': (2, 1)},
                    'B': {'row': 3, 'col': 3, 'size': (2, 1)},
                    'C': {'row': 2, 'col': 0, 'size': (2, 1)},
                    'D': {'row': 0, 'col': 3, 'size': (2, 1)},
                    'E': {'row': 1, 'col': 1, 'size': (1, 2)},
                    'F': {'row': 0, 'col': 2, 'size': (1, 1)},
                    'G': {'row': 0, 'col': 1, 'size': (1, 1)},
                    'H': {'row': 4, 'col': 1, 'size': (1, 1)},
                    'I': {'row': 4, 'col': 2, 'size': (1, 1)},
                },
                # Board 7
                {
                    'X': {'row': 2, 'col': 1, 'size': (2, 2)},
                    'A': {'row': 1, 'col': 0, 'size': (2, 1)},
                    'B': {'row': 0, 'col': 2, 'size': (2, 1)},
                    'C': {'row': 3, 'col': 0, 'size': (2, 1)},
                    'D': {'row': 0, 'col': 3, 'size': (2, 1)},
                    'E': {'row': 0, 'col': 0, 'size': (1, 2)},
                    'F': {'row': 4, 'col': 3, 'size': (1, 1)},
                    'G': {'row': 1, 'col': 1, 'size': (1, 1)},
                    'H': {'row': 4, 'col': 1, 'size': (1, 1)},
                    'I': {'row': 3, 'col': 3, 'size': (1, 1)},
                },
                # Board 8
                {
                    'X': {'row': 2, 'col': 1, 'size': (2, 2)},
                    'A': {'row': 0, 'col': 1, 'size': (2, 1)},
                    'B': {'row': 1, 'col': 3, 'size': (2, 1)},
                    'C': {'row': 0, 'col': 0, 'size': (2, 1)},
                    'D': {'row': 3, 'col': 3, 'size': (2, 1)},
                    'E': {'row': 0, 'col': 2, 'size': (1, 2)},
                    'F': {'row': 4, 'col': 1, 'size': (1, 1)},
                    'G': {'row': 1, 'col': 2, 'size': (1, 1)},
                    'H': {'row': 3, 'col': 0, 'size': (1, 1)},
                    'I': {'row': 4, 'col': 2, 'size': (1, 1)},
                },
                # Board 9
                {
                    'X': {'row': 2, 'col': 1, 'size': (2, 2)},
                    'D': {'row': 0, 'col': 1, 'size': (2, 1)},
                    'A': {'row': 1, 'col': 3, 'size': (2, 1)},
                    'C': {'row': 0, 'col': 0, 'size': (2, 1)},
                    'B': {'row': 3, 'col': 3, 'size': (2, 1)},
                    'E': {'row': 0, 'col': 2, 'size': (1, 2)},
                    'F': {'row': 4, 'col': 1, 'size': (1, 1)},
                    'G': {'row': 1, 'col': 2, 'size': (1, 1)},
                    'I': {'row': 4, 'col': 0, 'size': (1, 1)},
                    'H': {'row': 4, 'col': 2, 'size': (1, 1)},
                },
                # Board 10
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
                    'I': {'row': 4, 'col': 2, 'size': (1, 1)},
                },
                # Board 11
                {
                    'X': {'row': 2, 'col': 1, 'size': (2, 2)},
                    'A': {'row': 0, 'col': 1, 'size': (2, 1)},
                    'B': {'row': 1, 'col': 3, 'size': (2, 1)},
                    'C': {'row': 0, 'col': 0, 'size': (2, 1)},
                    'D': {'row': 3, 'col': 3, 'size': (2, 1)},
                    'E': {'row': 0, 'col': 2, 'size': (1, 2)},
                    'F': {'row': 3, 'col': 0, 'size': (1, 1)},
                    'G': {'row': 1, 'col': 2, 'size': (1, 1)},
                    'H': {'row': 2, 'col': 0, 'size': (1, 1)},
                    'I': {'row': 4, 'col': 2, 'size': (1, 1)},
                },
            ]
            clear_terminal()

            hint_board = [[' ' for _ in range(4)] for _ in range(5)] #create a list of 5 lists (rows), each with 4 elements (columns); change here also if dimension changes
                
            for piece, info in hintArrangements[cuurentBoardIndex].items():
                row, col = info['row'], info['col']
                height, width = info['size']
                for r in range(row, row + height):
                    for c in range(col, col + width):
                        hint_board[r][c] = piece

            for index,row in enumerate(hint_board):
                if index == 0:
                    print('+---------+')
                for rowIndex,item in enumerate(row):
                    if rowIndex == 0:
                        print('|', end=' ')
                    print(item, end=' ')
                    if rowIndex == len(row) - 1:
                        print('|', end=' ')
                print()
                if index == len(hint_board) - 1:
                    print('+---   ---+')  

            print_wrap("Hint: This is an intermediate arrangement of pieces to solve the current puzzle. Use it as a reference to guide your moves.")
            input('Press Enter to continue...')
            display_board(self.klotski_board)

        def display_hint(cuurentBoardIndex, energy=self.klotski_energy):
            if energy==None or self.klotski_hasHinted:
                hint_arrangement(cuurentBoardIndex)
                self.klotski_hasHinted = True
            elif energy>0:
                clear_terminal()
                print_wrap(f"You have {energy} hint energy left. Using a hint will cost 1 energy. Are you sure you want to use a hint? (y/n): ")
                if input().lower() == 'y':
                    self.klotski_energy -= 1
                    self.klotski_hasHinted = True
                    hint_arrangement(cuurentBoardIndex)
                else:
                    self.klotski_errorMessage = "Hint usage cancelled."
                    display_board(self.klotski_board)
            else:
                self.klotski_errorMessage = "You have no energy left to use hints."
                display_board(self.klotski_board)

        def print_wrap(text, delay=0.02):
            """Prints text wrapped to the 80-column terminal constraint."""
            paragraphs = text.split('\n')
            for p in paragraphs:
                if p.strip() == "":
                    print("")
                else:
                    wrapped = textwrap.fill(p, width=self.MAX_WIDTH)
                    print(wrapped)
                    time.sleep(delay)

        def clear_terminal():
            """Simulates clearing the terminal by printing newlines, staying within 24 rows."""
            print("\n" * self.MAX_HEIGHT)
        
        def display_board(klotski_board):
            clear_terminal()
            #print(f"Boards used: {self.klotski_usedBoards}") #for debugging
            print("[Mini-game 3: Klotski]")
            print(f"Difficulty: {self.klotski_difficultyRate}")
            print(f"Total moves made: {sum(self.klotski_moveCount)}")
            print(f"Energy left: {self.klotski_energy}")
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
            if self.klotski_errorMessage != "":
                print_wrap(self.klotski_errorMessage)
                self.klotski_errorMessage = ""

        def get_user_input():
            while True:
                if self.klotski_energy is not None:
                    print_wrap("Enter move (e.g., A up, B down, etc.), ':r' to reset board, or ':h' for hint: ")
                else:
                    print_wrap("Enter move (e.g., A up, B down, etc.), ':r' to reset board, ':h' for hint, or ':q' to exit: ")
                user_input = input("")
                if user_input.lower() == ':q':
                    return 'quit'
                if user_input.lower() == ':r':
                    return 'reset'
                if user_input.lower() == ':h':
                    return 'hint'

                parts = user_input.split()
                if len(parts) == 2 and parts[0].isalpha() and parts[1] in ['up', 'down', 'left', 'right']:
                    parts[0] = parts[0].upper()
                    return parts
                else:
                    self.klotski_errorMessage = "Invalid input. Please enter a valid move."
                    display_board(self.klotski_board)

        def move_piece(klotski_board, klotski_currentPieces, piece, direction):
            self.klotski_errorMessage = ""

            if piece not in klotski_currentPieces:
                self.klotski_errorMessage = f"Piece {piece} does not exist on the board."
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
                self.klotski_errorMessage = "Invalid direction."
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

                self.klotski_errorMessage = ""
                self.klotski_moveCount[-(self.klotski_gameCount-3)] += 1
            else:
                self.klotski_errorMessage = "Invalid move. The piece cannot be moved in that direction."

        def determine_win(klotski_board):
            #both for debugging
            #return False
            '''
            while self.klotski_gameCount > 0:
                return True
            '''
            # The exit is reached when the 2x2 core covers these goal cells.
            return (klotski_board[3][1] == 'X' and klotski_board[4][2] == 'X')

        def reset_board(last_board):
            klotski_currentPieces = initialise_pieces(last_board)
            klotski_board = initialise_board(self.klotski_gameCount, klotski_currentPieces)

            self.klotski_errorMessage = "Board has been reset to the initial state."
            self.klotski_moveCount[-(self.klotski_gameCount-3)] = 0

            return klotski_board, klotski_currentPieces
        
        self.klotski_energy = energy

        try:
            self.klotski_board, self.klotski_currentPieces = initialise_game(self.klotski_gameCount, difficulty=difficulty)
        except KeyboardInterrupt:
            pass

        for _ in range(self.klotski_gameCount):
            self.klotski_moveCount.append(0)

        while not self.klotski_gameCount == 0:
            if not determine_win(self.klotski_board):
                user_input = get_user_input()
                if user_input == 'quit': 
                    print_wrap("Game exited.")
                    return
                if user_input == 'reset':
                    self.klotski_board, self.klotski_currentPieces = reset_board(self.klotski_usedBoards[-1])
                    display_board(self.klotski_board)
                    continue
                if user_input == 'hint':
                    #print(self.klotski_usedBoards[-1])
                    display_hint(self.klotski_usedBoards[-1], energy=self.klotski_energy)
                    continue

                piece, direction = user_input
                move_piece(self.klotski_board, self.klotski_currentPieces, piece, direction)
                display_board(self.klotski_board)
            elif not self.klotski_gameCount == 0:
                self.klotski_gameCount -= 1
                self.klotski_hasHinted = False
                print_wrap("Congratulations! You've retrieved the engine part! Press Enter to continue...")
                input()
                self.klotski_board, self.klotski_currentPieces = initialise_game(self.klotski_gameCount)
        else:
            clear_terminal()
            print_wrap(f"\nCongratulations! You've retrieved all the engine parts with {sum(self.klotski_moveCount)} moves!\n")
            input()
            if sum(self.klotski_moveCount) < self.klotski_moveThreshold and self.effectiveDifficulty != 2:
                return (self.effectiveDifficulty+1, self.klotski_energy)
            elif sum(self.klotski_moveCount) == self.klotski_moveThreshold or self.effectiveDifficulty == 0:
                return (self.effectiveDifficulty, self.klotski_energy)
            elif sum(self.klotski_moveCount) > self.klotski_moveThreshold:
                return (self.effectiveDifficulty-1, self.klotski_energy)

if __name__ == "__main__":
    game = klotski()
    game.play_klotski()
