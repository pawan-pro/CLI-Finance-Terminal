"""
Final test to generate complete enhanced report with Wine MT5
"""
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.analysis.daily_report import DailyInvestmentReportGenerator

def test_enhanced_report():
    """Test generating enhanced report with Wine MT5"""
    print("Testing enhanced report generation with Wine MT5...")
    
    try:
        # Initialize report generator with Wine MT5 enabled
        report_gen = DailyInvestmentReportGenerator(use_wine_mt5=True)
        print("✅ Report generator initialized with Wine MT5")
        
        # Generate charts with specific timeframes
        print("\nGenerating enhanced charts...")
        chart_files = report_gen.generate_charts("./enhanced_test_reports/charts")
        print(f"✅ Generated {len(chart_files)} charts")
        for chart_file in chart_files[:5]:  # Show first 5
            print(f"  - {os.path.basename(chart_file)}")
        
        # Generate complete report
        print("\nGenerating complete enhanced report...")
        report_path = report_gen.generate_report("./enhanced_test_reports", "pdf")
        print(f"✅ Enhanced report generated successfully: {report_path}")
        
        # Shutdown
        report_gen.shutdown()
        print("✅ Report generator shutdown")
            
    except Exception as e:
        print(f"❌ Error generating enhanced report: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_enhanced_report()
    if success:
        print("\n🎉 Enhanced report generation test passed!")
    else:
        print("\n💥 Enhanced report generation test failed!")
        sys.exit(1)