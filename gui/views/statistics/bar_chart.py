import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")

class BarChart(tk.Frame):
    def __init__(self, parent, df):
        super().__init__(parent)
        self.df = df
        
        # Container for chart+table and listbox side by side
        bar_content_frame = ttk.Frame(self)
        bar_content_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # LEFT: Scrollable canvas container for chart + table
        scroll_canvas = tk.Canvas(bar_content_frame)
        scrollbar_y = ttk.Scrollbar(bar_content_frame, orient="vertical", command=scroll_canvas.yview)
        scrollbar_x = ttk.Scrollbar(bar_content_frame, orient="horizontal", command=scroll_canvas.xview)
        scroll_canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        scroll_canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns", padx=(0, 10))
        scrollbar_x.grid(row=1, column=0, columnspan=2, sticky="ew")

        bar_content_frame.columnconfigure(0, weight=1)
        bar_content_frame.rowconfigure(0, weight=1)

        scrollable_frame = ttk.Frame(scroll_canvas)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))
        )

        scroll_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # Bar chart + table container (vertical stack)
        chart_and_table_frame = ttk.Frame(scrollable_frame)
        chart_and_table_frame.pack(fill="both", expand=True)

        # Bar chart frame
        self.bar_chart_frame = ttk.Frame(chart_and_table_frame)
        self.bar_chart_frame.pack(fill="both", expand=True, padx=5, pady=(5, 0))

        # Fixed size table frame
        table_frame = ttk.Frame(chart_and_table_frame, width=600, height=180)
        table_frame.pack_propagate(False)  # Prevent the frame from resizing to its content
        table_frame.pack(anchor="w", padx=5, pady=(10, 10))  # Do NOT allow fill or expand

        # Treeview with fixed size inside the fixed frame
        self.table = ttk.Treeview(
            table_frame,
            columns=("Experiment", "Total"),
            show="headings",
            height=6,  # Controls number of visible rows
            style="Custom.Treeview"
        )
        self.table.heading("Experiment", text="Experiment")
        self.table.heading("Total", text="Total Energy")
        self.table.column("Experiment", width=120, anchor="center")
        self.table.column("Total", width=120, anchor="center")

        # Pack it without fill/expand — exact size
        self.table.pack(fill="both", expand=True)

        self.table.heading("Experiment", text="Experiment")
        self.table.heading("Total", text="Total Energy")
        self.table.column("Experiment", width=120, anchor="center")
        self.table.column("Total", width=120, anchor="center")
        self.table.pack(fill='x')

        self.table.heading("Experiment", text="Experiment")
        self.table.heading("Total", text="Total Energy")
        self.table.column("Experiment", width=120, anchor="center")
        self.table.column("Total", width=120, anchor="center")
        self.table.pack(pady=(10, 0), padx=5, fill='x')

        # RIGHT: Experiment listbox
        listbox_container = ttk.Frame(bar_content_frame)
        listbox_container.grid(row=0, column=2, sticky="ns")

        listbox_label = ttk.Label(listbox_container, text="Select Experiments:")
        listbox_label.pack(pady=(0, 5))

        self.bar_exp_listbox = tk.Listbox(listbox_container, selectmode=tk.MULTIPLE, exportselection=False, height=12)
        for exp in sorted(self.df['Experiment'].unique()):
            self.bar_exp_listbox.insert(tk.END, exp)
        self.bar_exp_listbox.pack()

        if self.bar_exp_listbox.size() > 0:
            self.bar_exp_listbox.selection_set(0)

        self.bar_exp_listbox.bind("<<ListboxSelect>>", lambda e: self.update())

        self.bar_canvas = None
        
        def _on_mousewheel(event):
            if event.num == 4:  # macOS scroll up
                scroll_canvas.yview_scroll(-1, "units")
            elif event.num == 5:  # macOS scroll down
                scroll_canvas.yview_scroll(1, "units")
            else:  # Windows and Linux
                scroll_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        def _on_shift_mousewheel(event):
            if event.num == 4:
                scroll_canvas.xview_scroll(-1, "units")
            elif event.num == 5:
                scroll_canvas.xview_scroll(1, "units")
            else:
                scroll_canvas.xview_scroll(int(-1*(event.delta/120)), "units")

        def _bind_mousewheel(widget):
            widget.bind("<Enter>", lambda e: _activate_mousewheel())
            widget.bind("<Leave>", lambda e: _deactivate_mousewheel())

        def _activate_mousewheel():
            # Windows & Linux
            scroll_canvas.bind_all("<MouseWheel>", _on_mousewheel)
            scroll_canvas.bind_all("<Shift-MouseWheel>", _on_shift_mousewheel)
            # macOS
            scroll_canvas.bind_all("<Button-4>", _on_mousewheel)
            scroll_canvas.bind_all("<Button-5>", _on_mousewheel)

        def _deactivate_mousewheel():
            scroll_canvas.unbind_all("<MouseWheel>")
            scroll_canvas.unbind_all("<Shift-MouseWheel>")
            scroll_canvas.unbind_all("<Button-4>")
            scroll_canvas.unbind_all("<Button-5>")
        
        _bind_mousewheel(scrollable_frame)


    def update(self, energy_type = None, df = None):
        if energy_type:
            self.energy_type = energy_type
        if df is not None:
            self.df = df
            self._refresh_experiment_list()
        selected_exps = self._get_selected_experiments()
        if not selected_exps or not self.energy_type or self.df is None:
            return
        
        grouped, y_label, sum_data = self._extract_data(selected_exps, self.energy_type)
        
        if self.bar_canvas:
            self.bar_canvas.get_tk_widget().destroy()
        self._plot_chart(energy_type, grouped, y_label)
        self._plot_table(sum_data)
        

    def _get_selected_experiments(self):
        selected_indices = self.bar_exp_listbox.curselection()
        selected_exps = [self.bar_exp_listbox.get(i) for i in selected_indices]
        return selected_exps

    def _extract_data(self, selected_exps, energy_type):
        bar_data = self.df[self.df['Experiment'].isin(selected_exps)]
        if energy_type == 'CPU Energy':
            grouped = bar_data.groupby(['Experiment', 'Task'], sort=False)['CPU Energy'].mean().reset_index()
            y_label = 'CPU Energy'
            sum_data = bar_data.groupby('Experiment', sort=False)['CPU Energy'].sum()
        elif energy_type == 'RAM Energy':
            grouped = bar_data.groupby(['Experiment', 'Task'], sort=False)['RAM Energy'].mean().reset_index()
            y_label = 'RAM Energy'
            sum_data = bar_data.groupby('Experiment', sort=False)['RAM Energy'].sum()
        else:
            bar_data = bar_data.copy()
            bar_data['Total Energy'] = bar_data['CPU Energy'] + bar_data['RAM Energy']
            grouped = bar_data.groupby(['Experiment', 'Task'], sort=False)['Total Energy'].mean().reset_index()
            y_label = 'Total Energy'
            sum_data = bar_data.groupby('Experiment', sort=False)['Total Energy'].sum()
        return grouped, y_label, sum_data


    def _refresh_experiment_list(self):
        # Clear and repopulate the experiment listbox
        self.bar_exp_listbox.delete(0, tk.END)
        for exp in sorted(self.df['Experiment'].unique()):
            self.bar_exp_listbox.insert(tk.END, exp)

        if self.bar_exp_listbox.size() > 0:
            self.bar_exp_listbox.selection_set(0)

    def _plot_chart(self, energy_type, grouped, y_label):
        energy_type = self.energy_type
        n_experiments = grouped['Experiment'].nunique()
        n_tasks = grouped['Task'].nunique()
        width = max(6, n_tasks * n_experiments * 0.1)
        height = 6

        fig, ax = plt.subplots(figsize=(width, height))
        sns.barplot(data=grouped, x='Task', y=y_label, hue='Experiment', palette="pastel", ax=ax)

        ax.set_title(f"{energy_type} by Task across Experiments", pad=10)
        ax.set_xlabel("Task")
        ax.set_ylabel(y_label)
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

        plt.tight_layout(pad=1.0)  # Minimize surrounding whitespace
        fig.subplots_adjust(top=0.92, bottom=0.25, left=0.08, right=0.95)

        self.bar_canvas = FigureCanvasTkAgg(fig, master=self.bar_chart_frame)
        self.bar_canvas.draw()
        self.bar_canvas.get_tk_widget().pack(pady=10, fill='both', expand=True)
        plt.close(fig)

    def _plot_table(self, sum_data):
        for row in self.table.get_children():
            self.table.delete(row)
        for i, (exp, total) in enumerate(sum_data.items()):
            tag = 'odd' if i % 2 == 0 else 'even'
            self.table.insert("", tk.END, values=(exp, round(total, 2)), tags=(tag,))
        self.table.tag_configure('odd', background='#f9f9f9')
        self.table.tag_configure('even', background='#e6f2ff')
        