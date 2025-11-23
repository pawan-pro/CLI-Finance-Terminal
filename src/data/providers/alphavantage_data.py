import pandas as pd
from datetime import datetime, timedelta
import requests
from typing import List, Dict, Optional
import logging
from urllib.parse import urlencode
import time
from io import StringIO

# Local imports
from src.data.cache_manager import cache_manager
from src.config.symbol_map import map_symbol_for_request, FOREX_SYMBOLS, CRYPTO_SYMBOLS
from src.data.providers.api_key_manager import api_key_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlphaVantageDataFetcher:
    """Optimized class to fetch data from Alpha Vantage API using a rotating API key and aggressive caching."""
    
    def __init__(self, use_cache: bool = True):
        self.base_url = "https://www.alphavantage.co/query"
        self.use_cache = use_cache

    def _get_cache_key(self, *args) -> str:
        # Create a key from sorted tuple of dictionary items for consistency
        key_args = []
        for arg in args:
            if isinstance(arg, dict):
                key_args.append(str(tuple(sorted(arg.items()))))
            else:
                key_args.append(str(arg))
        return f"alphavantage_{'_'.join(key_args)}"

    def _make_request(self, params: Dict, ttl: int) -> Optional[Dict]:
        """Makes a request to the Alpha Vantage API, handling rate limiting and caching with a specified TTL."""
        params['apikey'] = api_key_manager.get_key()
        # Create a cache key from the params, ignoring the API key, for reliable caching
        cache_key_params = {k: v for k, v in params.items() if k != 'apikey'}
        cache_key = self._get_cache_key(cache_key_params)
        
        if self.use_cache:
            cached = cache_manager.get(cache_key, ttl)
            if cached:
                logger.info(f"Returning cached data for {params.get('function')} on {params.get('symbol') or params.get('from_currency')}.")
                return cached

        logger.info(f"Making API request for {params['function']} on {params.get('symbol') or params.get('from_currency')}")
        
        time.sleep(1) # A small delay to be a good API citizen

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            if 'text/csv' in response.headers.get('Content-Type', ''):
                data = response.text
            else:
                data = response.json()

            if isinstance(data, dict) and ("Error Message" in data or "Note" in data):
                logger.warning(f"API Info/Error for {params.get('symbol')}: {data.get('Error Message') or data.get('Note')}")
                return None

            if self.use_cache:
                cache_manager.set(cache_key, data)
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {params.get('symbol')}: {e}")
            return None

    def get_global_quote(self, symbol: str) -> Optional[Dict]:
        """Fetches a quote for any asset class, calculating 24h change where necessary."""
        quote_ttl = 300 # 5 minutes
        internal_symbol = symbol
        av_symbol = map_symbol_for_request(internal_symbol)

        if internal_symbol in FOREX_SYMBOLS:
            from_currency, to_currency = av_symbol.split('/')
            params = {'function': 'CURRENCY_EXCHANGE_RATE', 'from_currency': from_currency, 'to_currency': to_currency}
            data = self._make_request(params, ttl=quote_ttl)
            if not (data and 'Realtime Currency Exchange Rate' in data): return None

            rate_data = data['Realtime Currency Exchange Rate']
            price = float(rate_data.get('5. Exchange Rate', 0))
            
            hist_data = self.get_historical_data(internal_symbol, days=2)
            change_pct = 0.0
            if hist_data is not None and not hist_data.empty and len(hist_data) > 1:
                prev_close = hist_data['close'].iloc[-2]
                change_pct = ((price - prev_close) / prev_close) * 100 if prev_close != 0 else 0

            return {'symbol': internal_symbol, 'price': price, 'change_percent': f"{change_pct:.2f}", 'volume': 'N/A'}

        elif internal_symbol in CRYPTO_SYMBOLS:
            params = {'function': 'DIGITAL_CURRENCY_DAILY', 'symbol': av_symbol, 'market': 'USD'}
            data = self._make_request(params, ttl=quote_ttl)
            if not (data and 'Time Series (Digital Currency Daily)' in data): return None

            time_series = data['Time Series (Digital Currency Daily)']
            dates = sorted(time_series.keys())
            if len(dates) < 2: return None

            latest_date, prev_date = dates[-1], dates[-2]
            price = float(time_series[latest_date].get('4a. close (USD)', 0))
            prev_close = float(time_series[prev_date].get('4a. close (USD)', 0))
            change_pct = ((price - prev_close) / prev_close) * 100 if prev_close != 0 else 0
            volume = float(time_series[latest_date].get('5. volume', 0))

            return {'symbol': internal_symbol, 'price': price, 'change_percent': f"{change_pct:.2f}", 'volume': volume}

        else: # Stocks, ETFs, Indices
            params = {'function': 'GLOBAL_QUOTE', 'symbol': av_symbol}
            data = self._make_request(params, ttl=quote_ttl)
            if not (data and 'Global Quote' in data and data['Global Quote']): return None
            
            quote = data['Global Quote']
            return {
                'symbol': internal_symbol, 'price': quote.get('05. price'),
                'change_percent': quote.get('10. change percent', '0%').strip('%'),
                'volume': quote.get('06. volume')
            }

    def get_historical_data(self, symbol: str, days: int = 90) -> pd.DataFrame:
        """Fetches daily historical data with a long cache TTL."""
        historical_ttl = 86400 # 24 hours
        av_symbol = map_symbol_for_request(symbol)

        if symbol in FOREX_SYMBOLS:
            params = {'function': 'FX_DAILY', 'from_symbol': av_symbol.split('/')[0], 'to_symbol': av_symbol.split('/')[1], 'outputsize': 'full'}
            data_key, price_col = 'Time Series FX (Daily)', '4. close'
        elif symbol in CRYPTO_SYMBOLS:
            params = {'function': 'DIGITAL_CURRENCY_DAILY', 'symbol': av_symbol, 'market': 'USD'}
            data_key, price_col = 'Time Series (Digital Currency Daily)', '4a. close (USD)'
        else:
            params = {'function': 'TIME_SERIES_DAILY_ADJUSTED', 'symbol': av_symbol, 'outputsize': 'full'}
            data_key, price_col = 'Time Series (Daily)', '5. adjusted close'

        data = self._make_request(params, ttl=historical_ttl)
        if not data or data_key not in data: return pd.DataFrame()

        df = pd.DataFrame.from_dict(data[data_key], orient='index')
        df.index = pd.to_datetime(df.index)
        df = df.sort_index().tail(days + 1) # Get a little extra for change calculations
        df['close'] = pd.to_numeric(df[price_col])
        return df[['close']].reset_index().rename(columns={'index': 'time'})

    def get_intraday_data(self, symbol: str, interval: str = '60min') -> pd.DataFrame:
        """Fetches intraday data with a medium cache TTL."""
        intraday_ttl = 3600 # 1 hour
        av_symbol = map_symbol_for_request(symbol)
        
        if symbol in FOREX_SYMBOLS:
            params = {'function': 'FX_INTRADAY', 'from_symbol': av_symbol.split('/')[0], 'to_symbol': av_symbol.split('/')[1], 'interval': interval, 'outputsize': 'compact'}
            data_key = f'Time Series FX ({interval})'
        elif symbol in CRYPTO_SYMBOLS:
            params = {'function': 'CRYPTO_INTRADAY', 'symbol': av_symbol, 'market': 'USD', 'interval': interval}
            data_key = f'Time Series Crypto ({interval})'
        else:
            params = {'function': 'TIME_SERIES_INTRADAY', 'symbol': av_symbol, 'interval': interval, 'outputsize': 'compact'}
            data_key = f'Time Series ({interval})'

        data = self._make_request(params, ttl=intraday_ttl)
        if not data or data_key not in data: return pd.DataFrame()

        df = pd.DataFrame.from_dict(data[data_key], orient='index')
        df.columns = ['open', 'high', 'low', 'close', 'volume']
        df.index = pd.to_datetime(df.index)
        df = df.apply(pd.to_numeric)
        return df.sort_index().reset_index().rename(columns={'index': 'time'})

    def get_news_sentiment(self, tickers: List[str] = None) -> Optional[List[Dict]]:
        """Fetches news sentiment with a medium cache TTL."""
        news_ttl = 7200 # 2 hours
        params = {'function': 'NEWS_SENTIMENT', 'limit': 20}
        if tickers:
            params['tickers'] = ",".join(tickers)
        
        data = self._make_request(params, ttl=news_ttl)
        return data.get('feed', []) if data else []

    def get_economic_calendar(self) -> pd.DataFrame:
        """Fetches economic calendar data with a long cache TTL."""
        calendar_ttl = 86400 # 24 hours
        params = {'function': 'ECONOMIC_CALENDAR', 'horizon': '3month'}
        data = self._make_request(params, ttl=calendar_ttl)
        
        if data and isinstance(data, str):
            try:
                return pd.read_csv(StringIO(data))
            except Exception as e:
                logger.error(f"Failed to parse economic calendar CSV: {e}")
        
        logger.warning("Could not fetch or parse economic calendar.")
        return pd.DataFrame()

    def get_sector_performance(self) -> Optional[Dict]:
        """Fetches sector performance data with a long cache TTL."""
        sector_ttl = 86400 # 24 hours
        params = {'function': 'SECTOR'}
        data = self._make_request(params, ttl=sector_ttl)
        return data if data and "Rank A: Real-Time Performance" in data else None