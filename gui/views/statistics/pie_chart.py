import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")

class PieChart(tk.Frame):
    def __init__(self, parent, df):
        super().__init__(parent)
        self.df = df
        
        ttk.Label(self, text="Select Experiment:").pack(pady=(10, 0))
        self.pie_exp_var = tk.StringVar()
        self.pie_exp_dropdown = ttk.Combobox(self, textvariable=self.pie_exp_var, state="readonly")
        self.pie_exp_dropdown['values'] = sorted(self.df['Experiment'].unique())
        self.pie_exp_dropdown.current(0)
        self.pie_exp_dropdown.pack(pady=5)
        self.pie_exp_dropdown.bind("<<ComboboxSelected>>", lambda e: self.update())
        self.pie_canvas = None
        
    def update(self, energy_type = None, df = None):
        if energy_type:
            self.energy_type = energy_type
        if df is not None:
            self.df = df
        selected_exp = self._get_selected_experiment()
        if not selected_exp or not self.energy_type or self.df is None:
            return

        avg_energy = self._extract_data(selected_exp)
            
        if self.pie_canvas:
            self.pie_canvas.get_tk_widget().destroy()
        self._plot_chart(selected_exp, avg_energy)
    
    def _get_selected_experiment(self):
        selected_exp = self.pie_exp_var.get()
        return selected_exp

    def _extract_data(self, selected_exp):
        exp_df = self.df[self.df['Experiment'] == selected_exp]
        if self.energy_type == 'CPU Energy':
            avg_energy = exp_df.groupby('Task')['CPU Energy'].mean()
        elif self.energy_type == 'RAM Energy':
            avg_energy = exp_df.groupby('Task')['RAM Energy'].mean()
        else:
            exp_df = exp_df.copy()
            exp_df['Total Energy'] = exp_df['CPU Energy'] + exp_df['RAM Energy']
            avg_energy = exp_df.groupby('Task')['Total Energy'].mean()
        return avg_energy

    def _plot_chart(self, selected_exp, avg_energy):
        fig, ax = plt.subplots()
        colors = sns.color_palette("pastel", len(avg_energy))
        ax.pie(avg_energy, labels=avg_energy.index, autopct='%1.1f%%', startangle=90, colors=colors)
        ax.axis('equal')
        plt.title(f"{self.energy_type} - {selected_exp}")
        self.pie_canvas = FigureCanvasTkAgg(fig, master=self)
        self.pie_canvas.draw()
        self.pie_canvas.get_tk_widget().pack(pady=10, fill='both', expand=True)
        plt.close(fig)
