from models.board import BoardModel
from models.constants import Direction
from models.tile import TileModel
import unittest as ut


class TestPlace(ut.TestCase):
    def setUp(self):
        self.board = BoardModel(15)

    def test_circle(self):
        self.board.place(0, 0, TileModel.Symbols.CIRCLE)
        self.assertEqual(TileModel.Symbols.CIRCLE, self.board[0][0].symbol.get())

    def test_cross(self):
        self.board.place(1, 0, TileModel.Symbols.CROSS)
        self.assertEqual(TileModel.Symbols.CROSS, self.board[1][0].symbol.get())

    def test_invalid(self):
        self.board.place(0, 0, TileModel.Symbols.CIRCLE)
        self.board.place(0, 0, TileModel.Symbols.CROSS)
        self.assertEqual(TileModel.Symbols.CIRCLE, self.board[0][0].symbol.get())


class TestNextTile(ut.TestCase):
    def setUp(self):
        self.board = BoardModel(15)

    def test_horizontal_first(self):
        self.assertEqual((0, 1), self.board.next_tile(0, 0, Direction.HORIZONTAL))

    def test_horizontal_one_but_last(self):
        self.assertEqual((14, 14), self.board.next_tile(14, 13, Direction.HORIZONTAL))

    def test_vertical_first(self):
        self.assertEqual((1, 0), self.board.next_tile(0, 0, Direction.VERTICAL))

    def test_vertical_one_but_last(self):
        self.assertEqual((14, 14), self.board.next_tile(13, 14, Direction.VERTICAL))

    def test_diagonal_a_first(self):
        self.assertEqual((1, 0), self.board.next_tile(0, 1, Direction.DIAGONAL_A))

    def test_diagonal_a_one_but_last(self):
        self.assertEqual((14, 13), self.board.next_tile(13, 14, Direction.DIAGONAL_A))

    def test_diagonal_a_center(self):
        self.assertEqual((14, 0), self.board.next_tile(13, 1, Direction.DIAGONAL_A))

    def test_diagonal_b_first(self):
        self.assertEqual((14, 1), self.board.next_tile(13, 0, Direction.DIAGONAL_B))

    def test_diagonal_b_one_but_last(self):
        self.assertEqual((1, 14), self.board.next_tile(0, 13, Direction.DIAGONAL_B))

    def test_diagonal_b_center(self):
        self.assertEqual((14, 14), self.board.next_tile(13, 13, Direction.DIAGONAL_B))


if __name__ == "__main__":
    ut.main()
