#!/usr/bin/env python3
"""
Script to fetch MT5 data and integrate it with the existing workflow.
This script downloads the latest MT5 data and prepares it for use in reporting.
"""

import sys
import os
from pathlib import Path
import pandas as pd
from datetime import datetime
import logging

# Add the mt5 directory to the path so we can import the downloader
sys.path.append(os.path.join(os.path.dirname(__file__), 'data', 'mt5'))

try:
    import mt5_file_downloader
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    print("Warning: MT5 downloader not available. Will skip MT5 data fetching.")

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fetch_mt5_data():
    """
    Fetch the latest MT5 data file.
    
    Returns:
        bool: True if successful or if MT5 is not available, False if there was an error
    """
    if not MT5_AVAILABLE:
        logger.warning("MT5 data fetching is not available. Skipping.")
        return True
    
    try:
        logger.info("Fetching MT5 data...")
        success = mt5_file_downloader.download_csv_file()
        if success:
            logger.info("MT5 data fetched successfully")
            return True
        else:
            logger.error("Failed to fetch MT5 data")
            return False
    except Exception as e:
        logger.error(f"Error fetching MT5 data: {str(e)}")
        return False

def convert_mt5_to_standard_format():
    """
    Convert MT5 data to the standard format used by the rest of the pipeline.
    """
    try:
        # Define paths
        mt5_dir = Path(__file__).parent / "data" / "mt5"
        today_str = datetime.now().strftime('%Y%m%d')
        mt5_file = mt5_dir / f"{today_str}.csv"
        
        # Check if MT5 file exists
        if not mt5_file.exists():
            logger.info("No MT5 data file found for today. Looking for most recent file...")
            # Look for the most recent MT5 file
            mt5_files = list(mt5_dir.glob("*.csv"))
            # Filter out any standardized files
            mt5_files = [f for f in mt5_files if "standardized" not in f.name.lower()]
            if not mt5_files:
                logger.warning("No MT5 data files found.")
                return False
            mt5_file = max(mt5_files, key=os.path.getctime)
            logger.info(f"Using most recent MT5 file: {mt5_file.name}")
        
        # Read MT5 data
        logger.info(f"Reading MT5 data from {mt5_file}")
        mt5_df = pd.read_csv(mt5_file)
        
        # Convert time format to match our standard format
        mt5_df['timestamp'] = pd.to_datetime(mt5_df['time'], format='%Y.%m.%d %H:%M', errors='coerce')
        
        # Drop rows with invalid timestamps
        mt5_df = mt5_df.dropna(subset=['timestamp'])
        
        # Rename columns to match our standard format
        mt5_df = mt5_df.rename(columns={
            'symbol': 'symbol',
            'open': 'open',
            'high': 'high',
            'low': 'low',
            'close': 'close',
            'volume': 'volume'
        })
        
        # Select only the columns we need
        mt5_df = mt5_df[['timestamp', 'symbol', 'open', 'high', 'low', 'close', 'volume']]
        
        # Save as a standardized file that can be used in the pipeline
        output_file = mt5_dir / "mt5_standardized.csv"
        mt5_df.to_csv(output_file, index=False)
        logger.info(f"MT5 data converted and saved to {output_file}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error converting MT5 data: {str(e)}")
        return False

def main():
    """
    Main function to fetch and process MT5 data.
    """
    logger.info("Starting MT5 data fetching and processing...")
    
    # Fetch MT5 data
    if not fetch_mt5_data():
        logger.error("Failed to fetch MT5 data")
        return False
    
    # Convert to standard format
    if not convert_mt5_to_standard_format():
        logger.error("Failed to convert MT5 data to standard format")
        return False
    
    logger.info("MT5 data fetching and processing completed successfully")
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)