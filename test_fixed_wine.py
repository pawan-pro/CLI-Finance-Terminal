"""
Direct test of fixed Wine MT5 connector
"""
import subprocess
import json
import os

def test_fixed_wine_mt5_connector():
    """Test the fixed Wine MT5 connector directly"""
    print("Testing fixed Wine MT5 connector...")
    
    script = '''
import json
import MetaTrader5 as mt5

try:
    if mt5.initialize():
        symbol_info = mt5.symbol_info("EURUSD")
        if symbol_info:
            # Safely extract attributes with correct names
            info_dict = {
                'name': symbol_info.name,
                'description': getattr(symbol_info, 'description', ''),
                'ask': float(getattr(symbol_info, 'ask', 0)),
                'bid': float(getattr(symbol_info, 'bid', 0)),
                'last': float(getattr(symbol_info, 'last', 0)),
                'volume': int(getattr(symbol_info, 'volume', 0)),
                'spread': int(getattr(symbol_info, 'spread', 0)),
                'digits': int(getattr(symbol_info, 'digits', 0)),
                'high': float(getattr(symbol_info, 'askhigh', 0)),  # Use askhigh as high
                'low': float(getattr(symbol_info, 'asklow', 0)),    # Use asklow as low
                'time': int(getattr(symbol_info, 'time', 0)) if getattr(symbol_info, 'time', None) else 0
            }
            print("RESULT:" + json.dumps(info_dict))
        else:
            print("RESULT:null")
        mt5.shutdown()
    else:
        print("RESULT:null")
except Exception as e:
    print("RESULT:null")
'''
    
    try:
        # Create temporary script file
        temp_dir = os.path.expanduser('~/.cache')
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        temp_script = os.path.join(temp_dir, 'test_fixed_wine.py')
        
        with open(temp_script, 'w') as f:
            f.write(script)
        
        # Run the script in Wine Python
        print("Running fixed Wine MT5 connector test...")
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
            
        # Extract only the RESULT line
        lines = result.stdout.split('\n')
        json_line = None
        for line in lines:
            if line.startswith("RESULT:"):
                json_line = line[7:]  # Remove "RESULT:" prefix
                break
        
        if json_line and json_line != "null":
            data = json.loads(json_line)
            print("✅ Successfully fetched EURUSD info:")
            for key, value in data.items():
                print(f"  {key}: {value}")
            return data
        else:
            print("❌ Failed to fetch EURUSD info")
            return None
            
    except Exception as e:
        print(f"❌ Error testing fixed Wine MT5 connector: {e}")
        return None

if __name__ == "__main__":
    test_fixed_wine_mt5_connector()