#!/usr/bin/env python3
"""
Test script to debug gold data fetching
"""

import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.data.providers.mt5_data import MT5DataFetcher
from src.data.providers.wine_mt5_connector import wine_mt5_connector

def test_gold_data_fetching():
    """Test gold data fetching with both methods"""
    print("Testing gold data fetching...")
    print("=" * 50)
    
    # Test with Wine MT5 connector directly
    print("Testing with Wine MT5 connector directly...")
    try:
        symbol_info = wine_mt5_connector.get_symbol_info('XAUUSD')
        if symbol_info:
            print(f"  ✓ Wine MT5 connector: {symbol_info}")
        else:
            print(f"  ✗ Wine MT5 connector: No data")
    except Exception as e:
        print(f"  ✗ Wine MT5 connector error: {e}")
    
    # Test with MT5 data fetcher
    print("\nTesting with MT5 data fetcher...")
    try:
        fetcher = MT5DataFetcher(use_wine_mt5=True)
        symbol_info = fetcher.get_symbol_info('XAUUSD')
        if symbol_info:
            print(f"  ✓ MT5 data fetcher: {symbol_info}")
        else:
            print(f"  ✗ MT5 data fetcher: No data")
    except Exception as e:
        print(f"  ✗ MT5 data fetcher error: {e}")

if __name__ == "__main__":
    test_gold_data_fetching()