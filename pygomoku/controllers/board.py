"""
MVC controller of the game app
"""

from tkinter import Menu, BooleanVar, IntVar

from pygomoku.models.game import Game
from pygomoku.models.tile import TileModel
from pygomoku.views.board import BoardView


class GameController:
    """
    The controller class
    """
    SIZE = 15

    def __init__(self, master):

        self.multiplayer_option_var = BooleanVar()
        self.multiplayer_option_var.set(False)

        self.difficulty_option_var = IntVar()
        self.difficulty_option_var.set(3)

        self.master = master
        self.game = Game(self.SIZE)
        self.view = BoardView(master, self.SIZE)
        self.view.place(relx=0.5, rely=0.5, anchor="c")

        self._setup_board()
        self._setup_menu()

        self._update_multiplayer_setting()
        self._update_difficulty_setting()

        self.game.new_game()

    def _setup_board(self):
        # Bind tiles
        for x in range(self.SIZE):
            for y in range(self.SIZE):
                tile_view = self.view.tiles[x][y]

                tile_view.bind_click(
                    lambda event: self.tile_click(
                        event.widget.x, event.widget.y))
                tile_view.bind_mouse_enter(
                    lambda event: self.tile_mouse_enter(
                        event.widget.x, event.widget.y))
                tile_view.bind_mouse_leave(
                    lambda event: self.tile_mouse_leave(
                        event.widget.x, event.widget.y))

                tile_model = self.game.board[x][y]
                tile_model.symbol.add_callable(
                    lambda value, parent: self.symbol_changed(parent, value))
                tile_model.state.add_callable(
                    lambda value, parent: self.state_changed(parent, value))

    def _setup_menu(self):
        self.menu = Menu(self.master)
        self.gamemenu = Menu(self.menu, tearoff=0)
        self.gamemenu.add_command(
            label="New game...", command=self.game.new_game)
        self.gamemenu.add_separator()
        self.gamemenu.add_checkbutton(label="Multiplayer",
                                      variable=self.multiplayer_option_var,
                                      command=self._update_multiplayer_setting)

        self.menu.add_cascade(menu=self.gamemenu, label="Game")

        self.difficultymenu = Menu(self.menu, tearoff=0)
        self.difficultymenu.add_radiobutton(
            label="Very very easy",
            variable=self.difficulty_option_var,
            value=1,
            command=self._update_difficulty_setting)
        self.difficultymenu.add_radiobutton(
            label="Very easy",
            variable=self.difficulty_option_var,
            value=2,
            command=self._update_difficulty_setting)
        self.difficultymenu.add_radiobutton(
            label="Easy",
            variable=self.difficulty_option_var,
            value=3,
            command=self._update_difficulty_setting)
        self.menu.add_cascade(menu=self.difficultymenu, label="Difficulty")

        self.master.config(menu=self.menu)

    def _update_multiplayer_setting(self):
        is_multiplayer = self.multiplayer_option_var.get()

        self.game.set_multiplayer(is_multiplayer)

    def _update_difficulty_setting(self):
        difficulty = self.difficulty_option_var.get()

        self.game.set_difficulty(difficulty)

    def get_tile_view(self, x, y):
        """
        Return tile view on coordinates (x, y)
        """
        return self.view.tiles[x][y]

    def tile_click(self, x, y):
        """
        Tile click event handled
        """
        self.game.play_move(x, y)

    def tile_mouse_enter(self, x, y):
        """
        Tile mouse enter event handler
        """
        tile = self.game.board[x][y]
        if self.game.active.get():
            tile.state.set(TileModel.States.PRELIT)

    def tile_mouse_leave(self, x, y):
        """
        Tile mouse leave event handler
        """
        tile = self.game.board[x][y]
        if self.game.active.get():
            tile.state.set(TileModel.States.NONE)

    def symbol_changed(self, parent, symbol):
        """
        Tile symbol change handler
        """
        tile_view = self.get_tile_view(parent.x, parent.y)
        if symbol == TileModel.Symbols.EMPTY:
            tile_view.reset()
        elif symbol == TileModel.Symbols.CROSS:
            tile_view.draw_cross()
        elif symbol == TileModel.Symbols.CIRCLE:
            tile_view.draw_circle()

    def state_changed(self, parent, value):
        """
        Tile state change handler
        """
        tile_view = self.get_tile_view(parent.x, parent.y)
        if value == TileModel.States.NONE:
            tile_view.no_prelight()
        elif value == TileModel.States.PRELIT:
            tile_view.prelight()
        elif value == TileModel.States.DISABLED:
            tile_view.disable()
        elif value == TileModel.States.MARKED_AS_WIN:
            tile_view.mark_as_win()
