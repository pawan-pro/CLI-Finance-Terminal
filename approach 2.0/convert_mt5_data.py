#!/usr/bin/env python3
"""
Script to convert MT5 data to standardized format for the workflow.
"""

import sys
import os
from pathlib import Path
import pandas as pd
from datetime import datetime
import glob

def convert_mt5_to_standardized():
    """
    Convert MT5 data to the standardized format used by the rest of the pipeline.
    """
    try:
        # Define paths
        mt5_dir = Path(__file__).parent / "data" / "mt5"
        
        # Find the most recent MT5 file
        mt5_files = list(mt5_dir.glob("*.csv"))
        if not mt5_files:
            print("No MT5 data files found.")
            return False
            
        # Filter out the standardized file itself
        mt5_files = [f for f in mt5_files if "standardized" not in f.name.lower()]
        
        if not mt5_files:
            print("No raw MT5 data files found.")
            return False
            
        # Get the most recent file
        mt5_file = max(mt5_files, key=os.path.getctime)
        print(f"Using most recent MT5 file: {mt5_file.name}")
        
        # Read MT5 data
        print(f"Reading MT5 data from {mt5_file}")
        mt5_df = pd.read_csv(mt5_file)
        
        # Check if data is empty
        if mt5_df.empty:
            print("MT5 data file is empty.")
            return False
        
        # Convert time format to match our standard format
        # MT5 data has time column in format like "2025.10.22 16:43"
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
        print(f"MT5 data converted and saved to {output_file}")
        print(f"Converted {len(mt5_df)} rows of data")
        
        return True
        
    except Exception as e:
        print(f"Error converting MT5 data: {str(e)}")
        return False

def main():
    """
    Main function to convert MT5 data to standardized format.
    """
    print("Converting MT5 data to standardized format...")
    
    if convert_mt5_to_standardized():
        print("✓ MT5 data conversion completed successfully")
        return True
    else:
        print("✗ Failed to convert MT5 data")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)