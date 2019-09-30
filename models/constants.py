from enum import Enum, auto


class Direction(Enum):
    HORIZONTAL = auto()
    VERTICAL = auto()
    DIAGONAL_A = auto()
    DIAGONAL_B = auto()

class Symbols(Enum):
    EMPTY = auto()
    CROSS = auto()
    CIRCLE = auto()
