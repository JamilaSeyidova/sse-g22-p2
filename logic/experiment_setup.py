import subprocess
import re
import os
import time
import datetime
import random

from logic.experiment_summary import extract_and_append_summary

def find_gradle_build(folder):
    global repository
    for root, _, files in os.walk(folder):
        if "build.gradle" in files or "build.gradle.kts" in files or "settings.gradle" in files or "settings.gradle.kts" in files:
            repository = root
            return repository
    return None


def find_energibridge(folder):
    global energibridge_path
    target_name = "energibridge.exe" if os.name == "nt" else "energibridge"

    for root, _, files in os.walk(folder):
        if target_name in files:
            energibridge_path = os.path.join(root, target_name)
            return energibridge_path  # Already OS-appropriate
    return None

def build_gradle_and_clean_commands(energibridge_path, output_dir, task):
    output_file = os.path.join(output_dir, "results.csv")

    gradle_command = f'gradle {task}'

    if os.name == 'nt':
        shell_command = f'cmd /c "{gradle_command}"'
        clean_command = 'cmd /c "gradle clean"'
    else:
        shell_command = f'sh -c \'{gradle_command}\''
        clean_command = 'sh -c \'gradle clean\''

    full_command = f'"{energibridge_path}" -o "{output_file}" --summary {shell_command}'
    return full_command, clean_command


def warmup_hardware(duration=300):
    """
    Warm up the hardware by calculating Fibonacci numbers for 5 minutes.
    This creates a CPU load that stabilizes the system before experiments.
    """
    print(f"Starting hardware warmup using Fibonacci sequence for {duration} seconds...")
    
    def fibonacci(n):
        if n <= 1:
            return n
        return fibonacci(n-1) + fibonacci(n-2)
    
    start_time = time.time()
    end_time = start_time + duration
    iterations = 0
    last_report_time = start_time
    
    while time.time() < end_time:
        # Calculate a Fibonacci number (using small values to avoid excessive computation)
        n = iterations % 30  # Keep n reasonably small to avoid long calculations
        fib_result = fibonacci(n)
        iterations += 1
        
        # Report progress every 10 seconds
        current_time = time.time()
        if current_time - last_report_time >= 30:
            elapsed = current_time - start_time
            remaining = end_time - current_time
            print(f"Warmup progress: {elapsed:.1f}s elapsed, {remaining:.1f}s remaining, {iterations} iterations completed")
            last_report_time = current_time
    
    total_time = time.time() - start_time
    print(f"Hardware warmup complete after {total_time:.2f} seconds with {iterations} Fibonacci calculations.\n")
    time.sleep(60)

def idle_consumption(output_file):
    """
    Measure the idle consumption of the system for 60s.
    """
    gradle_command = f'"{energibridge_path}" -o "{output_file}" --summary timeout /T 60'
    result = subprocess.run(gradle_command, shell=True, capture_output=True, text=True, cwd=repository)
    print(f"Idle consumption measured for 60 seconds. Output saved to {output_file}.")
    return result


def getTasks(cmd="build"):
    command = f"gradle {cmd} --rerun-tasks --dry-run"
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


def run_task(task, output_dir):
    """
    Runs a single task and saves results to the specified output directory.
    """
    print(f"Running task: {task}\n Output directory: {output_dir}")

    os.makedirs(output_dir, exist_ok=True)

    gradle_command, clean_command = build_gradle_and_clean_commands(energibridge_path, output_dir, task)

    try:
        subprocess.run(clean_command, shell=True, capture_output=True, text=True, cwd=repository)

        result = subprocess.run(gradle_command, shell=True, capture_output=True, text=True, cwd=repository)

        # Save the command output to a log file
        with open(os.path.join(output_dir, "command_output.log"), "w") as f:
            f.write(f"COMMAND: {gradle_command}\n\n")
            f.write(f"STDOUT:\n{result.stdout}\n\n")
            f.write(f"STDERR:\n{result.stderr}\n\n")
            f.write(f"RETURN CODE: {result.returncode}")

        print(result)
        print(f"Finished task: {task}\n")
        return result
    except Exception as e:
        print(f"Error running task: {str(e)}")
        return None


def run_experiment(experiment_name, iterations, timeout_between_repetitions, timeout_between_tasks, warmup, tasks, message_queue):
    """
    Run an experiment with the given configuration.
    """
    # Create a timestamp for the experiment
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Crea la directory principale dell'esperimento
    base_dir = os.path.join(repository, "experiment_results")  # Base directory for all experiments
    experiment_dir = os.path.join(base_dir, f"{experiment_name}_{timestamp}")
    os.makedirs(base_dir, exist_ok=True)  # Create base directory if it doesn't exist
    os.makedirs(experiment_dir, exist_ok=True)

    print(f"=== Starting Experiment: {experiment_name} ===\n")
    print(f"Results will be saved in: {experiment_dir}\n")

    idle_energy_result = idle_consumption(os.path.join(experiment_dir, "idle_consumption.csv"))
    print("Idle consumption measurement completed.\n Results: \n", idle_energy_result)

    # Perform warmup if required
    if warmup:
        warmup_hardware()

    # Run experiments for each task
    for task in tasks:
        task_dir_name = task.replace(':', '_')
        task_dir = os.path.join(experiment_dir, task_dir_name)
        os.makedirs(task_dir, exist_ok=True)

        print(f"--- Experiment for task: {task} ---")

        for i in range(iterations):
            iteration_number = i + 1
            # Create a directory for the current iteration
            iteration_dir = os.path.join(task_dir, f"{iteration_number}")
            os.makedirs(iteration_dir, exist_ok=True)

            print(f"Iteration {iteration_number}/{iterations} for task: {task}")

            # Execute task
            run_task(task, iteration_dir)

            print(f"Waiting {timeout_between_repetitions} seconds for tail energy to settle...\n")
            time.sleep(timeout_between_repetitions)

        print(f"Completed all {iterations} iterations for task: {task}.")
        print(f"Waiting {timeout_between_tasks} seconds before moving to the next task...\n")
        time.sleep(timeout_between_tasks)
        if timeout_between_tasks > 120:
            print("Hardware warmup after long pause.")
            warmup_hardware(120)

    print("=== Experiment completed. ===")
    print(f"All results saved in: {experiment_dir}")
    message_queue.put("Experiment completed.")

    extract_and_append_summary(experiment_dir)

    return experiment_dir