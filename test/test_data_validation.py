#!/usr/bin/env python3
"""
Debug script to validate data availability and symbol mapping for Alpha Vantage.
"""

import sys
import os
import pandas as pd
import pytest

# Ensure the src directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.providers.alphavantage_data import AlphaVantageDataFetcher
from src.config.symbol_map import map_symbol_for_request, ALPHAVANTAGE_SYMBOL_MAPPING

def test_data_availability(mock_api_request):
    """Test data availability for a predefined list of symbols using mocked data."""
    print("Testing data availability with mocked Alpha Vantage...")
    
    fetcher = AlphaVantageDataFetcher(use_cache=False)

    test_symbols = ['US500Roll', 'EURUSD', 'BTCUSD']
    print(f"Testing symbols: {test_symbols}")

    for symbol in test_symbols:
        print(f"\nTesting {symbol}:")
        
        # Get quote info
        quote_info = fetcher.get_global_quote(symbol)
        print(f"  Mocked Quote info: {quote_info}")
        
        assert quote_info is not None, f"Should receive quote info for {symbol}"
        assert quote_info.get('price') is not None, f"Price for {symbol} should not be None"

    print("  ✓ Data availability tests passed.")

def test_mapping_logic():
    """Test the new Alpha Vantage symbol mapping logic."""
    print("\nTesting Alpha Vantage mapping logic...")
    
    # Test cases based on the new symbol map
    mapping_tests = {
        'US500Roll': 'SPY',
        'US30Roll': 'DIA',
        'DE40Roll': '^GDAXI',
        'XAUUSD': 'GLD',
        'USOILRoll': 'USO',
        'VIXRoll': '^VIX',
        'TLT': 'TLT', # Should remain unchanged
        'BTCUSD': 'BTC',
        'EURUSD': 'EUR/USD'
    }

    for internal_symbol, expected_av_symbol in mapping_tests.items():
        mapped_symbol = map_symbol_for_request(internal_symbol)
        print(f"  Mapping {internal_symbol} -> {mapped_symbol} (Expected: {expected_av_symbol})")
        assert mapped_symbol == expected_av_symbol, f"Mapping for {internal_symbol} failed."

    print("  ✓ All mapping tests passed.")


if __name__ == "__main__":
    pytest.main([__file__])