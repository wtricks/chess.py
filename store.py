# Chess game data store
from constants import Constant

class Store:
    # E_PASSANT Capture
    E_PASSANT = -1

    # board squares
    SQUARE: list = []

    # positions of kings
    KINGS: list = [None, None] 

    # current status of game
    STATUS: str = ""

    # current turn
    TURN: str = Constant.WHITE

    # count move of both side
    MOVE_COUNT: list = [0, 0]

    # castle
    CASTLE: list = [0, 0]

    # Epassant move
    E_PASSANT: int = -1

    # Store FEN string
    FEN: dict = {}

    # Store History
    H_FORWARD: list = []
    H_BACKWARD: list = []

    # Store Unsafe Squares
    UNSAFE: tuple = ['N', {}]
