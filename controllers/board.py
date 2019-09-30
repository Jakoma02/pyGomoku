from tkinter import Menu

from models.game import Game
from models.tile import TileModel
from views.board import BoardView


class GameController:
    SIZE = 5

    def __init__(self, master):
        self.master = master
        self.game = Game(self.SIZE)
        self.view = BoardView(master, self.SIZE)
        self._setup_board()
        self._setup_menu()

    def _setup_board(self):
        # Bind tiles
        for x in range(self.SIZE):
            for y in range(self.SIZE):
                tile_view = self.view.tiles[x][y]

                tile_view.bind_click(lambda event: self.tile_click(event.widget.x, event.widget.y))
                tile_view.bind_mouse_enter(lambda event: self.tile_mouse_enter(event.widget.x, event.widget.y))
                tile_view.bind_mouse_leave(lambda event: self.tile_mouse_leave(event.widget.x, event.widget.y))

                tile_model = self.game.board[x][y]
                tile_model.symbol.add_callable(lambda value, parent: self.symbol_changed(parent, value))
                tile_model.state.add_callable(lambda value, parent: self.state_changed(parent, value))

    def _setup_menu(self):
        self.menu = Menu(self.master)
        self.gamemenu = Menu(self.menu, tearoff=0)
        self.gamemenu.add_command(label="New game...", command=self.game.new_game)
        self.menu.add_cascade(menu=self.gamemenu, label="Game")

        self.master.config(menu=self.menu)

    def get_tile_view(self, x, y):
        return self.view.tiles[x][y]

    def tile_click(self, x, y):
        self.game.play_move(x, y)

    def tile_mouse_enter(self, x, y):
        tile = self.game.board[x][y]
        if self.game.active.get():
            tile.state.set(TileModel.States.PRELIT)

    def tile_mouse_leave(self, x, y):
        tile = self.game.board[x][y]
        if self.game.active.get():
            tile.state.set(TileModel.States.NONE)

    def symbol_changed(self, parent, symbol):
        tile_view = self.get_tile_view(parent.x, parent.y)
        if symbol == TileModel.Symbols.EMPTY:
            tile_view.reset()
        elif symbol == TileModel.Symbols.CROSS:
            tile_view.draw_cross()
        elif symbol == TileModel.Symbols.CIRCLE:
            tile_view.draw_circle()

    def state_changed(self, parent, value):
        tile_view = self.get_tile_view(parent.x, parent.y)
        if value == TileModel.States.NONE:
            tile_view.no_prelight()
        elif value == TileModel.States.PRELIT:
            tile_view.prelight()
        elif value == TileModel.States.DISABLED:
            tile_view.disable()
        elif value == TileModel.States.MARKED_AS_WIN:
            tile_view.mark_as_win()
