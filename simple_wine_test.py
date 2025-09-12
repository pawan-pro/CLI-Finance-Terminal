"""
Simple test script to verify Wine MT5 functionality
"""
import subprocess
import json
import os

def test_wine_mt5():
    """Test Wine MT5 functionality"""
    print("Testing Wine MT5 functionality...")
    
    # Create a simple test script
    script = """
import json
import MetaTrader5 as mt5

try:
    if mt5.initialize():
        # Get a few symbols
        symbols = mt5.symbols_get()
        if symbols:
            symbol_names = [s.name for s in symbols[:5]]  # First 5 symbols
            print(json.dumps({"status": "success", "symbols": symbol_names}))
        else:
            print(json.dumps({"status": "success", "symbols": []}))
        mt5.shutdown()
    else:
        print(json.dumps({"status": "error", "message": "Failed to initialize MT5"}))
except Exception as e:
    print(json.dumps({"status": "error", "message": str(e)}))
"""
    
    # Write script to temporary file
    temp_script = os.path.expanduser('~/.cache/test_wine_mt5.py')
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
                    print(f"Found symbols: {data.get('symbols', [])}")
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
    success = test_wine_mt5()
    if success:
        print("\n🎉 Wine MT5 test passed!")
    else:
        print("\n💥 Wine MT5 test failed!")
