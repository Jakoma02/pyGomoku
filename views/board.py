import tkinter as tk

from views.tileview import TileView


class BoardView(tk.Frame):
    def __init__(self, master, size):
        super().__init__(master)
        self.master = master
        self.tiles = []
        for x in range(size):
            row = []
            for y in range(size):
                tile = TileView(master, x, y)
                tile.grid(row=x, column=y)
                row.append(tile)
            self.tiles.append(row)
