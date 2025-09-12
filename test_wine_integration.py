"""
Focused test for Wine MT5 integration
"""
import subprocess
import json
import os
from datetime import datetime, timedelta

def test_wine_mt5_integration():
    """Test Wine MT5 integration directly"""
    print("Testing Wine MT5 integration directly...")
    
    script = '''
import json
import MetaTrader5 as mt5
from datetime import datetime, timedelta

try:
    print("Initializing MT5...")
    if mt5.initialize():
        print("MT5 initialized successfully")
        
        # Test symbol info fetching
        symbols_to_test = ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "XAUUSD", "XAGUSD"]
        symbol_data = []
        
        for symbol_name in symbols_to_test:
            symbol_info = mt5.symbol_info(symbol_name)
            if symbol_info:
                symbol_data.append({
                    "name": symbol_info.name,
                    "description": symbol_info.description,
                    "ask": float(symbol_info.ask) if symbol_info.ask else 0,
                    "bid": float(symbol_info.bid) if symbol_info.bid else 0,
                    "spread": int(symbol_info.spread) if symbol_info.spread else 0
                })
        
        print("Symbol data fetched:", len(symbol_data), "symbols")
        
        # Test calendar/events
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        yesterday = today - timedelta(days=1)
        
        calendar_events = [
            {
                "date": tomorrow.strftime("%Y-%m-%d"),
                "time": "14:00",
                "currency": "USD",
                "event": "FOMC Decision",
                "importance": "High",
                "forecast": "5.25%",
                "previous": "5.25%"
            },
            {
                "date": tomorrow.strftime("%Y-%m-%d"),
                "time": "13:30",
                "currency": "USD",
                "event": "Non-Farm Payrolls",
                "importance": "High",
                "forecast": "198K",
                "previous": "229K"
            },
            {
                "date": yesterday.strftime("%Y-%m-%d"),
                "time": "13:15",
                "currency": "USD",
                "event": "ADP Employment Change",
                "importance": "Medium",
                "actual": "180K",
                "forecast": "165K",
                "previous": "175K"
            }
        ]
        
        # Test historical data for charts
        historical_data = {}
        eurusd_rates = mt5.copy_rates_from_pos("EURUSD", mt5.TIMEFRAME_M15, 0, 20)
        if eurusd_rates is not None and len(eurusd_rates) > 0:
            historical_data["EURUSD"] = []
            for rate in eurusd_rates:
                historical_data["EURUSD"].append({
                    "time": int(rate[0]),
                    "open": float(rate[1]),
                    "high": float(rate[2]),
                    "low": float(rate[3]),
                    "close": float(rate[4])
                })
        
        # Prepare result
        result = {
            "symbols": symbol_data,
            "calendar": calendar_events,
            "historical": historical_data
        }
        
        print("RESULT:" + json.dumps(result))
        mt5.shutdown()
        print("MT5 shutdown successfully")
    else:
        print("MT5 initialization failed")
        print("RESULT:{}")
except Exception as e:
    print("Exception in MT5 script:", str(e))
    print("RESULT:{}")
'''
    
    try:
        # Create temporary script file
        temp_dir = os.path.expanduser('~/.cache')
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        temp_script = os.path.join(temp_dir, 'temp_wine_test.py')
        
        with open(temp_script, 'w') as f:
            f.write(script)
        
        # Run the script in Wine Python
        print("Running script in Wine Python...")
        cmd = ['wine', 'python.exe', 'Z:\\\\' + temp_script.replace('/', '\\\\')]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        # Print full output for debugging
        print("STDOUT:")
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
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
                    print("✅ Successfully fetched data from Wine MT5:")
                    
                    # Print symbol data
                    if "symbols" in data:
                        print(f"\nSymbols ({len(data['symbols'])}):")
                        for symbol in data["symbols"]:
                            print(f"  - {symbol['name']}: {symbol['description']}")
                            print(f"    Ask: {symbol['ask']}, Bid: {symbol['bid']}, Spread: {symbol['spread']}")
                    
                    # Print calendar data
                    if "calendar" in data:
                        print(f"\nCalendar Events ({len(data['calendar'])}):")
                        for event in data["calendar"]:
                            print(f"  - {event['date']} {event['time']} {event['currency']} | {event['event']}")
                            if 'actual' in event:
                                print(f"    Actual: {event['actual']}")
                            if 'forecast' in event:
                                print(f"    Forecast: {event['forecast']}")
                            if 'previous' in event:
                                print(f"    Previous: {event['previous']}")
                    
                    # Print historical data
                    if "historical" in data:
                        print(f"\nHistorical Data:")
                        for symbol_name, hist_data in data["historical"].items():
                            print(f"  - {symbol_name}: {len(hist_data)} data points")
                else:
                    print("❌ No data returned from MT5")
            else:
                print("❌ No RESULT found in MT5 output")
        else:
            print(f"❌ Wine Python script failed with return code {result.returncode}")
            
    except Exception as e:
        print(f"❌ Error testing Wine MT5 integration: {e}")

if __name__ == "__main__":
    test_wine_mt5_integration()