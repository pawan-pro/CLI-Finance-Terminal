#!/usr/bin/env python3
"""
Main orchestrator script for the CLI Finance Terminal.
This script runs the complete workflow:
1. Fetch data with rate limiting
2. Align data across all asset classes
3. Compute market metrics
4. Generate daily reports
"""

import subprocess
import sys
import os
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_script(script_path: str) -> bool:
    """
    Run a Python script and return True if successful, False otherwise.
    
    Args:
        script_path: Path to the script to run
        
    Returns:
        True if script executed successfully, False otherwise
    """
    try:
        logger.info(f"Running {script_path}...")
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=os.path.dirname(script_path),
            capture_output=True,
            text=True,
            timeout=1200  # 20 minute timeout for each script (needed for rate-limited data fetching)
        )
        
        if result.returncode != 0:
            logger.error(f"Error running {script_path}:")
            logger.error(f"STDOUT: {result.stdout}")
            logger.error(f"STDERR: {result.stderr}")
            return False
            
        logger.info(f"Successfully completed {script_path}")
        if result.stdout.strip():
            logger.debug(f"Output: {result.stdout}")
        return True
        
    except subprocess.TimeoutExpired:
        logger.error(f"Timeout running {script_path}")
        return False
    except Exception as e:
        logger.error(f"Exception running {script_path}: {str(e)}")
        return False

def main():
    """
    Main orchestrator function that runs the complete workflow.
    """
    logger.info("Starting CLI Finance Terminal full workflow...")
    
    # Define the approach 2.0 directory
    approach_dir = Path(__file__).parent
    
    # Step 1: Downloading latest data from MT5 Server...
    mt5_downloader_script = approach_dir / "src/fetchers/mt5_file_downloader.py"
    logger.info("Step 1: Downloading latest data from MT5 Server...")
    if not run_script(str(mt5_downloader_script)):
        logger.warning("MT5 data download failed. Proceeding with existing data.")

    # Step 2: Fetch all data with rate limiting
    fetch_script = approach_dir / "fetch_all_data_batched.py"
    logger.info("Step 2: Fetching all market data with rate limiting...")
    if not run_script(str(fetch_script)):
        logger.error("Failed to fetch market data. Aborting workflow.")
        return False

    # Step 3: Align data from all asset classes
    align_script = approach_dir / "read_align_data.py"
    logger.info("Step 3: Aligning data from all asset classes...")
    if not run_script(str(align_script)):
        logger.error("Failed to align data. Aborting workflow.")
        return False
    
    # Step 4: Compute market metrics
    metrics_script = approach_dir / "compute_metrics.py"
    logger.info("Step 4: Computing market metrics...")
    if not run_script(str(metrics_script)):
        logger.error("Failed to compute market metrics. Aborting workflow.")
        return False
    
    # Step 5: Generate daily report (HTML)
    daily_report_script = approach_dir / "daily_report.py"
    logger.info("Step 5: Generating standard daily report...")
    if not run_script(str(daily_report_script)):
        logger.error("Failed to generate standard daily report.")
        # Continue execution as this is not a critical failure
    
    # Step 6: Generate enhanced daily report (HTML)
    daily_report_i_script = approach_dir / "daily_report-i.py"
    logger.info("Step 6: Generating enhanced daily report...")
    if not run_script(str(daily_report_i_script)):
        logger.error("Failed to generate enhanced daily report.")
        # Continue execution as this is not a critical failure
    
    logger.info("All workflow steps completed successfully!")
    logger.info("Reports generated:")
    logger.info(f"  - Standard report: {approach_dir / 'daily_report.html'}")
    logger.info(f"  - Enhanced report: {approach_dir / 'daily_report-i.html'}")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        logger.error("Workflow failed at some step!")
        sys.exit(1)
    logger.info("Workflow completed successfully!")