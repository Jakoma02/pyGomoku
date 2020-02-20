from .tile import TileModel
from .tile_generators import all_generators


def n_tet_counts(board, n):
        """
        Returns count of cross and circle n-sized sequences on board
        :param board: the board instance to be analysed
        :param n: count of tiles that need to be in row
        :return:
        """
        counts = [0, 0]

        for line, direction in all_generators(board):
            same = 1
            last = None

            for tile in line:
                symbol = tile.symbol.get()
                if symbol == TileModel.Symbols.EMPTY:
                    continue
                if symbol == last:
                    same += 1
                if same >= n:
                    if symbol == TileModel.Symbols.CROSS:
                        counts[0] += 1
                    elif symbol == TileModel.Symbols.CIRCLE:
                        counts[1] += 1
                    same = 1
                last = symbol

        return tuple(counts)
