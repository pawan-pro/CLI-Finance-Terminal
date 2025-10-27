#!/usr/bin/env python3
"""
Test script to validate MT5 data integration.
"""

import sys
import os
from pathlib import Path
import pandas as pd
import pickle

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_mt5_data_integration():
    """
    Test that MT5 data is properly integrated into the workflow.
    """
    print("Testing MT5 data integration...")
    
    # Check if MT5 data file exists
    mt5_file = Path("data/mt5/mt5_standardized.csv")
    if not mt5_file.exists():
        print("MT5 standardized data file not found")
        return False
    
    # Try to read MT5 data
    try:
        mt5_df = pd.read_csv(mt5_file, parse_dates=['timestamp'])
        print(f"✓ MT5 data file loaded successfully with {len(mt5_df)} rows")
        print(f"Sample data:")
        print(mt5_df.head())
        return True
    except Exception as e:
        print(f"Error reading MT5 data: {str(e)}")
        return False

def test_aligned_data_includes_mt5():
    """
    Test that the aligned data includes MT5 data.
    """
    print("\nTesting that aligned data includes MT5...")
    
    aligned_data_file = Path("data/latest_market_data.pkl")
    if not aligned_data_file.exists():
        print("Aligned data file not found")
        return False
    
    try:
        with open(aligned_data_file, 'rb') as f:
            latest_data = pickle.load(f)
        
        print(f"Loaded {len(latest_data)} asset classes")
        for asset_class in latest_data:
            print(f"  - {asset_class}: {len(latest_data[asset_class])} symbols")
        
        if 'mt5' in latest_data:
            print("✓ MT5 data found in aligned data")
            print(f"  MT5 symbols: {len(latest_data['mt5'])}")
            return True
        else:
            print("✗ MT5 data not found in aligned data")
            return False
            
    except Exception as e:
        print(f"Error reading aligned data: {str(e)}")
        return False

def main():
    """
    Run all integration tests.
    """
    print("=" * 60)
    print("MT5 DATA INTEGRATION TEST")
    print("=" * 60)
    
    success = True
    
    # Test 1: MT5 data file
    if not test_mt5_data_integration():
        success = False
    
    # Test 2: Aligned data includes MT5
    if not test_aligned_data_includes_mt5():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✓ All MT5 integration tests passed!")
    else:
        print("✗ Some MT5 integration tests failed!")
    print("=" * 60)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)