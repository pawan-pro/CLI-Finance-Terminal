#!/usr/bin/env python3
"""
Test script to verify that the economic calendar CSV reading functionality works correctly with the new format.
"""

import sys
import os
import pandas as pd

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.analysis.daily_report import DailyInvestmentReportGenerator

def test_calendar_csv_reading():
    """Test that we can read the economic calendar CSV file with the new format."""
    print("Testing economic calendar CSV reading functionality with new format...")
    
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
        print("\nData types:")
        print(calendar_data.dtypes)
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
                    print("First few rows:")
                    print(df.head())
                except Exception as e:
                    print(f"Direct read failed: {e}")
            else:
                print("CSV file does not exist at that location.")
        else:
            print(f"Wine path does not exist: {wine_path}")
        
        return False

def test_calendar_command_format():
    """Test converting the CSV data to the format expected by the CLI command."""
    print("\n" + "="*60)
    print("Testing conversion to CLI command format...")
    
    # Create a report generator instance
    report_gen = DailyInvestmentReportGenerator(use_wine_mt5=True)
    
    # Try to get the economic calendar data
    calendar_df = report_gen.get_economic_calendar()
    
    if not calendar_df.empty:
        print(f"Converting {len(calendar_df)} calendar events to CLI format...")
        
        # Convert DataFrame to list of EconomicEvent objects (similar to what the CLI command does)
        from src.data.models.economic_event import EconomicEvent
        calendar_data = []
        
        for _, row in calendar_df.head(5).iterrows():  # Just test with first 5 rows
            # Handle time formatting
            time_str = ""
            if 'Time' in row:
                time_obj = row['Time']
                if hasattr(time_obj, 'strftime'):
                    time_str = time_obj.strftime("%H:%M")
                elif isinstance(time_obj, str):
                    # Try to parse the time from string
                    try:
                        from datetime import datetime
                        time_parsed = datetime.strptime(time_obj.split()[-1], "%H:%M")
                        time_str = time_parsed.strftime("%H:%M")
                    except:
                        time_str = str(time_obj)
            
            # Handle importance mapping
            importance_map = {
                'High': 3,
                'Medium': 2,
                'Low': 1,
                'None': 1
            }
            importance = 1
            if 'Impact' in row:
                impact = str(row['Impact']).strip()
                importance = importance_map.get(impact, 1)
            
            # Create EconomicEvent object
            # Handle date extraction from Time column
            date_str = ''
            if 'Time' in row and pd.notna(row['Time']):
                date_str = row['Time'].strftime('%Y-%m-%d')
            
            event = EconomicEvent(
                date=date_str,
                time_ist=time_str,
                currency=row.get('Currency', ''),
                event_name=row.get('Name', ''),
                importance=importance,
                forecast=str(row.get('Forecast', '')) if pd.notna(row.get('Forecast', '')) else '',
                previous=str(row.get('Previous', '')) if pd.notna(row.get('Previous', '')) else '',
                notes=f"Country: {row.get('Country', '')}" if 'Country' in row else ''
            )
            calendar_data.append(event)
            
            print(f"  Event: {event.event_name}")
            print(f"    Date: {event.date}, Time: {event.time_ist}")
            print(f"    Currency: {event.currency}, Importance: {event.importance}")
            print(f"    Forecast: {event.forecast}, Previous: {event.previous}")
            print()
        
        print("Conversion successful!")
        return True
    else:
        print("No calendar data to convert.")
        return False

if __name__ == "__main__":
    success1 = test_calendar_csv_reading()
    success2 = test_calendar_command_format()
    
    if success1 and success2:
        print("\n" + "="*60)
        print("All tests passed! The economic calendar feature is working correctly.")
    else:
        print("\n" + "="*60)
        print("Some tests failed. Please check the implementation.")