"""
Test script to check SymbolInfo attributes
"""
import subprocess
import os

def test_symbol_info_attributes():
    """Test what attributes are available on SymbolInfo object"""
    print("Testing SymbolInfo attributes...")
    
    script = '''
import json
import MetaTrader5 as mt5

try:
    if mt5.initialize():
        symbol_info = mt5.symbol_info("EURUSD")
        if symbol_info:
            print("EURUSD symbol info found")
            # List all available attributes
            attributes = dir(symbol_info)
            print("Available attributes:")
            for attr in attributes:
                if not attr.startswith('_'):
                    try:
                        value = getattr(symbol_info, attr)
                        print(f"  {attr}: {value}")
                    except:
                        print(f"  {attr}: <error accessing>")
        else:
            print("EURUSD symbol info not found")
        mt5.shutdown()
    else:
        print("MT5 initialization failed")
except Exception as e:
    print("Exception:", str(e))
'''
    
    try:
        # Create temporary script file
        temp_dir = os.path.expanduser('~/.cache')
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        temp_script = os.path.join(temp_dir, 'test_symbol_attrs.py')
        
        with open(temp_script, 'w') as f:
            f.write(script)
        
        # Run the script in Wine Python
        print("Running attribute test script in Wine Python...")
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
        print(f"Error testing SymbolInfo attributes: {e}")

if __name__ == "__main__":
    test_symbol_info_attributes()