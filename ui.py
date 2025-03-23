import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pyuac import main_requires_admin

from logic.experiment_setup import find_gradle_build, run_experiment

root = None
repository = None
label = None
run_button = None

def update_label(text, color="#4CAF50"):
    label.config(text=text, foreground=color)

def browse_folder():
    global repository
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        gradle_file = find_gradle_build(folder_selected)
        if gradle_file:
            update_label(f"Found: {gradle_file}")
            repository = folder_selected
            run_button.config(state='normal')  
        else:
            update_label("gradle.build file not found", "#d32f2f")
            repository = None
            run_button.config(state='disabled')

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

@main_requires_admin
def main():
    global root, label, repository, run_button
    global exp_name_entry, iterations_entry, timeout_rep_entry, timeout_task_entry, warmup_var

    # Main window setup
    root = tk.Tk()
    root.title("GradleBridge")
    root.configure(bg="#f8f9fa")

    # Style configuration
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TFrame", background="#f8f9fa")
    style.configure("TLabel", font=("Arial", 14, "bold"), background="#f8f9fa", foreground="#333")
    style.configure("TEntry", font=("Arial", 12), padding=5)
    style.configure("run.TButton", font=("Arial", 12, "bold"), background="#4CAF50", foreground="white", padding=10)
    style.map("run.TButton", background=[("disabled", "#e0e0e0"), ("active", "#45a049")], foreground=[("disabled", "gray")])
    style.configure("browse.TButton", font=("Arial", 12, "bold"), background="#2196F3", foreground="white", padding=10)
    style.map("browse.TButton", background=[("active", "#1976D2")])

    main_frame = ttk.Frame(root, style="TFrame", padding=20)
    main_frame.pack(expand=True, fill="both", anchor="center")

    # Experiment configuration fields
    ttk.Label(main_frame, text="Experiment Name:", style="TLabel").pack(pady=5)
    exp_name_entry = ttk.Entry(main_frame, style="TEntry", width=30)
    exp_name_entry.pack(pady=5)

    ttk.Label(main_frame, text="Number of Iterations:", style="TLabel").pack(pady=5)
    iterations_entry = ttk.Entry(main_frame, style="TEntry", width=10)
    iterations_entry.pack(pady=5)

    ttk.Label(main_frame, text="Timeout between repetitions (s):", style="TLabel").pack(pady=5)
    timeout_rep_entry = ttk.Entry(main_frame, style="TEntry", width=10)
    timeout_rep_entry.pack(pady=5)

    ttk.Label(main_frame, text="Timeout between tasks (s):", style="TLabel").pack(pady=5)
    timeout_task_entry = ttk.Entry(main_frame, style="TEntry", width=10)
    timeout_task_entry.pack(pady=5)

    # Checkbox for hardware warmup
    warmup_var = tk.IntVar()
    warmup_check = ttk.Checkbutton(main_frame, text="Perform hardware warmup", variable=warmup_var)
    warmup_check.pack(pady=5)

    # Gradle project selection section
    browse_button = ttk.Button(main_frame, text="Select Folder", command=browse_folder, style="browse.TButton")
    browse_button.pack(side=tk.TOP, fill="x", pady=5)

    # Run Experiment button
    run_button = ttk.Button(main_frame, text="Run Experiment", command=run_experiment_wrapper, style="run.TButton", state='disabled')
    run_button.pack(side=tk.TOP, fill="x", pady=10)

    # Status label
    label = ttk.Label(main_frame, text="", style="TLabel")
    label.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()
