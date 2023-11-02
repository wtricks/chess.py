# Some related methods
from constants import Constant
from store import Store
import re

class Util:
    
    def __init__(self) -> None:
        self.STORE = None

    # initialize the board with 64 squares
    def __initialize(self, SQUARE: list):
        for _ in range(8): 
            row: list = []
            for __ in range(8):
                row.append(Constant.EMPTY)

            SQUARE.append(row)

    # laod a new game
    def load(self, fen: str):
        parts = re.split("\s+", fen)
        if len(parts) != 6:
            return "Invalid Fen String given!"

        rows = re.split("\/", parts[0])
        if len(rows) != 8:
            return "Invalid Fen String given!"
        
        prevStore = self.STORE
        store = self.STORE = Store() # store new positions
        self.__initialize(store.SQUARE) # create 64 squares

        index = 0
        for row in range(8):
            if index != 8 and index != 0:
                return f"Row {row} is Invalid in FEN"

            index = 0
            for col in range(len(rows[row])):
                current = rows[row][col]
                if current.isnumeric():
                    index += int(current)
                    continue

                else: index += 1

                if index > 8:
                    return f"Maximum 8 pieces are in row {row+1}"
                
                color = Constant.BLACK if "kqbnrp".find(current) >= 0 else Constant.WHITE if "KQRNBP".find(current) >= 0 else Constant.NO_FLAG
                if (color == None): return f"Invalid character '{current}' given in row {row+1}"
                
                # store position of pieces
                current = current.upper()
                store.SQUARE[row][index - 1] = (color, current)

                if current == Constant.KING:
                    if store.KINGS[0 if color == Constant.WHITE else 1] != None:
                        return "One can only have one king"
                    
                    store.KINGS[0 if color == Constant.WHITE else 1] = (index-1, row)
                
        if store.KINGS[0] == None or store.KINGS[1] == None:
            return "Both side must have 1 king"

        # count moves
        store.MOVE_COUNT[0] = int(parts[4])  
        store.MOVE_COUNT[1] = int(parts[5])   

        # set turn and epssant square position
        store.TURN = Constant.WHITE if parts[1] == 'w' else Constant.BLACK
        store.E_PASSANT = -1 if len(parts[3]) != 2 else 1 # need to get location

        if (parts[2].index('K') != -1): store.CASTLE[0] += 1
        if (parts[2].index('Q') != -1): store.CASTLE[0] += 2
        if (parts[2].index('k') != -1): store.CASTLE[1] += 1
        if (parts[2].index('q') != -1): store.CASTLE[1] += 2
        return (prevStore, self.STORE)
    
    # get the current position of pieces
    def currentPosition(self) -> str: 
        fen = []
        for row in self.STORE.SQUARE:
            fen_row = ''
            empty_count = 0

            for piece in row:
                if piece[0] == None:
                    empty_count += 1
                else:
                    if empty_count > 0:
                        fen_row += str(empty_count)
                        empty_count = 0
                    color, piece_type = piece
                    fen_row += self.__getPiece(piece_type, color)
            
            if empty_count > 0:
                fen_row += str(empty_count)

            fen.append(fen_row)

        return '/'.join(fen)

    def __getPiece(self, piece_type, color):
        if color == Constant.BLACK:
            return piece_type.lower()
        else:
            return piece_type.upper()    

    # Generate FEN string 
    def getFen(self):
        if (self.STORE == None):
            return ''
        
        # get the positions of current pieces
        fen = self.currentPosition()
        store = self.STORE
        temp = ' '

        if store.CASTLE[0] == 1 or store.CASTLE[0] == 3:
            temp += Constant.KING

        if store.CASTLE[0] >= 2:
            temp += Constant.QUEEN

        if store.CASTLE[1] == 1 or store.CASTLE[1] == 3:
            temp += Constant.KING.lower()

        if store.CASTLE[1] >= 2:
            temp += Constant.QUEEN.lower() 

        # add current turn
        fen += " " + store.TURN.lower()  
        fen += temp if temp != ' ' else ' -'

        # epassant
        fen += " - " if store.E_PASSANT == -1 else "e4 "
        fen += f"{store.MOVE_COUNT[0]} {store.MOVE_COUNT[1]}"
        
        return fen

    # print piecs
    def print(self):
        if (self.STORE == None):
            return ''
        
        # get the positions of current pieces
        position = self.STORE.SQUARE
        hold = ''

        for row in range(8):
            current = f"{(8 - row)} |"

            for col in range(8):
                if (position[row][col][0] == None):
                    current += ' - '

                else:
                    temp = position[row][col]
                    current += " " + (temp[1].upper() if temp[0] == Constant.WHITE else temp[1].lower()) + " "
            
            hold += current + '\n'

        hold += "- - -  -  -  -  -  -  -  -\n"
        hold += "  | a  b  c  d  e  f  g  h"
        print(hold)

    # update position of piece
    def update(self, _from: tuple, _to: tuple):
        self.STORE.SQUARE[_to[1]][_to[0]] = self.STORE.SQUARE[_from[1]][_from[0]]
        self.STORE.SQUARE[_from[1]][_from[0]] = Constant.EMPTY

    def getturn(self):
        return self.STORE.TURN
    
    def setturn(self, turn: str):
        self.STORE.TURN = turn

    # get piece at specified index
    def getPiece(self, square: tuple):
        x, y = square[0], square[1]
        return self.STORE.SQUARE[y][x]


    # get all places unsafe at specified index
    def getUnsafePlace(self, color: str, square: tuple):
        x = self.STORE.UNSAFE

        if x[0] == color and f"{square[0]}{square[1]}" in x[1]:
            return x[1][f"{square[0]}{square[1]}"]
        
        if x[0] != color:
            x[1].clear()

        return None

    # add places unsafe at specified index
    def addUnsafePlace(self, color: str, square: tuple, lst: list):
        self.STORE.UNSAFE[0] = color
        self.STORE.UNSAFE[1][f"{square[0]}{square[1]}"] = lst

    # set current player king square
    def setKingSquare(self, color: str, pos: tuple):
        self.STORE.KINGS[0 if color == Constant.WHITE else 1] = pos

    # get current player king square
    def getKingSquare(self, color: str):
        return self.STORE.KINGS[0 if color == Constant.WHITE else 1]

    # set current game status
    def getStatus(self):
        return self.STORE.STATUS

    # set current game status
    def setStatus(self, type: str):
        self.STORE.STATUS = str