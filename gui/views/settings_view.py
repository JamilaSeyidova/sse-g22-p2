import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

import os
import subprocess
import re

root = None
repository = None
label = None
run_button = None
# Refactor out of UI
energibridge_path = os.path.join(os.getcwd(), "energibridge", "energibridge.exe")



def update_label():
    label.config(text=f"Running energibridge...", foreground="#4CAF50")  # Green text
    
# Refactor out of UI
def find_gradle_build(folder):
    for root, _, files in os.walk(folder):
        if "build.gradle" in files or "build.gradle.kts" in files:
            return os.path.join(root, "build.gradle") if "build.gradle" in files else os.path.join(root, "build.gradle.kts")
    return None
    
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
# Refactor out of UI
def runTasks(tasks):
    for task in tasks:
        print(f"Running task: {task}")
        #command = f"{energibridge_path} --summary cmd /c \"gradle {task}\" --iterations {iterations_entry.get()} --sleep {sleep_entry.get()} --interval {interval_entry.get()}"
        command = f"{energibridge_path} --summary cmd /c \"gradle {task}\""
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=repository)
        print(result)
            
            
def runBridge():
    tasks = getTasks()
    runTasks(tasks)
    update_label()
    

class SettingsView(tk.Frame):
    
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        global root, label, repository, run_button
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
        ttk.Label(self, text="Iterations:", style="TLabel").pack(pady=5)
        iterations_entry = ttk.Entry(self, style="TEntry")
        iterations_entry.pack(pady=5)

        ttk.Label(self, text="Sleep (seconds):", style="TLabel").pack(pady=5)
        sleep_entry = ttk.Entry(self, style="TEntry")
        sleep_entry.pack(pady=5)

        ttk.Label(self, text="Interval (seconds):", style="TLabel").pack(pady=5)
        interval_entry = ttk.Entry(self, style="TEntry")
        interval_entry.pack(pady=5)

        #Buttons
        browse_button = ttk.Button(self, text="Select Folder", command=browse_folder, style="browse.TButton")
        browse_button.pack(side=tk.LEFT, expand=True)
        
        run_button = ttk.Button(self, text="Run", command=runBridge, style="run.TButton", state='disabled')
        run_button.pack(side=tk.LEFT, expand=True)

        
        
        label = ttk.Label(self, text="", style="TLabel")
        label.pack(pady=20)

        #root.mainloop()
    
    


