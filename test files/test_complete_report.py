"""
Test to generate a complete report with Wine MT5 data
"""
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.analysis.daily_report import DailyInvestmentReportGenerator

def test_complete_report():
    """Test generating a complete report with Wine MT5 data"""
    print("Testing complete report generation with Wine MT5 data...")
    
    try:
        # Initialize report generator with Wine MT5 enabled
        report_gen = DailyInvestmentReportGenerator(use_wine_mt5=True)
        print("✅ Report generator initialized with Wine MT5")
        
        # Generate a complete report
        print("\nGenerating complete report...")
        report_path = report_gen.generate_report("./test_reports", "pdf")
        print(f"✅ Report generated successfully: {report_path}")
        
        # Shutdown
        report_gen.shutdown()
        print("✅ Report generator shutdown")
            
    except Exception as e:
        print(f"❌ Error generating complete report: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_complete_report()
    if success:
        print("\n🎉 Complete report generation test passed!")
    else:
        print("\n💥 Complete report generation test failed!")
        sys.exit(1)