# Constant for the Chess

class Constant:

    # Represent White Piece
    WHITE = 'W'

    # Represent Black Piece
    BLACK = 'B'

    # Represent King
    KING = 'K'

    # Represent Queen
    QUEEN = 'Q'

    # Represent Bishop
    BISHOP = 'B'

    # Represent Knight
    KNIGHT = 'N'

    # Represent Rook
    ROOK = 'R'

    # Represent Pawn
    PAWN = 'P'

    # Represent King Side Castle
    KING_CASTLE = 'K'

    # Represent Queen Side Castle
    QUEEN_CASTLE = 'Q'

    # Represent Pawn Promiting
    PROMOTE_PAWN = 'P'

    # Represent Big pawn move
    BIG_PAWN = 'B'

    # Represent Epassant Capture
    E_PASSANT = 'E'

    # Whene nothing to be return
    NO_FLAG = None

    # Row number for pawn big move
    BIG_PAWN_ROW = (5, 2)

    # Row number for pawn promoting
    PROMOTE_ROW = (0, 7)

    # Default Position of pieces
    DEFAULT_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 0"

    ## ---- GAME ENDED TYPES ----

    # Checkmate
    CHECKMATE = 'C'

    # Stalement
    STALEMENT = 'S'

    # Inssufficiant Material
    IS_MATERIAL = 'I'

    # Three Fold Repetition
    TH_REPETITTION = 'T'

    # Fifty move
    FIFTY_MOVE = 'F'

    # just for use only
    EMPTY = (None, None)
    
    def __setattr__(self, _, __) -> None:
        print("You are not allowed to change constant value.")