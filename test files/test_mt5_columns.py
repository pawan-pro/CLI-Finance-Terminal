#!/usr/bin/env python3
"""
Test script to check what columns are available in MT5 data
"""

import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.data.providers.wine_mt5_connector import wine_mt5_connector

def test_mt5_data_columns():
    """Test what columns are available in MT5 data"""
    print("Testing MT5 data columns...")
    print("=" * 50)
    
    # Test a few symbols to see what columns are available
    symbols_to_test = ['US30Roll', 'XAUUSD', 'EURUSD']
    
    for symbol in symbols_to_test:
        try:
            print(f"\nTesting {symbol}...")
            symbol_info = wine_mt5_connector.get_symbol_info(symbol)
            if symbol_info:
                print(f"  Available columns:")
                for key, value in symbol_info.items():
                    print(f"    {key}: {value}")
            else:
                print(f"  No data available")
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    test_mt5_data_columns()