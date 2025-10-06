#!/usr/bin/env python3
"""
Debug script to test symbol mapping and data fetching
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from src.data.providers.mt5_data import MT5DataFetcher
from src.data.providers.alpha_vantage_data import AlphaVantageData

def test_mt5_connection():
    """Test MT5 connection and available symbols"""
    print("Testing MT5 connection...")
    try:
        fetcher = MT5DataFetcher(use_wine_mt5=True)  # Try to force Wine MT5
        print(f"MT5 connection successful: {fetcher is not None}")
        
        # Get available symbols
        symbols = fetcher.get_available_symbols()
        print(f"Available symbols ({len(symbols)}): {symbols}")
        
        # Test specific symbols that are causing issues
        test_symbols = ['US500Roll', 'US30Roll', 'UT100Roll', 'DE40Roll', 'UK100Roll', 
                       'SPX500', 'DJI30', 'NDX100', 'DAX30', 'FTSE100',
                       'EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD', 'XAGUSD',
                       'USOIL', 'UKOIL']
        
        print("\nTesting symbol mapping:")
        for symbol in test_symbols:
            print(f"\nTesting symbol: {symbol}")
            symbol_info = fetcher.get_symbol_info(symbol)
            if symbol_info:
                print(f"  Found: {symbol_info.get('name', 'N/A')} - Ask: {symbol_info.get('ask', 0)}, Bid: {symbol_info.get('bid', 0)}")
            else:
                print(f"  Not found: {symbol}")
                
        # Test 24h change for available symbols
        print("\nTesting 24h change:")
        for symbol in ['EURUSD', 'SPX500', 'DJI30']:
            change, pct_change = fetcher.get_24h_change(symbol)
            print(f"  {symbol} - Change: {change}, % Change: {pct_change}%")
            
        fetcher.shutdown()
    except Exception as e:
        print(f"Error testing MT5: {e}")
        import traceback
        traceback.print_exc()

def test_alpha_vantage():
    """Test Alpha Vantage connection"""
    print("\nTesting Alpha Vantage connection...")
    try:
        av = AlphaVantageData()
        # Test with a few common symbols
        test_symbols = ['SPY', 'TLT', 'IEF', 'SHY', 'LQD', 'GLD', 'SLV', 'USO']
        data = av.get_bond_etf_data(test_symbols)
        print(f"Alpha Vantage data fetched: {len(data)} records")
        if not data.empty:
            print("Sample data:")
            for idx, row in data.head().iterrows():
                print(f"  {row.get('name', 'N/A')}: Price: {row.get('Price', 'N/A')}, Change: {row.get('change', 'N/A')}, % Change: {row.get('pct_change', 'N/A')}")
        else:
            print("No data received from Alpha Vantage")
    except Exception as e:
        print(f"Error testing Alpha Vantage: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=== Testing Symbol Mapping and Data Fetching ===")
    test_mt5_connection()
    test_alpha_vantage()
    print("\n=== Test Complete ===")