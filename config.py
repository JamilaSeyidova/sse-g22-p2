import os
import platform
import subprocess


SYSTEM = platform.system()

if SYSTEM == "Darwin":  # macOS
    # Use sysctl to detect CPU type
    try:
        cpu_brand = subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"]).decode().strip()
        if "Apple" in cpu_brand:
            CPU_TYPE = "AppleSilicon"
        elif "Intel" in cpu_brand:
            CPU_TYPE = "Intel"
        else:
            CPU_TYPE = "Unknown"
    except Exception:
        CPU_TYPE = "Unknown"

elif SYSTEM == "Windows":
    CPU_TYPE = platform.processor()  # Typically returns 'Intel64 Family 6 Model ...'
    if "Intel" in CPU_TYPE:
        CPU_TYPE = "Intel" #check this command on your computer idk this is chatgpt!!!!!!!!!!
    else:
        CPU_TYPE = "Unknown"

elif SYSTEM == "Linux":
    CPU_TYPE = platform.processor()  # Often 'x86_64', 'armv7l', etc.
else:
    CPU_TYPE = "Unknown"


SYSTEM = platform.system()

if SYSTEM == "Windows":
    binary_name = "energibridge.exe"
else:
    binary_name = "energibridge"

ENERGIBRIDGE_PATH = os.path.join(os.getcwd(), "energibridge", binary_name)