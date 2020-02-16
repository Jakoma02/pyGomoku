from enum import Enum, auto

from models.observable import Observable


class TileModel:
    __slots__ = ("symbol", "state", "x", "y")

    class Symbols(Enum):
        EMPTY = auto()
        CROSS = auto()
        CIRCLE = auto()

    class States(Enum):
        NONE = auto()
        PRELIT = auto()
        DISABLED = auto()
        MARKED_AS_WIN = auto()

    def __init__(self, x, y):
        self.symbol = Observable(parent=self, default=TileModel.Symbols.EMPTY)
        self.state = Observable(parent=self, default=TileModel.States.NONE)
        self.x = x
        self.y = y
        super().__init__()

    def reset(self):
        self.symbol.set(self.Symbols.EMPTY)
        self.state.set(self.States.NONE)

    def empty(self):
        return self.symbol.get() == self.Symbols.EMPTY

    def clone(self):
        new_tile = TileModel(self.x, self.y)
        new_tile.symbol.set(self.symbol.get())
        new_tile.state.set(self.state.get())
        return new_tile
