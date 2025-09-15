# Try to import real MT5, fallback to mock if not available
try:
    # First try direct import (for Windows or Wine with proper setup)
    import MetaTrader5
    mt5 = MetaTrader5
    MT5_AVAILABLE = True
    print("Using real MT5 connection")
except ImportError:
    try:
        # Try importing Wine MT5 connector as mt5
        from src.data.providers.wine_mt5_connector import WineMT5Connector
        # Create a wrapper to make it compatible with MT5 API
        import src.data.providers.wine_mt5_connector as mt5
        MT5_AVAILABLE = True
        print("Using real MT5 connection (Wine connector)")
    except ImportError:
        # Use mock MT5 for development/testing
        import src.data.providers.mock_mt5 as mt5
        MT5_AVAILABLE = False
        print("Warning: Using mock MT5. For production with Wine, ensure MT5 Python package is properly installed in Wine environment.")
import pandas as pd
from datetime import datetime, timedelta
import pytz
from typing import List, Dict, Optional, Tuple
import logging
import json

# Local imports
from src.data.cache_manager import cache_manager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MT5DataFetcher:
    """Class to fetch data from MT5 terminal"""
    
    def __init__(self, use_cache: bool = True, cache_ttl: int = 3600, use_wine_mt5: bool = False):
        """Initialize MT5 connection"""
        self.use_cache = use_cache
        self.cache_ttl = cache_ttl
        self.use_wine_mt5 = use_wine_mt5
        
        # If using Wine MT5, we'll use the Wine MT5 connector methods
        if use_wine_mt5:
            logger.info("Using Wine MT5 connector for data fetching")
            # Import Wine MT5 connector for direct use
            from src.data.providers.wine_mt5_connector import WineMT5Connector
            self.wine_connector = WineMT5Connector()
            # Don't initialize MT5 directly here, we'll use Wine MT5 connector methods
        else:
            if not mt5.initialize():
                logger.error("MT5 initialization failed")
                raise Exception("MT5 initialization failed")
            logger.info("MT5 initialized successfully")
    
    def _get_cache_key(self, *args) -> str:
        """Generate cache key from arguments"""
        return f"mt5_{'_'.join(str(arg) for arg in args)}"
    
    def get_available_symbols(self) -> List[str]:
        """Get list of available symbols in MT5"""
        cache_key = self._get_cache_key("symbols")
        
        # Try to get from cache first
        if self.use_cache:
            cached = cache_manager.get(cache_key, self.cache_ttl)
            if cached is not None:
                logger.info("Returning symbols from cache")
                return cached
        
        symbols = mt5.symbols_get()
        if symbols is None:
            logger.error("Failed to get symbols")
            return []
        
        symbol_names = [symbol.name for symbol in symbols]
        logger.info(f"Retrieved {len(symbol_names)} symbols from MT5")
        
        # Cache the result
        if self.use_cache:
            cache_manager.set(cache_key, symbol_names)
        
        return symbol_names
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict]:
        """Fetches information about a specific symbol, using cache."""
        cache_key = self._get_cache_key("symbol_info", symbol)
        
        # Try to get from cache first
        if self.use_cache:
            cached = cache_manager.get(cache_key, self.cache_ttl)
            if cached is not None:
                logger.info(f"Returning info for {symbol} from cache")
                return cached
        
        # If using Wine MT5, we need to handle this differently
        if self.use_wine_mt5:
            # For Wine MT5, we'll use the Wine MT5 connector methods
            try:
                wine_symbol_info = self.wine_connector.get_symbol_info(symbol)
                if wine_symbol_info:
                    info_dict = {
                        'name': wine_symbol_info['name'],
                        'description': wine_symbol_info.get('description', ''),
                        'ask': wine_symbol_info['ask'],
                        'bid': wine_symbol_info['bid'],
                        'last': wine_symbol_info.get('last', 0),
                        'volume': wine_symbol_info.get('volume', 0),
                        'spread': wine_symbol_info.get('spread', 0),
                        'digits': wine_symbol_info.get('digits', 0),
                        'high': wine_symbol_info.get('high', 0),
                        'low': wine_symbol_info.get('low', 0),
                        'time': datetime.fromtimestamp(wine_symbol_info.get('time', 0)) if wine_symbol_info.get('time', 0) else None,
                    }
                    
                    # Apply fallback logic for zero ask/bid values
                    # Check if both ask and bid are zero, try to use last price
                    if info_dict.get('ask', 0) == 0 and info_dict.get('bid', 0) == 0:
                        if info_dict.get('last', 0) != 0:
                            info_dict['ask'] = info_dict['last']
                            info_dict['bid'] = info_dict['last']
                        # If last is also zero, we keep the zeros to indicate no data
                    
                    # Cache the result
                    if self.use_cache:
                        cache_manager.set(cache_key, info_dict)
                    
                    return info_dict
            except Exception as e:
                logger.error(f"Error getting symbol info for {symbol} from Wine MT5: {e}")
                return None
        
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            logger.warning(f"Failed to get symbol info for {symbol}")
            return None
        
        # Handle both dict and object formats
        if isinstance(symbol_info, dict):
            info_dict = {
                'name': symbol_info.get('name'),
                'path': symbol_info.get('path'),
                'description': symbol_info.get('description'),
                'ask': symbol_info.get('ask'),
                'bid': symbol_info.get('bid'),
                'last': symbol_info.get('last'),
                'volume': symbol_info.get('volume'),
                'spread': symbol_info.get('spread'),
                'digits': symbol_info.get('digits'),
                'trade_mode': symbol_info.get('trade_mode'),
                'trade_stops_level': symbol_info.get('trade_stops_level'),
                'trade_freeze_level': symbol_info.get('trade_freeze_level'),
                'point': symbol_info.get('point'),
                'high': symbol_info.get('high'),
                'low': symbol_info.get('low'),
                'time': datetime.fromtimestamp(symbol_info.get('time')) if symbol_info.get('time') else None,
                'time_msc': symbol_info.get('time_msc'),
                'session_open': symbol_info.get('session_open'),
                'session_close': symbol_info.get('session_close'),
            }
        else:
            info_dict = {
                'name': symbol_info.name,
                'path': symbol_info.path,
                'description': symbol_info.description,
                'ask': symbol_info.ask,
                'bid': symbol_info.bid,
                'last': symbol_info.last,
                'volume': symbol_info.volume,
                'spread': symbol_info.spread,
                'digits': symbol_info.digits,
                'trade_mode': symbol_info.trade_mode,
                'trade_stops_level': symbol_info.trade_stops_level,
                'trade_freeze_level': symbol_info.trade_freeze_level,
                'point': symbol_info.point,
                'high': symbol_info.high,
                'low': symbol_info.low,
                'time': datetime.fromtimestamp(symbol_info.time) if symbol_info.time else None,
                'time_msc': symbol_info.time_msc,
                'session_open': symbol_info.session_open,
                'session_close': symbol_info.session_close,
            }
        
        # Apply fallback logic for zero ask/bid values
        # Check if both ask and bid are zero, try to use last price
        if info_dict.get('ask', 0) == 0 and info_dict.get('bid', 0) == 0:
            if info_dict.get('last', 0) != 0:
                info_dict['ask'] = info_dict['last']
                info_dict['bid'] = info_dict['last']
            # If last is also zero, we keep the zeros to indicate no data
        
        # Cache the result
        if self.use_cache:
            cache_manager.set(cache_key, info_dict)
        
        return info_dict
    
    def fetch_historical_data(self, symbol: str, timeframe: int, start_time: datetime, end_time: datetime) -> pd.DataFrame:
        """Fetch historical data for a symbol"""
        cache_key = self._get_cache_key("historical", symbol, timeframe, 
                                       start_time.isoformat(), end_time.isoformat())
        
        # Try to get from cache first
        if self.use_cache:
            cached = cache_manager.get(cache_key, self.cache_ttl)
            if cached is not None:
                logger.info(f"Returning historical data for {symbol} from cache")
                df = pd.DataFrame(cached)
                if not df.empty and 'time' in df.columns:
                    df['time'] = pd.to_datetime(df['time'])
                return df
        
        # If using Wine MT5, we need to handle this differently
        if self.use_wine_mt5:
            try:
                # For Wine MT5, we'll use copy_rates_from_pos to get recent data
                # This is a simplified approach - in a real implementation, you'd want to
                # implement a proper copy_rates_range equivalent or use a different approach
                rates = self.wine_connector.copy_rates_from_pos(symbol, timeframe, 0, 1000)  # Get last 1000 bars
                if rates:
                    df = pd.DataFrame(rates)
                    if not df.empty:
                        df['time'] = pd.to_datetime(df['time'], unit='s', utc=True)
                        
                        # Ensure volume data is present
                        if 'real_volume' in df.columns:
                            df['volume'] = df['real_volume']
                        elif 'tick_volume' in df.columns:
                            df['volume'] = df['tick_volume']
                        else:
                            df['volume'] = df.get('tick_volume', 0)
                        
                        # Cache the result
                        if self.use_cache:
                            # Convert DataFrame to dict for caching
                            # Convert Timestamp objects to strings to make them JSON serializable
                            df_copy = df.copy()
                            for col in df_copy.columns:
                                if df_copy[col].dtype == 'datetime64[ns]':
                                    df_copy[col] = df_copy[col].astype(str)
                            cache_data = df_copy.to_dict('records')
                            cache_manager.set(cache_key, cache_data)
                        
                        return df
            except Exception as e:
                logger.error(f"Error fetching historical data for {symbol} from Wine MT5: {e}")
        
        # Convert to UTC for MT5
        start_time_utc = start_time.astimezone(pytz.UTC)
        end_time_utc = end_time.astimezone(pytz.UTC)
        
        rates = mt5.copy_rates_range(symbol, timeframe, start_time_utc, end_time_utc)
        if rates is None:
            logger.warning(f"Failed to fetch data for {symbol}")
            return pd.DataFrame()
        
        df = pd.DataFrame(rates)
        if df.empty:
            return df
            
        df['time'] = pd.to_datetime(df['time'], unit='s', utc=True)
        
        # Ensure volume data is present
        if 'real_volume' in df.columns and df['real_volume'].any():
            df['volume'] = df['real_volume']
        elif 'tick_volume' in df.columns:
            df['volume'] = df['tick_volume']
        else:
            df['volume'] = 0
        
        # Cache the result
        if self.use_cache:
            # Convert DataFrame to dict for caching
            # Convert Timestamp objects to strings to make them JSON serializable
            df_copy = df.copy()
            for col in df_copy.columns:
                if df_copy[col].dtype == 'datetime64[ns]':
                    df_copy[col] = df_copy[col].astype(str)
            cache_data = df_copy.to_dict('records')
            cache_manager.set(cache_key, cache_data)
        
        return df
    
    def fetch_latest_data(self, symbol: str, timeframe: int, count: int = 100) -> pd.DataFrame:
        """Fetch latest data for a symbol"""
        cache_key = self._get_cache_key("latest", symbol, timeframe, count)
        
        # Try to get from cache first
        if self.use_cache:
            cached = cache_manager.get(cache_key, self.cache_ttl)
            if cached is not None:
                logger.info(f"Returning latest data for {symbol} from cache")
                df = pd.DataFrame(cached)
                if not df.empty and 'time' in df.columns:
                    df['time'] = pd.to_datetime(df['time'])
                return df
        
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
        if rates is None:
            logger.warning(f"Failed to fetch latest data for {symbol}")
            return pd.DataFrame()
        
        df = pd.DataFrame(rates)
        if df.empty:
            return df
            
        df['time'] = pd.to_datetime(df['time'], unit='s', utc=True)
        
        # Ensure volume data is present
        if 'real_volume' in df.columns and df['real_volume'].any():
            df['volume'] = df['real_volume']
        elif 'tick_volume' in df.columns:
            df['volume'] = df['tick_volume']
        else:
            df['volume'] = 0
        
        # Cache the result
        if self.use_cache:
            # Convert DataFrame to dict for caching
            # Convert Timestamp objects to strings to make them JSON serializable
            df_copy = df.copy()
            for col in df_copy.columns:
                if df_copy[col].dtype == 'datetime64[ns]':
                    df_copy[col] = df_copy[col].astype(str)
            cache_data = df_copy.to_dict('records')
            cache_manager.set(cache_key, cache_data)
        
        return df
    
    def get_market_watch(self) -> pd.DataFrame:
        """Get current market watch data for all available symbols"""
        cache_key = self._get_cache_key("market_watch")
        
        # Try to get from cache first
        if self.use_cache:
            cached = cache_manager.get(cache_key, self.cache_ttl)
            if cached is not None:
                logger.info("Returning market watch from cache")
                df = pd.DataFrame(cached)
                if not df.empty and 'time' in df.columns:
                    df['time'] = pd.to_datetime(df['time'])
                return df
        
        symbols = self.get_available_symbols()
        watch_data = []
        
        for symbol_name in symbols[:50]:  # Limit to first 50 symbols to avoid overload
            info = self.get_symbol_info(symbol_name)
            if info:
                watch_data.append(info)
        
        df = pd.DataFrame(watch_data)
        
        # Cache the result
        if self.use_cache:
            # Convert DataFrame to dict for caching
            # Convert Timestamp objects to strings to make them JSON serializable
            df_copy = df.copy()
            for col in df_copy.columns:
                if df_copy[col].dtype == 'datetime64[ns]':
                    df_copy[col] = df_copy[col].astype(str)
            cache_data = df_copy.to_dict('records')
            cache_manager.set(cache_key, cache_data)
        
        return df
    
    def shutdown(self):
        """Shutdown MT5 connection"""
        mt5.shutdown()
        logger.info("MT5 connection shutdown")

# Example usage
if __name__ == "__main__":
    try:
        fetcher = MT5DataFetcher()
        
        # Get available symbols
        symbols = fetcher.get_available_symbols()
        print(f"Available symbols: {len(symbols)}")
        
        # Show some example symbols
        print("First 10 symbols:")
        for symbol in symbols[:10]:
            print(f"  {symbol}")
        
        # Get info for a specific symbol
        if symbols:
            symbol_info = fetcher.get_symbol_info(symbols[0])
            if symbol_info:
                print(f"\nSymbol info for {symbols[0]}:")
                for key, value in symbol_info.items():
                    print(f"  {key}: {value}")
        
        # Fetch some historical data
        if symbols:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=7)
            
            data = fetcher.fetch_historical_data(
                symbols[0], 
                mt5.TIMEFRAME_H1, 
                start_time, 
                end_time
            )
            print(f"\nHistorical data for {symbols[0]}:")
            print(data.head())
        
        fetcher.shutdown()
        
    except Exception as e:
        print(f"Error: {e}")