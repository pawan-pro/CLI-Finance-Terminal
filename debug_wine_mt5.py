import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.analysis.daily_report import DailyInvestmentReportGenerator

def test_error_location():
    """Test to find where the error is occurring"""
    print("Testing to find where the error is occurring...")
    
    try:
        # Initialize report generator with Wine MT5
        report_gen = DailyInvestmentReportGenerator(use_wine_mt5=True)
        print("✅ Report generator initialized with Wine MT5")
        
        # Test the _get_wine_symbol_info method directly
        print("\n--- Testing _get_wine_symbol_info directly ---")
        symbol_info = report_gen._get_wine_symbol_info("EURUSD")
        print(f"Symbol info from _get_wine_symbol_info: {symbol_info}")
        print(f"Type: {type(symbol_info)}")
        
        # Test the MT5 fetcher method
        print("\n--- Testing MT5 fetcher method ---")
        mt5_symbol_info = report_gen.mt5_fetcher.get_symbol_info("EURUSD")
        print(f"Symbol info from MT5 fetcher: {mt5_symbol_info}")
        print(f"Type: {type(mt5_symbol_info)}")
        
        # Test getting major indices data
        print("\n--- Testing major indices data ---")
        indices_data = report_gen.get_major_indices_data()
        print(f"Indices data shape: {indices_data.shape}")
        print(f"Indices data columns: {list(indices_data.columns) if not indices_data.empty else 'No data'}")
        if not indices_data.empty:
            print("First few rows:")
            print(indices_data.head())
            
    except Exception as e:
        print(f"❌ Error in test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_error_location()