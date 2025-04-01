# logic/experiment_summary.py

import os
import pandas as pd

import global_vars

def get_summary_csv_path():
    if global_vars.PROJECT_REPOSITORY_PATH is None:
            print('Summary CSV not available, project folder is not selected')
            return
    return os.path.join(global_vars.PROJECT_REPOSITORY_PATH, 'experiment_results', 'aggregated', 'all_experiments_summary.csv')


def compute_cpu_energy_from_csv(csv_path, idle_path):
    try:
        df = pd.read_csv(csv_path, nrows=1)
        columns = df.columns

        if "PACKAGE_ENERGY (J)" in columns or "CPU_ENERGY (J)" in columns:
            return compute_cpu_energy_direct(csv_path, idle_path)
            #return compute_cpu_energy_direct(csv_path)
        elif "SYSTEM_POWER (Watts)" in columns or "CPU_POWER (Watts)" in columns:
            return compute_cpu_energy_from_power(csv_path, idle_path)
            #return compute_cpu_energy_from_power(csv_path)
        else:
            raise NotImplementedError #should it be not implemented or metric not found?
    except Exception as e:
        print(f"Failed to compute CPU energy from {csv_path}: {e}")
        return None

#def compute_cpu_energy_direct(csv_path):
def compute_cpu_energy_direct(csv_path, idle_path):
    df = pd.read_csv(csv_path)
    col = "PACKAGE_ENERGY (J)" if "PACKAGE_ENERGY (J)" in df.columns else "CPU_ENERGY (J)"
    raw_energy = df[col].iloc[-1] - df[col].iloc[0]
    run_time = (df.iloc[-1]['Time'] - df.iloc[0]['Time']) / 1_000
    energy_consumed = compute_idle_energy_compensation(idle_path, run_time, raw_energy)
    return energy_consumed
    #return df[col].iloc[-1] - df[col].iloc[0]

def compute_cpu_energy_from_power(csv_path, idle_path):
    df = pd.read_csv(csv_path)
    power_col = "SYSTEM_POWER (Watts)" if "SYSTEM_POWER (Watts)" in df.columns else "CPU_POWER (Watts)"
    df["Delta_seconds"] = df["Delta"] / 1_000_000
    df["Energy_Joules"] = df[power_col] * df["Delta_seconds"]
    energy_consumed = compute_idle_energy_compensation(idle_path, df["Delta_seconds"].sum(), df["Energy_Joules"].sum())
    return energy_consumed
    #return df["Energy_Joules"].sum()

def compute_ram_energy_from_csv(csv_path):
    try:
        df = pd.read_csv(csv_path)
        if "DRAM_ENERGY (J)" in df.columns:
            return df["DRAM_ENERGY (J)"].iloc[-1] - df["DRAM_ENERGY (J)"].iloc[0]
        elif "USED_MEMORY" in df.columns:
            return -1 #Mac does not have ram energy metric
        else:
            raise NotImplementedError
    except Exception as e:
        print(f"Failed to compute RAM energy from {csv_path}: {e}")
        return None

def compute_idle_energy_compensation(csv_path, task_run_time, task_energy):
    try:
        df = pd.read_csv(csv_path)
        col = "PACKAGE_ENERGY (J)" if "PACKAGE_ENERGY (J)" in df.columns else "CPU_ENERGY (J)"
        total_idle_energy = df[col].iloc[-1] - df[col].iloc[0]
        idle_time = (df.iloc[-1]['Time'] - df.iloc[0]['Time']) / 1_000
        print(f"Idle time: {idle_time} seconds")
        idle_task_consumption = total_idle_energy * (task_run_time / idle_time)
        #print(f"\nTotal idle energy: {total_idle_energy} Joules")
        #print(f"Task run time: {task_run_time} seconds")
        #print(f"Task energy: {task_energy} Joules")
        #print(f"Idle task consumption: {idle_task_consumption} Joules\n")
        return task_energy - idle_task_consumption
    except Exception as e:
        print(f"Failed to read {csv_path}: {e}")
        return None
        

def get_latest_experiment_folder(base_dir="experiment_results"):
    folders = [
        d for d in os.listdir(base_dir)
        if os.path.isdir(os.path.join(base_dir, d))
    ]
    folders.sort(key=lambda name: name.split("_")[-1], reverse=True)
    return os.path.join(base_dir, folders[0]) if folders else None

def extract_and_append_summary(experiment_path):
    summary_csv = get_summary_csv_path()

    if not experiment_path:
        print("No experiment folders found.")
        return

    experiment_name = get_experiment_name(experiment_path)
    data = []

    print(f'Extracting results from `{experiment_path}`...')
    task_folders = [
        os.path.join(experiment_path, f)
        for f in os.listdir(experiment_path)
        if os.path.isdir(os.path.join(experiment_path, f))
    ]
    task_folders = sorted(task_folders, key=os.path.getctime)

    print(f"Found {len(task_folders)} task folders.")
    for task_folder in task_folders:
        task_path = os.path.join(experiment_path, task_folder)
        if not os.path.isdir(task_path):
            continue
        
        task_name = get_task_name(task_folder)

        for run_folder in os.listdir(task_path):
            run_path = os.path.join(task_path, run_folder)
            csv_file = os.path.join(run_path, "results.csv")
            if os.path.exists(csv_file):
                try:
                    #cpu = compute_cpu_energy_from_csv(csv_file)
                    cpu = compute_cpu_energy_from_csv(csv_file, os.path.join(experiment_path, "idle_consumption.csv"))
                    ram = compute_ram_energy_from_csv(csv_file)

                    run_number = int(run_folder)
                    data.append({
                        "Experiment": experiment_name,
                        "Task": task_name,
                        "Run": run_number,
                        "CPU Energy": cpu,
                        "RAM Energy": ram
                    })
                except Exception as e:
                    print(f"Error reading {csv_file}: {e}")

    df = pd.DataFrame(data)
    if not df.empty:
        if os.path.exists(summary_csv):
            df.to_csv(summary_csv, mode='a', header=False, index=False)
        else:
            df.to_csv(summary_csv, index=False)
        print(f"Appended {len(df)} rows to {summary_csv}")
    else:
        print("No valid results found in latest experiment.")

def get_experiment_name(path_to_experiment_folder):
    experiment_name = os.path.basename(path_to_experiment_folder)
    return experiment_name

def get_task_name(path_to_task_folder):
    task_name = os.path.basename(path_to_task_folder)
    return task_name
        
def aggregate_all_results():
    if global_vars.PROJECT_REPOSITORY_PATH is None:
            print('Project folder is not selected, not updating data')
            return
    
    experiments_folder = os.path.join(global_vars.PROJECT_REPOSITORY_PATH, 'experiment_results')
    csv_path = get_summary_csv_path()
    
    df = pd.read_csv(csv_path)
    
    for f in os.listdir(experiments_folder):
        experiment_path = os.path.join(experiments_folder, f)
        experiment_name = get_experiment_name(experiment_path)
        if os.path.isdir(experiment_path) and experiment_name not in df['Experiment'].values and experiment_name != 'aggregated':
            extract_and_append_summary(experiment_path)
    
    
