#!/usr/bin/env python3
"""
Test script to check if we can fetch historical data for candlestick charts
"""

import sys
import os
from datetime import datetime, timedelta

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.data.providers.wine_mt5_connector import wine_mt5_connector

# Try to import MT5 constants, fallback if not available
try:
    import MetaTrader5 as mt5
    TIMEFRAME_M15 = mt5.TIMEFRAME_M15
    TIMEFRAME_H4 = mt5.TIMEFRAME_H4
    TIMEFRAME_D1 = mt5.TIMEFRAME_D1
except ImportError:
    # Define constants manually
    TIMEFRAME_M15 = 15
    TIMEFRAME_H4 = 240
    TIMEFRAME_D1 = 1440

def test_historical_data():
    """Test fetching historical data for candlestick charts"""
    print("Testing historical data fetching for candlestick charts...")
    print("=" * 60)
    
    # Test symbols
    symbols_to_test = ['XAUUSD', 'US30Roll', 'EURUSD']
    
    for symbol in symbols_to_test:
        try:
            print(f"\nTesting {symbol}...")
            
            # Fetch historical data for the last 24 hours with 15-minute intervals
            end_time = datetime.now()
            start_time = end_time - timedelta(days=1)
            
            # Try to get historical data
            rates = wine_mt5_connector.copy_rates_range(
                symbol, TIMEFRAME_M15, start_time, end_time)
            
            if rates:
                print(f"  ✓ Successfully fetched {len(rates)} data points")
                if len(rates) > 0:
                    # Show first few data points
                    print(f"  First data point:")
                    first_point = rates[0]
                    for key, value in first_point.items():
                        print(f"    {key}: {value}")
                        
                    # Check if we have OHLC data
                    required_columns = ['time', 'open', 'high', 'low', 'close']
                    missing_columns = [col for col in required_columns if col not in first_point]
                    if not missing_columns:
                        print(f"  ✓ All required OHLC columns present for candlestick chart")
                    else:
                        print(f"  ✗ Missing columns: {missing_columns}")
            else:
                print(f"  ✗ No data available")
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_historical_data()