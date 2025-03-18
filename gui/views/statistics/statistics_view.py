import tkinter as tk
from tkinter import ttk
import pandas as pd

from gui.views.statistics.bar_chart import BarChart
from gui.views.statistics.pie_chart import PieChart

class StatisticsView(tk.Frame):
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # DataFrame Setup
        self.df = pd.DataFrame({
            'Experiment': ['Exp A', 'Exp A', 'Exp A', 'Exp B', 'Exp B', 'Exp B', 'Exp B', 'Exp C', 'Exp C', 'Exp C'],
            'Task':       ['Task 1', 'Task 1', 'Task 2', 'Task 1', 'Task 3', 'Task 2', 'Task 3', 'Task 2', 'Task 4', 'Task 1'],
            'Run':        [1, 2, 1, 1, 1, 2, 2, 1, 1, 1],
            'CPU Energy': [100, 120, 90, 95, 85, 88, 92, 89, 76, 102],
            'RAM Energy': [50,  55, 45, 48, 42, 47, 49, 46, 38, 53]
        })

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Header Label
        header_frame = ttk.Frame(self)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        label = ttk.Label(header_frame, text="Statistics View", font=("Helvetica", 18, "bold"))
        label.pack(side="left")
        home_btn = ttk.Button(header_frame, text="Back to Home", command=lambda: controller.show_frame("HomeView"))
        home_btn.pack(side="right")

        # Energy Selector
        selector_frame = ttk.Frame(self)
        selector_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(10, 0))
        ttk.Label(selector_frame, text="Select Energy Type:").pack(side="left", padx=(0, 10))
        self.energy_type_var = tk.StringVar()
        energy_options = ['CPU Energy', 'RAM Energy', 'Both']
        self.energy_dropdown = ttk.Combobox(selector_frame, textvariable=self.energy_type_var, values=energy_options, state="readonly", width=15)
        self.energy_dropdown.current(0)
        self.energy_dropdown.pack(side="left")
        self.energy_dropdown.bind("<<ComboboxSelected>>", self.update)

        # Notebook Tabs
        notebook = ttk.Notebook(self)
        notebook.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        pie_tab = ttk.Frame(notebook)
        bar_tab = ttk.Frame(notebook)
        notebook.add(pie_tab, text="Last Experiment")
        notebook.add(bar_tab, text="Compare Experiments")
        pie_tab.grid_rowconfigure(0, weight=1)
        pie_tab.grid_columnconfigure(0, weight=1)
        bar_tab.grid_rowconfigure(0, weight=1)
        bar_tab.grid_columnconfigure(0, weight=1)

        self.pie_view = PieChart(pie_tab, self.df)
        self.pie_view.pack(fill="both", expand=True)
        self.bar_view = BarChart(bar_tab, self.df)
        self.bar_view.pack(fill="both", expand=True)

        self.update()
        
    def update(self, event=None):
        energy_type = self.energy_type_var.get()
        self.pie_view.update(energy_type, self.df)
        self.bar_view.update(energy_type, self.df)
