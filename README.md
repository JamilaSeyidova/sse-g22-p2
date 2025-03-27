sse-g22-p2


## 🛠 Project Setup

This is a Python project managed with [UV](https://astral.sh/blog/uv/), a fast Python package and project manager.

### Step 1 – Install UV

```bash
# MacOS & Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Step 2 – Set Up the Project Environment

Create and activate a virtual environment, and install all dependencies:

```bash
uv sync

# MacOS & Linux
source .venv/bin/activate

# Windows (CMD)
.venv\Scripts\activate.bat

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

---

## ⚡ EnergyBridge Setup (Required for Energy Measurement)

This tool relies on **[EnergyBridge](https://github.com/tdurieux/EnergiBridge)** for measuring energy consumption during Gradle builds.

### EnergyBridge Installation

To use EnergyBridge, you can either:

- **Clone and build locally**: The recommended method is to clone the official [EnergyBridge repository](https://github.com/tdurieux/EnergiBridge) and build it locally. This ensures you always have the latest version.
  
- **Download a precompiled release**: Alternatively, you can download a precompiled release from the [EnergyBridge Releases](https://github.com/tdurieux/EnergiBridge/releases) page. Both methods will work, but building locally is recommended for staying up-to-date.

### ⚠️ Known Issue: Overflow error when subtracting durations

When using the official version of EnergyBridge, you may encounter the following **runtime error**:

```
thread 'main' panicked at /rustc/07dca489ac2d933c78d3c5158e3f43beefeb02ce/library/core/src/time.rs:954:31:
overflow when subtracting durations
note: run with RUST_BACKTRACE=1 environment variable to display a backtrace
```

To avoid this issue, we recommend using a **forked version** of EnergyBridge that resolves this problem. This version is available and can be found at the following repository:

👉 **[Forked EnergyBridge Repository](https://github.com/RobertoN0/EnergiBridge)**


## 🚀 Running the Tool

Once all dependencies are set up and EnergyBridge is ready, to start the application run the following command with **administrator privileges** (needed by EnergiBridge):

```bash
uv run main.py
```


Perfect! Here's a refined and detailed **"How to Use the Tool – Experiment Setup"** section for your README based on the UI screenshot and your description:

---

## 🧪 How to Use the Tool

### 🔧 Experiment Setup View

When the GUI starts, you can configure your experiment by navigating to the **Settings View**. This section allows you to define how the experiment will be run and which Gradle tasks to measure.

Here's what each field and button is used for:

---

### 📋 Input Fields

- **Experiment Name**  
  A custom name that will be used for the output CSV and internal labeling of the experiment. Choose something descriptive (e.g., `build_variants_test1`).

- **Number of Iterations**  
  Specifies how many times each selected build configuration should be repeated. A higher number (e.g., 5–10) ensures more reliable energy measurements.

- **Timeout Between Repetitions (s)**  
  Number of seconds to wait between each iteration of the experiment. Use this to cool down the system between builds and reduce measurement noise.

- **Timeout Between Tasks (s)**  
  When measuring individual Gradle tasks, this specifies how long the tool should wait between the execution of one task and the next. Helps isolate energy consumption per task.

- **Perform Hardware Warmup**  
  If checked, the tool will perform a warm-up phase to bring the hardware (especially CPU/GPU) to a consistent state before measuring energy usage. Recommended for more stable results.

🛈 Click the **❓ Help buttons** next to each field for best practices and example inputs.

---

### 📁 File/Folder Selection

- **Select Folder**  
  Opens a file browser to select the **Gradle project directory**. Once a valid directory is selected:
  - All available **Gradle Build tasks** are listed as checkboxes.
  - You can select/deselect specific tasks to be executed and measured in the experiment.

- **Select EnergiBridge Directory**  
  Prompts the user to select the folder where the `energibridge.exe` executable is located. This can be:
  - A **release version** downloaded from GitHub, typically found in `EnergyBridge/energibridge.exe`.
  - A **locally built version**, usually located at `EnergyBridge/target/release/energibridge.exe`.

---


## ➕ Managing Dependencies

To add or remove dependencies, use:

```bash
uv add <package-name>
uv remove <package-name>
```




