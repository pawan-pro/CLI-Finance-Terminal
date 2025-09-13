"""
Wine MT5 Connector

This module provides a direct interface to MT5 running under Wine.
"""

import subprocess
import json
import os
import pandas as pd
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WineMT5Connector:
    """Direct interface to MT5 running under Wine"""
    
    def __init__(self, wine_prefix: str = None):
        """
        Initialize Wine MT5 connector
        
        Args:
            wine_prefix: Path to Wine prefix (optional)
        """
        self.wine_prefix = wine_prefix or os.environ.get('WINEPREFIX', os.path.expanduser('~/.wine'))
        logger.info("Wine MT5 connector initialized")
    
    def _run_wine_python_script(self, script: str) -> str:
        """
        Run a Python script in Wine Python environment
        
        Args:
            script: Python script to execute
            
        Returns:
            Output from the script
        """
        try:
            # Create temporary script file
            temp_dir = os.path.expanduser('~/.cache')
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            
            temp_script = os.path.join(temp_dir, 'temp_wine_mt5_connector.py')
            
            with open(temp_script, 'w') as f:
                f.write(script)
            
            # Run the script in Wine Python
            cmd = ['wine', 'python.exe', 'Z:\\\\' + temp_script.replace('/', '\\\\')]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30,
                                  env={**os.environ, 'MVK_CONFIG_LOG_LEVEL': '0'})
            
            # Clean up
            if os.path.exists(temp_script):
                os.remove(temp_script)
            
            if result.returncode != 0:
                raise Exception(f"Script execution failed: {result.stderr}")
            
            return result.stdout.strip()
        except Exception as e:
            logger.error(f"Error running Wine Python script: {e}")
            raise
    
    def initialize(self) -> bool:
        """Initialize MT5 connection"""
        script = '''
import MetaTrader5 as mt5

try:
    if mt5.initialize():
        print("INITIALIZED")
        mt5.shutdown()
    else:
        print("FAILED")
except Exception as e:
    print("FAILED")
'''
        
        try:
            result = self._run_wine_python_script(script)
            return "INITIALIZED" in result
        except Exception as e:
            logger.error(f"Error initializing MT5: {e}")
            return False
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict]:
        """Get information about a specific symbol"""
        script = '''
import json
import MetaTrader5 as mt5

try:
    if mt5.initialize():
        symbol_info = mt5.symbol_info("''' + symbol + '''")
        if symbol_info:
            # Safely extract attributes with correct names
            # Handle both object and dictionary formats
            if hasattr(symbol_info, 'name'):
                # Object format
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
            else:
                # Dictionary format (from Wine MT5 script)
                info_dict = {
                    'name': symbol_info.get('name', symbol),
                    'description': symbol_info.get('description', ''),
                    'ask': float(symbol_info.get('ask', 0)),
                    'bid': float(symbol_info.get('bid', 0)),
                    'last': float(symbol_info.get('last', 0)),
                    'volume': int(symbol_info.get('volume', 0)),
                    'spread': int(symbol_info.get('spread', 0)),
                    'digits': int(symbol_info.get('digits', 0)),
                    'high': float(symbol_info.get('askhigh', symbol_info.get('high', 0))),  # Handle both keys
                    'low': float(symbol_info.get('asklow', symbol_info.get('low', 0))),      # Handle both keys
                    'time': int(symbol_info.get('time', 0)) if symbol_info.get('time', 0) else 0
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
            result = self._run_wine_python_script(script)
            # Extract only the RESULT line
            lines = result.split('\n')
            json_line = None
            for line in lines:
                if line.startswith("RESULT:"):
                    json_line = line[7:]  # Remove "RESULT:" prefix
                    break
            
            if json_line and json_line != "null":
                return json.loads(json_line)
            return None
        except Exception as e:
            logger.error(f"Error getting symbol info for {symbol}: {e}")
            return None
    
    def copy_rates_from_pos(self, symbol: str, timeframe: int, start_pos: int, count: int) -> Optional[List[Dict]]:
        """Copy rates from a specific position"""
        script = '''
import json
import MetaTrader5 as mt5

try:
    if mt5.initialize():
        rates = mt5.copy_rates_from_pos("''' + symbol + '''", ''' + str(timeframe) + ''', ''' + str(start_pos) + ''', ''' + str(count) + ''')
        if rates is not None and len(rates) > 0:
            # Convert to list of dictionaries
            rates_list = []
            for rate in rates:
                # Check if rate is iterable
                if hasattr(rate, '__getitem__'):
                    rates_list.append({
                        'time': int(rate[0]) if len(rate) > 0 else 0,
                        'open': float(rate[1]) if len(rate) > 1 else 0,
                        'high': float(rate[2]) if len(rate) > 2 else 0,
                        'low': float(rate[3]) if len(rate) > 3 else 0,
                        'close': float(rate[4]) if len(rate) > 4 else 0,
                        'tick_volume': int(rate[5]) if len(rate) > 5 else 0,
                        'spread': int(rate[6]) if len(rate) > 6 else 0,
                        'real_volume': int(rate[7]) if len(rate) > 7 else 0
                    })
                else:
                    # Handle case where rate is not iterable
                    rates_list.append({
                        'time': 0,
                        'open': 0,
                        'high': 0,
                        'low': 0,
                        'close': 0,
                        'tick_volume': 0,
                        'spread': 0,
                        'real_volume': 0
                    })
            print("RESULT:" + json.dumps(rates_list))
        else:
            print("RESULT:[]")
        mt5.shutdown()
    else:
        print("RESULT:[]")
except Exception as e:
    print("RESULT:[]")
'''
        
        try:
            result = self._run_wine_python_script(script)
            # Extract only the RESULT line
            lines = result.split('\n')
            json_line = None
            for line in lines:
                if line.startswith("RESULT:"):
                    json_line = line[7:]  # Remove "RESULT:" prefix
                    break
            
            if json_line and json_line != "[]":
                return json.loads(json_line)
            return []
        except Exception as e:
            logger.error(f"Error copying rates for {symbol}: {e}")
            return []

    def copy_rates_range(self, symbol: str, timeframe: int, start_time: datetime, end_time: datetime) -> Optional[List[Dict]]:
        """Copy rates in a specific time range"""
        # Convert datetime to timestamp for MT5
        start_timestamp = int(start_time.timestamp())
        end_timestamp = int(end_time.timestamp())
        
        script = '''
import json
import MetaTrader5 as mt5
from datetime import datetime

try:
    if mt5.initialize():
        # Convert timestamps back to datetime
        start_time = datetime.fromtimestamp(''' + str(start_timestamp) + ''')
        end_time = datetime.fromtimestamp(''' + str(end_timestamp) + ''')
        
        rates = mt5.copy_rates_range("''' + symbol + '''", ''' + str(timeframe) + ''', start_time, end_time)
        if rates is not None and len(rates) > 0:
            # Convert to list of dictionaries for JSON serialization
            data_list = []
            for rate in rates:
                data_list.append({
                    'time': int(rate[0]),  # time
                    'open': float(rate[1]),  # open
                    'high': float(rate[2]),  # high
                    'low': float(rate[3]),   # low
                    'close': float(rate[4]), # close
                    'tick_volume': int(rate[5]), # tick_volume
                    'spread': int(rate[6]),  # spread
                    'real_volume': int(rate[7])  # real_volume
                })
            print("RESULT:" + json.dumps(data_list))
        else:
            print("RESULT:[]")
        mt5.shutdown()
    else:
        print("RESULT:[]")
except Exception as e:
    print("RESULT:[]")
'''

        try:
            result = self._run_wine_python_script(script)
            # Extract only the RESULT line
            lines = result.split('\n')
            json_line = None
            for line in lines:
                if line.startswith("RESULT:"):
                    json_line = line[7:]  # Remove "RESULT:" prefix
                    break
            
            if json_line and json_line != "[]":
                return json.loads(json_line)
            return []
        except Exception as e:
            logger.error(f"Error copying rates range for {symbol}: {e}")
            return []

# For compatibility with existing code, we'll make this module look like MT5
# This allows importing WineMT5Connector as mt5
def initialize() -> bool:
    """Initialize MT5 connection"""
    connector = WineMT5Connector()
    return connector.initialize()

def shutdown() -> None:
    """Shutdown MT5 connection"""
    # For Wine MT5, we don't need to do anything special for shutdown
    # Each script handles its own initialization and shutdown
    pass

def symbol_info(symbol: str) -> Optional[Dict]:
    """Get symbol info"""
    connector = WineMT5Connector()
    return connector.get_symbol_info(symbol)

def copy_rates_from_pos(symbol: str, timeframe: int, start_pos: int, count: int) -> Optional[List[Dict]]:
    """Copy rates from position"""
    connector = WineMT5Connector()
    return connector.copy_rates_from_pos(symbol, timeframe, start_pos, count)

def copy_rates_range(symbol: str, timeframe: int, start_time: datetime, end_time: datetime) -> Optional[List[Dict]]:
    """Copy rates in a specific time range"""
    connector = WineMT5Connector()
    return connector.copy_rates_range(symbol, timeframe, start_time, end_time)

# Constants for timeframes
TIMEFRAME_M1 = 1
TIMEFRAME_M5 = 5
TIMEFRAME_M15 = 15
TIMEFRAME_M30 = 30
TIMEFRAME_H1 = 60
TIMEFRAME_H4 = 240
TIMEFRAME_D1 = 1440
TIMEFRAME_W1 = 10080
TIMEFRAME_MN1 = 43200

# Export the connector
wine_mt5_connector = WineMT5Connector()