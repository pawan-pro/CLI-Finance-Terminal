import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.data.providers.wine_mt5_connector import WineMT5Connector

def test_wine_connector_detailed():
    """Test the Wine MT5 connector in detail"""
    print("Testing Wine MT5 connector in detail...")
    
    try:
        # Initialize connector
        connector = WineMT5Connector()
        print("✅ Wine MT5 connector initialized")
        
        # Test symbol info
        print("\n--- Testing symbol info ---")
        symbol_info = connector.get_symbol_info("EURUSD")
        print(f"Symbol info for EURUSD: {symbol_info}")
        print(f"Type of symbol_info: {type(symbol_info)}")
        
        if symbol_info:
            print("✅ Symbol info retrieved successfully")
            if isinstance(symbol_info, dict):
                print("✅ Symbol info is a dictionary (correct)")
                print(f"Keys: {list(symbol_info.keys())}")
                print(f"Name: {symbol_info.get('name', 'N/A')}")
            else:
                print("❌ Symbol info is not a dictionary")
                if hasattr(symbol_info, 'name'):
                    print(f"Name attribute: {symbol_info.name}")
                else:
                    print("❌ No name attribute")
        else:
            print("⚠️ No symbol info returned")
            
        # Test copy_rates_from_pos
        print("\n--- Testing copy_rates_from_pos ---")
        from datetime import datetime
        import MetaTrader5 as mt5
        rates = connector.copy_rates_from_pos("EURUSD", mt5.TIMEFRAME_M15, 0, 10)
        print(f"Rates: {rates}")
        print(f"Type of rates: {type(rates)}")
        if rates:
            print(f"First rate: {rates[0] if len(rates) > 0 else 'N/A'}")
            print(f"Type of first rate: {type(rates[0]) if len(rates) > 0 else 'N/A'}")
            
    except Exception as e:
        print(f"❌ Error testing Wine MT5 connector: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_wine_connector_detailed()