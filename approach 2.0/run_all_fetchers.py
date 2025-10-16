import subprocess
import sys
import os
from dotenv import load_dotenv

def run_script(script_name, env):
    """Executes a python script with a modified environment and handles errors."""
    try:
        print(f"--- Running {script_name} ---")
        # Use the same python interpreter that is running this script
        process = subprocess.run([sys.executable, script_name], env=env, check=True, capture_output=True, text=True)
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
    project_root = os.path.abspath(os.path.join(script_dir, '..'))
    dotenv_path = os.path.join(project_root, '.env')
    load_dotenv(dotenv_path=dotenv_path)

    api_key = os.getenv('TWELVE_DATA_API_KEY')

    if not api_key:
        print("Error: TWELVE_DATA_API_KEY not found in .env file.")
        sys.exit(1)

    # Create a copy of the current environment and add the API key
    env = os.environ.copy()
    env['TWELVE_DATA_API_KEY'] = api_key

    for script in fetcher_scripts:
        script_path = os.path.join(script_dir, script)
        run_script(script_path, env)
    print(">>> All data fetching scripts executed successfully. <<<")
