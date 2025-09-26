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
import time

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
    
    def _run_wine_python_script(self, script: str, retries: int = 3, delay: int = 2) -> str:
        """
        Run a Python script in Wine Python environment with retry logic.
        
        Args:
            script: Python script to execute
            retries: Number of times to retry on failure.
            delay: Delay in seconds between retries.
            
        Returns:
            Output from the script
        """
        temp_script = None
        last_exception = None
        try:
            # Create temporary script file
            temp_dir = os.path.expanduser('~/.cache')
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            temp_script = os.path.join(temp_dir, 'temp_wine_mt5_connector.py')
            with open(temp_script, 'w') as f:
                f.write(script)
            logger.debug(f"Created temporary script at: {temp_script}")

            for attempt in range(retries):
                try:
                    # Convert the path to Windows format for Wine
                    wine_path = 'Z:' + temp_script.replace('/', '\\')

                    cmd = ['wine', 'python.exe', wine_path]
                    logger.debug(f"Attempt {attempt + 1}/{retries}: Running command: {' '.join(cmd)}")

                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30,
                                          env={**os.environ, 'MVK_CONFIG_LOG_LEVEL': '0'})

                    logger.debug(f"Command result - return code: {result.returncode}")
                    logger.debug(f"Command stdout: {result.stdout}")
                    if result.stderr:
                        logger.debug(f"Command stderr: {result.stderr}")

                    if result.returncode != 0:
                        raise Exception(f"Script execution failed with return code {result.returncode}: {result.stderr}")

                    # Success
                    return result.stdout.strip()

                except subprocess.TimeoutExpired as e:
                    logger.warning(f"Attempt {attempt + 1}/{retries}: Timeout expired. Retrying in {delay}s...")
                    last_exception = e
                    time.sleep(delay)
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1}/{retries}: Error running script: {e}. Retrying in {delay}s...")
                    last_exception = e
                    time.sleep(delay)

            logger.error(f"All {retries} attempts failed to run Wine Python script.")
            if last_exception:
                raise last_exception
            else:
                raise Exception("Unknown error after all retries.")
        finally:
            # Clean up the temporary script file
            if temp_script and os.path.exists(temp_script):
                os.remove(temp_script)
    
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

    def symbols_get(self) -> Optional[List[Dict]]:
        """Get all available symbols"""
        script = '''
import json
import MetaTrader5 as mt5

try:
    if mt5.initialize():
        symbols = mt5.symbols_get()
        if symbols is not None and len(symbols) > 0:
            symbols_list = []
            for symbol in symbols:
                # Convert symbol object to dictionary
                # Handle both object and tuple formats
                if hasattr(symbol, 'name'):
                    # Object format
                    symbol_dict = {
                        'name': symbol.name,
                        'path': getattr(symbol, 'path', ''),
                        'description': getattr(symbol, 'description', ''),
                        'ask': float(getattr(symbol, 'ask', 0)),
                        'bid': float(getattr(symbol, 'bid', 0)),
                        'last': float(getattr(symbol, 'last', 0)),
                        'volume': int(getattr(symbol, 'volume', 0)),
                        'spread': int(getattr(symbol, 'spread', 0)),
                        'digits': int(getattr(symbol, 'digits', 0)),
                        'high': float(getattr(symbol, 'high', 0)),
                        'low': float(getattr(symbol, 'low', 0)),
                        'time': int(getattr(symbol, 'time', 0)) if getattr(symbol, 'time', None) else 0
                    }
                else:
                    # Tuple format (index-based)
                    symbol_dict = {
                        'name': symbol[0] if len(symbol) > 0 else '',
                        'path': symbol[1] if len(symbol) > 1 else '',
                        'description': symbol[13] if len(symbol) > 13 else '',
                        'ask': float(symbol[2]) if len(symbol) > 2 else 0,
                        'bid': float(symbol[3]) if len(symbol) > 3 else 0,
                        'last': float(symbol[4]) if len(symbol) > 4 else 0,
                        'volume': int(symbol[5]) if len(symbol) > 5 else 0,
                        'spread': int(symbol[6]) if len(symbol) > 6 else 0,
                        'digits': int(symbol[7]) if len(symbol) > 7 else 0,
                        'high': float(symbol[8]) if len(symbol) > 8 else 0,
                        'low': float(symbol[9]) if len(symbol) > 9 else 0,
                        'time': int(symbol[10]) if len(symbol) > 10 else 0
                    }
                symbols_list.append(symbol_dict)
            print("RESULT:" + json.dumps(symbols_list))
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
            logger.error(f"Error getting symbols: {e}")
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

def symbols_get() -> Optional[List[Any]]:
    """Get all available symbols"""
    connector = WineMT5Connector()
    return connector.symbols_get()

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

def get_calendar_events() -> Optional[List[Dict]]:
    """Get economic calendar events"""
    connector = WineMT5Connector()
    script = '''
import json
import MetaTrader5 as mt5
from datetime import datetime, timedelta

try:
    if mt5.initialize():
        to_date = datetime.now() + timedelta(days=7)
        from_date = datetime.now() - timedelta(days=7)

        events = mt5.calendar_events(from_date, to_date)

        if events is not None and len(events) > 0:
            events_list = []
            for event in events:
                events_list.append({
                    'id': event.id,
                    'type': event.type,
                    'country_id': event.country_id,
                    'date': event.time,
                    'time_zone': event.time_zone,
                    'importance': event.importance,
                    'currency': event.currency,
                    'event': event.event,
                    'actual_value': event.actual_value,
                    'forecast_value': event.forecast_value,
                    'previous_value': event.previous_value,
                    'unit': event.unit
                })
            print("RESULT:" + json.dumps(events_list, default=str))
        else:
            print("RESULT:[]")
        mt5.shutdown()
    else:
        print("RESULT:[]")
except Exception as e:
    print(f"Error fetching calendar events: {e}")
    print("RESULT:[]")
'''

    try:
        result = connector._run_wine_python_script(script)
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
        logger.error(f"Error getting calendar events: {e}")
        return []

# Export the connector
wine_mt5_connector = WineMT5Connector()