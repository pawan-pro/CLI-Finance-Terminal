#!/usr/bin/env python3
"""
Tests for chart generation using mocked Alpha Vantage data.
"""

import sys
import os
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pandas as pd
import pytest

# Ensure the src directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.providers.alphavantage_data import AlphaVantageDataFetcher

@pytest.fixture
def fetcher():
    """Provides an instance of the AlphaVantageDataFetcher."""
    return AlphaVantageDataFetcher(use_cache=False)

def test_chart_generation_with_mock_data(fetcher, mock_api_request):
    """Test chart generation for a predefined list of symbols using mocked data."""
    print("Testing chart generation with mocked Alpha Vantage data...")
    
    test_symbols = ['US500Roll', 'EURUSD', 'BTCUSD']
    print(f"Testing chart generation for symbols: {test_symbols}")

    for symbol in test_symbols:
        print(f"\nTesting chart for: {symbol}")

        # Get historical data for the symbol for the last 30 days
        data = fetcher.get_historical_data(symbol, days=30)
        print(f"  Mocked historical data points: {len(data)}")
        
        assert data is not None and not data.empty, f"Should receive historical data for {symbol}"
        
        # Create a simple chart
        plt.figure(figsize=(12, 6))
        plt.plot(data['time'], data['close'], label=f'{symbol} Close')
        plt.title(f'{symbol} Price Chart (Last 30 days)')
        plt.xlabel('Time')
        plt.ylabel('Price')
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save chart to a dedicated test output directory
        chart_dir = './test/test_charts/'
        if not os.path.exists(chart_dir):
            os.makedirs(chart_dir)
        chart_file = os.path.join(chart_dir, f'{symbol}_test_chart.png')
        
        plt.savefig(chart_file)
        plt.close()
        print(f"  Chart saved to: {chart_file}")
        assert os.path.exists(chart_file), f"Chart file was not created for {symbol}"
        
        # Print some sample data
        print(f"  Sample data - Latest close: {data['close'].iloc[-1]:.5f}")

    print("  ✓ Chart generation tests passed.")

if __name__ == "__main__":
    pytest.main([__file__])