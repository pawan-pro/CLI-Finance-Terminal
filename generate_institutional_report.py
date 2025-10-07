#!/usr/bin/env python3
"""
Institutional Report Generator

This script provides a simple command to generate institutional-grade reports
using the Alpha Vantage API integration.
"""

import sys
import os
from datetime import datetime

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.analysis.daily_report import DailyInvestmentReportGenerator


def generate_institutional_report(save_dir="./reports", output_format="pdf"):
    """
    Generate an institutional-grade investment report
    
    Args:
        save_dir (str): Directory to save the report
        output_format (str): Format of the report ('pdf' or 'txt')
    """
    print(f"Generating institutional-grade report at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Format: {output_format.upper()}")
    
    try:
        # Initialize report generator
        report_gen = DailyInvestmentReportGenerator()
        
        # Generate institutional report
        report_path = report_gen.generate_report(
            save_dir=save_dir,
            format=output_format,
            institutional_grade=True  # This is the key parameter for institutional reports
        )
        
        # Shutdown the generator to clean up resources
        report_gen.shutdown()
        
        print(f"✅ Institutional report generated successfully!")
        print(f"📄 Report saved to: {report_path}")
        
        return report_path
        
    except Exception as e:
        print(f"❌ Error generating institutional report: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate institutional-grade investment report")
    parser.add_argument("--save-dir", default="./reports", help="Directory to save the report (default: ./reports)")
    parser.add_argument("--format", default="pdf", choices=["pdf", "txt"], help="Output format (default: pdf)")
    
    args = parser.parse_args()
    
    generate_institutional_report(save_dir=args.save_dir, output_format=args.format)