# logic/experiment_summary.py

import os
import pandas as pd


def compute_cpu_energy_from_csv(csv_path):
    try:
        df = pd.read_csv(csv_path, nrows=1)
        columns = df.columns

        if "PACKAGE_ENERGY (J)" in columns or "CPU_ENERGY (J)" in columns:
            return compute_cpu_energy_direct(csv_path)
        elif "SYSTEM_POWER (Watts)" in columns or "CPU_POWER (Watts)" in columns:
            return compute_cpu_energy_from_power(csv_path)
        else:
            raise NotImplementedError #should it be not implemented or metric not found?
    except Exception as e:
        print(f"Failed to compute CPU energy from {csv_path}: {e}")
        return None


def compute_cpu_energy_direct(csv_path):
    df = pd.read_csv(csv_path)
    col = "PACKAGE_ENERGY (J)" if "PACKAGE_ENERGY (J)" in df.columns else "CPU_ENERGY (J)"
    return df[col].iloc[-1] - df[col].iloc[0]

def compute_cpu_energy_from_power(csv_path):
    df = pd.read_csv(csv_path)
    power_col = "SYSTEM_POWER (Watts)" if "SYSTEM_POWER (Watts)" in df.columns else "CPU_POWER (Watts)"
    df["Delta_seconds"] = df["Delta"] / 1_000_000
    df["Energy_Joules"] = df[power_col] * df["Delta_seconds"]
    return df["Energy_Joules"].sum()

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



def get_latest_experiment_folder(base_dir="experiment_results"):
    folders = [
        d for d in os.listdir(base_dir)
        if os.path.isdir(os.path.join(base_dir, d))
    ]
    folders.sort(key=lambda name: name.split("_")[-1], reverse=True)
    return os.path.join(base_dir, folders[0]) if folders else None

def extract_and_append_summary(latest_exp_path, summary_csv="results/all_experiments_summary.csv"):
    if not latest_exp_path:
        print("No experiment folders found.")
        return

    experiment_name = os.path.basename(latest_exp_path)
    data = []

    for task_folder in os.listdir(latest_exp_path):
        task_path = os.path.join(latest_exp_path, task_folder)
        if not os.path.isdir(task_path):
            continue
        task_name = task_folder.replace("_", ":")

        for run_folder in os.listdir(task_path):
            run_path = os.path.join(task_path, run_folder)
            csv_file = os.path.join(run_path, "results.csv")
            if os.path.exists(csv_file):
                try:
                    cpu = compute_cpu_energy_from_csv(csv_file)
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
