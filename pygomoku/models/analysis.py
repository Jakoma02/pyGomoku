"""
Helper functions for board analysis.
"""

from .tile import TileModel
from .tile_generators import all_generators, next_in_direction, \
                             prev_in_direction


def n_tet_counts(board, n):
    """
    Returns count of cross and circle n-sized sequences on board

    OBSOLETE, kept here for completeness
    """

    def add_if_found():
        if same == n:  # Only equal, not greater
            if last == TileModel.Symbols.CROSS:
                counts[0] += 1
            elif last == TileModel.Symbols.CIRCLE:
                counts[1] += 1

    # [cross, circle]
    counts = [0, 0]

    for line, _ in all_generators(board):
        same = 1
        last = None

        for tile in line:
            symbol = tile.symbol.get()
            if symbol == last:
                same += 1
            else:
                add_if_found()
                same = 1
            last = symbol

        add_if_found()  # Last symbol can also form a correct n-tet

    return tuple(counts)


def find_attack(board, symbol, min_size, unblocked):
    """
    Finds a group of at least `min_size` symbols of `symbol`.
    If `unblocked`, the group must not be blocked from either side,
    otherwise it may be blocked from ONE side. If no such group
    exists, returns None
    """
    for group in board.groups:
        size = group.get_size()
        blocked = group.get_blocked()
        group_symbol = group.get_symbol()

        if unblocked:
            max_blocked = 0
        else:
            max_blocked = 1

        if size >= min_size and blocked <= max_blocked \
                and group_symbol == symbol:
            return group

    return None


def group_empty_end(board, group):
    """
    Finds and empty end next to a group.
    """
    x, y = group.x, group.y
    tile = board[x][y]
    symbol = tile.symbol.get()
    direction = group.direction

    end_tile = tile
    while end_tile is not None and \
            end_tile.symbol.get() == symbol:
        end_tile = next_in_direction(board, end_tile, direction)

    if end_tile is not None and end_tile.empty():
        return end_tile

    # Search in opposite direction
    end_tile = tile
    while end_tile is not None and \
            end_tile.symbol.get() == symbol:
        end_tile = prev_in_direction(board, end_tile, direction)

    return end_tile
