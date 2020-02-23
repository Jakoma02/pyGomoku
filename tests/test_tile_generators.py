import unittest

from models.board import BoardModel
from models.tile_generators import horizontal_generator, vertical_generator, diagonal_a_generator, diagonal_b_generator


class TestDirectionGenerators(unittest.TestCase):
    def setUp(self) -> None:
        self.board = BoardModel(4)

    def _test_generator(self, generator, expected):
        rowgens = list(generator(self.board))
        tiles = [list(g) for g in rowgens]

        self.assertEqual(len(rowgens), len(expected), "Wrong 'row' count")

        for res_row, exp_row in zip(tiles, expected):
            self.assertEqual(len(tiles), len(expected), "Wrong tile count")
            for res_tile, exp_xy in zip(res_row, exp_row):
                res_xy = (res_tile.x, res_tile.y)
                self.assertEqual(res_xy, exp_xy)

    def test_horizontal(self):
        expected = [
            [(0, 0), (0, 1), (0, 2), (0, 3)],
            [(1, 0), (1, 1), (1, 2), (1, 3)],
            [(2, 0), (2, 1), (2, 2), (2, 3)],
            [(3, 0), (3, 1), (3, 2), (3, 3)],
        ]
        self._test_generator(horizontal_generator, expected)

    def test_vertical(self):
        expected = [
            [(0, 0), (1, 0), (2, 0), (3, 0)],
            [(0, 1), (1, 1), (2, 1), (3, 1)],
            [(0, 2), (1, 2), (2, 2), (3, 2)],
            [(0, 3), (1, 3), (2, 3), (3, 3)]
        ]
        self._test_generator(vertical_generator, expected)

    def test_diagonal_b(self):
        expected = [
            [(0, 3)],
            [(0, 2), (1, 3)],
            [(0, 1), (1, 2), (2, 3)],
            [(0, 0), (1, 1), (2, 2), (3, 3)],
            [(1, 0), (2, 1), (3, 2)],
            [(2, 0), (3, 1)],
            [(3, 0)]
        ]
        self._test_generator(diagonal_b_generator, expected)

    def test_diagonal_a(self):
        expected = [
            [(0, 0)],
            [(0, 1), (1, 0)],
            [(0, 2), (1, 1), (2, 0)],
            [(0, 3), (1, 2), (2, 1), (3, 0)],
            [(1, 3), (2, 2), (3, 1)],
            [(2, 3), (3, 2)],
            [(3, 3)]
        ]
        self._test_generator(diagonal_a_generator, expected)


if __name__ == '__main__':
    unittest.main()
