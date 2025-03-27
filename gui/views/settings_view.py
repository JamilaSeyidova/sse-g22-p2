import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import os
import subprocess
import re
import threading
import queue

from logic.experiment_setup import find_energibridge, find_gradle_build, getTasks, run_experiment


class SettingsView(tk.Frame):

    repository = None
    label = None
    run_button = None
    exp_name_entry = None
    iterations_entry = None
    timeout_rep_entry = None
    timeout_task_entry = None
    warmup_var = None
    scrollable_frame = None
    vars_dict = None
    running = False
    message_queue = queue.Queue()
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Main window
        # root = tk.Tk()
        # root.title("GradleBridge")
        # #root.geometry("800x500")
        # root.configure(bg="#f8f9fa")

        #Style
        style = ttk.Style()
        style.theme_use("clam")  # Alternative themes: "alt", "default", "classic"
        style.configure("TFrame", background="#f8f9fa")
        style.configure("TLabel", font=("Arial", 14, "bold"), background="#f8f9fa", foreground="#333")
        style.configure("TEntry", font=("Arial", 12), padding=5)
        style.configure("run.TButton", font=("Arial", 12, "bold"), background="#4CAF50", foreground="white", padding=10)
        #style.map("run.TButton", background=[("active", "#45a049")]) 
        style.map("run.TButton", background=[("disabled", "#e0e0e0"), ("active", "#45a049")], foreground=[("disabled", "gray")])

        style.configure("browse.TButton", font=("Arial", 12, "bold"), background="#2196F3", foreground="white", padding=10)
        style.map("browse.TButton", background=[("active", "#1976D2")])  # Darker blue when hovered
        
        style.configure("TCheckbutton",
                        font=("Arial", 12),
                        foreground="#333",  # Text color
                        background="white",
                        padding=0,
                        width=20)

        style.map("TCheckbutton",
                  foreground=[("!selected", "#ff5733"), ("selected", "#33adff")])


        main_frame = ttk.Frame(self, style="TFrame", padding=20)
        main_frame.pack(expand=True, fill="both", anchor="center")

        #Entries (fields)
        ttk.Label(self, text="Experiment Name:", style="TLabel").pack(pady=5)
        self.exp_name_entry = ttk.Entry(self, style="TEntry", width=30)
        self.exp_name_entry.pack(pady=5)

        ttk.Label(self, text="Number of Iterations:", style="TLabel").pack(pady=5)
        self.iterations_entry = ttk.Entry(self, style="TEntry", width=10)
        self.iterations_entry.pack(pady=5)

        ttk.Label(self, text="Timeout between repetitions (s):", style="TLabel").pack(pady=5)
        self.timeout_rep_entry = ttk.Entry(self, style="TEntry", width=10)
        self.timeout_rep_entry.pack(pady=5)

        ttk.Label(self, text="Timeout between tasks (s):", style="TLabel").pack(pady=5)
        self.timeout_task_entry = ttk.Entry(self, style="TEntry", width=10)
        self.timeout_task_entry.pack(pady=5)

        # Checkbox for hardware warmup
        self.warmup_var = tk.IntVar()
        self.warmup_check = ttk.Checkbutton(self, text="Perform hardware warmup", variable=self.warmup_var)
        self.warmup_check.pack(pady=5)

        #listbox = tk.Listbox(self)
        #listbox.pack(pady=5)

        # Scrollable frame for task list
        container = ttk.Frame(self)
        canvas = tk.Canvas(container, bg="white", )
        canvas.pack(side="left", fill="both", expand=True)

        def on_mouse_wheel(event):
            canvas.yview_scroll(-1 * (event.delta // 120), "units")

        canvas.bind_all("<MouseWheel>", on_mouse_wheel)
        canvas.bind_all("<Button-4>", on_mouse_wheel)
        canvas.bind_all("<Button-5>", on_mouse_wheel)

        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e, canvas=canvas: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        scrollbar.pack(side="right", fill="both")

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        container.pack(fill="both", expand=True)

        # Gradle project selection section
        browse_button = ttk.Button(self, text="Select Folder", command=self.browse_folder, style="browse.TButton")
        browse_button.pack(side=tk.TOP, fill="x", pady=5)

        enerB_button = ttk.Button(self, text="Select EnergiBridge Directory", command=self.browse_folder_energibridge, style="browse.TButton")
        enerB_button.pack(side=tk.TOP, fill="x", pady=5)

        # Run Experiment button
        self.run_button = ttk.Button(self, text="Run Experiment", command=self.run_experiment_wrapper, style="run.TButton", state='disabled')
        self.run_button.pack(side=tk.TOP, fill="x", pady=10)
        
        self.label = ttk.Label(self, text="", style="TLabel")
        self.label.pack(pady=20)

    def update_label(self, text:str):
        self.label.config(text=text, foreground="#4CAF50")  # Green text


    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected :
            gradle_file = find_gradle_build(folder_selected)
            if gradle_file:
                self.label.config(text=f"Found: {gradle_file}")
                self.updateTaskList()
            else:
                self.label.config(text="gradle.build file not found")
                self.run_button.config(state='disabled')

    def browse_folder_energibridge(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            energibridge_path = find_energibridge(folder_selected)
            if energibridge_path:
                self.label.config(text=f"Found: {energibridge_path}")
                if not self.running:
                    self.run_button.config(state='normal')
            else:
                self.label.config(text="energibridge.exe not found")
                self.run_button.config(state='disabled')


    def getEnabledTasks(self):
        enabled_tasks = []
        for task, var in self.task_dict.items():
            if var.get():
                enabled_tasks.append(task)
        return enabled_tasks

    def run_experiment_wrapper(self):
        # Check if a Gradle project folder was selected
        if (self.running):
            messagebox.showerror("Input Error", "Experiment already running.")
            return

        # Retrieve values from the UI entries.
        exp_name = self.exp_name_entry.get()
        if not exp_name:
            messagebox.showerror("Input Error", "Please enter an experiment name.")
            return

        try:
            iterations = int(self.iterations_entry.get())
        except ValueError:
            messagebox.showerror("Input Error", "Number of iterations must be an integer.")
            return

        try:
            timeout_rep = float(self.timeout_rep_entry.get())
        except ValueError:
            messagebox.showerror("Input Error", "Timeout between repetitions must be a number (seconds).")
            return

        try:
            timeout_task = float(self.timeout_task_entry.get())
        except ValueError:
            messagebox.showerror("Input Error", "Timeout between tasks must be a number (seconds).")
            return

        enabled_tasks = self.getEnabledTasks()
        print(enabled_tasks)

        if enabled_tasks == []:
            messagebox.showerror("Input Error", "No tasks selected.")
            return

        warmup = bool(self.warmup_var.get())

        if (self.running):
            messagebox.showerror("Input Error", "Experiment already running.")
            return
        self.run_button.config(state='disabled')
        self.running = True
        self.update_label("Running experiment...")

        # Call the experiment logic with the provided parameters.
        threading.Thread(target=run_experiment
                        , args=(exp_name, iterations, timeout_rep, timeout_task, warmup, enabled_tasks, self.message_queue), daemon=True).start()

        self.check_result()


    def updateTaskList(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.task_dict = {}
        task_list = getTasks()
        for task in task_list:
            var = tk.IntVar(value=1)
            self.task_dict[task] = var
            chk = ttk.Checkbutton(self.scrollable_frame, text=task, variable=var, style="TCheckbutton")
            chk.pack(anchor="nw", fill="both")
        self.update_idletasks()


    def check_result(self):
        try:
            # Try to get message from queue (non-blocking)
            message = self.message_queue.get_nowait() # We can use this message later if we want. Or change the logic to show what is currently running.
            messagebox.showinfo("Experiment", "Experiment completed.")
            self.update_label("Experiment completed.")
            self.running = False
            if (self.repository):
                self.run_button.config(state='normal')
        except queue.Empty:
            # If empty, check again after 1000ms
            self.after(1000, self.check_result)






