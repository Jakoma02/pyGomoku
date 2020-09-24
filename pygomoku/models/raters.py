"""
This module is OBSOLETED by RatedBoard, but is kept for completeness
"""

from random import randint
from collections import namedtuple
from copy import deepcopy

from .tile import TileModel
from .board import BoardModel
from .analysis import n_tet_counts
from .constants import Direction
from .tile_generators import direction_neighbors


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
