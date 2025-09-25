"""
Test script for daily investment report generation
"""
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.analysis.daily_report import DailyInvestmentReportGenerator

def test_daily_report():
    """Test daily investment report generation"""
    print("Testing daily investment report generation...")
    
    try:
        # Initialize report generator
        report_gen = DailyInvestmentReportGenerator()
        print("✅ Report generator initialized")
        
        # Test market status
        market_status = report_gen.get_market_status()
        print(f"✅ Market status: {market_status}")
        
        # Test report generation (text format)
        print("Generating text report...")
        txt_report_path = report_gen.generate_report("./test_reports", "txt")
        print(f"✅ Text report generated: {txt_report_path}")
        
        # Test report generation (PDF format)
        print("Generating PDF report...")
        pdf_report_path = report_gen.generate_report("./test_reports", "pdf")
        print(f"✅ PDF report generated: {pdf_report_path}")
        
        # Shutdown
        report_gen.shutdown()
        print("✅ Report generator shutdown")
        
    except Exception as e:
        print(f"❌ Error testing daily report generation: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_daily_report()
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)