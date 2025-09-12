import requests
from src.config.settings import settings
import time
import json
from src.data import cache_manager

class AlphaVantage:
    def __init__(self):
        self.api_key = settings["api_keys"]["alpha_vantage"]
        if not self.api_key:
            raise ValueError("Alpha Vantage API key not found. Please set it in your .env file.")
        self.base_url = "https://www.alphavantage.co/query"

    def get_quote(self, symbol):
        """Fetches a quote for a given symbol, using cache."""
        params = {"function": "GLOBAL_QUOTE", "symbol": symbol}
        cache_key = f"quote_{symbol}"

        cached_data = cache_manager.cache_manager.get(cache_key)
        if cached_data is not None:
            return {symbol: cached_data}

        params["apikey"] = self.api_key
        try:
            time.sleep(15)
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()

            if "Global Quote" in data and data["Global Quote"]:
                quote_data = data["Global Quote"]
                if not quote_data:
                    print(f"Warning: Empty 'Global Quote' for {symbol}. Caching failure.")
                    cache_manager.cache_manager.set(cache_key, None)
                    return {symbol: None}
                cache_manager.cache_manager.set(cache_key, quote_data)
                return {symbol: quote_data}
            elif "Information" in data:
                print(f"API Info for {symbol}: {data['Information']}")
                cache_manager.cache_manager.set(cache_key, None)
                return {symbol: None}
            else:
                print(f"Warning: Unexpected response for {symbol}. Full response: {data}")
                cache_manager.cache_manager.set(cache_key, None)
                return {symbol: None}
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from Alpha Vantage for {symbol}: {e}")
            cache_manager.cache_manager.set(cache_key, None)
            return {symbol: None}
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON for {symbol}. Response text: {response.text}")
            cache_manager.cache_manager.set(cache_key, None)
            return {symbol: None}

    def get_dashboard_data(self, symbols: list[str]) -> dict:
        """Fetches quotes for a list of symbols sequentially."""
        combined_results = {}
        for symbol in symbols:
            result = self.get_quote(symbol)
            combined_results.update(result)
        return combined_results

    def get_forex_rate(self, from_currency, to_currency):
        """Fetches the exchange rate between two currencies, using cache."""
        cache_key = f"forex_{from_currency}_{to_currency}"

        cached_data = cache_manager.cache_manager.get(cache_key)
        if cached_data is not None:
            return cached_data

        params = {"function": "CURRENCY_EXCHANGE_RATE", "from_currency": from_currency, "to_currency": to_currency, "apikey": self.api_key}
        try:
            time.sleep(15)
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            if "Realtime Currency Exchange Rate" in data and data["Realtime Currency Exchange Rate"]:
                forex_data = data["Realtime Currency Exchange Rate"]
                cache_manager.cache_manager.set(cache_key, forex_data)
                return forex_data
            else:
                print(f"Warning: Unexpected forex response. Full response: {data}")
                cache_manager.cache_manager.set(cache_key, None)
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching forex data: {e}")
            cache_manager.cache_manager.set(cache_key, None)
            return None

    def get_treasury_yield(self, maturity="10year"):
        """Fetches the treasury yield for a given maturity, using cache."""
        cache_key = f"treasury_{maturity}"

        cached_data = cache_manager.cache_manager.get(cache_key)
        if cached_data is not None:
            return cached_data

        params = {"function": "TREASURY_YIELD", "maturity": maturity, "interval": "daily", "apikey": self.api_key}
        try:
            time.sleep(15)
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            if "data" in data and data["data"]:
                yield_data = data["data"][0]
                cache_manager.cache_manager.set(cache_key, yield_data)
                return yield_data
            else:
                print(f"Warning: Unexpected treasury yield response. Full response: {data}")
                cache_manager.cache_manager.set(cache_key, None)
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching treasury yield data: {e}")
            cache_manager.cache_manager.set(cache_key, None)
            return None

    def get_commodity_data(self, commodity: str):
        """Fetches data for a given commodity, using cache."""
        cache_key = f"commodity_{commodity}"

        cached_data = cache_manager.cache_manager.get(cache_key)
        if cached_data is not None:
            return cached_data

        params = {"function": commodity.upper(), "interval": "daily", "apikey": self.api_key}
        try:
            time.sleep(15)
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            if "data" in data and data["data"]:
                commodity_data = data["data"][0]
                cache_manager.cache_manager.set(cache_key, commodity_data)
                return commodity_data
            else:
                print(f"Warning: Unexpected commodity response for {commodity}. Full response: {data}")
                cache_manager.cache_manager.set(cache_key, None)
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {commodity} data: {e}")
            cache_manager.cache_manager.set(cache_key, None)
            return None

    def get_historical_data(self, symbol: str):
        """Fetches daily historical data for a symbol."""
        cache_key = f"historical_{symbol}"

        cached_data = cache_manager.cache_manager.get(cache_key)
        if cached_data is not None:
            return cached_data

        params = {"function": "TIME_SERIES_DAILY", "symbol": symbol, "apikey": self.api_key}
        try:
            time.sleep(15)
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()

            if "Time Series (Daily)" in data:
                historical_data = data["Time Series (Daily)"]
                cache_manager.cache_manager.set(cache_key, historical_data)
                return historical_data
            elif "Information" in data:
                print(f"API Info for {symbol}: {data['Information']}")
                cache_manager.cache_manager.set(cache_key, None)
                return None
            else:
                print(f"Warning: No 'Time Series (Daily)' in response for {symbol}. Full response: {data}")
                cache_manager.cache_manager.set(cache_key, None)
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching historical data for {symbol}: {e}")
            cache_manager.cache_manager.set(cache_key, None)
            return None
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON for {symbol}. Response text: {response.text}")
            cache_manager.cache_manager.set(cache_key, None)
            return None

    def search_symbol(self, keywords):
        """Searches for a symbol using keywords."""
        params = {"function": "SYMBOL_SEARCH", "keywords": keywords, "apikey": self.api_key}
        # Not caching search results as they should be fresh
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("bestMatches", [])
        except requests.exceptions.RequestException as e:
            print(f"Error searching for symbol on Alpha Vantage: {e}")
            return []
        except ValueError as e:
            print(f"Error decoding JSON from Alpha Vantage: {e}")
            return []

    def get_market_status(self):
        """Fetches the current market status of major trading venues."""
        cache_key = "market_status"

        cached_data = cache_manager.cache_manager.get(cache_key)
        if cached_data:
            return cached_data

        params = {"function": "MARKET_STATUS", "apikey": self.api_key}
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            if "markets" in data:
                market_data = data["markets"]
                cache_manager.cache_manager.set(cache_key, market_data)
                return market_data
            else:
                print(f"Warning: Unexpected market status response. Full response: {data}")
                cache_manager.cache_manager.set(cache_key, None)
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching market status from Alpha Vantage: {e}")
            cache_manager.cache_manager.set(cache_key, None)
            return None
        except ValueError:
            print(f"Error decoding JSON from Alpha Vantage.")
            cache_manager.cache_manager.set(cache_key, None)
            return None

    def get_sector_performance(self):
        """Fetches sector performance data."""
        cache_key = "sector_performance"

        cached_data = cache_manager.cache_manager.get(cache_key)
        if cached_data:
            return cached_data

        params = {"function": "SECTOR", "apikey": self.api_key}
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            if "Rank A: Real-Time Performance" in data:
                sector_data = data
                cache_manager.cache_manager.set(cache_key, sector_data)
                return sector_data
            else:
                print(f"Warning: Unexpected sector performance response. Full response: {data}")
                cache_manager.cache_manager.set(cache_key, None)
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching sector performance from Alpha Vantage: {e}")
            cache_manager.cache_manager.set(cache_key, None)
            return None
        except ValueError:
            print(f"Error decoding JSON from Alpha Vantage.")
            cache_manager.cache_manager.set(cache_key, None)
            return None

if __name__ == '__main__':
    # For testing
    pass