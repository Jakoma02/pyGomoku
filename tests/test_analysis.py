import unittest

from pygomoku.models import analysis
from pygomoku.models.board import BoardModel
from pygomoku.models.tile import TileModel


class TestCounting(unittest.TestCase):
    def setUp(self) -> None:
        self.board = BoardModel(15)

    def _place_multiple(self, symbol, positions):
        for p in positions:
            self.board.place(*p, symbol)

    def test_circle(self):
        self.board.place(0, 0, TileModel.Symbols.CIRCLE)
        self.board.place(0, 1, TileModel.Symbols.CIRCLE)
        doubles = analysis.n_tet_counts(self.board, 2)
        self.assertEqual(doubles, (0, 1))

    def test_cross(self):
        self.board.place(0, 0, TileModel.Symbols.CROSS)
        self.board.place(0, 1, TileModel.Symbols.CROSS)
        doubles = analysis.n_tet_counts(self.board, 2)
        self.assertEqual(doubles, (1, 0))

    def test_both(self):
        self.board.place(0, 0, TileModel.Symbols.CIRCLE)
        self.board.place(0, 1, TileModel.Symbols.CIRCLE)
        self.board.place(1, 0, TileModel.Symbols.CROSS)
        self.board.place(2, 0, TileModel.Symbols.CROSS)

        doubles = analysis.n_tet_counts(self.board, 2)
        self.assertEqual(doubles, (1, 1))

    def test_longer(self):
        self.board.place(0, 0, TileModel.Symbols.CIRCLE)
        self.board.place(1, 0, TileModel.Symbols.CIRCLE)
        self.board.place(2, 0, TileModel.Symbols.CIRCLE)

        doubles = analysis.n_tet_counts(self.board, 2)

        self.assertEqual(doubles, (0, 0))

    def test_last_symbol(self):
        pos = [(0, 13), (0, 14)]
        self._place_multiple(TileModel.Symbols.CIRCLE, pos)

        doubles = analysis.n_tet_counts(self.board, 2)
        self.assertEqual(doubles, (0, 1))

    def test_vertical(self):
        pos = [(0, 0), (1, 0)]
        self._place_multiple(TileModel.Symbols.CIRCLE, pos)

        doubles = analysis.n_tet_counts(self.board, 2)
        self.assertEqual(doubles, (0, 1))

    def test_diagonal(self):
        pos = [(0, 0), (1, 1)]
        self._place_multiple(TileModel.Symbols.CIRCLE, pos)

        doubles = analysis.n_tet_counts(self.board, 2)
        self.assertEqual(doubles, (0, 1))

    def test_more_in_line(self):
        pos = [(0, 0), (0, 1), (0, 2), (0, 4), (0, 5), (0, 6)]
        self._place_multiple(TileModel.Symbols.CIRCLE, pos)

        doubles = analysis.n_tet_counts(self.board, 3)
        self.assertEqual(doubles, (0, 2))


if __name__ == '__main__':
    unittest.main()
