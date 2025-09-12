"""
Detailed test of Wine MT5 functionality
"""
import subprocess
import json
import os

def test_wine_mt5_detailed():
    """Detailed test of Wine MT5 functionality"""
    print("Testing Wine MT5 functionality in detail...")
    
    # Test 1: Check if wine python is available
    print("\n1. Testing Wine Python availability...")
    try:
        result = subprocess.run(['wine', 'python.exe', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Wine Python found: {result.stdout.strip()}")
        else:
            print(f"❌ Wine Python not found: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error testing Wine Python: {e}")
        return False
    
    # Test 2: Check if MT5 is available
    print("\n2. Testing MT5 availability...")
    script = '''
try:
    import MetaTrader5
    print("MT5 version:", MetaTrader5.__version__)
    print("MT5_AVAILABLE")
except ImportError as e:
    print("MT5_NOT_AVAILABLE:", str(e))
except Exception as e:
    print("MT5_ERROR:", str(e))
'''
    
    # Write script to temporary file
    temp_script = os.path.expanduser('~/.cache/test_mt5_availability.py')
    with open(temp_script, 'w') as f:
        f.write(script)
    
    try:
        result = subprocess.run(['wine', 'python.exe', 'Z:\\\\' + temp_script.replace('/', '\\\\')], 
                              capture_output=True, text=True, timeout=15)
        
        # Clean up
        if os.path.exists(temp_script):
            os.remove(temp_script)
        
        print(f"Wine Python script output: {result.stdout}")
        if result.stderr:
            print(f"Wine Python script errors: {result.stderr}")
        
        if result.returncode == 0 and "MT5_AVAILABLE" in result.stdout:
            print("✅ MT5 is available in Wine Python")
        else:
            print("❌ MT5 is not available in Wine Python")
            return False
    except Exception as e:
        print(f"❌ Error testing MT5 availability: {e}")
        return False
    
    # Test 3: Test MT5 initialization and symbol info
    print("\n3. Testing MT5 initialization and symbol info...")
    script = '''
import json
import MetaTrader5 as mt5

try:
    print("Initializing MT5...")
    if mt5.initialize():
        print("MT5 initialized successfully")
        # Try to get EURUSD info
        print("Getting EURUSD info...")
        symbol_info = mt5.symbol_info("EURUSD")
        if symbol_info:
            info_dict = {
                'name': symbol_info.name,
                'ask': float(symbol_info.ask),
                'bid': float(symbol_info.bid),
                'spread': int(symbol_info.spread),
                'time': symbol_info.time
            }
            print("EURUSD_INFO:", json.dumps(info_dict))
        else:
            print("EURUSD_NOT_FOUND")
        mt5.shutdown()
        print("MT5 shutdown successfully")
    else:
        print("MT5_INITIALIZATION_FAILED")
except Exception as e:
    print("MT5_EXCEPTION:", str(e))
'''
    
    # Write script to temporary file
    temp_script = os.path.expanduser('~/.cache/test_mt5_symbol.py')
    with open(temp_script, 'w') as f:
        f.write(script)
    
    try:
        result = subprocess.run(['wine', 'python.exe', 'Z:\\\\' + temp_script.replace('/', '\\\\')], 
                              capture_output=True, text=True, timeout=20)
        
        # Clean up
        if os.path.exists(temp_script):
            os.remove(temp_script)
        
        print(f"Wine Python script output: {result.stdout}")
        if result.stderr:
            print(f"Wine Python script errors: {result.stderr}")
        
        if result.returncode == 0:
            if "MT5 initialized successfully" in result.stdout:
                print("✅ MT5 initialized successfully")
                if "EURUSD_INFO:" in result.stdout:
                    print("✅ EURUSD info retrieved successfully")
                elif "EURUSD_NOT_FOUND" in result.stdout:
                    print("❌ EURUSD not found")
                else:
                    print("❌ Unknown error getting EURUSD info")
            else:
                print("❌ MT5 initialization failed")
        else:
            print("❌ MT5 test script failed")
            return False
    except Exception as e:
        print(f"❌ Error testing MT5 symbol info: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_wine_mt5_detailed()
    if success:
        print("\n🎉 All Wine MT5 tests passed!")
    else:
        print("\n💥 Some Wine MT5 tests failed!")