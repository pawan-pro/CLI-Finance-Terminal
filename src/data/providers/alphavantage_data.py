"""
Alpha Vantage Data Provider
This module provides data fetching capabilities using the Alpha Vantage API,
replacing the previous MT5/Finhub-based implementations.
"""
import pandas as pd
from datetime import datetime, timedelta
import pytz
import requests
from typing import List, Dict, Optional, Tuple
import logging
import json
import time
from urllib.parse import urlencode

# Local imports
from src.data.cache_manager import cache_manager
from src.config.symbol_map import map_symbol_for_request, get_internal_symbol

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlphaVantageDataFetcher:
    """Class to fetch data from Alpha Vantage API"""
    
    def __init__(self, api_key: str, use_cache: bool = True, cache_ttl: int = 3600):
        """
        Initialize Alpha Vantage connection
        
        Args:
            api_key: Alpha Vantage API key
            use_cache: Whether to use caching
            cache_ttl: Cache time-to-live in seconds
        """
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
        self.use_cache = use_cache
        self.cache_ttl = cache_ttl
        
        # Validate API key
        if not self.api_key:
            raise ValueError("Alpha Vantage API key is required")
    
    def _get_cache_key(self, *args) -> str:
        """Generate cache key from arguments"""
        return f"alphavantage_{'_'.join(str(arg) for arg in args)}"
    
    def _make_request(self, params: Dict) -> Optional[Dict]:
        """
        Make a request to the Alpha Vantage API
        
        Args:
            params: Request parameters (function, symbol, etc.)
            
        Returns:
            Response data or None
        """
        # Add API key to parameters
        params['apikey'] = self.api_key
        
        url = f"{self.base_url}?{urlencode(params)}"
        
        try:
            # Add delay to respect API rate limits (5 calls per minute free tier)
            time.sleep(12)  # 12 seconds to stay well under the limit
            
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            # Check for API errors
            if "Error Message" in data:
                logger.error(f"Alpha Vantage error: {data['Error Message']}")
                return None
            if "Note" in data:
                logger.warning(f"Alpha Vantage note: {data['Note']}")
                return None
            if "Information" in data:
                logger.info(f"Alpha Vantage info: {data['Information']}")
                return None
                
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to {url}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON response from {url}: {e}")
            return None

    def get_available_symbols(self) -> List[str]:
        """
        Get list of available symbols in Alpha Vantage
        This is a simplified implementation - in practice you might want to fetch
        a specific exchange or sector rather than all symbols.
        """
        cache_key = self._get_cache_key("symbols")
        
        # Try to get from cache first
        if self.use_cache:
            cached = cache_manager.get(cache_key, self.cache_ttl)
            if cached is not None:
                logger.info("Returning symbols from cache")
                return cached
        
        # Note: Alpha Vantage doesn't have a universal symbol endpoint, but we can get symbols for specific exchanges
        # For now, we'll return a placeholder list that represents major asset classes
        symbols = [
            "^GSPC", "^DJI", "^IXIC", "^GDAXI", "^FTSE", "^FCHI", "^N225", "^HSI",  # Indices
            "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "JPM", "XOM",  # Stocks
            "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF",  # Forex
            "XAUUSD", "XAGUSD", "CL=F", "GC=F",  # Commodities
        ]
        
        # Cache the result
        if self.use_cache:
            cache_manager.set(cache_key, symbols)
        
        logger.info(f"Retrieved {len(symbols)} symbols from Alpha Vantage")
        return symbols
    
    def get_quote(self, symbol: str) -> Optional[Dict]:
        """
        Fetches the latest quote for a specific symbol, using cache.
        
        Args:
            symbol: Symbol to fetch quote for (internal application symbol)
            
        Returns:
            Quote information dictionary
        """
        # Map internal symbol to Alpha Vantage symbol
        av_symbol = map_symbol_for_request(symbol, "alphavantage")
        cache_key = self._get_cache_key("quote", symbol)
        
        # Try to get from cache first
        if self.use_cache:
            cached = cache_manager.get(cache_key, self.cache_ttl)
            if cached is not None:
                logger.info(f"Returning quote for {symbol} from cache")
                return cached
        
        # Log data fetch attempt
        logger.info(f"Attempting to fetch quote for: {symbol} (mapped to {av_symbol})")
        
        # Get quote data from Alpha Vantage using GLOBAL_QUOTE
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": av_symbol
        }
        quote_response = self._make_request(params)
        
        if quote_response is None or "Global Quote" not in quote_response:
            logger.error(f"Failed to get quote for {symbol} (mapped to {av_symbol})")
            return None
        
        quote_data = quote_response["Global Quote"]
        if not quote_data:
            logger.error(f"No quote data found for {symbol} (mapped to {av_symbol})")
            return None
        
        # Construct quote dictionary matching expected format
        quote_dict = {
            'name': symbol,  # Use original symbol name for consistency
            'description': f"{av_symbol} data",  # Description based on the API response
            'ask': float(quote_data.get('05. price', 0)),  # Current price
            'bid': float(quote_data.get('05. price', 0)),  # Using current price as bid (for now)
            'last': float(quote_data.get('05. price', 0)),  # Last traded price
            'volume': int(quote_data.get('06. volume', 0)),  # Volume
            'spread': 0,  # Calculate spread if available
            'digits': 2,  # Default to 2 decimal places
            'high': float(quote_data.get('03. high', 0)),  # High price
            'low': float(quote_data.get('04. low', 0)),   # Low price
            'time': datetime.now(),  # Time (Alpha Vantage doesn't always provide exact timestamp in global quote)
            'change': float(quote_data.get('09. change', 0)),  # Change
            'change_percent': float(quote_data.get('10. change percent', '0').replace('%', '')),  # Change percentage
        }
        
        # Cache the result
        if self.use_cache:
            cache_manager.set(cache_key, quote_dict)
        
        logger.info(f"Got quote for {symbol}")
        return quote_dict

    def get_symbol_info(self, symbol: str) -> Optional[Dict]:
        """
        Fetches information about a specific symbol, using cache.
        This method is an alias for get_quote to maintain compatibility with the existing interface.
        
        Args:
            symbol: Symbol to fetch info for (internal application symbol)
            
        Returns:
            Symbol information dictionary
        """
        return self.get_quote(symbol)

    def fetch_historical_data(self, symbol: str, resolution: str, start_time: datetime, end_time: datetime) -> pd.DataFrame:
        """
        Fetch historical data for a symbol
        
        Args:
            symbol: Symbol to fetch data for (internal application symbol)
            resolution: Time resolution (e.g., 'D', 'W', 'M', '1', '5', etc.)
            start_time: Start time for historical data
            end_time: End time for historical data
            
        Returns:
            DataFrame with historical data
        """
        # Map internal symbol to Alpha Vantage symbol
        av_symbol = map_symbol_for_request(symbol, "alphavantage")
        cache_key = self._get_cache_key("historical", symbol, resolution, 
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
        
        # Determine the appropriate function based on resolution
        if resolution in ['1', '5', '15', '30', '60']:
            # Intraday data
            params = {
                'function': f'TIME_SERIES_INTRADAY',
                'symbol': av_symbol,
                'interval': f'{resolution}min',
                'outputsize': 'full'  # Get full history, we'll filter by time
            }
            time_series_key = f'Time Series ({resolution}min)'
        elif resolution in ['daily', 'D']:
            # Daily data
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': av_symbol,
                'outputsize': 'full'  # Get full history, we'll filter by time
            }
            time_series_key = 'Time Series (Daily)'
        elif resolution in ['weekly', 'W']:
            # Weekly data
            params = {
                'function': 'TIME_SERIES_WEEKLY',
                'symbol': av_symbol
            }
            time_series_key = 'Weekly Time Series'
        elif resolution in ['monthly', 'M']:
            # Monthly data
            params = {
                'function': 'TIME_SERIES_MONTHLY',
                'symbol': av_symbol
            }
            time_series_key = 'Monthly Time Series'
        else:
            # Default to daily
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': av_symbol,
                'outputsize': 'full'
            }
            time_series_key = 'Time Series (Daily)'
        
        response = self._make_request(params)
        
        if response is None or time_series_key not in response:
            logger.warning(f"Failed to fetch historical data for {symbol} (mapped to {av_symbol})")
            return pd.DataFrame()
        
        time_series_data = response[time_series_key]
        
        # Create DataFrame and filter by requested date range
        rows = []
        for date_str, values in time_series_data.items():
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            # If the date is within our requested range
            if start_time <= date_obj <= end_time:
                rows.append({
                    'time': date_obj,
                    'open': float(values['1. open']),
                    'high': float(values['2. high']),
                    'low': float(values['3. low']),
                    'close': float(values['4. close']),
                    'volume': int(values['5. volume'])
                })
        
        # Create DataFrame
        df = pd.DataFrame(rows)
        
        if not df.empty:
            # Sort by time to ensure correct order
            df = df.sort_values(by='time').reset_index(drop=True)
        else:
            logger.warning(f"No historical data found for {symbol} in the specified date range")
        
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

    def get_24h_change(self, symbol: str) -> Tuple[float, float]:
        """
        Calculate the 24-hour change and percentage change for a symbol.
        
        Args:
            symbol: Symbol to calculate change for (internal application symbol)
            
        Returns:
            Tuple of (change, percentage_change)
        """
        current_info = self.get_quote(symbol)
        if not current_info or current_info.get('ask', 0) == 0:
            logger.warning(f"Could not get current info or ask price for {symbol}")
            return 0.0, 0.0

        current_price = current_info['ask']
        
        # Get historical data for the last day
        end_time = datetime.now(pytz.utc)
        start_time = end_time - timedelta(days=1)

        # Fetch daily historical data to get the previous day's closing price
        # Use a larger time window to ensure we get at least the previous day's data
        extended_start_time = start_time - timedelta(days=7)  # Look back a week to ensure we find data
        historical_data = self.fetch_historical_data(symbol, 'daily', extended_start_time, start_time)
        
        if historical_data.empty:
            logger.warning(f"No historical data available for {symbol} in the past week.")
            return 0.0, 0.0

        # Sort by time to ensure correct order and get the most recent historical price before now
        historical_data = historical_data.sort_values(by='time', ascending=False).reset_index(drop=True)
        
        # Get the previous day's closing price (or most recent available before today)
        if not historical_data.empty:
            previous_price = historical_data.iloc[0]['close']
        else:
            logger.warning(f"No suitable historical data found for {symbol}")
            return 0.0, 0.0

        change = current_price - previous_price
        pct_change = (change / previous_price * 100) if previous_price != 0 else 0.0

        return change, pct_change

    def get_financial_news(self, category: str = "general", min_id: int = None) -> List[Dict]:
        """
        Fetch financial news from various sources.
        Alpha Vantage doesn't provide a news endpoint in the free tier.
        This method could be enhanced to use other free news APIs or return cached data.
        """
        cache_key = self._get_cache_key("news", category, min_id or 0)
        
        # Try to get from cache first
        if self.use_cache:
            cached = cache_manager.get(cache_key, self.cache_ttl)
            if cached is not None:
                logger.info("Returning news from cache")
                return cached
        
        # Since Alpha Vantage free tier doesn't provide news, return empty list
        # In a full implementation, we might want to integrate with NewsAPI or other sources
        news_data = []
        
        # Cache the result
        if self.use_cache:
            cache_manager.set(cache_key, news_data)
        
        return news_data

    def get_economic_calendar(self, from_date: str = None, to_date: str = None) -> List[Dict]:
        """
        Fetch economic calendar data.
        Alpha Vantage doesn't provide detailed economic calendar in the free tier.
        This method might be integrated with other economic data sources in a full implementation.
        """
        cache_key = self._get_cache_key("economic_calendar", from_date or "", to_date or "")
        
        # Try to get from cache first
        if self.use_cache:
            cached = cache_manager.get(cache_key, self.cache_ttl)
            if cached is not None:
                logger.info("Returning economic calendar from cache")
                return cached
        
        # Alpha Vantage doesn't have an economic calendar endpoint in the free tier
        # Return empty list - in a complete implementation we might want to use
        # other services or a CSV file for this data
        calendar_data = []
        
        # Cache the result
        if self.use_cache:
            cache_manager.set(cache_key, calendar_data)
        
        return calendar_data