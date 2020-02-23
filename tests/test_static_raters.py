import unittest

from models.board import BoardModel
from models.static_raters import SimpleRater
from models.tile import TileModel


class TestSimpleRater(unittest.TestCase):
    def setUp(self) -> None:
        self.board = BoardModel(15)
        self.rater = SimpleRater()

    def test_empty(self):
        rating = self.rater.rate(self.board)
        self.assertEqual(rating, 0)

    def test_couples(self):
        self.board.place(0, 0, TileModel.Symbols.CROSS)
        self.board.place(1, 0, TileModel.Symbols.CROSS)
        self.board.place(3, 0, TileModel.Symbols.CROSS)
        self.board.place(4, 0, TileModel.Symbols.CROSS)
        self.board.place(6, 0, TileModel.Symbols.CIRCLE)
        self.board.place(7, 0, TileModel.Symbols.CIRCLE)

        rating = self.rater.rate(self.board)

        self.assertEqual(rating, 5)  # Replace with a constant?

    def test_win(self):
        self.board.place(0, 0, TileModel.Symbols.CROSS)
        self.board.place(0, 1, TileModel.Symbols.CROSS)
        self.board.place(0, 2, TileModel.Symbols.CROSS)
        self.board.place(0, 3, TileModel.Symbols.CROSS)
        self.board.place(0, 4, TileModel.Symbols.CROSS)

        rating = self.rater.rate(self.board)
        self.assertEqual(rating, 99999)  # Replace with a constant?


if __name__ == '__main__':
    unittest.main()
