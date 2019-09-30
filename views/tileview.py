import tkinter as tk


class TileView(tk.Canvas):
    def __init__(self, master, x, y):
        super().__init__(master, width=20, height=20, bg="white")
        self.x = x
        self.y = y

    def prelight(self):
        self.config(bg="yellow")

    def no_prelight(self):
        self.config(bg="white")

    def disable(self):
        self.config(bg="gray")

    def mark_as_win(self):
        self.config(bg="green")

    def reset(self):
        self.delete(tk.ALL)

    def draw_cross(self):
        self.reset()
        self.create_line(2, 2, 18, 18, fill="red", width=2)
        self.create_line(2, 18, 18, 2, fill="red", width=2)

    def draw_circle(self):
        self.reset()
        self.create_oval(2, 2, 18, 18, outline="blue", width=2)

    def bind_click(self, clb):
        self.bind("<Button-1>", clb)

    def bind_mouse_enter(self, clb):
        self.bind("<Enter>", clb)

    def bind_mouse_leave(self, clb):
        self.bind("<Leave>", clb)
