from enum import Enum, auto


class Direction(Enum):
    HORIZONTAL = auto()
    VERTICAL = auto()
    DIAGONAL_A = auto()
    DIAGONAL_B = auto()

    @classmethod
    def all(cls):
        return [
            cls.HORIZONTAL,
            cls.VERTICAL,
            cls.DIAGONAL_A,
            cls.DIAGONAL_B
        ]

class Symbols(Enum):
    EMPTY = auto()
    CROSS = auto()
    CIRCLE = auto()
