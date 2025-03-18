import tkinter as tk
from tkinter import ttk

class StatisticsView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Header Label
        label = ttk.Label(self, text="Statistics View", font=("Helvetica", 18, "bold"))
        label.pack(pady=20)

        # Back Navigation
        home_btn = ttk.Button(self, text="Back to Home", command=lambda: controller.show_frame("HomeView"))
        home_btn.pack(pady=10)