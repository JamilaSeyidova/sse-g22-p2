import subprocess
import re
import os
import time
import datetime
import random
import threading
import queue

energibridge_path = os.path.join(os.getcwd(), "energibridge", "energibridge.exe")

def find_gradle_build(folder):
    for root, _, files in os.walk(folder):
        if "build.gradle" in files or "build.gradle.kts" in files:
            return os.path.join(root, "build.gradle") if "build.gradle" in files else os.path.join(root, "build.gradle.kts")
    return None


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

def getTasks(repository: str):
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


def run_task(task, repository, output_dir):
    """
    Runs a single task and saves results to the specified output directory.
    """
    print(f"Running task: {task}\n Output directory: {output_dir}")
    
    # Assicurati che la directory esista
    os.makedirs(output_dir, exist_ok=True)
    
    # Normalizza il percorso usando solo backslash per Windows
    normalized_output_dir = output_dir.replace('/', '\\')
    print(f"Normalized output directory: {normalized_output_dir}")
    
    # Usa citazioni per percorsi con spazi
    command = f'"{energibridge_path}" -o "{normalized_output_dir}\\results.csv" --summary cmd /c "gradle {task}"'
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=repository)
        
        # Salva l'output in un file di log
        with open(os.path.join(output_dir, "command_output.log"), "w") as f:
            f.write(f"COMMAND: {command}\n\n")
            f.write(f"STDOUT:\n{result.stdout}\n\n")
            f.write(f"STDERR:\n{result.stderr}\n\n")
            f.write(f"RETURN CODE: {result.returncode}")
        
        print(result)
        print(f"Finished task: {task}\n")
        return result
    except Exception as e:
        print(f"Error running task: {str(e)}")
        return None
    


def run_experiment(repository, experiment_name, iterations, timeout_between_repetitions, timeout_between_tasks, warmup, tasks, message_queue):
    """
    Run an experiment with the given configuration.
    """
    # Crea un timestamp per l'esperimento
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Crea la directory principale dell'esperimento
    base_dir = os.path.join(repository, "experiment_results")  # Salva in repository
    experiment_dir = os.path.join(base_dir, f"{experiment_name}_{timestamp}")
    os.makedirs(base_dir, exist_ok=True)  # Crea la directory base se non esiste
    os.makedirs(experiment_dir, exist_ok=True)
    
    print(f"=== Starting Experiment: {experiment_name} ===\n")
    print(f"Results will be saved in: {experiment_dir}\n")
    
    # Perform warmup if required
    if warmup:
        warmup_hardware()
    
    # Get tasks from the repository
    #tasks = getTasks(repository)
    
    # Run experiments for each task
    for task in tasks:
        # Sostituisci i caratteri non validi nei nomi delle directory
        task_dir_name = task.replace(':', '_')
        task_dir = os.path.join(experiment_dir, task_dir_name)
        os.makedirs(task_dir, exist_ok=True)
        
        print(f"--- Experiment for task: {task} ---")
        
        for i in range(iterations):
            iteration_number = i + 1
            # Crea una directory specifica per l'iterazione
            iteration_dir = os.path.join(task_dir, f"iterazione{iteration_number}")
            os.makedirs(iteration_dir, exist_ok=True)
            
            print(f"Iteration {iteration_number}/{iterations} for task: {task}")
            
            # Esegui il task e salva i risultati nella directory dell'iterazione
            run_task(task, repository, iteration_dir)
            
            print(f"Waiting {timeout_between_repetitions} seconds for tail energy to settle...\n")
            time.sleep(timeout_between_repetitions)
        
        print(f"Completed all {iterations} iterations for task: {task}.")
        print(f"Waiting {timeout_between_tasks} seconds before moving to the next task...\n")
        time.sleep(timeout_between_tasks)
    
    print("=== Experiment completed. ===")
    print(f"All results saved in: {experiment_dir}")
    message_queue.put("Experiment completed.")
    return experiment_dir