#!/usr/bin/env python3
"""
Test script to check XAUUSD (gold) data in detail
"""

import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.data.providers.wine_mt5_connector import wine_mt5_connector

def test_gold_data():
    """Test XAUUSD data in detail"""
    print("Testing XAUUSD (gold) data...")
    print("=" * 50)
    
    try:
        symbol_info = wine_mt5_connector.get_symbol_info('XAUUSD')
        if symbol_info:
            print("XAUUSD Symbol Info:")
            for key, value in symbol_info.items():
                print(f"  {key}: {value}")
        else:
            print("No data available for XAUUSD")
    except Exception as e:
        print(f"Error getting XAUUSD data: {e}")

if __name__ == "__main__":
    test_gold_data()