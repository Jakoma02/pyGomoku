from random import choice

from .raters import SimpleRater, RandomRater
from .tile_generators import all_empty_tiles, relevant_tiles, relevant_usage, \
                             next_in_direction, prev_in_direction
from .tile import TileModel


class RandomAI:
    def __init__(self, board):
        self.board = board

    def get_move(self, cross_turn):
        relevant = list(relevant_tiles(self.board))

        move = choice(relevant)
        return (move.x, move.y)

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

        # print(f"depth={depth}")
        if self.i % 1000 == 0:
            print(self.i)
        self.i += 1

        stop = False

        if depth == 0:
            # rating = self.rater.rate(board)
            rating = board.rating
            return last_move_tile, rating

        # Order positions by rating
        position_options = []  # (tile, rating)

        symbol = TileModel.Symbols.CROSS if cross_turn else TileModel.Symbols.CIRCLE

        for new_tile in relevant_tiles(board):
            board.place(new_tile.x, new_tile.y, symbol)
            rating = board.rating
            position_options.append((new_tile, rating))
            board.undo()
            
        if cross_turn:
            key = lambda x: -x[1]
        else:
            key = lambda x: x[1]

        position_options.sort(key=key)
        position_options = position_options[:30]  # 30 (heuristically) best moves

        # print("Chosen adepts:")
        # for tile, rating in position_options:
            # board.place(tile.x, tile.y, symbol)
            # board.dump()
            # print()
            # board.undo()
            # input()

        minimax_results = []
        for new_tile, rating in position_options:
        # for new_tile in relevant_tiles(board):
            # TODO: Dont really change the TileModels, the gui doesnt have to get updated
            # Add new symbol to board (temporarily)
            board.place(new_tile.x, new_tile.y, symbol)
            minimax_result = self.minimax(board, depth - 1, not cross_turn,
                                          alpha=alpha, beta=beta, last_move_tile=new_tile)

            result_rating = minimax_result[1]

            # Check alpha and beta
            if (cross_turn and result_rating >= beta) or (not cross_turn and result_rating <= alpha):
                # Don't go further, this result will be ignored
                # print(f"alpha-beta helped (depth={depth})")
                minimax_results = [minimax_result]
                stop = True  # Still needs to be cleaned up
            else:
                # print(f"alpha-beta DIDN'T help (depth={depth})")
                pass

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
        detached_board = self.board.clone()
        # detached_board = self.board  # Right, this is very much attached... :)
        tile, rating = self.minimax(detached_board, self.depth, cross_turn, alpha=float("-inf"), beta=float("inf"))

        role = "maximizing" if cross_turn else "minimizing"
        print(f"Chose position with rating {rating}, was {role}")
        print(f"Place calls: {detached_board.place_call_count}")
        print(f"Relevat tiles calls: {relevant_usage()}")
        return tile.x, tile.y


class RuleAI:
    def __init__(self, board):
        self.board = board

    def find_attack(self, symbol, min_size, unblocked):
        for group in self.board.groups:
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

    def group_empty_end(self, group):
        x, y = group.x, group.y
        tile = self.board[x][y]
        symbol = tile.symbol.get()
        direction = group.direction

        end_tile = tile
        while end_tile is not None and \
                end_tile.symbol.get() == symbol:
            end_tile = next_in_direction(self.board, end_tile, direction)

        if end_tile is not None and end_tile.empty():
            return end_tile

        # Search in opposite direction
        end_tile = tile
        while end_tile is not None and \
                end_tile.symbol.get() == symbol:
            end_tile = prev_in_direction(self.board, end_tile, direction)

        return end_tile

    def get_move(self, cross_turn):
        if cross_turn:
            my_symbol = TileModel.Symbols.CROSS
            other_symbol = TileModel.Symbols.CIRCLE
        else:
            my_symbol = TileModel.Symbols.CIRCLE
            other_symbol = TileModel.Symbols.CROSS

        my_fourth = self.find_attack(my_symbol, 4, False)
        if my_fourth is not None:
            end = self.group_empty_end(my_fourth)
            return (end.x, end.y)

        print("I don't have a fourth")

        other_fourth = self.find_attack(other_symbol, 4, False)
        if other_fourth is not None:
            end = self.group_empty_end(other_fourth)
            return (end.x, end.y)

        print("The human doesn't have a fourth")

        my_open_third = self.find_attack(my_symbol, 3, True)
        if my_open_third is not None:
            end = self.group_empty_end(my_open_third)
            return (end.x, end.y)

        print("I don't have an open third")

        other_open_third = self.find_attack(other_symbol, 3, True)
        if other_open_third is not None:
            end = self.group_empty_end(other_open_third)
            return (end.x, end.y)

        print("The human doesn't have an open third")

        my_open_couple = self.find_attack(my_symbol, 2, True)
        if my_open_couple is not None:
            end = self.group_empty_end(my_open_couple)
            return (end.x, end.y)

        print("I don't have an open couple")

        other_open_couple = self.find_attack(other_symbol, 2, True)
        if other_open_couple is not None:
            end = self.group_empty_end(other_open_couple)
            return (end.x, end.y)

        print("The human doesn't have an open couple")
        
        # Choose randomly (from relevant tiles)

        relevant = list(relevant_tiles(self.board))
        tile = choice(relevant)

        return (tile.x, tile.y)


class CombinedAI(MinimaxAI, RuleAI):
    def get_move(self, cross_turn):
        if cross_turn:
            my_symbol = TileModel.Symbols.CROSS
            other_symbol = TileModel.Symbols.CIRCLE
        else:
            my_symbol = TileModel.Symbols.CIRCLE
            other_symbol = TileModel.Symbols.CROSS

        my_fourth = self.find_attack(my_symbol, 4, False)
        if my_fourth is not None:
            end = self.group_empty_end(my_fourth)
            return (end.x, end.y)

        print("I don't have a fourth")

        other_fourth = self.find_attack(other_symbol, 4, False)
        if other_fourth is not None:
            end = self.group_empty_end(other_fourth)
            return (end.x, end.y)

        print("The human doesn't have a fourth")

        my_open_third = self.find_attack(my_symbol, 3, True)
        if my_open_third is not None:
            end = self.group_empty_end(my_open_third)
            return (end.x, end.y)

        print("I don't have an open third")

        # Let minimax decide ho to handle opponent open thirds

        return super().get_move(cross_turn)
