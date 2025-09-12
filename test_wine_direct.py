"""
Direct test of Wine MT5 functionality
"""
import subprocess
import json
import os

def test_wine_mt5_direct():
    """Test Wine MT5 functionality directly"""
    print("Testing Wine MT5 functionality directly...")
    
    # Create a simple test script
    script = '''
import json
import MetaTrader5 as mt5

try:
    if mt5.initialize():
        # Test getting symbol info
        eurusd_info = mt5.symbol_info("EURUSD")
        if eurusd_info:
            info_dict = {
                'name': eurusd_info.name,
                'ask': float(eurusd_info.ask),
                'bid': float(eurusd_info.bid),
                'spread': int(eurusd_info.spread)
            }
            print(json.dumps({"status": "success", "data": info_dict}))
        else:
            print(json.dumps({"status": "error", "message": "Failed to get EURUSD info"}))
        mt5.shutdown()
    else:
        print(json.dumps({"status": "error", "message": "Failed to initialize MT5"}))
except Exception as e:
    print(json.dumps({"status": "error", "message": str(e)}))
'''
    
    # Write script to temporary file
    temp_script = os.path.expanduser('~/.cache/test_wine_mt5_direct.py')
    with open(temp_script, 'w') as f:
        f.write(script)
    
    try:
        # Run the script in Wine Python
        result = subprocess.run(['wine', 'python.exe', 'Z:\\\\' + temp_script.replace('/', '\\\\')], 
                              capture_output=True, text=True, timeout=30)
        
        # Clean up
        if os.path.exists(temp_script):
            os.remove(temp_script)
        
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout.strip())
                if data.get("status") == "success":
                    print(f"✅ MT5 is working correctly")
                    print(f"EURUSD Info: {data.get('data', {})}")
                    return True
                else:
                    print(f"❌ MT5 error: {data.get('message', 'Unknown error')}")
                    return False
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON response: {result.stdout}")
                return False
        else:
            print(f"❌ Script execution failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Script execution timed out")
        return False
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return False

if __name__ == "__main__":
    success = test_wine_mt5_direct()
    if success:
        print("\n🎉 Wine MT5 direct test passed!")
    else:
        print("\n💥 Wine MT5 direct test failed!")