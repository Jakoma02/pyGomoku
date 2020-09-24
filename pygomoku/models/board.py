"""
This module contains boards
"""

from collections import namedtuple
from copy import deepcopy

from .tile import TileModel
from .tile_generators import all_generators, all_tiles, direction_neighbors, \
                             next_in_direction

from .constants import Direction

# (x1, y1), (x2, y2) are being merged, (x3, y3) is the position that merged
# them
UndoMerge = namedtuple("UndoMerge", ["x1", "y1", "x2", "y2", "x3", "y3",
                                     "direction", "local_state1",
                                     "local_state2"])
UndoCreate = namedtuple("UndoCreate", ["x", "y", "direction"])
UndoChange = namedtuple("UndoChange", ["x", "y", "direction", "state"])
UndoExtend = namedtuple("UndoExtend", ["x", "y", "direction", "state"])


class BoardModel:
    """
    Standard board model, containing TileModels.
    Supports undoing moves.
    """
    WINNING_COUNT = 5
    __slots__ = ("size", "_board", "_added_tiles_stack")

    def __init__(self, size):
        self.size = size
        self._board = [[TileModel(x, y) for y in range(self.size)]
                       for x in range(self.size)]
        self._added_tiles_stack = []  # So that we can undo

    def __getitem__(self, x):
        return self._board[x]

    def reset(self):
        """
        Clear all symbols on board
        """
        for row in self._board:
            for tile in row:
                tile.reset()
        return self

    def place(self, x, y, symbol):
        """
        Places `symbol` at (x, y)
        """
        tile = self._board[x][y]
        if not tile.empty():
            return False
        tile.symbol.set(symbol)

        self._added_tiles_stack.append((x, y))
        return self

    def undo(self):
        """
        "Unplaces" last tile placement
        """
        x, y = self._added_tiles_stack.pop()

        tile = self._board[x][y]
        tile.symbol.set(TileModel.Symbols.EMPTY)

    def check_win(self):
        """
        Check if one of the players won

        Returns False or winning position start and direction
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
        """
        Make the board disabled/gray
        """
        for tile in all_tiles(self):
            tile.state.set(TileModel.States.DISABLED)
        return self

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
                raise TileException(
                    "There are no more tiles in this direction")
            return r, c + 1

        if direction == Direction.VERTICAL:
            if r >= self.size - 1:
                raise TileException(
                    "There are no more tiles in this direction")
            return r + 1, c

        if direction == Direction.DIAGONAL_A:
            if r >= self.size - 1 or c <= 0:
                raise TileException(
                    "There are no more tiles in this direction")
            return r + 1, c - 1

        if direction == Direction.DIAGONAL_B:
            if r >= self.size - 1 or c >= self.size - 1:
                raise TileException(
                    "There are no more tiles in this direction")
            return r + 1, c + 1

    def enable(self):
        """
        Make the board enabled/white
        """
        for tile in all_tiles(self):
            tile.state.set(TileModel.States.NONE)
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
        """
        Return a copy of the board
        """
        # This could be subclassed
        cls = self.__class__
        cloned_board = cls(self.size)

        cloned_board._board = [[tile.clone() for tile in row]
                               for row in self._board]
        return cloned_board


class SymbolGroup:
    """
    A group of symbols in ONE DIRECTION
    """
    def __init__(self, symbol, blocked, x, y, direction):
        self._parent = None  # DFU-like, for merging the groups
        self._size = 1
        self._symbol = symbol  # ?
        self._blocked = blocked  # 0-2, from how many sides it is protected
        self.x = x
        self.y = y
        self.direction = direction

    def root(self):
        """
        Merging groups uses DFU-like structure, this finds its root
        """
        if self._parent is None:
            return self
        else:
            return self._parent.root()

    def get_state(self):
        """
        Return the group state
        """
        if self._parent is not None:
            return self.root().get_state()

        return (
            self._size,
            self._symbol,
            self._blocked
        )

    def set_state(self, state):
        """
        Set the group state
        """
        if self._parent is not None:
            self.root().set_state(state)
            return

        size, symbol, blocked = state
        self._size = size
        self._symbol = symbol
        self._blocked = blocked

    def get_local_state(self):
        """
        Return the state of this group instance, without
        looking up the root

        This is useful for unmerge (don't lookup parent)
        """

        return (
            self._parent,
            self._size,
            self._symbol,
            self._blocked
        )

    def force_local_state(self, local_state):
        """
        Set the state of this group instance, without
        looking up the root
        This is useful for unmerge (force parent)
        """

        parent, size, symbol, blocked = local_state

        self._parent = parent
        self._size = size
        self._symbol = symbol
        self._blocked = blocked

    def get_symbol(self):
        """
        Return the group symbol
        """
        root = self.root()
        return root._symbol

    def get_size(self):
        """
        Return the group size
        """
        root = self.root()
        return root._size

    def increment_size(self):
        """
        Increment the group size
        """
        root = self.root()
        root._size += 1

    def get_blocked(self):
        """
        Return the number of blocked sides
        """
        root = self.root()
        return root._blocked

    def increment_blocked(self):
        """
        Increase the number of blocked sides
        """
        root = self.root()
        root._blocked += 1

    def merge(self, other):
        """
        Merge two groups.

        This works like DFU union
        """
        my_root = self.root()
        other_root = other.root()

        assert my_root != other_root

        other_root._parent = my_root
        my_root._size += other_root._size
        my_root._blocked += other_root._blocked

        assert my_root._symbol == other_root._symbol
        assert my_root._blocked <= 2

    def score(self):
        """
        Return group score
        """
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
    """
    A better version of BoardModel that keeps track of its groups
    and its rating (all the time)
    """
    __slots__ = BoardModel.__slots__ + \
        ("board_context", "_context_undo_stack", "rating", "groups")

    def __init__(self, size):
        super().__init__(size)
        self._reset_context()

        self.groups = []

    def reset(self):
        super().reset()
        self._reset_context()
        return self

    def _reset_context(self):
        self.board_context = [[PositionContext() for _ in range(self.size)]
                              for _ in range(self.size)]
        self._context_undo_stack = []
        self.rating = 0
        self.groups = []

    def place(self, x, y, symbol):
        placing_success = super().place(x, y, symbol)

        if not placing_success:
            return False

        position_context = self.board_context[x][y]
        undo_instructions = []

        for direction in Direction.all():
            dir_neighbors = direction_neighbors(self, direction, x, y)
            nei_contexts = [self.board_context[nx][ny]
                            for (nx, ny) in dir_neighbors]

            nei_groups = (context.directions[direction]
                          for context in nei_contexts)

            same_symbol_groups = []  # Tuples (coords, group)
            other_symbol_groups = []

            # Coords are needed for undo instructions
            for coords, group in zip(dir_neighbors, nei_groups):
                if group is None:
                    continue

                # Unrate all groups, will be rated again after
                # they are (possibly) changed
                self.rating -= group.score()

                if group.get_symbol() == symbol:
                    same_symbol_groups.append((coords, group))
                else:
                    other_symbol_groups.append((coords, group))

            assert len(same_symbol_groups) + len(other_symbol_groups) <= 2

            for coords, group in same_symbol_groups:
                # Otherwise it can't have a neighbor of the same color
                assert group.get_blocked() <= 1

            blocked_count = len(other_symbol_groups)

            my_group = None  # The group that lies up on (x, y)

            if not same_symbol_groups:
                # Must create own group
                new_group = SymbolGroup(symbol, blocked_count, x, y, direction)
                self.groups.append(new_group)

                my_group = new_group

                instruction = UndoCreate(x, y, direction)
                undo_instructions.append(instruction)

            else:
                # Extend existing group

                old_group = same_symbol_groups[0][1]  # group

                if len(same_symbol_groups) == 2:
                    # These two groups need to be merged
                    second_group = same_symbol_groups[1][1]

                    # Create unmerge instruction
                    local_state1 = old_group.get_local_state()
                    local_state2 = second_group.get_local_state()

                    x1, y1 = same_symbol_groups[0][0]
                    x2, y2 = same_symbol_groups[1][0]
                    instruction = UndoMerge(x1, y1, x2, y2, x, y, direction,
                                            local_state1, local_state2)
                    undo_instructions.append(instruction)

                    second_group.merge(old_group)

                else:
                    # Create undo EXTEND instruction
                    group_state = old_group.get_state()
                    instruction = UndoExtend(x, y, direction, group_state)
                    undo_instructions.append(instruction)

                old_group.increment_size()

                if blocked_count:
                    old_group.increment_blocked()

                my_group = old_group

            for coords, group in other_symbol_groups:
                # Create undo instructions
                changed_x, changed_y = coords
                state = group.get_state()

                t_size, t_symbol, t_blocked = state
                assert symbol != t_symbol

                instruction = UndoChange(changed_x, changed_y,
                                         direction, state)
                undo_instructions.append(instruction)
                # This new symbol is now blocking opponent groups
                group.increment_blocked()

            # Update (x, y) position context
            position_context.directions[direction] = my_group

            # There is definitely only one group of the same symbol --
            # my_group, and exactly those groups of the other symbol as in the
            # beginning (only possibly changed). Use these for rating.

            self.rating += my_group.score()
            for coords, group in other_symbol_groups:
                self.rating += group.score()

        undo_instructions.reverse()

        self._context_undo_stack.append(undo_instructions)

        # self._check_invariants()
        return self

    def _check_invariants(self):
        """
        Check that the board state is consistent.

        This takes quite a lot of time, only use when debugging.
        """
        print("Checking")
        for i in range(self.size):
            for j in range(self.size):
                tile = self[i][j]

                groups = self.board_context[i][j].directions

                for direction, group in groups.items():
                    if tile.empty():
                        assert group is None, \
                            f"Group ({i}, {j}) should be None " \
                            f"in direction {direction}"
                        continue

                    assert group is not None, \
                        f"Group ({i}, {j}) should not be " \
                        f"None in direction {direction}"
                    assert group._parent != group

                    in_chain = set([group])
                    last = group

                    while last._parent is not None:
                        last = last._parent

                        assert last not in in_chain
                        in_chain.add(last)

        for move_undo_instructions in self._context_undo_stack:
            for instruction in move_undo_instructions:
                if isinstance(instruction, UndoChange):
                    x, y, direction, state = instruction
                    group = self.board_context[x][y].directions[direction]
                    symbol = self[x][y].symbol.get()

                    assert group is not None, \
                        f"({x}, {y}) group should not " \
                        f"be None in direction {direction}"
                    assert symbol is not TileModel.Symbols.EMPTY, \
                        f"({x}, {y}) symbol in direction {direction}" \
                        f"should not be empty"

    def _undo_extend(self, instruction):
        self._undo_change(instruction)

        # Remove the block from the position
        x, y, direction, _ = instruction

        self.board_context[x][y].directions[direction] = None
        # self._check_invariants()

    def _undo_change(self, instruction):
        # print("Undoing change")
        x, y, direction, state = instruction

        group = self.board_context[x][y].directions[direction]

        # Unrate group
        self.rating -= group.score()

        group.set_state(state)

        # Rerate
        self.rating += group.score()

        # It shouldn't be possible that blocked >= 2
        assert group.get_blocked() < 2

        # self._check_invariants()

    def _undo_merge(self, instruction):
        # print("Undoing merge")
        x1, y1, x2, y2, x3, y3, direction, \
            local_state1, local_state2 = instruction

        group1 = self.board_context[x1][y1].directions[direction]
        group2 = self.board_context[x2][y2].directions[direction]
        self.rating -= group1.score()

        # Force both local states
        group1.force_local_state(local_state1)
        group2.force_local_state(local_state2)

        # Remove the added tile (this bug took a looot of time to find :)
        self.board_context[x3][y3].directions[direction] = None

        # Rerate both groups
        self.rating += group1.score()
        self.rating += group2.score()

        # It shouldn't be possible that both groups are fully blocked
        assert group1.get_blocked() < 2
        assert group2.get_blocked() < 2

        # self._check_invariants()

    def _undo_create(self, instruction):
        x, y, direction = instruction

        group = self.board_context[x][y].directions[direction]
        self.groups.remove(group)

        # Unrate group
        self.rating -= group.score()

        # Delete group
        self.board_context[x][y].directions[direction] = None

        # self._check_invariants()

    def undo(self):
        # All changes in the last method call
        move_undo_instructions = self._context_undo_stack.pop()

        super().undo()

        for instruction in move_undo_instructions:
            if isinstance(instruction, UndoChange):
                self._undo_change(instruction)
            elif isinstance(instruction, UndoExtend):
                self._undo_extend(instruction)
            elif isinstance(instruction, UndoMerge):
                self._undo_merge(instruction)
            elif isinstance(instruction, UndoCreate):
                self._undo_create(instruction)

        # self._check_invariants()

    def clone(self):
        cloned = BoardModel.clone(self)
        cloned.rating = self.rating
        cloned.board_context = deepcopy(self.board_context)
        cloned._context_undo_stack = deepcopy(self._context_undo_stack)

        return cloned
