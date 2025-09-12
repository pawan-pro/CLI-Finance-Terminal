"""
Test to verify Wine MT5 data fetching in daily report
"""
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.analysis.daily_report import DailyInvestmentReportGenerator

def test_wine_mt5_data():
    """Test Wine MT5 data fetching"""
    print("Testing Wine MT5 data fetching in daily report...")
    
    try:
        # Initialize report generator with Wine MT5 enabled
        report_gen = DailyInvestmentReportGenerator(use_wine_mt5=True)
        print("✅ Report generator initialized with Wine MT5")
        
        # Test getting major indices data
        print("\nFetching major indices data...")
        indices_data = report_gen.get_major_indices_data()
        print(f"✅ Got indices data with {len(indices_data)} symbols")
        if not indices_data.empty:
            print("Sample indices data:")
            print(indices_data[['name', 'ask', 'bid', 'spread']].head())
        
        # Test getting currency data
        print("\nFetching currency data...")
        currency_data = report_gen.get_currency_data()
        print(f"✅ Got currency data with {len(currency_data)} symbols")
        if not currency_data.empty:
            print("Sample currency data:")
            print(currency_data[['name', 'ask', 'bid', 'spread']].head())
        
        # Test getting commodities data
        print("\nFetching commodities data...")
        commodities_data = report_gen.get_commodities_data()
        print(f"✅ Got commodities data with {len(commodities_data)} symbols")
        if not commodities_data.empty:
            print("Sample commodities data:")
            print(commodities_data[['name', 'ask', 'bid', 'spread']].head())
            
    except Exception as e:
        print(f"❌ Error testing Wine MT5 data: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_wine_mt5_data()
    if success:
        print("\n🎉 All Wine MT5 data tests passed!")
    else:
        print("\n💥 Some Wine MT5 data tests failed!")
        sys.exit(1)