import tkinter as tk

from controllers.board import GameController

root = tk.Tk()
root.title("Gomoku")
board = GameController(root)
root.mainloop()
