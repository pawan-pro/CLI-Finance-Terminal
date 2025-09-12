"""
Mock MetaTrader5 module for testing on non-Windows systems
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock MT5 constants
TIMEFRAME_M1 = 1
TIMEFRAME_M5 = 5
TIMEFRAME_M15 = 15
TIMEFRAME_M30 = 30
TIMEFRAME_H1 = 60
TIMEFRAME_H4 = 240
TIMEFRAME_D1 = 1440
TIMEFRAME_W1 = 10080
TIMEFRAME_MN1 = 43200

# Mock symbol info structure
class SymbolInfo:
    def __init__(self, **kwargs):
        self.name = kwargs.get('name', 'MOCK_SYMBOL')
        self.path = kwargs.get('path', 'Mock/Symbols')
        self.description = kwargs.get('description', 'Mock Symbol')
        self.ask = kwargs.get('ask', 1.0)
        self.bid = kwargs.get('bid', 0.999)
        self.last = kwargs.get('last', 1.0)
        self.volume = kwargs.get('volume', 1000)
        self.spread = kwargs.get('spread', 1)
        self.digits = kwargs.get('digits', 5)
        self.trade_mode = kwargs.get('trade_mode', 0)
        self.trade_stops_level = kwargs.get('trade_stops_level', 0)
        self.trade_freeze_level = kwargs.get('trade_freeze_level', 0)
        self.point = kwargs.get('point', 0.00001)
        self.high = kwargs.get('high', 1.001)
        self.low = kwargs.get('low', 0.999)
        self.time = kwargs.get('time', int(datetime.now().timestamp()))
        self.time_msc = kwargs.get('time_msc', int(datetime.now().timestamp() * 1000))
        self.session_open = kwargs.get('session_open', 0.9995)
        self.session_close = kwargs.get('session_close', 1.0005)

# Global state
_initialized = False

def initialize() -> bool:
    """Initialize MT5 connection"""
    global _initialized
    _initialized = True
    logger.info("Mock MT5 initialized")
    return True

def shutdown() -> None:
    """Shutdown MT5 connection"""
    global _initialized
    _initialized = False
    logger.info("Mock MT5 shutdown")

def symbols_get() -> List[SymbolInfo]:
    """Get list of available symbols"""
    if not _initialized:
        return None
    
    # Return mock symbols
    mock_symbols = [
        SymbolInfo(name='EURUSD', ask=1.0850, bid=1.0848, description='Euro vs US Dollar'),
        SymbolInfo(name='GBPUSD', ask=1.2700, bid=1.2698, description='British Pound vs US Dollar'),
        SymbolInfo(name='USDJPY', ask=149.50, bid=149.48, description='US Dollar vs Japanese Yen'),
        SymbolInfo(name='USDCAD', ask=1.3500, bid=1.3498, description='US Dollar vs Canadian Dollar'),
        SymbolInfo(name='USDCHF', ask=0.9200, bid=0.9198, description='US Dollar vs Swiss Franc'),
        SymbolInfo(name='AUDUSD', ask=0.6500, bid=0.6498, description='Australian Dollar vs US Dollar'),
        SymbolInfo(name='NZDUSD', ask=0.6000, bid=0.5998, description='New Zealand Dollar vs US Dollar'),
        SymbolInfo(name='XAUUSD', ask=1950.00, bid=1949.80, description='Gold vs US Dollar'),
        SymbolInfo(name='XAGUSD', ask=23.50, bid=23.48, description='Silver vs US Dollar'),
        SymbolInfo(name='USOIL', ask=85.00, bid=84.98, description='US Oil'),
        SymbolInfo(name='UKOIL', ask=88.00, bid=87.98, description='UK Oil'),
        SymbolInfo(name='SPX500', ask=4500.00, bid=4499.50, description='S&P 500'),
        SymbolInfo(name='DJI30', ask=35000.00, bid=34999.50, description='Dow Jones Industrial Average'),
        SymbolInfo(name='NDX100', ask=15000.00, bid=14999.50, description='NASDAQ 100'),
        SymbolInfo(name='DAX30', ask=16000.00, bid=15999.50, description='DAX 30'),
        SymbolInfo(name='FTSE100', ask=7800.00, bid=7799.50, description='FTSE 100'),
        SymbolInfo(name='VIX', ask=15.50, bid=15.48, description='CBOE Volatility Index')
    ]
    
    return mock_symbols

def symbol_info(symbol_name: str) -> Optional[SymbolInfo]:
    """Get information about a specific symbol"""
    if not _initialized:
        return None
    
    # Get all symbols and find the matching one
    symbols = symbols_get()
    if symbols is None:
        return None
    
    for symbol in symbols:
        if symbol.name == symbol_name:
            return symbol
    
    return None

def copy_rates_range(symbol: str, timeframe: int, start_time: datetime, end_time: datetime) -> Optional[np.ndarray]:
    """Copy historical data for a symbol in a specified time range"""
    if not _initialized:
        return None
    
    # Generate mock data
    delta = end_time - start_time
    num_periods = max(1, int(delta.total_seconds() / (timeframe * 60)))
    
    # Generate time series
    times = [start_time + timedelta(minutes=timeframe * i) for i in range(num_periods)]
    
    # Generate OHLC data with some randomness
    opens = [1.0 + np.random.normal(0, 0.001) for _ in range(num_periods)]
    highs = [o + np.random.uniform(0, 0.002) for o in opens]
    lows = [o - np.random.uniform(0, 0.002) for o in opens]
    closes = [np.random.uniform(low, high) for low, high in zip(lows, highs)]
    volumes = [int(np.random.uniform(1000, 10000)) for _ in range(num_periods)]
    spreads = [int(np.random.uniform(1, 5)) for _ in range(num_periods)]
    
    # Create structured array
    dtype = [
        ('time', 'datetime64[s]'),
        ('open', 'f8'),
        ('high', 'f8'),
        ('low', 'f8'),
        ('close', 'f8'),
        ('tick_volume', 'i8'),
        ('spread', 'i8'),
        ('real_volume', 'i8')
    ]
    
    data = np.array(
        list(zip(times, opens, highs, lows, closes, volumes, spreads, volumes)),
        dtype=dtype
    )
    
    return data

def copy_rates_from_pos(symbol: str, timeframe: int, start_pos: int, count: int) -> Optional[np.ndarray]:
    """Get bars from the specified position counting from the last bar"""
    if not _initialized:
        return None
    
    # Generate mock data for the last 'count' bars
    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=timeframe * (count + start_pos))
    
    return copy_rates_range(symbol, timeframe, start_time, end_time)