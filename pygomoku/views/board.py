import tkinter as tk

from pygomoku.views.tileview import TileView


class BoardView(tk.Frame):
    """
    A Tkinter frame containing tile views
    """
    def __init__(self, master, size):
        super().__init__(master)
        self.master = master
        self.tiles = []
        for x in range(size):
            row = []
            for y in range(size):
                tile = TileView(self, x, y)
                tile.grid(row=x, column=y)
                row.append(tile)
            self.tiles.append(row)
