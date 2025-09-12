"""
Test script to check if MT5 is properly installed in Wine environment
"""
import subprocess
import os

def test_wine_python():
    """Test if Python is available in Wine environment"""
    print("Testing Wine Python installation...")
    
    # Test if wine python is available
    try:
        result = subprocess.run(['wine', 'python.exe', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Wine Python found: {result.stdout.strip()}")
            return True
        else:
            print("❌ Wine Python not found")
            print("Make sure Python is installed in your Wine environment.")
            print("You can install Python in Wine by downloading the Windows Python installer")
            print("and running it with: wine python-installer.exe")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Wine Python test timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing Wine Python: {e}")
        return False

def test_mt5_installation():
    """Test if MT5 package is installed in Wine Python environment"""
    print("\nTesting MT5 installation in Wine Python...")
    
    script = """
try:
    import MetaTrader5
    print("MT5 package is installed")
    print(f"MT5 version: {MetaTrader5.__version__}")
except ImportError:
    print("MT5 package is not installed")
"""
    
    try:
        # Write test script to temporary file
        temp_script = os.path.expanduser('~/.cache/test_mt5.py')
        with open(temp_script, 'w') as f:
            f.write(script)
        
        # Run the script in Wine Python
        result = subprocess.run(['wine', 'python.exe', 'Z:\\\\' + temp_script.replace('/', '\\\\')], 
                              capture_output=True, text=True, timeout=15)
        
        # Clean up
        if os.path.exists(temp_script):
            os.remove(temp_script)
        
        if result.returncode == 0:
            print(f"✅ {result.stdout.strip()}")
            return "MT5 package is installed" in result.stdout
        else:
            print("❌ Error running MT5 test script")
            print(f"Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ MT5 test timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing MT5 installation: {e}")
        return False

def test_mt5_initialization():
    """Test if MT5 can be initialized"""
    print("\nTesting MT5 initialization...")
    
    script = """
try:
    import MetaTrader5 as mt5
    
    if mt5.initialize():
        print("MT5 initialized successfully")
        # Try to get some basic info
        symbols = mt5.symbols_get()
        if symbols:
            print(f"Found {len(symbols)} symbols")
        else:
            print("No symbols found")
        mt5.shutdown()
    else:
        print("Failed to initialize MT5")
except Exception as e:
    print(f"Error initializing MT5: {e}")
"""
    
    try:
        # Write test script to temporary file
        temp_script = os.path.expanduser('~/.cache/test_mt5_init.py')
        with open(temp_script, 'w') as f:
            f.write(script)
        
        # Run the script in Wine Python
        result = subprocess.run(['wine', 'python.exe', 'Z:\\\\' + temp_script.replace('/', '\\\\')], 
                              capture_output=True, text=True, timeout=20)
        
        # Clean up
        if os.path.exists(temp_script):
            os.remove(temp_script)
        
        if result.returncode == 0:
            print(f"✅ {result.stdout.strip()}")
            return "MT5 initialized successfully" in result.stdout
        else:
            print("❌ Error running MT5 initialization test")
            print(f"Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ MT5 initialization test timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing MT5 initialization: {e}")
        return False

if __name__ == "__main__":
    print("=== Wine MT5 Installation Test ===\n")
    
    python_available = test_wine_python()
    if not python_available:
        exit(1)
    
    mt5_installed = test_mt5_installation()
    if not mt5_installed:
        print("\nTo install MT5 package in Wine Python, run:")
        print("wine python.exe -m pip install MetaTrader5")
        exit(1)
    
    mt5_working = test_mt5_initialization()
    if not mt5_working:
        print("\nMT5 package is installed but not working properly.")
        print("Make sure MT5 terminal is running and DLL imports are enabled.")
        exit(1)
    
    print("\n🎉 All tests passed! Wine MT5 is properly configured.")