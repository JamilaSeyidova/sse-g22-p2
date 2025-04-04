import os
import platform
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import threading
import queue

from logic.experiment_setup import getTasks, run_experiment, set_energibridge_path, set_gradle_repository_path


class SettingsView(tk.Frame):

    repository = None
    label = None
    run_button = None
    exp_name_entry = None
    iterations_entry = None
    timeout_rep_entry = None
    timeout_task_entry = None
    command_entry = None
    warmup_var = None
    scrollable_frame = None
    vars_dict = None
    running = False
    message_queue = queue.Queue()

    HELP_TEXTS = {
         "iterations": "Repeating the experiment improves measurement reliability.\nRecommended: 30+ iterations for statistical significance.",
         "timeout_repetitions": "Rest between repetitions helps stabilize system temperature and avoids tail energy consumption.\nRecommended: 60 seconds depending on task duration and computational intesity.",
         "timeout_tasks": "Pause between tasks prevents overlap and system noise during measurements of different tasks.\nRecommended: 5 minutes depending on task duration and computational intesity.\nIn case of timeout > 120s, another warmup session is executed.",
         "warmup": "Perform a warmup run to stabilize hardware temperature avoiding bias from cooler initial runs.\nBest practice: run CPU-intensive tasks, in our case 5 minutes of Fibonacci sequence.",
         "system_precautions": 
         """ Zen Mode:
         - all applications should be closed, notifications should be turned off;
         - only the required hardware should be connected (avoid USB drives, external disks, external displays, etc.);
         - turn off notifications;
         - remove any unnecessary services running in the background (e.g., web server, file sharing, etc.);
         - if you do not need an internet or intranet connection, switch off your network;
         - prefer cable over wireless: the energy consumption from a cable connection is more stable than from a wireless connection.
         
         \nFreeze and report your settings:
         - Fix screen brightness/resolution.
         - Fix energy settings (e.g., disable screen saver, sleep mode, etc.).
 
         \nKeep it cool:
         - Run experiments in a stable-temperature room.
         - If not possible, consider logging temperature and discarding outliers."""
     }
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Style configurations
        style = ttk.Style()
        style.theme_use("clam")  # Alternative themes: "alt", "default", "classic"
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", font=("Arial", 14, "bold"), background="#f0f0f0", foreground="#333")
        style.configure("TEntry", font=("Arial", 12), padding=5)
        style.configure("run.TButton", font=("Arial", 12, "bold"), background="#4CAF50", foreground="white", padding=10)
        style.map("run.TButton", background=[("disabled", "#e0e0e0"), ("active", "#45a049")], foreground=[("disabled", "gray")])

        style.configure("browse.TButton", font=("Arial", 12, "bold"), background="#2196F3", foreground="white", padding=10, width=25)
        style.map("browse.TButton", background=[("active", "#1976D2")])

        style.configure("TCheckbutton", font=("Arial", 12), foreground="#333", background="#f0f0f0", padding=0, width=20)
        style.configure("task.TCheckbutton", font=("Arial", 12), foreground="#333", background="white", padding=0, width=20)
        style.map("task.TCheckbutton", foreground=[("!selected", "#000000"), ("selected", "#33adff")])

        style.configure("help.TButton", font=("Arial", 10, "bold"), padding=5, foreground="#ffffff", background="#2196F3", relief="flat")
        style.map("help.TButton", background=[("active", "#1976D2")], foreground=[("disabled", "gray")])

        header_frame = ttk.Frame(self, style="TFrame")
        header_frame.pack(side="top", fill="x", padx=10, pady=(10, 20))

        label = ttk.Label(header_frame, text="Settings View", font=("Helvetica", 18, "bold"), style="TLabel")
        label.pack(side="left")

        # Tips button in the header
        tips_btn = ttk.Button(header_frame, text="System Setup Tips", style="help.TButton", 
                              command=lambda: self.show_help("System Precautions", self.HELP_TEXTS["system_precautions"]))
        tips_btn.pack(side="right", padx=10)  # padx aggiunge spazio tra i due bottoni

        # Back to Home button in the header
        home_btn = ttk.Button(header_frame, text="Back to Home", command=lambda: [
                                controller.geometry("500x300"),
                                 controller.show_frame("HomeView")])
        home_btn.pack(side="right")

        # Main content frame
        main_frame = ttk.Frame(self, style="TFrame", padding=20)
        main_frame.pack(expand=True, fill="both", anchor="center")


        # Entries (fields)
        ttk.Label(self, text="Experiment Name:", style="TLabel").pack(pady=5)
        self.exp_name_entry = ttk.Entry(self, style="TEntry", width=30)
        self.exp_name_entry.pack(pady=5)
        self.exp_name_entry.insert(0, "My Experiment")
    

        frame1 = ttk.Frame(self)
        frame1.pack(pady=5)
        ttk.Label(frame1, text="Number of Iterations:", style="TLabel").pack(side="left")
        ttk.Button(frame1, text="?", width=2, style="help.TButton", command=lambda: self.show_help("Number of iterations", self.HELP_TEXTS["iterations"])).pack(side="left", padx=5)
        self.iterations_entry = ttk.Entry(self, style="TEntry", width=30, validate="key", validatecommand=(self.register(lambda P: P.isdigit() or P == ""), "%P"))
        self.iterations_entry.pack(pady=5)
        self.iterations_entry.insert(0, "30")

        frame1 = ttk.Frame(self)
        frame1.pack(pady=5)
        ttk.Label(frame1, text="Timeout between repetitions (s):", style="TLabel").pack(side="left")
        ttk.Button(frame1, text="?", width=2, style="help.TButton", command=lambda: self.show_help("Timeout between repetitions (s)", self.HELP_TEXTS["timeout_repetitions"])).pack(side="left", padx=5)
        self.timeout_rep_entry = ttk.Entry(self, style="TEntry", width=30, validate="key", validatecommand=(self.register(lambda P: P.isdigit() or P == ""), "%P"))
        self.timeout_rep_entry.pack(pady=5)
        self.timeout_rep_entry.insert(0, "60")

        frame1 = ttk.Frame(self)
        frame1.pack(pady=5)
        ttk.Label(frame1, text="Timeout between tasks (s):", style="TLabel").pack(side="left")
        ttk.Button(frame1, text="?", width=2, style="help.TButton", command=lambda: self.show_help("Timeout between tasks (s)", self.HELP_TEXTS["timeout_tasks"])).pack(side="left", padx=5)
        self.timeout_task_entry = ttk.Entry(self, style="TEntry", width=30, validate="key", validatecommand=(self.register(lambda P: P.isdigit() or P == ""), "%P"))
        self.timeout_task_entry.pack(pady=5)
        self.timeout_task_entry.insert(0, "300")
        
        frame1 = ttk.Frame(self)
        frame1.pack(pady=5)
        ttk.Label(frame1, text="Gradle task", style="TLabel").pack(side="left")
        #ttk.Button(frame1, text="?", width=2, style="help.TButton", command=lambda: self.show_help("Timeout between tasks (s)", self.HELP_TEXTS["timeout_tasks"])).pack(side="left", padx=5)

        frame2 = ttk.Frame(self)
        frame2.pack(pady=5)
        self.command_entry = ttk.Entry(frame2, style="TEntry", width=30)
        self.command_entry.pack(pady=6, side="left")
        self.command_entry.insert(0, "build")
        ttk.Button(frame2, text="Refresh", width=7, style="help.TButton", command=lambda: self.updateTaskList()).pack(side="right", padx=5)

        frame3 = ttk.Frame(self)
        frame3.pack(pady=5)

        self.filter_entry = ttk.Entry(frame3, style="TEntry", width=30)
        self.filter_entry.pack(pady=6, side="left")
        self.filter_entry.insert(0, "*")  # Wildcard by default

        ttk.Button(frame3, text="Filter", width=7, style="help.TButton", command=lambda: self.updateTaskList()).pack(
            side="right", padx=5)

        # Checkbox for hardware warmup
        self.warmup_var = tk.IntVar()
        warmup_frame = ttk.Frame(self)
        warmup_frame.pack(pady=5)
        self.warmup_check = ttk.Checkbutton(warmup_frame, text="Perform hardware warmup ", variable=self.warmup_var)
        self.warmup_check.pack(side="left")
        ttk.Button(warmup_frame, text="?", width=2, style="help.TButton", command=lambda: self.show_help("Warmup", self.HELP_TEXTS["warmup"])).pack(side="left", padx=5)
        
        buttons_frame = ttk.Frame(self)
        buttons_frame.pack(side=tk.TOP, pady=5)

        # EnergiBridge directory selection button
        enerB_button = ttk.Button(buttons_frame, text="Select EnergiBridge Directory", 
                                  command=self.browse_folder_energibridge, style="browse.TButton")
        enerB_button.pack(side=tk.LEFT, padx=(0, 5))

        # Gradle project selection button
        browse_button = ttk.Button(buttons_frame, text="Select Gradle Project", 
                                  command=self.browse_folder, style="browse.TButton")
        browse_button.pack(side=tk.LEFT)

        # Run Experiment button
        self.run_button = ttk.Button(self, text="Run Experiment", command=self.run_experiment_wrapper, style="run.TButton", state='disabled')
        self.run_button.pack(side=tk.TOP, fill="x", pady=10)

        # Scrollable frame for task list
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True, pady=10)

        canvas = tk.Canvas(container, bg="white", highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        self.scrollable_frame = ttk.Frame(canvas)

        # Make the scroll region adapt to content
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # container.pack(fill="both", expand=True) 

        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        
        self.label = ttk.Label(self, text="", style="TLabel")
        self.label.pack(pady=20)

    def update_label(self, text:str):
        self.label.config(text=text, foreground="#4CAF50")  # Green text

    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select a Gradle project folder")
        if folder:
            for fname in ["build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts"]:
                candidate = os.path.join(folder, fname)
                if os.path.isfile(candidate):
                    set_gradle_repository_path(folder)
                    self.repository = candidate
                    self.label.config(text=f"Found: {os.path.basename(candidate)}")
                    self.run_button.config(state='normal')
                    self.updateTaskList()
                    return
            self.label.config(text="No valid Gradle file found in selected folder")
            self.run_button.config(state='disabled')
        else:
            self.label.config(text="No folder selected")
            self.run_button.config(state='disabled')

    # def browse_folder_energibridge(self):
    #     energibridge_path = filedialog.askopenfilename(title="Pick a file in the target folder", filetypes=[("Executables", "*.exe;*.out;*.sh;"), ("All files", "*.*")])
    #     energibridge_path = set_energibridge_path(energibridge_path)
    #     if energibridge_path:
    #         self.label.config(text=f"Found: {energibridge_path}")
    #         if not self.running:
    #             self.run_button.config(state='normal')
    #     else:
    #         self.label.config(text="energibridge.exe not found")
    #         self.run_button.config(state='disabled')


    def find_energibridge_executable(self, folder_path):
        """Search for energibridge executable in the selected folder."""
        candidates = ["energibridge", "energibridge.exe", "energibridge.sh", "energibridge.out"]

        for filename in os.listdir(folder_path):
            full_path = os.path.join(folder_path, filename)
            if filename.lower() in candidates and os.path.isfile(full_path):
                if platform.system() == "Windows":
                    if filename.lower().endswith((".exe", ".bat", ".cmd")):
                        return full_path
                else:
                    if os.access(full_path, os.X_OK):
                        return full_path
        return None

    def browse_folder_energibridge(self):
        folder_path = filedialog.askdirectory(
            title="Select the folder containing energibridge"
        )

        if folder_path:
            executable_path = self.find_energibridge_executable(folder_path)
            if executable_path:
                executable_path = set_energibridge_path(executable_path)
                self.label.config(text=f"Found: {executable_path}")
                if not self.running:
                    self.run_button.config(state='normal')
            else:
                self.label.config(text="energibridge executable not found in folder")
                self.run_button.config(state='disabled')
        else:
            self.label.config(text="No folder selected")
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
        if self.repository is None:
            messagebox.showerror("Error", "Please select a Gradle project folder.")
            return

        # Clear current checkboxes
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.task_dict = {}
        task_list = getTasks(self.command_entry.get())
        filter_text = self.filter_entry.get().strip().lower()

        for task in task_list:
            var = tk.IntVar(value=0)  # Default deselected

            # Auto-select tasks matching filter
            if not filter_text or filter_text == "*" or filter_text in task.lower():
                var.set(1)

            self.task_dict[task] = var
            chk = ttk.Checkbutton(self.scrollable_frame, text=task, variable=var, style="task.TCheckbutton")
            chk.pack(anchor="nw", fill="both")

        self.update_idletasks()

        if not self.running:
            self.run_button.config(state='normal')

        if len(task_list) == 0:
            messagebox.showerror("Input Error", "No tasks found")

    def check_result(self):
        try:
            # Try to get message from queue (non-blocking)
            message = self.message_queue.get_nowait() # We can use this message later if we want. Or change the logic to show what is currently running.
            messagebox.showinfo("Experiment", "Experiment completed.")
            self.update_label("Experiment completed.")
            #self.run_button.config(state='normal')
            self.running = False
            if (self.repository):
                self.run_button.config(state='normal')
        except queue.Empty:
            # If empty, check again after 1000ms
            self.after(1000, self.check_result)

    def show_help(self, title, message):
        help_window = tk.Toplevel(self)
        help_window.title(title)
        help_window.resizable(True, True)

        # Create text widget first without packing
        text = tk.Text(help_window, wrap="word", padx=10, pady=10, font=("Arial", 14))
        text.insert("1.0", message)
        text.config(state="disabled")  # Make read-only

        # Calculate needed size based on content
        # Get the text dimensions
        text.update_idletasks()
        lines = message.count('\n') + 1
        max_line_length = max([len(line) for line in message.split('\n')])

        # Estimate window size based on content
        width = min(1000, max(300, max_line_length * 15)) # 15 pixels per character
        height = min(1000, max(100, lines * 30 )) # 30 pixels per line

        # Set window size
        help_window.geometry(f"{width}x{height}")

        # Pack the text widget
        text.pack(expand=True, fill="both")

        # Center the window
        help_window.update_idletasks()
        screen_width = help_window.winfo_screenwidth()
        screen_height = help_window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        help_window.geometry(f"+{x}+{y}")