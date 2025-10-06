#!/usr/bin/env python3
"""
Debug script to validate data availability and cache behavior
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from src.data.providers.mt5_data import MT5DataFetcher
from src.data.cache_manager import cache_manager
import pandas as pd

def test_data_availability():
    """Test data availability and cache behavior"""
    print("Testing data availability and cache behavior...")
    
    try:
        # Initialize fetcher without cache to see fresh data
        fetcher = MT5DataFetcher(use_cache=False, use_wine_mt5=True)
        available_symbols = fetcher.get_available_symbols()
        print(f"Available symbols: {available_symbols}")
        
        # Test fetching specific symbols that are in the available list
        symbols_to_test = [s for s in available_symbols[:8] if s in ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD', 'XAGUSD', 'USOIL', 'UKOIL', 'SPX500', 'DJI30', 'NDX100', 'DAX30', 'FTSE100']]
        if not symbols_to_test:
            symbols_to_test = available_symbols[:5]  # Use first 5 if our preferred ones aren't available
            
        print(f"Testing symbols: {symbols_to_test}")
        
        for symbol in symbols_to_test:
            print(f"\nTesting {symbol}:")
            
            # Get symbol info
            symbol_info = fetcher.get_symbol_info(symbol)
            if symbol_info:
                print(f"  Symbol info: name={symbol_info.get('name')}, ask={symbol_info.get('ask')}, bid={symbol_info.get('bid')}")
            else:
                print(f"  Symbol info: None")
                
            # Get 24h change
            change, pct_change = fetcher.get_24h_change(symbol)
            print(f"  24h change: {change}, {pct_change}%")
            
            # Test with cache enabled for comparison
            fetcher_with_cache = MT5DataFetcher(use_cache=True, use_wine_mt5=True)
            symbol_info_cached = fetcher_with_cache.get_symbol_info(symbol)
            print(f"  With cache: name={symbol_info_cached.get('name') if symbol_info_cached else 'None'}")
            fetcher_with_cache.shutdown()
            
        fetcher.shutdown()
        
        # Check what's in cache
        print(f"\nCache contents:")
        # Since we can't directly access the cache contents without modifying the cache manager,
        # we'll just proceed with testing
        
    except Exception as e:
        print(f"Error in data availability test: {e}")
        import traceback
        traceback.print_exc()

def test_mapping_logic():
    """Test the symbol mapping logic"""
    print("\nTesting mapping logic...")
    
    from src.data.providers.mt5_data import MT5DataFetcher
    try:
        fetcher = MT5DataFetcher(use_cache=False, use_wine_mt5=True)
        available_symbols = fetcher.get_available_symbols()
        print(f"Available symbols: {available_symbols}")
        
        # Test mapping from common aliases to actual symbols
        mapping_tests = [
            ('US500Roll', 'SPX500'),
            ('US30Roll', 'DJI30'), 
            ('UT100Roll', 'NDX100'),
            ('DE40Roll', 'DAX30'),
            ('UK100Roll', 'FTSE100'),
        ]
        
        for original, expected in mapping_tests:
            print(f"\nTesting mapping {original} -> {expected}:")
            
            if expected in available_symbols:
                print(f"  Expected symbol {expected} IS available")
                # Test get_symbol_info with original name
                result = fetcher.get_symbol_info(original)
                if result:
                    print(f"  Result for original {original}: {result.get('name')}")
                    if result.get('name') == original:
                        print(f"  ✓ Correct: Original name preserved in result")
                    else:
                        print(f"  ? Result has different name: {result.get('name')}")
                else:
                    print(f"  ✗ No result for {original}")
            else:
                print(f"  Expected symbol {expected} is NOT available in this MT5 instance")
                
        fetcher.shutdown()
        
    except Exception as e:
        print(f"Error in mapping logic test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=== Testing Data Availability and Cache Behavior ===")
    test_data_availability()
    test_mapping_logic()
    print("\n=== Data Validation Test Complete ===")