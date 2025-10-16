import subprocess
import sys
import os

def run_script(script_name):
    """Executes a python script and handles errors."""
    try:
        print(f"--- Running {script_name} ---")
        # Use the same python interpreter that is running this script
        process = subprocess.run([sys.executable, script_name], check=True, capture_output=True, text=True)
        print(process.stdout)
        if process.stderr:
            print("Errors:", process.stderr)
        print(f"--- Finished {script_name} ---\n")
    except subprocess.CalledProcessError as e:
        print(f"!!! ERROR running {script_name}:")
        print(e.stdout)
        print(e.stderr)

# List of all data fetching scripts
fetcher_scripts = [
    't12-comm.py',
    't12-crypto.py',
    't12-fx.py',
    't12-i.py',
    't12-sec.py',
    't12-sec2.py',
    't12-vix.py',
    't12-b.py',
]

if __name__ == "__main__":
    # Get the absolute path to the directory containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    for script in fetcher_scripts:
        script_path = os.path.join(script_dir, script)
        run_script(script_path)
    print(">>> All data fetching scripts executed successfully. <<<")
