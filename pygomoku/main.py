#!/usr/bin/env python3
"""
Game entry class
"""

import tkinter as tk

from pygomoku.controllers.board import GameController


def main():
    """
    Game entry point
    """
    root = tk.Tk()
    root.title("Gomoku")
    root.geometry("350x350")
    root.resizable(0, 0)

    GameController(root)  # The instance just needs to be created
    root.mainloop()


if __name__ == "__main__":
    main()
