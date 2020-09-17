from .static_raters import SimpleRater, RandomRater
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
        self.rater = RandomRater()
        # self.rater = PositionRater()
        self.i = 0   # to be removed

    @staticmethod
    def _board_with_tile(board, tile, cross_turn):
        symbol = TileModel.Symbols.CROSS if cross_turn else TileModel.Symbols.CIRCLE
        return board.clone().place(tile.x, tile.y, symbol)

    def minimax(self, board, depth, cross_turn, alpha, beta, last_move_tile=None):
        """
        Cross maximizes, circle minimizes

        :param board:
        :param depth:
        :param cross_turn:
        :param last_move_tile:
        :return: Tile object and rating
        """

        if self.i % 1000 == 0:
            print(self.i)
        self.i += 1

        stop = False

        if depth == 0:
            return last_move_tile, self.rater.rate(board)

        minimax_results = []
        for new_tile in all_empty_tiles(board):
            # TODO: Dont really change the TileModels, the gui doesnt have to get updated
            # Add new symbol to board (temporarily)
            symbol = TileModel.Symbols.CROSS if cross_turn else TileModel.Symbols.CIRCLE
            board.place(new_tile.x, new_tile.y, symbol)
            minimax_result = self.minimax(board, depth - 1, not cross_turn,
                                          alpha=alpha, beta=beta, last_move_tile=new_tile)

            result_rating = minimax_result[1]

            # Check alpha and beta
            if (cross_turn and result_rating >= beta) or (not cross_turn and result_rating <= alpha):
                # Don't go further, this result will be ignored
                minimax_results = [minimax_result]
                stop = True  # Still needs to be cleaned up

            # Set new alpha/beta
            if cross_turn and result_rating > alpha:
                alpha = result_rating
            elif not cross_turn and result_rating < beta:
                beta = result_rating

            # Remove the added symbol
            board.undo()

            if stop:
                break

            minimax_results.append(minimax_result)

        if cross_turn:
            best_tile = max(minimax_results, key=lambda x: x[1])
        else:
            best_tile = min(minimax_results, key=lambda x: x[1])
        return best_tile

    def get_move(self, cross_turn):
        detached_board = self.board.clone()
        tile, rating = self.minimax(detached_board, self.depth, cross_turn, alpha=float("-inf"), beta=float("inf"))

        role = "maximizing" if cross_turn else "minimizing"
        print(f"Chose position with rating {rating}, was {role}")
        return tile.x, tile.y
