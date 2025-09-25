# Setting up MT5 Python Package with Wine on macOS

This guide explains how to set up the MT5 Python package to work with MT5 running under Wine on macOS.

## Prerequisites

1. Wine installed on your macOS system
2. MT5 installed and running under Wine
3. Python installed in your Wine environment

## Installation Steps

1. **Install Python in Wine (if not already done):**
   ```bash
   # Download Python for Windows (32-bit or 64-bit based on your MT5)
   # Install it using Wine
   wine python-installer.exe
   ```

2. **Install MT5 Python Package in Wine Python Environment:**
   ```bash
   # Navigate to your Wine Python Scripts directory
   cd ~/.wine/drive_c/Python39/Scripts  # Adjust path as needed
   
   # Install the MT5 package
   wine python.exe -m pip install MetaTrader5
   ```

3. **Verify Installation:**
   ```bash
   # Test the installation
   wine python.exe -c "import MetaTrader5; print('MT5 package installed successfully')"
   ```

## Configuration

1. **Ensure MT5 is Running:**
   Before using the MT5 Python package, make sure MT5 is running in your Wine environment.

2. **Enable DLL Imports in MT5:**
   In MT5, go to `Tools` > `Options` > `Expert Advisors` and check:
   - "Allow DLL imports"
   - "Allow external experts"

3. **Enable Python Integration:**
   In MT5, go to `Tools` > `Options` > `Expert Advisors` and check:
   - "Allow Python engine"

## Testing the Setup

You can test your setup with the following Python script:

```python
import MetaTrader5 as mt5

# Initialize MT5
if mt5.initialize():
    print("MT5 initialized successfully")
    
    # Get some data
    symbols = mt5.symbols_get()
    print(f"Found {len(symbols)} symbols")
    
    # Get EURUSD data
    eurusd_info = mt5.symbol_info("EURUSD")
    if eurusd_info:
        print(f"EURUSD Ask: {eurusd_info.ask}")
        print(f"EURUSD Bid: {eurusd_info.bid}")
    
    # Shutdown
    mt5.shutdown()
else:
    print("Failed to initialize MT5")
```

## Troubleshooting

1. **Import Error:**
   If you get import errors, make sure the MT5 Python package is installed in the correct Wine Python environment.

2. **Initialization Failure:**
   If MT5 fails to initialize:
   - Ensure MT5 is running
   - Check that DLL imports are enabled
   - Verify Python integration is enabled
   - Make sure no firewall is blocking the connection

3. **Connection Issues:**
   If you have connection issues:
   - Try initializing with specific path: `mt5.initialize(path="C:\\Program Files\\MetaTrader 5\\terminal64.exe")`
   - Ensure the path matches your MT5 installation in Wine

## Using with Finance Terminal

Once properly configured, the Finance Terminal should automatically use your Wine-based MT5 setup for real-time data fetching and daily investment report generation.