"""
Test script to verify MT5 integration
"""
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.providers.mt5_data import MT5DataFetcher

def test_mt5_integration():
    """Test MT5 integration"""
    print("Testing MT5 integration...")
    
    try:
        # Initialize MT5 fetcher
        fetcher = MT5DataFetcher()
        print("✅ MT5 initialized successfully")
        
        # Get available symbols
        symbols = fetcher.get_available_symbols()
        print(f"✅ Retrieved {len(symbols)} symbols")
        
        if symbols:
            # Show some example symbols
            print("First 5 symbols:")
            for symbol in symbols[:5]:
                print(f"  - {symbol}")
            
            # Get info for the first symbol
            symbol_info = fetcher.get_symbol_info(symbols[0])
            if symbol_info:
                print(f"✅ Symbol info for {symbols[0]}:")
                print(f"  - Ask: {symbol_info.get('ask', 'N/A')}")
                print(f"  - Bid: {symbol_info.get('bid', 'N/A')}")
                print(f"  - Spread: {symbol_info.get('spread', 'N/A')}")
            else:
                print(f"⚠️  Could not get info for {symbols[0]}")
        else:
            print("⚠️  No symbols available")
        
        # Shutdown
        fetcher.shutdown()
        print("✅ MT5 shutdown successfully")
        
    except Exception as e:
        print(f"❌ Error testing MT5 integration: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_mt5_integration()
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)