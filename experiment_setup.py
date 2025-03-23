import subprocess
import re
import os
import time
import datetime
import random

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

#def run_task(task, repository, output_dir):
#    """
#    Placeholder function to simulate running a single task.
#    Replace or extend this function with the actual experiment code.
#    """
#    print(f"Running task: {task}\n")
#    command = f"{energibridge_path} -o {output_dir} --summary cmd /c \"gradle {task}\""
#    result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=repository)
#    print(result)
#    print(f"Finished task: {task}\n")

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

def run_experiment(repository, experiment_name, iterations, timeout_between_repetitions, timeout_between_tasks, warmup):
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
    tasks = getTasks(repository)
    
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
    
    return experiment_dir



#def runTasks(tasks, repository):
#    for task in tasks:
#        print(f"Running task: {task}")
#        
#        #command = f"{energibridge_path} --summary cmd /c \"gradle {task}\" --iterations {iterations_entry.get()} --sleep {sleep_entry.get()} --interval {interval_entry.get()}"
#        command = f"{energibridge_path} -o  --summary cmd /c \"gradle {task}\""
#        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=repository)
#        print(result)
#            
#            
#def runTasks(tasks, repository, iterations=1, sleep=0, interval=0):
#    # Crea una directory principale per l'esperimento con timestamp
#    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
#    experiment_dir = os.path.join(os.getcwd(), "results", f"experiment_{timestamp}")
#    
#    # Assicurati che la directory principale esista
#    os.makedirs(experiment_dir, exist_ok=True)
#    
#    results = []
#    
#    for task in tasks:
#        print(f"Running task: {task}")
#        
#        # Crea una directory specifica per il task
#        task_dir = os.path.join(experiment_dir, task.replace(':', '_'))
#        os.makedirs(task_dir, exist_ok=True)
#        
#        # Aggiorna il comando per salvare l'output nella directory del task
#        # L'opzione -o di energibridge specifica la directory di output
#        command = f"{energibridge_path} -o {task_dir} --summary cmd /c \"gradle {task}\""
#        
#        print(f"Executing: {command}")
#        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=repository)
#        print(result)
#        
#        # Salva i risultati del comando in un file di log nel task_dir
#        with open(os.path.join(task_dir, "command_output.log"), "w") as f:
#            f.write(f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}")
#        
#        results.append({
#            "task": task,
#            "directory": task_dir,
#            "output": result.stdout,
#            "error": result.stderr,
#            "return_code": result.returncode
#        })
#    
#    # Crea un file di riepilogo dell'esperimento
#    with open(os.path.join(experiment_dir, "experiment_summary.txt"), "w") as f:
#        f.write(f"Experiment run at: {timestamp}\n")
#        f.write(f"Tasks executed: {len(tasks)}\n")
#        f.write(f"Parameters: iterations={iterations}, sleep={sleep}, interval={interval}\n\n")
#        
#        for i, task_result in enumerate(results):
#            f.write(f"Task {i+1}: {task_result['task']}\n")
#            f.write(f"  Directory: {task_result['directory']}\n")
#            f.write(f"  Return code: {task_result['return_code']}\n\n")
#    
#    print(f"Experiment results saved in: {experiment_dir}")
#    return results, experiment_dir