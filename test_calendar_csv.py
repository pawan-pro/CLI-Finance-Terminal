#!/usr/bin/env python3
"""
Test script to verify that the economic calendar CSV reading functionality works correctly.
"""

import sys
import os
import pandas as pd

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.analysis.daily_report import DailyInvestmentReportGenerator

def test_calendar_csv_reading():
    """Test that we can read the economic calendar CSV file."""
    print("Testing economic calendar CSV reading functionality...")
    
    # Create a report generator instance
    report_gen = DailyInvestmentReportGenerator(use_wine_mt5=True)
    
    # Try to get the economic calendar data
    calendar_data = report_gen.get_economic_calendar()
    
    # Display results
    if not calendar_data.empty:
        print(f"Successfully read {len(calendar_data)} calendar events from CSV!")
        print("\nFirst few rows of calendar data:")
        print(calendar_data.head())
        print("\nColumn names:")
        print(list(calendar_data.columns))
        return True
    else:
        print("No calendar data found or CSV file not accessible.")
        print("This is expected if the MQ5 script hasn't generated the CSV file yet,")
        print("or if the file path is incorrect in the Wine environment.")
        
        # Let's also check if the file exists at the expected location
        import os
        wine_path = os.path.expanduser("~/.wine/drive_c")
        calendar_csv_path = "C:/Users/Administrator/AppData/Roaming/MetaQuotes/Terminal/Common/Files/economic_calendar.csv"
        if os.path.exists(wine_path):
            calendar_csv_path = calendar_csv_path.replace("C:", wine_path, 1)
            print(f"\nChecking for CSV file at: {calendar_csv_path}")
            if os.path.exists(calendar_csv_path):
                print("CSV file exists!")
                # Try to read it directly with pandas
                try:
                    df = pd.read_csv(calendar_csv_path)
                    print(f"Direct read successful: {len(df)} rows")
                    print("Columns:", list(df.columns))
                except Exception as e:
                    print(f"Direct read failed: {e}")
            else:
                print("CSV file does not exist at that location.")
        else:
            print(f"Wine path does not exist: {wine_path}")
        
        return False

if __name__ == "__main__":
    test_calendar_csv_reading()