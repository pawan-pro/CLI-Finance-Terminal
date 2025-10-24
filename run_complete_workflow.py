import subprocess
import sys

def run_script(script_path):
    """Executes a Python script and checks for errors."""
    try:
        print(f"--- Running {script_path} ---")
        result = subprocess.run([sys.executable, script_path], check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Errors:\n", result.stderr)
        print(f"--- Finished {script_path} ---\n")
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_path}:")
        print(e.stdout)
        print(e.stderr)
        sys.exit(1)

def main():
    """Main function to run the complete workflow."""
    print("=== Starting the Complete Data Pipeline Workflow ===\n")

    # Step 1: Fetching data
    fetcher_scripts = [
        "src/fetchers/t12-b.py",
        "src/fetchers/t12-comm.py",
        "src/fetchers/t12-crypto.py",
        "src/fetchers/t12-fx.py",
        "src/fetchers/t12-i.py",
        "src/fetchers/t12-sec.py",
        "src/fetchers/t12-sec2.py",
        "src/fetchers/t12-vix.py",
    ]
    for script in fetcher_scripts:
        run_script(script)

    # Step 2: Aligning data
    run_script("src/processing/read_align_data.py")

    # Step 3: Computing metrics
    run_script("src/processing/compute_metrics.py")

    # Step 4: Generating report
    run_script("src/processing/daily_report.py")

    print("=== Workflow Completed Successfully ===")

if __name__ == "__main__":
    main()
