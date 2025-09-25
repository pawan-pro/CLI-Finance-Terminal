import sys
import os
sys.path.insert(0, '.')

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

try:
    # Try to import real MT5, fallback to mock if not available
    import MetaTrader5
    mt5 = MetaTrader5
    MT5_AVAILABLE = True
    print("Using real MT5 connection")
except ImportError:
    try:
        # Try importing Wine MT5 connector as mt5
        from src.data.providers.wine_mt5_connector import WineMT5Connector
        # Create a wrapper to make it compatible with MT5 API
        import src.data.providers.wine_mt5_connector as mt5
        MT5_AVAILABLE = True
        print("Using real MT5 connection (Wine connector)")
    except ImportError:
        # Use mock MT5 for development/testing
        import src.data.providers.mock_mt5 as mt5
        MT5_AVAILABLE = False
        print("Warning: Using mock MT5. For production with Wine, ensure MT5 Python package is properly installed in Wine environment.")

from src.data.providers.mt5_data import MT5DataFetcher

def main():
    try:
        # Initialize data fetcher with Wine MT5
        fetcher = MT5DataFetcher(use_wine_mt5=True)
        print("MT5DataFetcher initialized successfully with Wine MT5")
        
        # Get available symbols
        symbols = fetcher.get_available_symbols()
        print(f"Found {len(symbols)} symbols")
        
        # Show first 20 symbols
        print("First 20 symbols:")
        for i, symbol in enumerate(symbols[:20]):
            print(f"  {i+1:2d}. {symbol}")
            
        # Check for specific symbols
        target_symbols = ['US500Roll', 'DE40Roll', 'EURUSD', 'XAUUSD']
        print("\nChecking for specific symbols:")
        for symbol in target_symbols:
            if symbol in symbols:
                print(f"  ✓ {symbol} - Available")
                # Try to get symbol info
                info = fetcher.get_symbol_info(symbol)
                if info:
                    print(f"    Ask: {info.get('ask', 'N/A')}, Bid: {info.get('bid', 'N/A')}, Last: {info.get('last', 'N/A')}")
                else:
                    print(f"    Failed to get info for {symbol}")
            else:
                print(f"  ✗ {symbol} - Not available")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()