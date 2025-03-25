# logic/experiment_summary.py

import os
import pandas as pd

from config import CPU_TYPE, SYSTEM


def compute_energy_from_csv(csv_path):
    if SYSTEM == "Darwin":
        if CPU_TYPE == "Intel":
            return compute_energy_macos_intel(csv_path)
        else:
            raise NotImplementedError
    if SYSTEM == "Windows":
        if CPU_TYPE == "m1": #idk ask to check name of the cpu
            return NotImplementedError
            # return compute_energy_windows_m1(csv_path)
        if CPU_TYPE == "Intel":
            return compute_energy_windows_intel(csv_path)
        else:
            raise NotImplementedError
    else:
        raise NotImplementedError


def compute_energy_macos_intel(csv_path):
    try:
        df = pd.read_csv(csv_path)

        if df.empty:
            raise ValueError("CSV is empty")

        for col in ["Delta", "SYSTEM_POWER (Watts)", "USED_MEMORY"]:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")

        df['Delta_seconds'] = df['Delta'] / 1_000_000
        df['Energy_Joules'] = df['SYSTEM_POWER (Watts)'] * df['Delta_seconds']
        cpu_energy = df['Energy_Joules'].sum()

        avg_used_mem_bytes = df['USED_MEMORY'].mean()
        ram_energy = (avg_used_mem_bytes / 1e9) * 0.372

        return cpu_energy, ram_energy

    except Exception as e:
        print(f"Error parsing {csv_path}: {e}")
        return None  # ← this avoids unpacking crash

def compute_energy_windows_intel(csv_path):
    try:
        df = pd.read_csv(csv_path)

        if df.empty:
            raise ValueError("CSV is empty")

        for col in ["DRAM_ENERGY (J)", "PACKAGE_ENERGY (J)"]:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")

        # CPU energy = max - min of PACKAGE_ENERGY (J)
        cpu_energy = df["PACKAGE_ENERGY (J)"].iloc[-1] - df["PACKAGE_ENERGY (J)"].iloc[0]

        # RAM energy = max - min of DRAM_ENERGY (J)
        ram_energy = df["DRAM_ENERGY (J)"].iloc[-1] - df["DRAM_ENERGY (J)"].iloc[0]

        return cpu_energy, ram_energy

    except Exception as e:
        print(f"Error parsing {csv_path} on Windows Intel: {e}")
        return None

def get_latest_experiment_folder(base_dir="experiment_results"):
    folders = [
        d for d in os.listdir(base_dir)
        if os.path.isdir(os.path.join(base_dir, d))
    ]
    folders.sort(key=lambda name: name.split("_")[-1], reverse=True)
    return os.path.join(base_dir, folders[0]) if folders else None

def extract_and_append_summary(latest_exp_path, summary_csv="all_experiments_summary.csv"):
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
                    cpu, ram = compute_energy_from_csv(csv_file)
                    run_number = int(run_folder.replace("iterazione", ""))
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
