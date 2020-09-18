from random import randint

from models.tile import TileModel
from models.board import BoardModel
from .analysis import n_tet_counts
from .constants import Direction
from models.tile_generators import direction_neighbors


class RandomRater:
    def rate(self, board):
        return randint(1, 100)


class SimpleRater:
    def rate(self, board):
        COUPLE_COST = 5
        TRIPLET_COST = 20
        QUARTET_COST = 50
        WIN_COST = 99999

        couple_counts = n_tet_counts(board, 2)
        triplet_counts = n_tet_counts(board, 3)
        quartet_counts = n_tet_counts(board, 4)
        win_counts = n_tet_counts(board, 5)

        rating = (couple_counts[0] - couple_counts[1]) * COUPLE_COST + \
                 (triplet_counts[0] - triplet_counts[1]) * TRIPLET_COST + \
                 (quartet_counts[0] - quartet_counts[1]) * QUARTET_COST + \
                 (win_counts[0] - win_counts[1]) * WIN_COST

        return rating


class SymbolGroup:
    def __init__(self, symbol, blocked):
        self._parent = None  # DFU-like, for merging the groups
        self._size = 0
        self._symbol = None  # ?
        self._blocked = 0  # 0-2, from how many sides it is protected

    def _root(self):
        if self._parent is None:
            return self
        else:
            return self._parent._root()

    def get_symbol(self):
        root = self._root()
        return root._symbol

    def get_size(self):
        root = self._root()
        return root._size

    def increment_size(self):
        root = self._root()
        root._size += 1

    def get_blocked(self):
        root = self._root()
        return root._blocked

    def increment_blocked(self):
        root = self._root()
        root._blocked += 1

    def merge(self, other):
        # DFU-like union
        my_root = self._root()
        other_root = other._root()

        other_root._parent = my_root
        my_root._size += other_root._size
        my_root._blocked += other_root._blocked

        assert my_root._symbol == other_root._symbol
        assert my_root._blocked <= 2

    def score(self):
        size = self.get_size()
        blocked = self.get_blocked()

        score = 0

        if blocked == 2:
            score = 0  # It is useless in this direction

        elif size == 1:
            if blocked == 1:
                score = 1
            else:
                score = 2

        elif size == 2:
            if blocked == 1:
                score = 3
            else:
                score = 5

        elif size == 3:
            if blocked == 1:
                score = 7
            else:
                score = 15

        elif size == 4:
            if blocked == 1:
                score = 20
            else:
                score = 5000

        else:
            score = 99999

        if self.get_symbol() == TileModel.Symbols.CIRCLE:
            score = -score

        return score


class PositionContext:
    """
    Remember what symbol groups are in all directions
    on a given position
    """
    def __init__(self):
        # Group in each direction
        self.directions = {
            direction: None for direction in Direction.all()
        }


class RatedBoard(BoardModel):
    def __init__(self, size):
        super().__init__(size)
        self.board_context = [[PositionContext for _ in range(size)]
                              for _ in range(size)]
        self.rating = 0

    def reset(self):
        super().reset()
        self.board_context = [[PositionContext for _ in range(self.size)]
                              for _ in range(self.size)]
        self.rating = 0

    def place(self, x, y, symbol):
        super().place(x, y, symbol)

        position_context = self.board_context[x][y]

        for direction in Direction.all():
            dir_neighbors = direction_neighbors(self, direction, x, y)
            nei_contexts = [self.board_context[x][y]
                            for (x, y) in dir_neighbors]

            nei_groups = (context.directions[direction]
                          for context in nei_contexts)

            same_symbol_groups = []
            other_symbol_groups = []

            for group in nei_groups:
                if group is None:
                    continue

                # Unrate all groups, will be rated again after
                # they are (possibly) changed
                self.rating -= group.score()

                if group.get_symbol() == symbol:
                    same_symbol_groups.append(group)
                else:
                    other_symbol_groups.append(group)

            blocked_count = len(other_symbol_groups)

            my_group = None  # The group that lies up on (x, y)

            if not same_symbol_groups:
                # Must create own group
                new_group = SymbolGroup(symbol, blocked_count)
                my_group = new_group

            else:
                # Extend existing group
                old_group = same_symbol_groups[0]
                old_group.increment_size()

                if blocked_count:
                    old_group.increment_blocked()

                my_group = old_group

                if len(same_symbol_groups) == 2:
                    # These two groups need to be merged
                    second_group = same_symbol_groups[1]
                    old_group.merge(second_group)

            for group in other_symbol_groups:
                # This new symbol is now blocking opponent groups
                group.increment_blocked()

            # Update (x, y) position context
            position_context.directions[direction] = my_group

            # There is definitely only one group of the same symbol --
            # my_group, and exactly those groups of the other symbol as in the
            # beginning (only possibly changed). Use these for rating.

            self.rating += my_group.score()
            for group in other_symbol_groups:
                self.rating += group.score()



    def undo(self):
        super().undo()
