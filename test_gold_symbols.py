#!/usr/bin/env python3
"""
Test script to check different gold symbols
"""

import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.data.providers.wine_mt5_connector import wine_mt5_connector

def test_gold_symbols():
    """Test different gold symbols"""
    print("Testing different gold symbols...")
    print("=" * 50)
    
    # Common gold symbol variations
    gold_symbols = ['XAUUSD', 'XAU/USD', 'GOLD', 'GC1!', 'GCZ23', 'XAUUSDpro']
    
    for symbol in gold_symbols:
        try:
            print(f"Testing {symbol}...")
            symbol_info = wine_mt5_connector.get_symbol_info(symbol)
            if symbol_info:
                print(f"  ✓ Available: ask={symbol_info.get('ask', 'N/A')}, bid={symbol_info.get('bid', 'N/A')}")
            else:
                print(f"  ✗ Not available")
        except Exception as e:
            print(f"  ✗ Error: {e}")

if __name__ == "__main__":
    test_gold_symbols()