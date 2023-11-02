# main chess class
from pattern import Pattern
from constants import Constant

class Chess:
    # piece that will be replaced with the pawn
    DEFAULT_P: str = Constant.QUEEN
    TH_RP = False
    IS_MA = True
    H_MOVE = True

    def __init__(self) -> None:
        self.pattern = Pattern()

    # load and construct board
    def load(self, fen: str = Constant.DEFAULT_FEN) -> str:
        x = self.pattern.load(fen)
        if type(x) == str:
            return x

        # set as default
        self.TH_RP = self.IS_MA = False
        
        # check game status
        if self.isGameOver():
            return "Game is Over"

        # add current piece positions
        self.pattern.STORE.FEN[self.pattern.currentPosition()] = 0
        return ""
        
    # get current turn
    def turn(self):
        return self.pattern.getturn()

    # get the opposite color
    def getOppositeColor(self):
        return Constant.WHITE if self.turn() == Constant.BLACK else Constant.BLACK

    # print the position of pieces
    def print(self):
        self.pattern.print()

    # Get the FEN of current board position
    def fen(self):
        return self.pattern.getFen()
    
    # move piece
    def move(self, _to: tuple, _from: tuple = Constant.EMPTY):
        return self.__move(_to, _from, True)

    def __move(self, _to: tuple, _from: tuple, remove: bool = False) -> bool:
        if self.lastMoves[0] == None:
            return False
        
        move = None
        for m in self.lastMoves:
            if m['to'][0] == _to[0] and m['to'][1] == _to[1]:
                if _from[0] == None:
                    move = m
                    break
                elif m['from'][0] == _from[0] and m['from'][1] == _from[1]:
                    move = m

        # if move is not valid or other reason
        if move == None or self.pattern.getStatus() != '':
            return False

        color = self.pattern.STORE.SQUARE[move['from'][1]][move['from'][0]][0]
        if self.turn() != color:
            return False
        
        # some important things
        castle = self.pattern.STORE.CASTLE
        ePassant = self.pattern.STORE.E_PASSANT
        count = self.pattern.STORE.MOVE_COUNT
        index = 0 if self.turn() == Constant.WHITE else 1
        squares = self.pattern.STORE.SQUARE
        capture = squares[_to[1]][_to[0]] if move['capture'] else Constant.EMPTY

        # first index will hold total turns
        if Constant.BLACK == color:
            count[0] += 1

        # if piece is pawn, we can sure that same position will not arive
        if move['piece'] == Constant.PAWN or move['capture']:
            self.pattern.STORE.FEN.clear()

        if move['flag'] != Constant.E_PASSANT:
            self.pattern.STORE.E_PASSANT = -1

        # if we are moving king or rook, so now current are not able to do castling
        if move['piece'] == Constant.KING or move['piece'] == Constant.ROOK:
            castle[index] = -1

        # if we are capturing piece using ePassant
        if move['flag'] == Constant.E_PASSANT:
            realPiecePosition = (ePassant, 4 if index == 0 else 3)
            count[1] = 0 # make zero, it will be use in fifty move draw
            capture = (self.getOppositeColor(), Constant.PAWN)
            self.pattern.STORE.E_PASSANT = -1
            squares[realPiecePosition[1]][realPiecePosition[0]] = Constant.EMPTY

        # if we can capture
        elif move['capture']:
            count[1] = 0 # make zero, it will be use in fifty move draw
       
        elif move['piece'] == Constant.PAWN:
            if move['flag'] == Constant.BIG_PAWN:
                self.pattern.STORE.E_PASSANT = _to[0] + 1 if color == Constant.WHITE else 1
            
            count[1] = 0 # make zero, it will be use in fifty move draw
        else: count[1] += 1

        # now let's move piece
        squares[_to[1]][_to[0]] = squares[move['from'][1]][move['from'][0]]
        squares[move['from'][1]][move['from'][0]] = Constant.EMPTY

        # check if pawn can be promoted
        if move['flag'] == Constant.PROMOTE_PAWN:
            squares[move['from'][1]][move['from'][0]] = Constant.EMPTY
            squares[_to[1]][_to[0]] = (self.turn(), self.DEFAULT_P)
        
        # queen side castling
        elif move['flag'] == Constant.QUEEN_CASTLE:
            from_ = (0,7) if index == 0 else (0,0)
            to_   = (3, 7) if index == 0 else (3, 0)

            squares[to_[1]][to_[0]] = squares[from_[1]][from_[0]]
            squares[from_[1]][from_[0]] = Constant.EMPTY

        # king side castling
        elif move['flag'] == Constant.KING_CASTLE:
            from_ = (7,7) if index == 0 else (7,0)
            to_   = (5, 7) if index == 0 else (5, 0)

            squares[to_[1]][to_[0]] = squares[from_[1]][from_[0]]
            squares[from_[1]][from_[0]] = Constant.EMPTY

        self.lastMoves = None
        self.__addPiecePosition()
        self.pattern.setturn(self.getOppositeColor())
        self.pattern.STORE.H_FORWARD.append([move, castle, capture, ePassant])

        # no more undo
        if remove:
            self.pattern.STORE.H_BACKWARD.clear()

        # check game status
        if self.isGameOver():
            return False

        return True

    # get all moves of current player or get of a specific square
    def getmoves(self, _square: tuple = Constant.EMPTY):
        currentColor = self.turn()
        temp = self.pattern.STORE.SQUARE
        self.lastMoves = []

        # get all moves 
        if _square[0] == None:
            for row in range(8):
                for col in range(8):
                    if temp[row][col][0] == currentColor:     
                        self.lastMoves += self.__getmoves(temp[row][col][1], currentColor, (col, row))
        else: 
            # check chess board boundry
            if _square[0] < 0 or _square[1] or _square[0] > 7 or _square[1] > 7:
                return self.lastMoves
            
            piece = temp[_square[1]][_square[0]]
            if piece[0] == None: # piece must be there
                return self.lastMoves
            
            self.lastMoves = self.__getmoves(piece[1], piece[0], _square)

        return self.lastMoves

    def __getmoves(self, piece: str, color: str, _square: tuple):
        moves = self.pattern.evaluatePattern(piece, color, _square)
        
        if piece == Constant.KING:
            return self.__kingmoves(moves, _square)

        # if two piece doing check the check
        if len(self.__inCheck()) > 1:
            moves.clear()
            return moves

        # will the king be safe, if we remove current piece
        self.pattern.STORE.SQUARE[_square[1]][_square[0]] = Constant.EMPTY
        if len(self.__inCheck()) > 1:
            moves.clear()
            return moves

        self.pattern.STORE.SQUARE[_square[1]][_square[0]] = (color, piece)
        
        # if king is in check, check if we can capture that piece or not
        if len(self.__inCheck()) == 1:
            return self.canPieceMove(_square, moves)
        
        return moves
    
    # check if a piece can moves if king is in check
    def canPieceMove(self, _square: tuple, moves: tuple):
        unsafe = self.__inCheck()[0]
        piece = self.pattern.getPiece(unsafe)

        targetMove = None
        for move in moves:
            if move['capture'] and move['to'][0] == unsafe[0] and move['to'][0] == unsafe[0]:
                targetMove = move
                break

        # if checker is knight or pawn
        # we can block the way of these piece, we can just capture them
        if piece[1] == Constant.KNIGHT or piece[1] == Constant.PAWN:
            moves.clear()
            if targetMove != None:
                moves.append(targetMove)
            
            return moves


        newMove = []
        if targetMove != None:
            newMove.append(targetMove)

        newMove += self.pattern.get_square_between(moves, unsafe, _square)
        return newMove
    
    # get kings moves
    def __kingmoves(self, moves: list, _square: tuple):
        castle = self.pattern.STORE.CASTLE
        index = 0 if self.turn() == Constant.WHITE else 1
        
        # check if king can castle
        if castle[index] == -1:
            return moves
        
        # king should not be in check
        if len(self.__inCheck()) > 0:
            return moves
        
        if castle[index] == 1 or castle[index] == 3:
            box = ((6, 7), (5, 7)) if self.turn() == Constant.WHITE else ((6, 0), (5, 0))
            if self.__isValid(box):
                moves.append({ 
                    "piece": Constant.KING, 
                    "capture": False, 
                    "flag": Constant.KING_CASTLE, 
                    "from": _square, 
                    "to": box[0]
                })
        if castle[index] == 1 or castle[index] == 3:
            box = ((1, 7), (2, 7), (3, 7)) if self.turn() == Constant.WHITE else ((1, 0), (2, 0), (3, 0))
            if self.__isValid(box):
                moves.append({ 
                    "piece": Constant.KING, 
                    "capture": False, 
                    "flag": Constant.KING_CASTLE, 
                    "from": _square, 
                    "to": box[1]
                })

        return moves

    # check if castle is valid
    def __isValid(self, squares: tuple):
        # each square must be empty and must not in check
        for sqr in squares:
            if self.pattern.getPiece(sqr)[0] != None or len(self.pattern.getUnsafePositions(self.turn(), sqr)) > 0:
                return False
        
        return True

    # undo move
    def undo(self):
        if len(self.pattern.STORE.H_FORWARD) == 0:
            return
        
        # # get last inserted history
        # last = self.pattern.STORE.H_FORWARD.pop()
        # self.pattern.STORE.H_BACKWARD.append(last)

        # isWhiteTurn = self.turn() == Constant.WHITE
        
        pass

    # redo move
    def redo(self):
        pass

    # get history
    def history():
        pass

    # detect three fold repetition (Draw)
    def isThreeFoldRepetition(self):
        return self.TH_RP

    def isInsufficiantMaterial(self):
        if self.IS_MA:
            return False
        
        sqr = self.pattern.STORE.SQUARE
        whiteNight = -1
        blackNight = -1
        count = 0

        for row in range(8):
            for col in range(8):
                piece = sqr[col][row]
                if piece[0] == None:
                    continue

                if piece[0] == Constant.BLACK:
                    if piece[1] == Constant.KNIGHT:
                        blackNight = (row, col)
                    count += ord(piece[1].lower())
                
                else:
                    if piece[1] == Constant.KNIGHT:
                        whiteNight = (row, col)
                    count += ord(piece[1])

        if count == 66 or count == 78 or count == 156 or count == 98 or count == 110 or count == 220:
            return True

        if count == 156 and whiteNight != -1 and blackNight != -1 and whiteNight % 8 != blackNight % 8:
            return True

        return False

    # when king is npt in check, but also have no valid move
    def isStalemate(self):
        self.H_MOVE = self.__hasMoves()
        return not self.H_MOVE and not self.inCheck()

    # detect checkmate
    def isCheckmate(self):
        if not self.H_MOVE and self.inCheck():
            self.pattern.setStatus(Constant.CHECKMATE)
            return True
        
        return False

    # check if current player can move
    def __hasMoves(self):
        x = self.pattern.STORE.KINGS[0 if self.turn() == Constant.WHITE else 1]
        moves = self.__getmoves(Constant.KING, self.turn(), x)
        self.inCheck()

        # check if king can make move
        if len(moves) > 0:
            return True

        for row in range(8):
            for col in range(8):
                piece = self.pattern.getPiece((row, col))
                if not self.IS_MA and (piece == Constant.QUEEN or piece == Constant.PAWN or piece == Constant.ROOK):
                    self.IS_MA = True
                if piece[0] == self.turn() and len(self.__getmoves(piece[1], piece[0], (row,col))) > 0:
                    return True

        return False

    # check if current player's king is safe or not
    def __inCheck(self):
        x = self.pattern.STORE.KINGS[0 if self.turn() == Constant.WHITE else 1]
        return self.pattern.getUnsafePositions(self.turn(), x)
        
    # detect if king is in check
    def inCheck(self):
        return len(self.__inCheck()) > 0
    
    # detect if game is draw
    def isDraw(self):
        if self.pattern.getStatus() != "":
            return False
        
        status = ""
        if self.pattern.STORE.MOVE_COUNT[1] >= 100:
            status = Constant.FIFTY_MOVE
        
        elif self.isStalemate():
            status = Constant.STALEMENT
        
        elif self.isInsufficiantMaterial():
            status = Constant.IS_MATERIAL
        
        elif self.isThreeFoldRepetition():
            status = Constant.TH_REPETITTION

        self.pattern.setStatus(status)
        return status != ""

    # check if game is over
    def isGameOver(self):
        if self.isDraw() or self.isCheckmate():
            return True
        
        return False
    
    # add current position and also check three fold repetition
    def __addPiecePosition(self):
        fen = self.pattern.currentPosition()
        store = self.pattern.STORE.FEN
        count = 0

        if fen in store:
            count = store[fen]
            if count >= 3:
                self.TH_RP = True
        else:
            store[fen] = count + 1

    # get the piece color at spciefied square
    def colorAt(self, square: tuple):
        return self.pattern.getPiece(square[0], square[1])[0]

    # get the piece name at spciefied square
    def pieceAt(self, square: tuple):
        return self.pattern.getPiece(square[0], square[1])[1]

    # get square name from indexs, ex. (0,0) -> A1
    def getSquareFromIndex(self, square: tuple):
        return f"{chr(65+square[0])}{8-square[1]}"
    
    # get square name from indexs, ex.  A1 -> (0,0)
    def getSquareFromString(self, square: str):
        if len(square) < 2:
            return None
        
        x = 65 if ord(square[0]) < 97 else 97
        return (ord(square[0]) - x, (8-int(square[1])))
