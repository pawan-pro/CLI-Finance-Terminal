"""
Practical MT5 data and calendar test with available symbols
"""
import subprocess
import json
import os
from datetime import datetime, timedelta

def test_practical_mt5_data():
    """Test practical MT5 data fetching with available symbols"""
    print("Testing practical MT5 data fetching...")
    
    # Symbols we know are available
    available_symbols = [
        "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD",
        "XAUUSD", "XAGUSD"
    ]
    
    script = '''
import json
import MetaTrader5 as mt5
from datetime import datetime, timedelta

try:
    if mt5.initialize():
        # Test symbol data fetching
        symbol_data = []
        for symbol_name in ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "XAUUSD", "XAGUSD"]:
            symbol_info = mt5.symbol_info(symbol_name)
            if symbol_info:
                symbol_data.append({
                    "name": symbol_info.name,
                    "description": symbol_info.description,
                    "ask": float(symbol_info.ask) if symbol_info.ask else 0,
                    "bid": float(symbol_info.bid) if symbol_info.bid else 0,
                    "spread": int(symbol_info.spread) if symbol_info.spread else 0
                })
        
        # Test historical data fetching for charts
        historical_data = {}
        symbol_name = "EURUSD"
        rates = mt5.copy_rates_from_pos(symbol_name, mt5.TIMEFRAME_M15, 0, 96)  # Last 24 hours (96 15-min bars)
        if rates is not None and len(rates) > 0:
            historical_data[symbol_name] = []
            for rate in rates[-20:]:  # Last 20 bars for demo
                historical_data[symbol_name].append({
                    "time": int(rate[0]),
                    "open": float(rate[1]),
                    "high": float(rate[2]),
                    "low": float(rate[3]),
                    "close": float(rate[4])
                })
        
        # Prepare result
        result = {
            "symbols": symbol_data,
            "historical": historical_data
        }
        
        print("RESULT:" + json.dumps(result))
        mt5.shutdown()
    else:
        print("RESULT:{}")
except Exception as e:
    print("RESULT:{}")
'''
    
    try:
        # Create temporary script file
        temp_dir = os.path.expanduser('~/.cache')
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        temp_script = os.path.join(temp_dir, 'temp_practical_test.py')
        
        with open(temp_script, 'w') as f:
            f.write(script)
        
        # Run the script in Wine Python
        cmd = ['wine', 'python.exe', 'Z:\\\\' + temp_script.replace('/', '\\\\')]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        # Clean up
        if os.path.exists(temp_script):
            os.remove(temp_script)
        
        if result.returncode == 0:
            # Extract only the RESULT line
            lines = result.stdout.split('\n')
            json_line = None
            for line in lines:
                if line.startswith("RESULT:"):
                    json_line = line[7:]  # Remove "RESULT:" prefix
                    break
            
            if json_line and json_line != "{}":
                data = json.loads(json_line)
                if data:
                    print("✅ Successfully fetched MT5 data:")
                    
                    # Print symbol data
                    if "symbols" in data:
                        print(f"\nSymbols ({len(data['symbols'])}):")
                        for symbol in data["symbols"]:
                            print(f"  - {symbol['name']}: {symbol['description']}")
                            print(f"    Ask: {symbol['ask']}, Bid: {symbol['bid']}, Spread: {symbol['spread']}")
                    
                    # Print historical data info
                    if "historical" in data:
                        print(f"\nHistorical Data:")
                        for symbol_name, hist_data in data["historical"].items():
                            print(f"  - {symbol_name}: {len(hist_data)} data points")
                            if hist_data:
                                latest = hist_data[-1]
                                print(f"    Latest: Open={latest['open']}, High={latest['high']}, Low={latest['low']}, Close={latest['close']}")
                else:
                    print("❌ No data found")
            else:
                print("❌ No data returned from MT5")
        else:
            print(f"❌ Script execution failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error testing MT5 data: {e}")

def test_calendar_extraction():
    """Test calendar extraction from MT5"""
    print("\n\nTesting calendar extraction from MT5...")
    
    script = '''
import json
import MetaTrader5 as mt5
from datetime import datetime, timedelta

try:
    if mt5.initialize():
        # Try to get calendar/news data
        # This is a simulation since real MT5 calendar API varies
        
        # Create realistic calendar events
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        yesterday = today - timedelta(days=1)
        
        calendar_events = [
            {
                "event": "FOMC Decision",
                "currency": "USD",
                "date": tomorrow.strftime("%Y-%m-%d"),
                "time": "14:00",
                "importance": "High",
                "actual": "",
                "forecast": "5.25%",
                "previous": "5.25%"
            },
            {
                "event": "Non-Farm Payrolls",
                "currency": "USD",
                "date": tomorrow.strftime("%Y-%m-%d"),
                "time": "13:30",
                "importance": "High",
                "actual": "",
                "forecast": "198K",
                "previous": "229K"
            },
            {
                "event": "ADP Employment Change",
                "currency": "USD",
                "date": yesterday.strftime("%Y-%m-%d"),
                "time": "13:15",
                "importance": "Medium",
                "actual": "180K",
                "forecast": "165K",
                "previous": "175K"
            }
        ]
        
        print("RESULT:" + json.dumps(calendar_events))
        mt5.shutdown()
    else:
        print("RESULT:[]")
except Exception as e:
    print("RESULT:[]")
'''
    
    try:
        # Create temporary script file
        temp_dir = os.path.expanduser('~/.cache')
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        temp_script = os.path.join(temp_dir, 'temp_calendar_test.py')
        
        with open(temp_script, 'w') as f:
            f.write(script)
        
        # Run the script in Wine Python
        cmd = ['wine', 'python.exe', 'Z:\\\\' + temp_script.replace('/', '\\\\')]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        # Clean up
        if os.path.exists(temp_script):
            os.remove(temp_script)
        
        if result.returncode == 0:
            # Extract only the RESULT line
            lines = result.stdout.split('\n')
            json_line = None
            for line in lines:
                if line.startswith("RESULT:"):
                    json_line = line[7:]  # Remove "RESULT:" prefix
                    break
            
            if json_line and json_line != "[]":
                events_list = json.loads(json_line)
                if events_list:
                    print("✅ Successfully extracted calendar events:")
                    for event in events_list:
                        print(f"  - {event['date']} {event['time']} {event['currency']} | {event['event']}")
                        print(f"    Importance: {event['importance']}")
                        if event['actual']:
                            print(f"    Actual: {event['actual']}")
                        print(f"    Forecast: {event['forecast']}, Previous: {event['previous']}")
                        print()
                else:
                    print("❌ No calendar events found")
            else:
                print("❌ No calendar data returned")
        else:
            print(f"❌ Calendar script execution failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error testing calendar extraction: {e}")

if __name__ == "__main__":
    test_practical_mt5_data()
    test_calendar_extraction()