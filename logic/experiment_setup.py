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
        if "settings.gradle" in files or "settings.gradle.kts" in files:
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


def warmup_hardware():
    """
    Simulate a hardware warmup using a Bernoulli sequence.
    For demonstration, we run a fixed number of warmup iterations,
    and each iteration randomly reports a success (simulating the Bernoulli trial).
    """
    print("Starting hardware warmup using Bernoulli sequence...")
    warmup_iterations = 10
    successes = 0
    for i in range(warmup_iterations):
        # Simulate a Bernoulli trial (p=0.5 chance for 'success')
        trial = random.random() < 0.5
        if trial:
            successes += 1
        print(f"Warmup iteration {i+1}/{warmup_iterations}: {'Success' if trial else 'Failure'}")
        time.sleep(0.5)  # short delay between warmup runs
    print(f"Hardware warmup complete with {successes}/{warmup_iterations} successful runs.\n")

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

    print("=== Experiment completed. ===")
    print(f"All results saved in: {experiment_dir}")
    message_queue.put("Experiment completed.")

    extract_and_append_summary(experiment_dir)

    return experiment_dir