"""
Different AIs for gomoku
"""

from random import choice

from .tile_generators import relevant_tiles, next_in_direction, \
                             prev_in_direction
from .analysis import find_attack, group_empty_end
from .tile import TileModel


class AbstractAI:
    """
    A common superclass to all AIs
    """
    def __init__(self, board):
        self.board = board
        self.stopped = False

    # pylint: disable=unused-argument
    def get_move(self, cross_turn):
        """
        Returns a tuple (x, y) of chosen move position
        """
        self.stopped = False

    def stop(self):
        """
        Stop finding the move (from another thread)
        """
        self.stopped = True


class RandomAI(AbstractAI):
    """
    Plays random relevant moves
    """
    def get_move(self, cross_turn):
        super().get_move(cross_turn)

        relevant = list(relevant_tiles(self.board))

        move = choice(relevant)

        return (move.x, move.y)


class MinimaxAI(AbstractAI):
    """
    Uses minimax to find a good move.
    """
    def __init__(self, board, depth):
        super().__init__(board)

        self.depth = depth

    def minimax(self, board, depth, cross_turn, alpha, beta,
                last_move_tile=None):
        """
        Run the minimax algorithm.

        Cross maximizes, circle minimizes
        """

        stop = False

        if depth == 0:
            # rating = self.rater.rate(board)
            rating = board.rating
            return last_move_tile, rating

        # Order positions by rating
        position_options = []  # (tile, rating)

        symbol = TileModel.Symbols.CROSS if cross_turn \
            else TileModel.Symbols.CIRCLE

        for new_tile in relevant_tiles(board):
            board.place(new_tile.x, new_tile.y, symbol)
            rating = board.rating
            position_options.append((new_tile, rating))
            board.undo()

            if self.stopped:
                return None

        if cross_turn:
            def key(rating_tuple):
                return -rating_tuple[1]
        else:
            def key(rating_tuple):
                return rating_tuple[1]

        position_options.sort(key=key)
        # 30 (heuristically) best moves
        position_options = position_options[:30]

        minimax_results = []
        for new_tile, rating in position_options:
            if self.stopped:
                return None

            # Add new symbol to board (temporarily)
            board.place(new_tile.x, new_tile.y, symbol)
            minimax_result = self.minimax(board, depth - 1, not cross_turn,
                                          alpha=alpha, beta=beta,
                                          last_move_tile=new_tile)

            if self.stopped:
                return None

            result_rating = minimax_result[1]

            # Check alpha and beta
            if (cross_turn and result_rating >= beta) or \
                    (not cross_turn and result_rating <= alpha):
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

            # The rating that can be enforced after playing new_tile
            added_tile_result = (new_tile, result_rating)

            minimax_results.append(added_tile_result)

        if cross_turn:
            best_tile = max(minimax_results, key=lambda x: x[1])
        else:
            best_tile = min(minimax_results, key=lambda x: x[1])
        return best_tile

    def get_move(self, cross_turn):
        AbstractAI.get_move(self, cross_turn)

        detached_board = self.board.clone()
        minimax_result = self.minimax(detached_board, self.depth, cross_turn,
                                      alpha=float("-inf"), beta=float("inf"))

        if minimax_result is None:
            # Was stopped
            return None

        tile, _ = minimax_result

        return tile.x, tile.y


class RuleAI(AbstractAI):
    """
    Uses simple rules to find a move. If none apply,
    chooses a random relevant tile.
    """

    def get_move(self, cross_turn):
        super().get_move(cross_turn)

        if cross_turn:
            my_symbol = TileModel.Symbols.CROSS
            other_symbol = TileModel.Symbols.CIRCLE
        else:
            my_symbol = TileModel.Symbols.CIRCLE
            other_symbol = TileModel.Symbols.CROSS

        my_fourth = find_attack(self.board, my_symbol, 4, False)
        if my_fourth is not None:
            end = group_empty_end(self.board, my_fourth)
            return (end.x, end.y)

        other_fourth = find_attack(self.board, other_symbol, 4, False)
        if other_fourth is not None:
            end = group_empty_end(self.board, other_fourth)
            return (end.x, end.y)

        my_open_third = find_attack(self.board, my_symbol, 3, True)
        if my_open_third is not None:
            end = group_empty_end(self.board, my_open_third)
            return (end.x, end.y)

        other_open_third = find_attack(self.board, other_symbol, 3, True)
        if other_open_third is not None:
            end = group_empty_end(self.board, other_open_third)
            return (end.x, end.y)

        my_open_couple = find_attack(self.board, my_symbol, 2, True)
        if my_open_couple is not None:
            end = group_empty_end(self.board, my_open_couple)
            return (end.x, end.y)

        other_open_couple = find_attack(self.board, other_symbol, 2, True)
        if other_open_couple is not None:
            end = group_empty_end(self.board, other_open_couple)
            return (end.x, end.y)

        # Choose randomly (from relevant tiles)

        relevant = list(relevant_tiles(self.board))
        tile = choice(relevant)

        return (tile.x, tile.y)


class CombinedAI(MinimaxAI, RuleAI):
    """
    First apply some simple rules, then use minimax
    """
    def get_move(self, cross_turn):
        AbstractAI.get_move(self, cross_turn)

        if cross_turn:
            my_symbol = TileModel.Symbols.CROSS
            other_symbol = TileModel.Symbols.CIRCLE
        else:
            my_symbol = TileModel.Symbols.CIRCLE
            other_symbol = TileModel.Symbols.CROSS

        my_fourth = find_attack(self.board, my_symbol, 4, False)
        if my_fourth is not None:
            end = group_empty_end(self.board, my_fourth)
            return (end.x, end.y)

        other_fourth = find_attack(self.board, other_symbol, 4, False)
        if other_fourth is not None:
            end = group_empty_end(self.board, other_fourth)
            return (end.x, end.y)

        my_open_third = find_attack(self.board, my_symbol, 3, True)
        if my_open_third is not None:
            end = group_empty_end(self.board, my_open_third)
            return (end.x, end.y)

        # Let minimax decide ho to handle opponent open thirds

        return MinimaxAI.get_move(self, cross_turn)
