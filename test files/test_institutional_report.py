"""
Test script for institutional-grade daily investment report generation
"""
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Force use of mock MT5 by ensuring MT5 is not available
try:
    # Remove any existing MT5 imports
    if 'MetaTrader5' in sys.modules:
        del sys.modules['MetaTrader5']
    if 'mt5' in sys.modules:
        del sys.modules['mt5']
except:
    pass

from src.analysis.daily_report import DailyInvestmentReportGenerator

def test_institutional_report():
    """Test institutional-grade daily investment report generation"""
    print("Testing institutional-grade daily investment report generation...")
    
    try:
        # Initialize report generator with mock data (no Wine MT5)
        report_gen = DailyInvestmentReportGenerator(use_wine_mt5=False)
        print("✅ Report generator initialized with mock data")
        
        # Test market status
        market_status = report_gen.get_market_status()
        print(f"✅ Market status: {market_status}")
        
        # Test report generation (institutional PDF format)
        print("Generating institutional PDF report...")
        institutional_pdf_path = report_gen.generate_report("./test_reports", "pdf", institutional_grade=True)
        print(f"✅ Institutional PDF report generated: {institutional_pdf_path}")
        
        # Shutdown
        report_gen.shutdown()
        print("✅ Report generator shutdown")
        
    except Exception as e:
        print(f"❌ Error testing institutional report generation: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_institutional_report()
    if success:
        print("\n🎉 All institutional report tests passed!")
    else:
        print("\n💥 Some institutional report tests failed!")
        sys.exit(1)