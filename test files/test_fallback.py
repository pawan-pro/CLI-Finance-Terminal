#!/usr/bin/env python3
"""
Test script to verify our fallback logic is working
"""

import sys
import os
import pandas as pd

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.analysis.daily_report import DailyInvestmentReportGenerator

def test_fallback_logic():
    """Test our fallback logic for zero values"""
    print("Testing fallback logic for zero values...")
    print("=" * 50)
    
    try:
        # Create report generator with Wine MT5 enabled
        report_gen = DailyInvestmentReportGenerator(use_wine_mt5=True)
        
        # Test getting commodities data
        print("Testing commodities data with fallback logic...")
        commodities_data = report_gen.get_commodities_data()
        print(f"Commodities data shape: {commodities_data.shape}")
        
        if not commodities_data.empty:
            # Look for XAUUSD (gold)
            gold_rows = commodities_data[commodities_data['name'] == 'XAUUSD']
            if not gold_rows.empty:
                gold_row = gold_rows.iloc[0]
                print(f"\nGold (XAUUSD) data:")
                print(f"  Name: {gold_row.get('name', 'N/A')}")
                print(f"  Ask: {gold_row.get('ask', 'N/A')}")
                print(f"  Bid: {gold_row.get('bid', 'N/A')}")
                print(f"  Last: {gold_row.get('last', 'N/A')}")
                print(f"  Calculated Price: {gold_row.get('Price', 'N/A')}")
                
                # Check if fallback logic worked correctly
                ask = gold_row.get('ask', 0)
                bid = gold_row.get('bid', 0)
                last = gold_row.get('last', 0)
                price = gold_row.get('Price', 0)
                
                if ask == 0 and bid == 0:
                    print(f"  Fallback logic: Both ask and bid are zero")
                    if last != 0:
                        print(f"  Using last price: {last}")
                        if price == last:
                            print(f"  ✓ Fallback logic working correctly")
                        else:
                            print(f"  ✗ Fallback logic not working - price is {price}")
                    else:
                        print(f"  Last price is also zero")
                else:
                    expected_price = (ask + bid) / 2
                    print(f"  Expected price: {expected_price}")
                    if price == expected_price:
                        print(f"  ✓ Normal calculation working correctly")
                    else:
                        print(f"  ✗ Normal calculation not working - price is {price}")
            else:
                print("Gold (XAUUSD) not found in commodities data")
        else:
            print("No commodities data found")
            
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fallback_logic()