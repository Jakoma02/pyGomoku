from random import randint
from collections import namedtuple
from copy import deepcopy

from models.tile import TileModel
from models.board import BoardModel
from .analysis import n_tet_counts
from .constants import Direction
from models.tile_generators import direction_neighbors


# (x1, y1), (x2, y2) are being merged, (x3, y3) is the position that merged them
UndoMerge = namedtuple("UndoMerge", ["x1", "y1", "x2", "y2", "x3", "y3", "direction",
                                     "local_state1", "local_state2"])
UndoCreate = namedtuple("UndoCreate", ["x", "y", "direction"])
UndoChange = namedtuple("UndoChange", ["x", "y", "direction", "state"])
UndoExtend = namedtuple("UndoExtend", ["x", "y", "direction", "state"])


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
        self._size = 1
        self._symbol = symbol  # ?
        self._blocked = blocked  # 0-2, from how many sides it is protected

    def root(self):
        if self._parent is None:
            return self
        else:
            return self._parent.root()

    def get_state(self):
        if self._parent is not None:
            return self.root().get_state()

        return (
            self._size,
            self._symbol,
            self._blocked
        )

    def set_state(self, state):
        if self._parent is not None:
            self.root().set_state(state)
            return

        size, symbol, blocked = state
        self._size = size
        self._symbol = symbol
        self._blocked = blocked

    def get_local_state(self):
        # Useful for unmerge (don't lookup parent)
        return (
            self._parent,
            self._size,
            self._symbol,
            self._blocked
        )

    def force_local_state(self, local_state):
        # Useful for unmerge (force parent)
        parent, size, symbol, blocked = local_state

        self._parent = parent
        self._size = size
        self._symbol = symbol
        self._blocked = blocked

    def get_symbol(self):
        root = self.root()
        return root._symbol

    def get_size(self):
        root = self.root()
        return root._size

    def increment_size(self):
        root = self.root()
        root._size += 1

    def get_blocked(self):
        root = self.root()
        return root._blocked

    def increment_blocked(self):
        root = self.root()
        root._blocked += 1

    def merge(self, other):
        # DFU-like union
        my_root = self.root()
        other_root = other.root()

        print("Before merge: ")
        print(f"id1={id(self)}, id2={id(other)}")
        print(f"  Root 1: {self.get_state()}")
        print(f"  Root 2: {other.get_state()}")
        print(f"  Local 1: {self.get_local_state()}")
        print(f"  Local 2: {self.get_local_state()}")

        assert my_root != other_root

        other_root._parent = my_root
        my_root._size += other_root._size
        my_root._blocked += other_root._blocked

        print("After merge: ")
        print(f"  Root 1: {self.get_state()}")
        print(f"  Root 2: {other.get_state()}")
        print(f"  Local 1: {self.get_local_state()}")
        print(f"  Local 2: {self.get_local_state()}")

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

        # print(f"Counting {score}, size is {size}")

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
    __slots__ = BoardModel.__slots__ + \
        ("board_context", "_context_undo_stack", "rating")

    def __init__(self, size):
        super().__init__(size)
        self._reset_context()

    def reset(self):
        super().reset()
        self._reset_context()
        return self

    def _reset_context(self):
        self.board_context = [[PositionContext() for _ in range(self.size)]
                              for _ in range(self.size)]
        self._context_undo_stack = []
        self.rating = 0

    def place(self, x, y, symbol):
        # print(f"Placing ({x}, {y})")
        # print("Before:")
        # self.dump()
        # print()

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
                # print("Removing: ", end="")
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
                new_group = SymbolGroup(symbol, blocked_count)
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

                # TODO: Temp
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

        # self.dump()

        # print(f"board: placed at ({x}, {y})")
        # TODO: Look for crap in the stack
        # print(f"board: stack: {self._context_undo_stack}")

        self._check_invariants()
        return self

    def _check_invariants(self):
        for i in range(self.size):
            for j in range(self.size):
                tile = self[i][j]

                groups = self.board_context[i][j].directions

                for direction, group in groups.items():
                    if tile.empty():
                        assert group is None, f"Group ({i}, {j}) should be None in direction {direction}"
                        continue

                    assert group is not None, f"Group ({i}, {j}) should not be None in direction {direction}"
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

                    assert group is not None, f"({x}, {y}) group should not be None in direction {direction}"
                    assert symbol is not TileModel.Symbols.EMPTY, f"({x}, {y}) symbol in direction {direction}" \
                                f"should not be empty"

    def _undo_extend(self, instruction):
        # print("Undoing extend")
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
        # print("Removing: ", end="")
        try:
            self.rating -= group.score()
        except:
            self.dump()
            print(self.board_context[x][y].directions)
            print()
            print(f"Was undoing: {instruction}")

        group.set_state(state)

        # Rerate
        self.rating += group.score()

        # It shouldn't be possible that blocked >= 2
        assert group.get_blocked() < 2

        # self._check_invariants()

    def _undo_merge(self, instruction):
        # print("Undoing merge")
        x1, y1, x2, y2, x3, y3, direction, local_state1, local_state2 = instruction

        group1 = self.board_context[x1][y1].directions[direction]
        group2 = self.board_context[x2][y2].directions[direction]

        self.dump()

        print(f"UNmerging ({x1}, {y1}) and ({x2}, {y2}) with ({x3}, {y3})")
        print(f"id1={id(group1)}, id2={id(group2)}")
        print("Before unmerge: ")
        print(f"  Root 1: {group1.get_state()}")
        print(f"  Root 2: {group2.get_state()}")
        print(f"  Local 1: {group1.get_local_state()}")
        print(f"  Local 2: {group2.get_local_state()}")

        # Unrate - both groups have the same score, as one points to
        # the other
        # print("Removing: ", end="")
        self.rating -= group1.score()

        # Force both local states
        group1.force_local_state(local_state1)
        group2.force_local_state(local_state2)

        # Remove the added tile (this bug took a looot of time to find :)
        self.board_context[x3][y3].directions[direction] = None

        # Rerate both groups
        self.rating += group1.score()
        self.rating += group2.score()

        print("After unmerge: ")
        print(f"  Root 1: {group1.get_state()}")
        print(f"  Root 2: {group2.get_state()}")
        print(f"  Local 1: {group1.get_local_state()}")
        print(f"  Local 2: {group2.get_local_state()}")

        # It shouldn't be possible that both groups are fully blocked
        assert group1.get_blocked() < 2
        assert group2.get_blocked() < 2

        # self._check_invariants()

    def _undo_create(self, instruction):
        # print("Undoing create")
        x, y, direction = instruction

        group = self.board_context[x][y].directions[direction]

        # Unrate group
        # print("Removing: ", end="")
        self.rating -= group.score()

        # Delete group
        self.board_context[x][y].directions[direction] = None

        # self._check_invariants()

    def undo(self):
        # All changes in the last method call
        move_undo_instructions = self._context_undo_stack.pop()

        # print("Before:")
        # self.dump()

        super().undo()

        # print("\nAfter:")
        # self.dump()
        # print()

        for instruction in move_undo_instructions:
            # print(f"board: Undoing {instruction}")
            if isinstance(instruction, UndoChange):
                self._undo_change(instruction)
            elif isinstance(instruction, UndoExtend):
                self._undo_extend(instruction)
            elif isinstance(instruction, UndoMerge):
                self._undo_merge(instruction)
            elif isinstance(instruction, UndoCreate):
                self._undo_create(instruction)

        self._check_invariants()


    def clone(self):
        cloned = BoardModel.clone(self)
        # TODO: These errors seem important
        cloned.rating = self.rating
        cloned.board_context = deepcopy(self.board_context)
        cloned._context_undo_stack = deepcopy(self._context_undo_stack)

        return cloned

    def dump(self):
        """
        Print out board contents
        """
        # TODO: Move to main board class
        for i in range(self.size):
            row = []
            for j in range(self.size):
                tile = self._board[j][i]
                symbol = tile.symbol.get()
                str_symbol = ""

                if symbol == TileModel.Symbols.CIRCLE:
                    str_symbol = "o"
                elif symbol == TileModel.Symbols.CROSS:
                    str_symbol = "x"
                elif symbol == TileModel.Symbols.EMPTY:
                    str_symbol = " "

                row.append(str_symbol)
            str_row = "".join(row)
            print(str_row)
