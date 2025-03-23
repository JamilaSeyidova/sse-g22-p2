import tkinter as tk
from gui.views.home_view import HomeView
from gui.views.statistics.statistics_view import StatisticsView
from gui.views.settings_view import SettingsView
import matplotlib.pyplot as plt

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GRADLENERGY GUI")
        self.geometry("800x600")
        self.minsize(600, 400)

        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self._init_views()
        self.show_frame("HomeView")

        # Register clean shutdown handler
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _init_views(self):
        for ViewClass in (HomeView, StatisticsView, SettingsView):
            view_name = ViewClass.__name__
            frame = ViewClass(parent=self.container, controller=self)
            self.frames[view_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

    def show_frame(self, view_name):
        frame = self.frames[view_name]
        frame.tkraise()

    def on_closing(self):
        # Clean up matplotlib figures to prevent delays on exit
        plt.close('all')
        self.destroy()