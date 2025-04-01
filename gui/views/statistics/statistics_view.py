import tkinter as tk
from tkinter import ttk
import pandas as pd
import os

import global_vars
from gui.views.statistics.bar_chart import BarChart
from gui.views.statistics.pie_chart import PieChart
from logic.experiment_summary import aggregate_all_results, get_summary_csv_path

class StatisticsView(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.init_data()

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Header Label
        header_frame = ttk.Frame(self)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        label = ttk.Label(header_frame, text="Statistics View", font=("Helvetica", 18, "bold"))
        label.pack(side="left")
        home_btn = ttk.Button(header_frame,
                                text="Back to Home",
                                command=lambda: [
                                controller.geometry("500x300"),  # Resize the window
                                controller.show_frame("HomeView")
            ] )
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

        # Reload CSV Button
        reload_btn = ttk.Button(self, text="Reload CSV", command=self.update)
        reload_btn.grid(row=1, column=1, sticky="e", padx=10)

        # Reload status label (MUST be before calling self.update())
        self.reload_status = ttk.Label(self, text="", foreground="green")
        self.reload_status.grid(row=3, column=0, sticky="w", padx=10, pady=(0, 5))

        self.update()
        
    def init_data(self):
        if global_vars.PROJECT_REPOSITORY_PATH is None:
            print('Project folder is not selected, not initializing statistics views')
            self.df = pd.DataFrame(columns=['Experiment', 'Task', 'Run', 'CPU Energy', 'RAM Energy'])
            return
        
        # csv_path = "results/all_experiments_summary.csv"
        csv_path = get_summary_csv_path()

        # Create the CSV file with headers if it doesn't exist
        if not os.path.exists(csv_path):
            os.makedirs(os.path.dirname(csv_path), exist_ok=True)
            pd.DataFrame(columns=['Experiment', 'Task', 'Run', 'CPU Energy', 'RAM Energy']).to_csv(csv_path,
                                                                                                   index=False)
        
        aggregate_all_results()
        
        # DataFrame Setup
        try:
            self.df = pd.read_csv(csv_path)
        except Exception as e:
            print(f"Error loading CSV: {e}")
            self.df = pd.DataFrame(columns=['Experiment', 'Task', 'Run', 'CPU Energy', 'RAM Energy'])

    def update(self, event=None):
        if global_vars.PROJECT_REPOSITORY_PATH is None:
            print('Project folder is not selected, not updating statistics views')
            return
        # csv_path = "results/all_experiments_summary.csv"
        
        self.init_data()
        csv_path = get_summary_csv_path()
        
        try:
            self.df = pd.read_csv(csv_path)
            self.reload_status.config(text="CSV successfully loaded.")
        except Exception as e:
            print(f"Error loading CSV: {e}")
            self.df = pd.DataFrame(columns=['Experiment', 'Task', 'Run', 'CPU Energy', 'RAM Energy'])
            self.reload_status.config(text="Failed to reload CSV.")

        energy_type = self.energy_type_var.get()
        self.pie_view.update(energy_type, self.df)
        self.bar_view.update(energy_type, self.df)
