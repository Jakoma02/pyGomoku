import unittest

from models import analysis
from models.board import BoardModel
from models.tile import TileModel


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
        self.assertEqual((0, 1), doubles)

    def test_cross(self):
        self.board.place(0, 0, TileModel.Symbols.CROSS)
        self.board.place(0, 1, TileModel.Symbols.CROSS)
        doubles = analysis.n_tet_counts(self.board, 2)
        self.assertEqual((1, 0), doubles)

    def test_both(self):
        self.board.place(0, 0, TileModel.Symbols.CIRCLE)
        self.board.place(0, 1, TileModel.Symbols.CIRCLE)
        self.board.place(1, 0, TileModel.Symbols.CROSS)
        self.board.place(2, 0, TileModel.Symbols.CROSS)

        doubles = analysis.n_tet_counts(self.board, 2)
        self.assertEqual((1, 1), doubles)

    def test_longer(self):
        self.board.place(0, 0, TileModel.Symbols.CIRCLE)
        self.board.place(1, 0, TileModel.Symbols.CIRCLE)
        self.board.place(2, 0, TileModel.Symbols.CIRCLE)

        doubles = analysis.n_tet_counts(self.board, 2)
        self.assertEqual((0, 0), doubles)

    def test_last_symbol(self):
        pos = [(0, 13), (0, 14)]
        self._place_multiple(TileModel.Symbols.CIRCLE, pos)

        doubles = analysis.n_tet_counts(self.board, 2)
        self.assertEqual((0, 1), doubles)

    def test_vertical(self):
        pos = [(0, 0), (1, 0)]
        self._place_multiple(TileModel.Symbols.CIRCLE, pos)

        doubles = analysis.n_tet_counts(self.board, 2)
        self.assertEqual((0, 1), doubles)

    def test_diagonal(self):
        pos = [(0, 0), (1, 1)]
        self._place_multiple(TileModel.Symbols.CIRCLE, pos)

        doubles = analysis.n_tet_counts(self.board, 2)
        self.assertEqual((0, 1), doubles)


if __name__ == '__main__':
    unittest.main()
