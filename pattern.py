# Chess Path Pattern Resolver
from constants import Constant
from util import Util

class Pattern(Util):
    # pattern for king
    king = (
        (-1, 0), (1, 0), (0, -1), (0, 1),
        (-1, 1), (1, -1), (1, 1), (-1, -1)
    )

    # pattern for queen
    queen = king

    # pattern for rook
    rook = (
        (-1, 0), (1, 0), (0, -1), (0, 1)
    )

    # pattern for bishop
    bishop = (
        (-1, 1), (1, -1), (1, 1), (-1, -1)
    ) 

    # pattern for knight
    knight = (
        (-1, 2), (1, -2), (-1, -2), (1, 2),
        (-2, 1), (-2, -1), (2, 1), (2, -1)
    )

    # pattern for black pawn
    blackPawn = ((0, 1), (-1, 1), (1, 1))

    # pattern for white pawn
    whitePawn = ((0, -1), (-1, -1), (1, -1))

    # Maximum box move by a piece
    moves = (
        (Constant.KING, 1, king), 
        (Constant.QUEEN, 7, queen), 
        (Constant.BISHOP, 7, bishop),
        (Constant.PAWN, 1, whitePawn, blackPawn), 
        (Constant.KNIGHT, 1, knight), 
        (Constant.ROOK, 7, rook)
    ) 

    # get direction between two square in chess board
    # if there are not in cross, horiozontal or in vertical, return null
    # usage: (0, 0), (7, 7): return "cross"
    def __getDirection(self, pos1, pos2):
        if pos1[0] == pos2[0] or pos1[1] == pos2[1]:
            return "plus"
        elif abs(pos1[0] - pos2[0]) == abs(pos1[1] - pos2[1]):
            return "cross"
        else:
            return "null"

    # get maximum path can a piece move
    # usage: K : return (tuple)
    def __getPieceInfo(self, piece: str):
        for i in self.moves:
            if i[0] == piece: 
                return i
            
        return Constant.NO_FLAG
    
    # evaluate patterns
    # usage: K, B, (0, 3): return []
    def evaluatePattern(self, piece: str, color: str, square: tuple):
        info = self.__getPieceInfo(piece)
        if (info == Constant.NO_FLAG):
            return []
        
        moves = []
        for move in self.helperFn(color, info):
            x = square[0]
            y = square[1]

            for _ in range(info[1]):
                x += move[0] # new x position
                y += move[1] # new y position

                # if it is out of boundry
                if (x < 0 or y < 0 or y > 7 or x > 7):
                    break
                    
                # get piece stored at that place 
                temp = self.getPiece((x, y))

                # if in current box, has a same colored piece
                # if the piece is king
                if temp[0] == color or (piece == Constant.KING and len(self.getUnsafePositions(color, (x, y))) > 0):
                    break
                
                # Current move object
                currentMove = { "piece": piece, "capture": False, "flag": Constant.NO_FLAG, "from": square, "to": (x,y) }

                # if piece is pawn
                if piece == Constant.PAWN:
                    # check pawn is going to be promoted
                    index = 0 if color == Constant.WHITE else 1
                    isPromoted = y == Constant.PROMOTE_ROW[index]
                    
                    # check if we can capture with pawn
                    if move[0] != 0 and temp[0] != None and (color != temp[0] or self.STORE.E_PASSANT == x):
                        currentMove["capture"] = True
                        currentMove["flag"] = Constant.E_PASSANT if self.STORE.E_PASSANT == x else Constant.PROMOTE_PAWN if isPromoted else Constant.NO_FLAG
                    
                    # straight move, we can not capture, but can move
                    elif move[0] == 0 and temp[0] == None:
                        if y == Constant.BIG_PAWN_ROW[index] and self.getPiece((x, (y + (1 if index == 0 else -1))))[0] == None:
                            moves.append({ "piece": piece, "capture": False, "flag": Constant.BIG_PAWN, "from": square, "to": (x,(y + (1 if index == 0 else -1))) })

                    else: currentMove["piece"] = Constant.NO_FLAG

                # if there is piece at target box and has not same color    
                elif temp[0] != None and temp[0] != color:
                    currentMove["capture"] = True
                
                # append move object
                if currentMove["piece"] != Constant.NO_FLAG:
                    moves.append(currentMove)
        
        return moves

    def helperFn(self, color: str, moves: tuple):
        if moves[0] == Constant.PAWN:
            return moves[2] if color == Constant.WHITE else moves[3]
        return moves[2]
                 
    # get square position, who can capture current position
    def getUnsafePositions(self, color: str, square: tuple):
        unsafe = self.getUnsafePlace(color, square)
        if unsafe != None:
            return unsafe
        
        # current position of king
        current = self.getKingSquare(color)
        self.setKingSquare(color, Constant.EMPTY)
        result = []

        piece = (Constant.QUEEN, Constant.PAWN, Constant.KNIGHT)
        for nm in range(3):

            # get all valid moves
            moves = self.evaluatePattern(piece[nm], color, square)
            for move in moves:
                if not move['capture']:
                    continue
                
                # get captured piece name
                capture = self.getPiece(move['to'])[1]
                if piece[nm] != Constant.QUEEN:
                    
                    # target piece and current piece must be same
                    if (capture == piece[nm]):
                        result.append(move['to'])
                        continue

                direction = self.__getDirection(square, move['to'])
                distance = abs(square[0]-move['to'][0]) if abs(square[0]-move['to'][0]) > 0 else abs(square[1]-move['to'][1])
                
                # king can capture from distance 1 only
                if (piece[nm] == Constant.QUEEN or 
                    (piece[nm] == Constant.KING and distance == 1) or 
                    (piece[nm] == Constant.ROOK and direction == 'plus') or
                    piece[nm] == Constant.BISHOP and direction == 'cross'
                ): result.append(move['to'])

        self.setKingSquare(color, current) # add again king to the board
        self.addUnsafePlace(color, square, result) # store result

        return result

    # get square between two square
    def get_square_between(self, moves: tuple, start: tuple, end: tuple):
        x, y, index = end[0] - start[0],  end[1] - start[1], 0

        x = 0 if x == 0 else 1 if x > 0 else -1
        y = 0 if y == 0 else 1 if y > 0 else -1

        _x, _y, index = start[0], start[1], 0
        sqr = []

        while index < 8 or not (_x == end[0] and _y == end[1]):
            _x, _y = _x + x, _y + y

            # check for boundry
            if _y < 0 or _x < 0 or _x > 7 or _y > 7:
                break

            for m in moves:
                if m['to'][0] == _x and m['to'][1] == _y:
                    sqr.append(m)

            index += 1

        return sqr