import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")

class PieChart(tk.Frame):
    def __init__(self, parent, df):
        super().__init__(parent)
        self.df = df
        self.energy_type = None

        ttk.Label(self, text="Select Experiment:").pack(pady=(10, 0))
        self.pie_exp_var = tk.StringVar()
        self.pie_exp_dropdown = ttk.Combobox(self, textvariable=self.pie_exp_var, state="readonly")
        self.pie_exp_dropdown['values'] = sorted(self.df['Experiment'].unique())

        if self.pie_exp_dropdown['values']:
            self.pie_exp_dropdown.current(0)

        # self.pie_exp_dropdown.current(0)
        self.pie_exp_dropdown.pack(pady=5)
        self.pie_exp_dropdown.bind("<<ComboboxSelected>>", lambda e: self.update(self.energy_type, self.df))

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

        self.pie_exp_dropdown['values'] = sorted(self.df['Experiment'].unique())
        if self.pie_exp_dropdown['values']:
            self.pie_exp_dropdown.current(0)

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

        base_colors = sns.color_palette("pastel")
        colors = base_colors * (len(avg_energy) // len(base_colors) + 1)

        if avg_energy.empty or avg_energy.isna().all() or avg_energy.sum() == 0:
            print("Skipping pie chart: data is empty, all NaN, or zero.")
            return

        # Draw the pie chart
        wedges, _, autotexts = ax.pie(
            avg_energy,
            labels=None,  # No labels on the pie itself
            autopct='%1.1f%%',
            startangle=90,
            colors=colors[:len(avg_energy)],
            pctdistance=1.2
        )

        for autotext in autotexts:
            autotext.set_fontsize(8)

        # Create legend labels with percentages
        total = avg_energy.sum()
        labels = [
            f"{task} ({energy / total * 100:.1f}%)"
            for task, energy in avg_energy.items()
        ]

        # Add the legend next to the chart
        ax.legend(
            wedges,
            labels,
            title="Tasks",
            loc="center left",
            bbox_to_anchor=(1.1, 0.5),  # Move legend further right
            fontsize=10
        )

        ax.axis('equal')
        plt.title(f"{self.energy_type} - {selected_exp}")
        plt.tight_layout()

        self.pie_canvas = FigureCanvasTkAgg(fig, master=self)
        self.pie_canvas.draw()
        self.pie_canvas.get_tk_widget().pack(pady=10, fill='both', expand=True)
        plt.close(fig)
