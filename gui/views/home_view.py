import tkinter as tk
from tkinter import ttk

class HomeView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Header Label
        label = ttk.Label(self, text="Home View", font=("Helvetica", 18, "bold"))
        label.pack(pady=20)

        # Navigation Buttons
        statistics_btn = ttk.Button(
            self,
            text="Go to Statistics",
            command=lambda: [
                controller.geometry("1000x800"),  # Resize the window
                controller.show_frame("StatisticsView"),
                controller.frames["StatisticsView"].update()
            ]
        )
        statistics_btn.pack(pady=10)

        settings_btn = ttk.Button(
            self,
            text="Go to Settings",
            command=lambda: [
                controller.geometry("700x1000"),  # Resize the window
                controller.show_frame("SettingsView")
            ]
        )

        settings_btn.pack(pady=10)