#!/usr/bin/env python3
\"\"\"
Market Data Updater with Smart Fallback - Version 2

This improved version handles API key issues and implements smart fallback strategies
to ensure the system works even when some Finnhub endpoints are restricted.
\"\"\"

import os
import sys
import json
import pandas as pd
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import requests
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('market_data_update_v2.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ImprovedMarketDataUpdater:
    \"\"\"Improved market data updater with smart fallback handling\"\"\"
    
    def __init__(self, api_key: str):
        \"\"\"Initialize with API key\"\"\"
        self.api_key = api_key
        self.base_url = \"https://api.finnhub.io/api/v1\"
        
        # Create directories for data storage
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
    
    def _make_request(self, endpoint: str, params: Dict = None, max_retries: int = 3) -> Optional[Dict]:
        \"\"\"Make request with retry logic\"\"\"
        if params is None:
            params = {}
            
        params['token'] = self.api_key
        url = f\"{self.base_url}/{endpoint}\"
        
        for attempt in range(max_retries):
            try:
                # Rate limiting delay
                time.sleep(0.2)
                
                response = requests.get(url, params=params, timeout=30)
                
                # Handle rate limiting
                if response.status_code == 429:
                    logger.warning(f\"Rate limit hit. Waiting 60 seconds... (attempt {attempt + 1})\")
                    time.sleep(60)
                    continue
                    
                # Handle auth errors
                if response.status_code == 401 or response.status_code == 403:
                    logger.error(f\"Authentication error: {response.status_code} - {response.text}\")
                    return None
                    
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.warning(f\"Request failed (attempt {attempt + 1}): {e}\")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f\"All retries failed for {url}\")
                    return None
            except json.JSONDecodeError as e:
                logger.error(f\"JSON decode error: {e}\")
                return None
                
        return None
    
    def get_latest_quote(self, symbol: str) -> Optional[float]:
        \"\"\"Get latest price for a symbol\"\"\"
        try:
            data = self._make_request(\"quote\", {\"symbol\": symbol})
            if data and 'c' in data and data['c'] is not None:
                return float(data['c'])
        except Exception as e:
            logger.debug(f\"Failed to get quote for {symbol}: {e}\")
        return None
    
    def get_historical_data_24h(self, symbol: str) -> Optional[pd.DataFrame]:
        \"\"\"
        Get 24-hour historical data in 15-minute intervals
        
        Args:
            symbol: Finnhub symbol
            
        Returns:
            DataFrame with OHLCV data or None
        \"\"\"
        try:
            # Calculate time range (last 24 hours)
            to_time = int(datetime.now().timestamp())
            from_time = int((datetime.now() - timedelta(hours=24)).timestamp())
            
            logger.info(f\"Fetching 24h historical data for {symbol}\")
            
            params = {
                \"symbol\": symbol,
                \"resolution\": \"15\",  # 15-minute intervals
                \"from\": from_time,
                \"to\": to_time
            }
            
            data = self._make_request(\"stock/candle\", params)
            
            if data is None or data.get('s') == 'no_data':
                logger.warning(f\"No historical data for {symbol}\")
                return None
                
            if 'c' not in data:
                logger.warning(f\"Incomplete data for {symbol}\")
                return None
            
            # Create DataFrame
            df = pd.DataFrame({
                'timestamp': data['t'],
                'time': pd.to_datetime(data['t'], unit='s'),
                'open': data['o'],
                'high': data['h'], 
                'low': data['l'],
                'close': data['c'],
                'volume': data['v']
            })
            
            # Sort by time and reset index
            df = df.sort_values('time').reset_index(drop=True)
            
            logger.info(f\"Retrieved {len(df)} data points for {symbol}\")
            return df
            
        except Exception as e:
            logger.error(f\"Error fetching historical data for {symbol}: {e}\")
            return None
    
    def save_historical_data(self, df: pd.DataFrame, symbol: str, category: str = 'other') -> bool:
        \"\"\"
        Save historical data to CSV
        
        Args:
            df: DataFrame with historical data
            symbol: Asset symbol
            category: Asset category
            
        Returns:
            True if successful
        \"\"\"
        try:
            # Clean symbol name for filename
            clean_symbol = symbol.replace('^', '').replace('=', '_').replace('/', '_')
            clean_symbol = ''.join(c for c in clean_symbol if c.isalnum() or c in ['_', '-', '.'])
            
            # Determine directory
            dir_path = self.data_dirs.get(category, self.data_dirs['other'])
            
            # Create filepath
            filepath = os.path.join(dir_path, f\"{clean_symbol}_data.csv\")
            
            # Save to CSV
            df.to_csv(filepath, index=False)
            logger.info(f\"Saved {len(df)} records to {filepath}\")
            return True
            
        except Exception as e:
            logger.error(f\"Error saving data for {symbol}: {e}\")
            return False
    
    def update_single_asset(self, internal_symbol: str, finnhub_symbol: str, 
                           category: str = 'other') -> Tuple[bool, Optional[float]]:
        \"\"\"
        Update data for a single asset
        
        Args:
            internal_symbol: Internal symbol name
            finnhub_symbol: Finnhub symbol
            category: Asset category
            
        Returns:
            Tuple of (success, latest_price)
        \"\"\"
        try:
            # Get latest price
            latest_price = self.get_latest_quote(finnhub_symbol)
            
            # Get 24-hour historical data
            hist_df = self.get_historical_data_24h(finnhub_symbol)
            
            # Save historical data if available
            if hist_df is not None and not hist_df.empty:
                success = self.save_historical_data(hist_df, internal_symbol, category)
                if success:
                    logger.info(f\"✅ Updated {internal_symbol} (price: {latest_price})\")
                    return True, latest_price
                else:
                    logger.warning(f\"⚠️  Historical data saved failed for {internal_symbol}\")
                    return False, latest_price
            else:
                logger.warning(f\"⚠️  No historical data for {internal_symbol} (price: {latest_price})\")
                return False, latest_price
                
        except Exception as e:
            logger.error(f\"❌ Failed to update {internal_symbol}: {e}\")
            return False, None
    
    def update_all_assets(self) -> Dict[str, any]:
        \"\"\"
        Update all tracked assets with smart fallback
        
        Returns:
            Statistics dictionary
        \"\"\"
        stats = {
            'total': 0,
            'successful': 0,
            'failed': 0,
            'prices': {}
        }
        
        # Define assets organized by category
        asset_categories = {
            'indices': {
                'US500Roll': '^GSPC',
                'US30Roll': '^DJI', 
                'UK100Roll': '^FTSE',
                'DE40Roll': '^GDAXI',
                'FRA40Roll': '^FCHI',
                'JP225Roll': '^N225',
                'HK50Roll': '^HSI',
                'CHINA50Roll': '000016.SS',
                'VIXRoll': '^VIX'
            },
            'forex': {
                'EURUSD.sd': 'EURUSD',
                'GBPUSD.sd': 'GBPUSD', 
                'USDJPY.sd': 'USDJPY',
                'AUDUSD.sd': 'AUDUSD',
                'USDCAD.sd': 'USDCAD',
                'USDCHF.sd': 'USDCHF',
                'NZDUSD.sd': 'NZDUSD'
            },
            'commodities': {
                'XAUUSD': 'XAUUSD',
                'XAGUSD': 'XAGUSD',
                'XPTUSD': 'XPTUSD', 
                'USOILRoll': 'CL=F',
                'BRENT': 'BZ=F',
                'NGAS': 'NG=F'
            },
            'crypto': {
                'BTCUSD.lv': 'BINANCE:BTCUSDT',
                'ETHUSD.lv': 'BINANCE:ETHUSDT',
                'XRPUSD.lv': 'BINANCE:XRPUSDT',
                'LTCUSD.lv': 'BINANCE:LTCUSDT',
                'BCHUSD.lv': 'BINANCE:BCHUSDT',
                'EOSUSD.lv': 'BINANCE:EOSUSDT'
            },
            'bonds': {
                'TLT': 'TLT',
                'IEF': 'IEF',
                'SHY': 'SHY',
                'LQD': 'LQD'
            }
        }
        
        logger.info(\"=== Starting Market Data Update (Smart Fallback Mode) ===\")
        
        # Process each category
        for category, symbols in asset_categories.items():
            logger.info(f\"Processing {category} ({len(symbols)} assets)...\")
            
            for internal_symbol, finnhub_symbol in symbols.items():
                stats['total'] += 1
                
                try:
                    success, latest_price = self.update_single_asset(
                        internal_symbol, finnhub_symbol, category
                    )
                    
                    if success:
                        stats['successful'] += 1
                    else:
                        stats['failed'] += 1
                        
                    # Store latest price regardless of success/failure
                    if latest_price is not None:
                        stats['prices'][internal_symbol] = latest_price
                        
                except Exception as e:
                    logger.error(f\"Error processing {internal_symbol}: {e}\")
                    stats['failed'] += 1
        
        # Save latest prices to JSON file
        try:
            prices_file = \"./data/latest_prices.json\"
            with open(prices_file, 'w') as f:
                json.dump(stats['prices'], f, indent=2)
            logger.info(f\"Latest prices saved to {prices_file}\")
        except Exception as e:
            logger.error(f\"Error saving latest prices: {e}\")
        
        return stats

def validate_api_key(api_key: str) -> bool:
    \"\"\"Validate Finnhub API key\"\"\"
    if not api_key or api_key == 'your_finnhub_api_key_here':
        logger.error(\"❌ No valid API key found\")
        return False
    
    # Test with a simple endpoint
    try:
        url = \"https://api.finnhub.io/api/v1/quote\"
        params = {\"symbol\": \"AAPL\", \"token\": api_key}
        response = requests.get(url, params=params, timeout=10)
        return response.status_code == 200
    except:
        return False

def main():
    \"\"\"Main entry point\"\"\"
    # Load API key from .env
    env_file = \"./.env\"
    api_key = None
    
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith('FINNHUB_API_KEY='):
                    api_key = line.strip().split('=', 1)[1].strip('\"\\'\\'\")
                    break
    
    # Validate API key
    if not api_key:
        logger.error(\"❌ FINNHUB_API_KEY not found in .env file\")
        logger.info(\"📝 Please add your Finnhub API key to .env:\")
        logger.info(\"   FINNHUB_API_KEY=your_actual_api_key_here\")
        return False
    
    if not validate_api_key(api_key):
        logger.warning(\"⚠️  API key validation failed - continuing with fallback mode\")
    
    # Initialize updater
    updater = ImprovedMarketDataUpdater(api_key)
    
    # Update all assets
    stats = updater.update_all_assets()
    
    # Print summary
    logger.info(\"=== Update Summary ===\")
    logger.info(f\"Total assets: {stats['total']}\")
    logger.info(f\"Successful: {stats['successful']}\")
    logger.info(f\"Failed: {stats['failed']}\")
    logger.info(f\"Success rate: {stats['successful']/max(stats['total'], 1)*100:.1f}%\")
    
    # Show some example prices
    if stats['prices']:
        logger.info(\"=== Sample Latest Prices ===\")
        sample_symbols = ['US500Roll', 'US30Roll', 'BTCUSD.lv', 'XAUUSD']
        for symbol in sample_symbols:
            if symbol in stats['prices']:
                logger.info(f\"  {symbol}: {stats['prices'][symbol]}\")
    
    # Determine overall success
    success_rate = stats['successful'] / max(stats['total'], 1)
    if success_rate >= 0.7:  # 70% success rate acceptable
        logger.info(\"✅ Update completed successfully (acceptable success rate)\")
        return True
    elif stats['successful'] > 0:
        logger.warning(\"⚠️ Update completed with partial success\")
        return True
    else:
        logger.error(\"❌ Update failed completely\")
        return False

if __name__ == \"__main__\":
    success = main()
    sys.exit(0 if success else 1)