#!/usr/bin/env python3
"""
Debug script to test chart generation
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from src.data.providers.mt5_data import MT5DataFetcher
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pandas as pd

def test_chart_generation():
    """Test chart generation for available symbols"""
    print("Testing chart generation...")
    
    try:
        fetcher = MT5DataFetcher(use_wine_mt5=True)  # Try to force Wine MT5
        available_symbols = fetcher.get_available_symbols()
        print(f"Available symbols: {available_symbols[:10]}...")  # Show first 10
        
        # Try to generate charts for available symbols
        test_symbols = [s for s in available_symbols if s in ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD', 'XAGUSD', 'SPX500', 'DJI30', 'NDX100', 'DAX30', 'FTSE100']]
        if not test_symbols:
            # If the preferred symbols aren't available, just use first few
            test_symbols = available_symbols[:5]
        
        print(f"Testing chart generation for symbols: {test_symbols}")
        
        for symbol in test_symbols:
            print(f"\nTesting chart for: {symbol}")
            try:
                # Get historical data for the symbol
                end_time = datetime.now()
                start_time = end_time - timedelta(days=30)  # Last 30 days
                
                data = fetcher.fetch_historical_data(symbol, 60, start_time, end_time)  # TIMEFRAME_H1 = 60
                print(f"  Historical data points: {len(data)}")
                
                if not data.empty:
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
                    
                    # Save chart
                    chart_file = f'./test/{symbol}_test_chart.png'
                    plt.savefig(chart_file)
                    plt.close()
                    print(f"  Chart saved to: {chart_file}")
                    
                    # Print some sample data
                    print(f"  Sample data - Latest close: {data['close'].iloc[-1]:.5f}, Open: {data['open'].iloc[-1]:.5f}")
                else:
                    print(f"  No historical data available for {symbol}")
                    
            except Exception as e:
                print(f"  Error generating chart for {symbol}: {e}")
                import traceback
                traceback.print_exc()
        
        fetcher.shutdown()
        
    except Exception as e:
        print(f"Error in chart generation test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=== Testing Chart Generation ===")
    test_chart_generation()
    print("\n=== Chart Test Complete ===")