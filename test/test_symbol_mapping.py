#!/usr/bin/env python3
"""
Tests for symbol mapping and data fetching with the AlphaVantageDataFetcher using mocks.
"""

import sys
import os
import pytest

# Ensure the src directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.providers.alphavantage_data import AlphaVantageDataFetcher
from src.config.symbol_map import map_symbol_for_request

@pytest.fixture
def fetcher():
    """Provides an instance of the AlphaVantageDataFetcher."""
    return AlphaVantageDataFetcher(use_cache=False)

# Test cases for symbol mapping
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

@pytest.mark.parametrize("internal_symbol, expected_av_symbol", mapping_tests.items())
def test_symbol_mapping(internal_symbol, expected_av_symbol):
    """Test that internal symbols are correctly mapped to Alpha Vantage symbols."""
    print(f"Testing mapping: {internal_symbol} -> {expected_av_symbol}")
    mapped_symbol = map_symbol_for_request(internal_symbol)
    assert mapped_symbol == expected_av_symbol

@pytest.mark.parametrize("symbol, expected_price", [
    ('US500Roll', "500.00"),
    ('EURUSD', "1.08"),
    ('BTCUSD', "70000.00")
])
def test_data_fetching_with_mapping(fetcher, mock_api_request, symbol, expected_price):
    """Test that data can be fetched using an internal symbol that requires mapping."""
    print(f"Testing mocked data fetching for mapped symbol: {symbol}")
    quote = fetcher.get_global_quote(symbol)
    assert quote is not None, f"Failed to fetch quote for {symbol}"
    assert quote.get('price') is not None, f"Price for {symbol} should not be None"
    assert float(quote.get('price')) == float(expected_price)
    print(f"  Successfully fetched mocked quote for {symbol}: Price={quote.get('price')}")

def test_unmapped_symbol_passthrough(fetcher, mock_api_request):
    """Test that a symbol not in the map is passed through directly and fetches data."""
    unmapped_symbol = "IBM" # A standard stock ticker
    print(f"Testing passthrough for unmapped symbol: {unmapped_symbol}")
    mapped_symbol = map_symbol_for_request(unmapped_symbol)
    assert mapped_symbol == unmapped_symbol

    # Also test that it fetches data correctly using the mock
    quote = fetcher.get_global_quote(unmapped_symbol)
    assert quote is not None, f"Failed to fetch quote for unmapped symbol {unmapped_symbol}"
    assert quote.get('price') is not None, f"Price for {unmapped_symbol} should not be None"
    assert str(quote.get('price')) == "150.00"
    print(f"  Successfully fetched mocked quote for {unmapped_symbol}: Price={quote.get('price')}")

if __name__ == "__main__":
    pytest.main([__file__])