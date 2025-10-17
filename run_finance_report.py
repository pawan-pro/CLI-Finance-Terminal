#!/usr/bin/env python3
"""
Convenience script to run the complete CLI Finance Terminal workflow.
This script runs all steps: data fetching, alignment, metrics computation, and report generation.
"""

import subprocess
import sys
import os

def run_complete_workflow():
    """Run the complete workflow from the approach 2.0 directory."""
    approach_dir = os.path.join(os.path.dirname(__file__), "approach 2.0")
    
    # Change to the approach 2.0 directory
    original_dir = os.getcwd()
    os.chdir(approach_dir)
    
    try:
        print("Starting CLI Finance Terminal complete workflow...")
        print("This will take approximately 20-25 minutes due to API rate limiting.")
        
        # Run the orchestrator script
        result = subprocess.run([
            sys.executable,
            "run_complete_workflow.py"
        ], timeout=1800)  # 30 minute timeout
        
        if result.returncode == 0:
            print("\n✓ Workflow completed successfully!")
            print("Reports generated:")
            print("  - Standard report: daily_report.html")
            print("  - Enhanced report: daily_report-i.html")
        else:
            print(f"\n✗ Workflow failed with return code: {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print("\n✗ Workflow timed out after 30 minutes")
        return False
    except Exception as e:
        print(f"\n✗ Error running workflow: {e}")
        return False
    finally:
        # Change back to original directory
        os.chdir(original_dir)
    
    return True

if __name__ == "__main__":
    success = run_complete_workflow()
    sys.exit(0 if success else 1)