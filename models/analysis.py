from .tile import TileModel
from .tile_generators import all_generators


def n_tet_counts(board, n):
    """
    Returns count of cross and circle n-sized sequences on board
    :param board: the board instance to be analysed
    :param n: count of tiles that need to be in row
    :return:
    """

    def add_if_found():
        if same == n:  # Only equal, not greater
            if last == TileModel.Symbols.CROSS:
                counts[0] += 1
            elif last == TileModel.Symbols.CIRCLE:
                counts[1] += 1

    # [cross, circle]
    counts = [0, 0]

    for line, direction in all_generators(board):
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
