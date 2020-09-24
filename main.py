import tkinter as tk

from controllers.board import GameController

root = tk.Tk()
root.title("Gomoku")
root.geometry("350x350")
root.resizable(0, 0)

board = GameController(root)
root.mainloop()
