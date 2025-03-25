import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import os
import platform
import subprocess
import re

from logic.experiment_setup import find_gradle_build, run_experiment
from config import ENERGIBRIDGE_PATH


root = None
repository = None
label = None
run_button = None
# Refactor out of UI
# energibridge_path = os.path.join(os.getcwd(), "energibridge", "energibridge.exe")



def update_label(text:str):
    label.config(text=text, foreground="#4CAF50")
    # label.config(text, foreground="#4CAF50")  # Green text
    
def browse_folder():
    global repository
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        gradle_file = find_gradle_build(folder_selected)
        if gradle_file:
            label.config(text=f"Found: {gradle_file}")
            repository = folder_selected
            run_button.config(state='normal')  
        else:
            label.config(text="gradle.build file not found")
            repository = None
            run_button.config(state='disabled')
            
# Refactor out of UI        
def getTasks():
    command = f"gradle build --rerun-tasks --dry-run"
    result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=repository)
    print("hi")
    regex = re.compile(r"^:(\S+) SKIPPED")
    tasks = []

    for line in result.stdout.splitlines():
        match = regex.match(line)
        if match:
            task = match.group(1) 
            print(f"Found task: {task}")
            tasks.append(task)
    return tasks

def run_experiment_wrapper():
    # Check if a Gradle project folder was selected
    if not repository:
        messagebox.showerror("Input Error", "Please select a valid Gradle project folder.")
        return

    # Retrieve values from the UI entries.
    exp_name = exp_name_entry.get()
    if not exp_name:
        messagebox.showerror("Input Error", "Please enter an experiment name.")
        return

    try:
        iterations = int(iterations_entry.get())
    except ValueError:
        messagebox.showerror("Input Error", "Number of iterations must be an integer.")
        return

    try:
        timeout_rep = float(timeout_rep_entry.get())
    except ValueError:
        messagebox.showerror("Input Error", "Timeout between repetitions must be a number (seconds).")
        return

    try:
        timeout_task = float(timeout_task_entry.get())
    except ValueError:
        messagebox.showerror("Input Error", "Timeout between tasks must be a number (seconds).")
        return

    warmup = bool(warmup_var.get())

    update_label("Starting experiment...")

    # Call the experiment logic with the provided parameters.
    run_experiment(repository, exp_name, iterations, timeout_rep, timeout_task, warmup)

    messagebox.showinfo("Experiment", "Experiment completed.")
    update_label("Experiment completed.")

    

class SettingsView(tk.Frame):
    
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        global root, label, repository, run_button
        global exp_name_entry, iterations_entry, timeout_rep_entry, timeout_task_entry, warmup_var
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
        

        main_frame = ttk.Frame(root, style="TFrame", padding=20)
        main_frame.pack(expand=True, fill="both", anchor="center")

        #Entries (fields)
        ttk.Label(self, text="Experiment Name:", style="TLabel").pack(pady=5)
        exp_name_entry = ttk.Entry(self, style="TEntry", width=30)
        exp_name_entry.pack(pady=5)

        ttk.Label(self, text="Number of Iterations:", style="TLabel").pack(pady=5)
        iterations_entry = ttk.Entry(self, style="TEntry", width=10)
        iterations_entry.pack(pady=5)

        ttk.Label(self, text="Timeout between repetitions (s):", style="TLabel").pack(pady=5)
        timeout_rep_entry = ttk.Entry(self, style="TEntry", width=10)
        timeout_rep_entry.pack(pady=5)

        ttk.Label(self, text="Timeout between tasks (s):", style="TLabel").pack(pady=5)
        timeout_task_entry = ttk.Entry(self, style="TEntry", width=10)
        timeout_task_entry.pack(pady=5)

        # Checkbox for hardware warmup
        warmup_var = tk.IntVar()
        warmup_check = ttk.Checkbutton(self, text="Perform hardware warmup", variable=warmup_var)
        warmup_check.pack(pady=5)

        # Gradle project selection section
        browse_button = ttk.Button(self, text="Select Folder", command=browse_folder, style="browse.TButton")
        browse_button.pack(side=tk.TOP, fill="x", pady=5)

        # Run Experiment button
        run_button = ttk.Button(self, text="Run Experiment", command=run_experiment_wrapper, style="run.TButton", state='disabled')
        run_button.pack(side=tk.TOP, fill="x", pady=10)
        
        
        label = ttk.Label(self, text="", style="TLabel")
        label.pack(pady=20)

        #root.mainloop()
    
    


