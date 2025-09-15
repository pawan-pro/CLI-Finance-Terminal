#!/usr/bin/env python3
"""
Test script to check which symbols are available in Wine MT5
"""

import sys
import os
import pandas as pd

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.data.providers.wine_mt5_connector import wine_mt5_connector

def test_symbols():
    """Test which symbols are available"""
    symbols_to_test = [
        'US500Roll', 'US30Roll', 'UT100Roll', 'DE40Roll', 'UK100Roll',
        'EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD',
        'XAUUSD', 'XAGUSD', 'USOIL', 'UKOIL'
    ]
    
    print("Testing symbol availability in Wine MT5...")
    print("=" * 50)
    
    available_symbols = []
    
    for symbol in symbols_to_test:
        try:
            print(f"Testing {symbol}...")
            symbol_info = wine_mt5_connector.get_symbol_info(symbol)
            if symbol_info:
                print(f"  ✓ Available: {symbol_info}")
                available_symbols.append(symbol)
            else:
                print(f"  ✗ Not available")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print("\nAvailable symbols:")
    for symbol in available_symbols:
        print(f"  - {symbol}")

if __name__ == "__main__":
    test_symbols()