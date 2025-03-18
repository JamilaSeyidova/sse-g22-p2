sse-g22-p2

## Project Setup
This is a python project managed through UV. UV is a package and project manager. In order to start, install UV:
```bash
# MacOS & Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Then, setup and activate the virtual environment and install all dependencies using:
```bash
uv sync

# MacOS & Linux
source .venv/bin/activate

# Windows (CMD)
.venv\Scripts\activate.bat

#Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

Finally, run the project using:
```bash
uv run main.py
```

If you want to add or remove dependencies, use `uv add <dependency_name>` or `uv remove <dependency_name>`