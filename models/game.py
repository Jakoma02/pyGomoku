from threading import Thread

from models.board import BoardModel
from models.tile import TileModel
from models.observable import Observable
from models.raters import RatedBoard
from .ai import RandomAI, MinimaxAI, RuleAI, CombinedAI


class Game:
    def __init__(self, size):
        self.board = RatedBoard(size)
        # self.board = BoardModel(size)
        self.active = Observable(self, True)
        self.cross_turn = True
        self.player_turn = True
        self.player_starting = True  # This will be flipped in the beginning
        self.multiplayer = True
        # self.ai = MinimaxAI(self.board, 4)
        # self.ai = RandomAI(self.board)
        # self.ai = RuleAI(self.board)
        self.ai = CombinedAI(self.board, 4)

    def play_move(self, x, y):
        if not self.active.get():
            return
        symbol = TileModel.Symbols.CROSS if self.cross_turn else TileModel.Symbols.CIRCLE

        place_success = self.board.place(x, y, symbol)
        if not place_success:
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
                t = Thread(target=self._ai_turn)
                t.start()

    def _ai_turn(self):
        self.active.set(False)
        self.board.disable()
        x, y = self.ai.get_move(self.cross_turn)
        self.active.set(True)
        self.play_move(x, y)
        self.board.enable()

    def end_game(self):
        self.active.set(False)
        self.board.disable()

    def new_game(self):
        self.board.reset()
        self.active.set(True)

        self.player_turn = self.player_starting
        self.player_starting = not self.player_starting
        self.cross_turn = True

        if not self.player_turn:
            self._ai_turn()
