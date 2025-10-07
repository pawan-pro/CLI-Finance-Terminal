#!/usr/bin/env python3
"""
Real-time Market Data Updater for CLI Finance Terminal

This script fetches real-time 24-hour market data from Finnhub API at 15-minute intervals
and saves it to CSV files for chart generation. It also provides latest quotes for reports.

Usage:
    python update_market_data.py
"""

import os
import sys
import json
import pandas as pd
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests
import logging

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('market_data_update.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class FinnhubMarketDataUpdater:
    """Fetches and updates real-time market data from Finnhub API"""
    
    def __init__(self, api_key: str):
        """
        Initialize the updater with Finnhub API key
        
        Args:
            api_key: Finnhub API key
        """
        self.api_key = api_key
        self.base_url = "https://api.finnhub.io/api/v1"
        self.headers = {"X-Finnhub-Token": self.api_key}
        
        # Define asset symbols to track with Finnhub-compatible symbols
        self.assets = {
            # Indices
            'indices': {
                'US500Roll': '^GSPC',      # S&P 500
                'US30Roll': '^DJI',        # Dow Jones
                'UK100Roll': '^FTSE',      # FTSE 100
                'DE40Roll': '^GDAXI',      # DAX
                'FRA40Roll': '^FCHI',      # CAC 40
                'JP225Roll': '^N225',      # Nikkei 225
                'HK50Roll': '^HSI',        # Hang Seng
                'CHINA50Roll': '000016.SS', # SSE 50
                'VIXRoll': '^VIX',         # VIX Volatility
            },
            # Forex pairs
            'forex': {
                'EURUSD.sd': 'EURUSD',
                'GBPUSD.sd': 'GBPUSD',
                'USDJPY.sd': 'USDJPY',
                'AUDUSD.sd': 'AUDUSD',
                'USDCAD.sd': 'USDCAD',
                'USDCHF.sd': 'USDCHF',
                'NZDUSD.sd': 'NZDUSD',
            },
            # Commodities
            'commodities': {
                'XAUUSD': 'XAUUSD',         # Gold
                'XAGUSD': 'XAGUSD',         # Silver
                'XPTUSD': 'XPTUSD',         # Platinum
                'USOILRoll': 'CL=F',       # Crude Oil
                'BRENT': 'BZ=F',           # Brent Oil
                'NGAS': 'NG=F',            # Natural Gas
            },
            # Crypto
            'crypto': {
                'BTCUSD.lv': 'BINANCE:BTCUSDT',  # Bitcoin
                'ETHUSD.lv': 'BINANCE:ETHUSDT',  # Ethereum
                'XRPUSD.lv': 'BINANCE:XRPUSDT',  # Ripple
                'LTCUSD.lv': 'BINANCE:LTCUSDT',  # Litecoin
                'BCHUSD.lv': 'BINANCE:BCHUSDT',  # Bitcoin Cash
                'EOSUSD.lv': 'BINANCE:EOSUSDT',  # EOS
            },
            # Bonds/ETFs
            'bonds': {
                'TLT': 'TLT',              # 20+ Year Treasury
                'IEF': 'IEF',              # 7-10 Year Treasury
                'SHY': 'SHY',              # 1-3 Year Treasury
                'LQD': 'LQD',              # Corporate Bond ETF
            }
        }
        
        # Create data directories if they don't exist
        self.data_dirs = {
            'indices': './data/indices',
            'forex': './data/forex',
            'commodities': './data/commodities',
            'crypto': './data/crypto',
            'bonds': './data/bonds',
            'other': './data/other'
        }
        
        for dir_path in self.data_dirs.values():
            os.makedirs(dir_path, exist_ok=True)
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """
        Make a request to Finnhub API with rate limiting handling
        
        Args:
            endpoint: API endpoint
            params: Request parameters
            
        Returns:
            Response data or None
        """
        if params is None:
            params = {}
            
        params['token'] = self.api_key
        url = f"{self.base_url}/{endpoint}"
        
        try:
            # Add delay to respect rate limits
            time.sleep(0.1)  # 100ms delay between requests
            
            response = requests.get(url, params=params, timeout=30)
            
            # Handle rate limiting
            if response.status_code == 429:
                logger.warning("Rate limit exceeded. Waiting 60 seconds...")
                time.sleep(60)
                response = requests.get(url, params=params, timeout=30)
                
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to {url}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON response from {url}: {e}")
            return None
    
    def get_current_quote(self, symbol: str) -> Optional[Dict]:
        """
        Get current quote for a symbol
        
        Args:
            symbol: Finnhub symbol
            
        Returns:
            Quote data or None
        """
        logger.info(f"Fetching current quote for {symbol}")
        data = self._make_request("quote", {"symbol": symbol})
        return data
    
    def get_historical_data(self, symbol: str, resolution: str = "15", 
                          from_time: int = None, to_time: int = None) -> Optional[pd.DataFrame]:
        """
        Get historical data for a symbol
        
        Args:
            symbol: Finnhub symbol
            resolution: Time resolution (1, 5, 15, 30, 60, D, W, M)
            from_time: Unix timestamp for start time
            to_time: Unix timestamp for end time
            
        Returns:
            DataFrame with historical data or None
        """
        if from_time is None:
            # Default to 24 hours ago
            from_time = int((datetime.now() - timedelta(hours=24)).timestamp())
            
        if to_time is None:
            to_time = int(datetime.now().timestamp())
        
        logger.info(f"Fetching {resolution}-minute historical data for {symbol} from {from_time} to {to_time}")
        
        params = {
            "symbol": symbol,
            "resolution": resolution,
            "from": from_time,
            "to": to_time
        }
        
        data = self._make_request("stock/candle", params)
        
        if data is None or data.get('s') == 'no_data':
            logger.warning(f"No historical data available for {symbol}")
            return None
            
        if 'c' not in data:
            logger.warning(f"Incomplete historical data for {symbol}: {data}")
            return None
        
        # Create DataFrame
        df = pd.DataFrame({
            'time': pd.to_datetime(data['t'], unit='s'),
            'open': data['o'],
            'high': data['h'],
            'low': data['l'],
            'close': data['c'],
            'volume': data['v']
        })
        
        # Sort by time and reset index
        df = df.sort_values('time').reset_index(drop=True)
        
        logger.info(f"Fetched {len(df)} data points for {symbol}")
        return df
    
    def save_to_csv(self, df: pd.DataFrame, symbol: str, category: str, 
                   filename_suffix: str = "_data.csv") -> str:
        """
        Save DataFrame to CSV file
        
        Args:
            df: DataFrame to save
            symbol: Asset symbol
            category: Asset category (indices, forex, etc.)
            filename_suffix: CSV filename suffix
            
        Returns:
            Path to saved file
        """
        # Clean symbol name for filename (remove special characters)
        clean_symbol = symbol.replace('^', '').replace('=', '_').replace('/', '_')
        clean_symbol = ''.join(c for c in clean_symbol if c.isalnum() or c in ['_', '-', '.'])
        
        # Determine directory based on category
        if category in self.data_dirs:
            dir_path = self.data_dirs[category]
        else:
            dir_path = self.data_dirs['other']
            
        # Create full filepath
        filepath = os.path.join(dir_path, f"{clean_symbol}{filename_suffix}")
        
        # Save to CSV
        try:
            df.to_csv(filepath, index=False)
            logger.info(f"Saved {len(df)} records to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error saving data to {filepath}: {e}")
            return ""
    
    def update_asset_data(self, symbol: str, finnhub_symbol: str, category: str) -> bool:
        """
        Update data for a single asset
        
        Args:
            symbol: Internal symbol name
            finnhub_symbol: Finnhub-compatible symbol
            category: Asset category
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Fetch current quote for latest price
            quote = self.get_current_quote(finnhub_symbol)
            if quote and quote.get('c'):
                logger.info(f"Current price for {symbol}: {quote['c']}")
            
            # Fetch 24-hour historical data at 15-minute intervals
            hist_df = self.get_historical_data(finnhub_symbol, resolution="15")
            
            if hist_df is not None and not hist_df.empty:
                # Add symbol column for identification
                hist_df['symbol'] = symbol
                
                # Save to CSV
                filepath = self.save_to_csv(hist_df, symbol, category)
                if filepath:
                    logger.info(f"Successfully updated data for {symbol}")
                    return True
                else:
                    logger.error(f"Failed to save data for {symbol}")
                    return False
            else:
                logger.warning(f"No historical data available for {symbol}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating data for {symbol}: {e}")
            return False
    
    def update_all_assets(self) -> Dict[str, int]:
        """
        Update data for all tracked assets
        
        Returns:
            Dictionary with update statistics
        """
        stats = {
            'total': 0,
            'successful': 0,
            'failed': 0
        }
        
        logger.info("Starting market data update for all assets...")
        
        # Iterate through all asset categories
        for category, symbols in self.assets.items():
            logger.info(f"Updating {category} assets...")
            
            for internal_symbol, finnhub_symbol in symbols.items():
                stats['total'] += 1
                
                try:
                    if self.update_asset_data(internal_symbol, finnhub_symbol, category):
                        stats['successful'] += 1
                    else:
                        stats['failed'] += 1
                        
                except Exception as e:
                    logger.error(f"Failed to update {internal_symbol}: {e}")
                    stats['failed'] += 1
        
        logger.info(f"Update complete. Stats: {stats}")
        return stats
    
    def get_latest_prices(self) -> Dict[str, float]:
        """
        Get latest prices for all tracked assets
        
        Returns:
            Dictionary mapping symbols to current prices
        """
        prices = {}
        
        logger.info("Fetching latest prices for all assets...")
        
        # Iterate through all asset categories
        for category, symbols in self.assets.items():
            for internal_symbol, finnhub_symbol in symbols.items():
                try:
                    quote = self.get_current_quote(finnhub_symbol)
                    if quote and quote.get('c'):
                        prices[internal_symbol] = quote['c']
                        logger.info(f"{internal_symbol}: {quote['c']}")
                    else:
                        logger.warning(f"Could not get price for {internal_symbol}")
                        
                except Exception as e:
                    logger.error(f"Error getting price for {internal_symbol}: {e}")
        
        return prices

def main():
    """Main function to update market data"""
    # Load API key from .env file
    env_file = "./.env"
    api_key = None
    
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith('FINNHUB_API_KEY='):
                    api_key = line.strip().split('=', 1)[1].strip('"\'')
                    break
    
    if not api_key or api_key == 'your_finnhub_api_key_here':
        logger.error("Finnhub API key not found in .env file or is placeholder value")
        logger.info("Please add your Finnhub API key to .env file:")
        logger.info("FINNHUB_API_KEY=your_actual_api_key_here")
        return False
    
    # Initialize updater
    updater = FinnhubMarketDataUpdater(api_key)
    
    # Update all assets
    logger.info("=== Starting Market Data Update ===")
    stats = updater.update_all_assets()
    
    # Get latest prices
    logger.info("=== Fetching Latest Prices ===")
    latest_prices = updater.get_latest_prices()
    
    # Save latest prices to a JSON file for easy access
    prices_file = "./data/latest_prices.json"
    try:
        with open(prices_file, 'w') as f:
            json.dump(latest_prices, f, indent=2)
        logger.info(f"Latest prices saved to {prices_file}")
    except Exception as e:
        logger.error(f"Error saving latest prices: {e}")
    
    # Print summary
    logger.info("=== Update Summary ===")
    logger.info(f"Total assets: {stats['total']}")
    logger.info(f"Successful updates: {stats['successful']}")
    logger.info(f"Failed updates: {stats['failed']}")
    
    if stats['failed'] == 0:
        logger.info("✅ All assets updated successfully!")
        return True
    else:
        logger.warning(f"⚠️  {stats['failed']} assets failed to update")
        return stats['failed'] < stats['total'] * 0.5  # Success if less than 50% failed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)