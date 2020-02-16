from models.tile import TileModel
from .tile_generators import all_generators
from .constants import Direction


class BoardModel:
    WINNING_COUNT = 5
    __slots__ = ("size", "_board")

    def __init__(self, size):
        self.size = size
        self._board = [[TileModel(x, y) for y in range(self.size)]
                       for x in range(self.size)]

    def __getitem__(self, x):
        return self._board[x]

    def reset(self):
        for row in self._board:
            for tile in row:
                tile.reset()
        return self

    def place(self, x, y, symbol):
        tile = self._board[x][y]
        if not tile.empty():
            return False
        tile.symbol.set(symbol)
        return self

    def clear_tile(self, x, y):
        tile = self._board[x][y]
        tile.symbol.set(TileModel.Symbols.EMPTY)

    def next_tile(self, r, c, direction):
        class TileException(Exception):
            pass

        """
        Returns next tile coordinates in given direction
        :param r: Current tile row
        :param c: Current tile column
        :param direction: Direction
        :return: Next tile coordinates
        """
        if direction == Direction.HORIZONTAL:
            if c >= self.size - 1:
                raise TileException(f"There are no more tiles in this direction")
            return r, c + 1
        elif direction == Direction.VERTICAL:
            if r >= self.size - 1:
                raise TileException(f"There are no more tiles in this direction")
            return r + 1, c
        elif direction == Direction.DIAGONAL_A:
            if r >= self.size - 1 or c <= 0:
                raise TileException(f"There are no more tiles in this direction")
            return r + 1, c - 1
        elif direction == Direction.DIAGONAL_B:
            if r >= self.size - 1 or c >= self.size - 1:
                raise TileException(f"There are no more tiles in this direction")
            return r + 1, c + 1

    def check_win(self):
        """
        Check if one of the players won
        :return: False or winning position start and direction
        """
        for line, direction in all_generators(self):
            count = 0
            first_group_tile = None
            last_symbol = TileModel.Symbols.EMPTY
            for tile in line:
                symbol = tile.symbol.get()
                if symbol == last_symbol:
                    count += 1
                else:
                    count = 1
                    last_symbol = symbol
                    first_group_tile = tile
                if count >= BoardModel.WINNING_COUNT and \
                        last_symbol != TileModel.Symbols.EMPTY:
                    return first_group_tile, direction, last_symbol
        return False

    def disable(self):
        for row in self._board:
            for tile in row:
                tile.state.set(TileModel.States.DISABLED)
        return self

    def mark_win(self, win_info):
        tile, direction, symbol = win_info
        x, y = tile.x, tile.y
        self._board[x][y].state.set(TileModel.States.MARKED_AS_WIN)
        for _ in range(self.WINNING_COUNT - 1):
            x, y = self.next_tile(x, y, direction)
            self._board[x][y].state.set(TileModel.States.MARKED_AS_WIN)
        return self
    
    def clone(self):
        cloned_board = BoardModel(self.size)
        cloned_board._board = [[tile.clone() for tile in row] for row in self._board]
        return cloned_board
