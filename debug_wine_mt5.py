"""
Debug test for Wine MT5 symbol info
"""
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.analysis.daily_report import DailyInvestmentReportGenerator

def debug_wine_mt5():
    """Debug Wine MT5 symbol info"""
    print("Debugging Wine MT5 symbol info...")
    
    try:
        # Initialize report generator with Wine MT5 enabled
        report_gen = DailyInvestmentReportGenerator(use_wine_mt5=True)
        print("✅ Report generator initialized with Wine MT5")
        
        # Test getting symbol info directly
        print("\nTesting direct symbol info fetch for EURUSD...")
        eurusd_info = report_gen._get_wine_symbol_info("EURUSD")
        print(f"EURUSD info result: {eurusd_info}")
            
    except Exception as e:
        print(f"❌ Error debugging Wine MT5: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = debug_wine_mt5()
    if success:
        print("\n🎉 Debug test completed!")
    else:
        print("\n💥 Debug test failed!")
        sys.exit(1)