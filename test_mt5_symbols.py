"""
Test script to check available symbols in MT5
"""
import subprocess
import json
import os

def test_mt5_symbols():
    """Test which symbols are available in MT5"""
    print("Testing MT5 symbol availability...")
    
    script = '''
import json
import MetaTrader5 as mt5

try:
    if mt5.initialize():
        # Get all available symbols
        all_symbols = mt5.symbols_get()
        if all_symbols:
            # Filter for common symbols
            common_symbols = [
                "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD",
                "US500Roll.sd", "US30Roll.sd", "UT100Roll.sd", "DE30Roll.sd", "UK100Roll.sd",
                "XAUUSD", "XAGUSD", "USOIL", "UKOIL",
                "TLT", "IEF", "SHY", "LQD",
                "VIX", "VXN", "VXD"
            ]
            
            available_symbols = []
            for symbol in common_symbols:
                symbol_info = mt5.symbol_info(symbol)
                if symbol_info:
                    available_symbols.append({
                        "name": symbol_info.name,
                        "description": symbol_info.description,
                        "ask": float(symbol_info.ask) if symbol_info.ask else 0,
                        "bid": float(symbol_info.bid) if symbol_info.bid else 0,
                        "spread": int(symbol_info.spread) if symbol_info.spread else 0
                    })
            
            print("RESULT:" + json.dumps(available_symbols))
        else:
            print("RESULT:[]")
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
        
        temp_script = os.path.join(temp_dir, 'temp_symbol_test.py')
        
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
                symbols_list = json.loads(json_line)
                if symbols_list:
                    print(f"✅ Found {len(symbols_list)} available symbols:")
                    for symbol in symbols_list:
                        print(f"  - {symbol['name']}: {symbol['description']} (Ask: {symbol['ask']}, Bid: {symbol['bid']}, Spread: {symbol['spread']})")
                else:
                    print("❌ No common symbols found")
            else:
                print("❌ No symbols found or error occurred")
        else:
            print(f"❌ Script execution failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error testing MT5 symbols: {e}")

if __name__ == "__main__":
    test_mt5_symbols()