from .raters import SimpleRater
from .tile_generators import all_empty_tiles
from .tile import TileModel


class RandomAI:
    def __init__(self, board):
        self.board = board

    def get_move(self, cross_turn):
        from random import randint

        while True:
            a = randint(0, self.board.size - 1)
            b = randint(0, self.board.size - 1)
            if self.board[a][b].empty():
                break
        return a, b


class MinimaxAI:
    def __init__(self, board, depth):
        self.board = board
        self.depth = depth
        self.rater = SimpleRater()

    @staticmethod
    def _board_with_tile(board, tile, cross_turn):
        symbol = TileModel.Symbols.CROSS if cross_turn else TileModel.Symbols.CIRCLE
        return board.clone().place(tile.x, tile.y, symbol)

    def minimax(self, board, depth, cross_turn, last_move_tile=None):
        """
        :param board:
        :param depth:
        :param cross_turn:
        :param last_move_tile:
        :return: Tile object and rating
        """
        if depth == 0:
            return last_move_tile, self.rater.rate(board)

        minimax_results = []
        for new_tile in all_empty_tiles(board):
            minimax_result = self.minimax(self._board_with_tile(board, new_tile, cross_turn), depth - 1,
                                          not cross_turn, new_tile)
            minimax_results.append(minimax_result)

        if cross_turn:
            best_tile = max(minimax_results, key=lambda x: x[1])
        else:
            best_tile = min(minimax_results, key=lambda x: x[1])
        return best_tile

    def get_move(self, cross_turn):
        tile, rating = self.minimax(self.board, self.depth, cross_turn)
        return tile.x, tile.y
