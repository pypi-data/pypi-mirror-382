import sys
import re
import subprocess
import shutil
import importlib.util


def check_dependencies():
    """Check if required dependencies are installed."""
    if sys.version_info < (3, 6):
        print("Error: Python 3.6 or higher is required.")
        sys.exit(1)
    
    if importlib.util.find_spec("requests") is None:
        print("Error: Python 'requests' package is not installed.")
        print("Install it with: pip3 install requests")
        sys.exit(1)
    
    if not shutil.which("git"):
        print("Error: Git is not installed.")
        print("Install it with your package manager (e.g., 'sudo apt install git' or 'brew install git').")
        sys.exit(1)
    
    if not shutil.which("vim"):
        print("Error: Vim is not installed.")
        print("Install it with your package manager (e.g., 'sudo apt install vim' or 'brew install vim').")
        sys.exit(1)


def run_command(command):
    """Run a shell command and return its output."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command '{command}': {e.stderr}")
        sys.exit(1)


def sanitize_text(text):
    """Remove control characters (U+0000 to U+001F) from text."""
    return re.sub(r'[\x00-\x1F]', '', text)