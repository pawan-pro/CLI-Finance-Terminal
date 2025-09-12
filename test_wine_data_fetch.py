"""
Test script to verify Wine MT5 data fetching in daily report
"""
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.analysis.daily_report import DailyInvestmentReportGenerator

def test_wine_mt5_data_fetching():
    """Test Wine MT5 data fetching"""
    print("Testing Wine MT5 data fetching in daily report generator...")
    
    try:
        # Initialize report generator with Wine MT5 enabled
        report_gen = DailyInvestmentReportGenerator(use_wine_mt5=True)
        print("✅ Report generator initialized with Wine MT5")
        
        # Test getting major indices data
        print("Fetching major indices data...")
        indices_data = report_gen.get_major_indices_data()
        print(f"✅ Got indices data with {len(indices_data)} symbols")
        if not indices_data.empty:
            print("First few rows of indices data:")
            print(indices_data.head())
        
        # Test getting currency data
        print("\nFetching currency data...")
        currency_data = report_gen.get_currency_data()
        print(f"✅ Got currency data with {len(currency_data)} symbols")
        if not currency_data.empty:
            print("First few rows of currency data:")
            print(currency_data.head())
        
        # Test getting symbol info directly
        print("\nTesting direct symbol info fetch...")
        eurusd_info = report_gen._get_wine_symbol_info("EURUSD")
        if eurusd_info:
            print(f"✅ EURUSD Info: Ask={eurusd_info['ask']}, Bid={eurusd_info['bid']}, Spread={eurusd_info['spread']}")
        else:
            print("❌ Failed to get EURUSD info")
            
    except Exception as e:
        print(f"❌ Error testing Wine MT5 data fetching: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_wine_mt5_data_fetching()
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)