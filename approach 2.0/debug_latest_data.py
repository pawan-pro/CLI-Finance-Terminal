#!/usr/bin/env python3
"""
Debug script to check what data is in the latest_market_data.pkl file.
"""

import pickle
import pandas as pd

def debug_latest_data():
    """
    Debug the latest market data to see what's in it.
    """
    try:
        with open('data/latest_market_data.pkl', 'rb') as f:
            latest_data = pickle.load(f)
        
        print("Keys in latest_data:", list(latest_data.keys()))
        
        for key, df in latest_data.items():
            print(f"\n{key}: {len(df)} rows")
            if not df.empty:
                print(f"Columns: {list(df.columns)}")
                print("First few rows:")
                print(df.head())
                print("---")
        
        return True
    except Exception as e:
        print(f"Error reading latest market data: {str(e)}")
        return False

if __name__ == "__main__":
    debug_latest_data()