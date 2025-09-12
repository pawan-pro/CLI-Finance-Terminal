"""
Test to verify all data types in daily report with Wine MT5
"""
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.analysis.daily_report import DailyInvestmentReportGenerator

def test_all_data_types():
    """Test all data types in daily report with Wine MT5"""
    print("Testing all data types in daily report with Wine MT5...")
    
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
        
        # Test getting bonds data
        print("\nFetching bonds data...")
        bonds_data = report_gen.get_bonds_data()
        print(f"✅ Got bonds data with {len(bonds_data)} symbols")
        if not bonds_data.empty:
            print("Sample bonds data:")
            print(bonds_data[['name', 'ask', 'bid', 'spread']].head())
        
        # Test getting volatility data
        print("\nFetching volatility data...")
        volatility_data = report_gen.get_volatility_data()
        print(f"✅ Got volatility data with {len(volatility_data)} symbols")
        if not volatility_data.empty:
            print("Sample volatility data:")
            print(volatility_data[['name', 'ask', 'bid']].head())
        
        # Test getting calendar data
        print("\nFetching calendar data...")
        calendar_data = report_gen.get_economic_calendar()
        print(f"✅ Got calendar data with {len(calendar_data)} events")
        if not calendar_data.empty:
            print("Sample calendar data:")
            print(calendar_data.head())
        
        # Test getting top movers
        print("\nFetching top movers...")
        all_data = [indices_data, currency_data, commodities_data, bonds_data]
        combined_data = pd.concat([df for df in all_data if not df.empty])
        top_movers = report_gen.get_top_movers(combined_data)
        print(f"✅ Got top movers with {len(top_movers)} symbols")
        if not top_movers.empty:
            print("Sample top movers:")
            print(top_movers[['name', 'ask', 'pct_change']].head())
            
    except Exception as e:
        print(f"❌ Error testing all data types: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    import pandas as pd
    success = test_all_data_types()
    if success:
        print("\n🎉 All data types test passed!")
    else:
        print("\n💥 Some data types tests failed!")
        sys.exit(1)