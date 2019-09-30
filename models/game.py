from models.board import BoardModel
from models.tile import TileModel
from models.observable import Observable
from models.raters import SimpleRater
from .ai import RandomAI, MinimaxAI


class Game:
    def __init__(self, size):
        self.board = BoardModel(size)
        self.active = Observable(self, True)
        self.cross_turn = True
        self.player_turn = True
        self.multiplayer = True
        self.ai = MinimaxAI(self.board, 4)
        self.rater = SimpleRater()

    def play_move(self, x, y):
        if not self.active.get():
            return
        symbol = TileModel.Symbols.CROSS if self.cross_turn else TileModel.Symbols.CIRCLE
        if not self.board.place(x, y, symbol):
            return
        win_info = self.board.check_win()
        if win_info:
            self.end_game()
            self.board.mark_win(win_info)
            return
        self.cross_turn = not self.cross_turn
        if self.multiplayer:
            self.player_turn = not self.player_turn
            if not self.player_turn:
                self._ai_turn()

    def _ai_turn(self):
        x, y = self.ai.get_move(self.cross_turn)
        self.play_move(x, y)

    def end_game(self):
        self.active.set(False)
        self.board.disable()

    def new_game(self):
        self.board.reset()
        self.active.set(True)
        if not self.player_turn:
            self._ai_turn()
