#!/usr/bin/env python3
"""
Test script to verify our fixes for the daily report generation
"""

import sys
import os
import pandas as pd

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.analysis.daily_report import DailyInvestmentReportGenerator

def test_report_generation():
    """Test the daily report generation with our fixes"""
    print("Testing daily report generation with fixes...")
    print("=" * 50)
    
    try:
        # Create report generator with Wine MT5 enabled
        report_gen = DailyInvestmentReportGenerator(use_wine_mt5=True)
        
        # Test getting major indices data
        print("Testing major indices data...")
        indices_data = report_gen.get_major_indices_data()
        print(f"Indices data shape: {indices_data.shape}")
        if not indices_data.empty:
            print("First few rows:")
            print(indices_data.head())
            print("\nColumns:")
            print(list(indices_data.columns))
            
            # Check for Price column and values
            if 'Price' in indices_data.columns:
                print("\nPrice column values (should be integers for indices):")
                for idx, row in indices_data.head().iterrows():
                    name = row.get('name', 'Unknown')
                    price = row.get('Price', 0)
                    # Check if it's an integer value (no decimal places)
                    if isinstance(price, (int, float)):
                        if price == int(price):
                            print(f"  {name}: {int(price)} (Integer)")
                        else:
                            print(f"  {name}: {price:.2f} (Decimal)")
        
        # Test getting commodities data (specifically gold)
        print("\nTesting commodities data...")
        commodities_data = report_gen.get_commodities_data()
        print(f"Commodities data shape: {commodities_data.shape}")
        if not commodities_data.empty:
            print("First few rows:")
            print(commodities_data.head())
            
            # Look for XAUUSD (gold)
            gold_data = commodities_data[commodities_data['name'] == 'XAUUSD']
            if not gold_data.empty:
                print("\nGold (XAUUSD) data:")
                print(gold_data)
            else:
                print("\nGold (XAUUSD) not found in commodities data")
        
        # Test getting economic calendar
        print("\nTesting economic calendar...")
        calendar_data = report_gen.get_economic_calendar()
        print(f"Calendar data shape: {calendar_data.shape}")
        if not calendar_data.empty:
            print("First few rows:")
            print(calendar_data.head())
            print("\nColumns:")
            print(list(calendar_data.columns))
        else:
            print("No calendar data found")
            
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_report_generation()