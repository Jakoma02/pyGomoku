"""
This module controls core game logic
"""

from threading import Thread

from models.board import BoardModel, RatedBoard
from models.tile import TileModel
from models.observable import Observable
from .ai import RandomAI, MinimaxAI, RuleAI, CombinedAI


class Game:
    """
    The class controlling core game logic
    """
    def __init__(self, size):
        self.board = RatedBoard(size)
        self.active = Observable(self, True)
        self.cross_turn = True
        self.player_turn = True
        self.player_starting = True

        self.multiplayer = False
        self.difficulty = 1

        self.ai = None
        self._update_ai()

    def play_move(self, x, y):
        """
        If active, place a symbol on (x, y) for the player
        whose turn it is. Then (if not in multiplayer),
        initiate AI move.
        """
        if not self.active.get():
            return
        symbol = TileModel.Symbols.CROSS if self.cross_turn \
            else TileModel.Symbols.CIRCLE

        place_success = self.board.place(x, y, symbol)
        if not place_success:
            return
        win_info = self.board.check_win()
        if win_info:
            self.end_game()
            self.board.mark_win(win_info)
            return
        self.cross_turn = not self.cross_turn
        if not self.multiplayer:
            self.player_turn = not self.player_turn
            if not self.player_turn:
                ai_thread = Thread(target=self._ai_turn)
                ai_thread.start()

    def _ai_turn(self):
        self.active.set(False)
        self.board.disable()

        move = self.ai.get_move(self.cross_turn)

        if self.ai.stopped:
            return

        x, y = move

        self.active.set(True)
        self.board.enable()
        self.play_move(x, y)

    def end_game(self):
        """
        Ends the game, disables all further move attempts
        """
        self.active.set(False)
        self.board.disable()

    def new_game(self):
        """
        Start a new game
        """
        self.ai.stop()  # If AI is currently looking for a move, termininate it

        self.board.reset()
        self.active.set(True)

        self.player_turn = self.player_starting
        self.player_starting = not self.player_starting
        self.cross_turn = True

        if not self.multiplayer and not self.player_turn:
            ai_thread = Thread(target=self._ai_turn)
            ai_thread.start()

    def set_multiplayer(self, is_multiplayer):
        """
        Set multiplayer setting to `is_multiplayer`.

        Starts a new game if needed.
        """
        if self.multiplayer == is_multiplayer:
            return  # Nothing to do here

        self.multiplayer = is_multiplayer
        self.new_game()

    def _update_ai(self):
        if self.difficulty == 1:
            self.ai = RandomAI(self.board)
        elif self.difficulty == 2:
            self.ai = RuleAI(self.board)
        elif self.difficulty == 3:
            self.ai = CombinedAI(self.board, 4)

    def set_difficulty(self, difficulty):
        """
        Set difficulty setting to `difficulty`.

        Starts a new game if needed.
        """
        if self.difficulty == difficulty:
            return

        self.difficulty = difficulty
        self._update_ai()

        if not self.multiplayer:
            self.new_game()
