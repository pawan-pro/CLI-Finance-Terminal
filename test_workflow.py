#!/usr/bin/env python3
"""
Test script to run the complete workflow and verify it works properly.
This script will run the fetch script with proper timeout handling.
"""

import subprocess
import sys
import os

def main():
    """
    Main function to run the complete workflow.
    """
    print("Starting the complete workflow...")
    
    # Change to approach 2.0 directory
    approach_dir = os.path.join(os.path.dirname(__file__), "approach 2.0")
    os.chdir(approach_dir)
    
    print(f"Changed to directory: {os.getcwd()}")
    
    # Run the orchestrator script
    try:
        print("Running the complete workflow...")
        result = subprocess.run([
            sys.executable, 
            "run_complete_workflow.py"
        ], timeout=1800)  # 30 minute timeout for the entire workflow
        
        if result.returncode == 0:
            print("Workflow completed successfully!")
        else:
            print(f"Workflow failed with return code: {result.returncode}")
            
    except subprocess.TimeoutExpired:
        print("Workflow timed out after 30 minutes")
    except Exception as e:
        print(f"Error running workflow: {e}")

if __name__ == "__main__":
    main()