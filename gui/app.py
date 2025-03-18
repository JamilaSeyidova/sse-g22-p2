import tkinter as tk
from gui.views.home_view import HomeView
from gui.views.statistics_view import StatisticsView

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SSE G22 P2 GUI")
        self.geometry("800x600")

        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.frames = {}
        self._init_views()
        self.show_frame("HomeView")

    def _init_views(self):
        for ViewClass in (HomeView, StatisticsView):
            view_name = ViewClass.__name__
            frame = ViewClass(parent=self.container, controller=self)
            self.frames[view_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

    def show_frame(self, view_name):
        frame = self.frames[view_name]
        frame.tkraise()
