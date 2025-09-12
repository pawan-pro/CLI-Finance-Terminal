"""
Debug Wine MT5 connector
"""
import subprocess
import os

def debug_wine_mt5_connector():
    """Debug Wine MT5 connector"""
    print("Debugging Wine MT5 connector...")
    
    script = '''
import json
import MetaTrader5 as mt5

try:
    print("Initializing MT5...")
    if mt5.initialize():
        print("MT5 initialized successfully")
        symbol_info = mt5.symbol_info("EURUSD")
        if symbol_info:
            print("EURUSD symbol info found")
            info_dict = {
                'name': symbol_info.name,
                'description': symbol_info.description,
                'ask': float(symbol_info.ask) if symbol_info.ask else 0,
                'bid': float(symbol_info.bid) if symbol_info.bid else 0,
                'last': float(symbol_info.last) if symbol_info.last else 0,
                'volume': int(symbol_info.volume) if symbol_info.volume else 0,
                'spread': int(symbol_info.spread) if symbol_info.spread else 0,
                'digits': int(symbol_info.digits) if symbol_info.digits else 0,
                'high': float(symbol_info.high) if symbol_info.high else 0,
                'low': float(symbol_info.low) if symbol_info.low else 0,
                'time': int(symbol_info.time) if symbol_info.time else 0
            }
            print("RESULT:" + json.dumps(info_dict))
        else:
            print("RESULT:null")
        mt5.shutdown()
        print("MT5 shutdown successfully")
    else:
        print("MT5 initialization failed")
        print("RESULT:null")
except Exception as e:
    print("Exception in MT5 script:", str(e))
    print("RESULT:null")
'''
    
    try:
        # Create temporary script file
        temp_dir = os.path.expanduser('~/.cache')
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        temp_script = os.path.join(temp_dir, 'debug_wine_mt5.py')
        
        with open(temp_script, 'w') as f:
            f.write(script)
        
        # Run the script in Wine Python
        print("Running debug script in Wine Python...")
        cmd = ['wine', 'python.exe', 'Z:\\\\' + temp_script.replace('/', '\\\\')]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        # Print output
        print("STDOUT:")
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        # Clean up
        if os.path.exists(temp_script):
            os.remove(temp_script)
            
    except Exception as e:
        print(f"Error debugging Wine MT5 connector: {e}")

if __name__ == "__main__":
    debug_wine_mt5_connector()