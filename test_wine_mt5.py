"""
Test script for Wine MT5 connector
"""
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.providers.wine_mt5_connector import WineMT5Connector

def test_wine_mt5_connector():
    """Test Wine MT5 connector"""
    print("Testing Wine MT5 connector...")
    
    try:
        # Initialize Wine MT5 connector
        connector = WineMT5Connector()
        print(f"✅ Wine MT5 connector initialized")
        print(f"✅ MT5 available: {connector.mt5_available}")
        
        if connector.mt5_available:
            # Test getting available symbols
            print("Fetching available symbols...")
            symbols = connector.get_available_symbols()
            print(f"✅ Found {len(symbols)} symbols")
            if symbols:
                print(f"First 5 symbols: {symbols[:5]}")
            
            # Test getting symbol info for a common symbol
            if "EURUSD" in symbols:
                print("Fetching EURUSD info...")
                eurusd_info = connector.get_symbol_info("EURUSD")
                if eurusd_info:
                    print(f"✅ EURUSD Info: Ask={eurusd_info.get('ask', 'N/A')}, Bid={eurusd_info.get('bid', 'N/A')}")
                else:
                    print("❌ Failed to get EURUSD info")
            
            # Test getting symbol info for a major index
            major_indices = ["SPX500", "DJI30", "NDX100"]
            for index in major_indices:
                if index in symbols:
                    print(f"Fetching {index} info...")
                    index_info = connector.get_symbol_info(index)
                    if index_info:
                        print(f"✅ {index} Info: Ask={index_info.get('ask', 'N/A')}, Bid={index_info.get('bid', 'N/A')}")
                    break
        else:
            print("❌ MT5 is not available in Wine environment")
            
    except Exception as e:
        print(f"❌ Error testing Wine MT5 connector: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_wine_mt5_connector()
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)