#!/usr/bin/env python3
"""
Unified script to fetch market data from TwelveData API with rate limiting.
This script consolidates all data fetching from individual t12-*.py scripts
and processes them in batches to respect the API rate limits.
"""

import time
import requests
import pandas as pd
import os
from typing import List, Dict, Tuple, Any
from collections import defaultdict
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API Configuration - Support multiple API keys for rotation
API_KEYS = [
    'd423c8d01edf48fc940b88a5a894bb2f',  # Primary key
    '91779d585fad4cbcbb8d931485aef741',  # Secondary key
    '64a2a64ac0d143ca8a81eac2c4cbfe4e',  # Tertiary key
    # Add additional API keys here as needed
]
BASE_URL = 'https://api.twelvedata.com/time_series'
INTERVAL = '15min'
OUTPUT_SIZE = 96

# Track API key usage to rotate effectively
api_key_usage = {key: 0 for key in API_KEYS}
current_api_key_index = 0

def get_all_symbols_by_asset_class() -> Dict[str, List[str]]:
    """
    Returns a dictionary containing all symbols organized by asset class.
    This mirrors the individual t12-*.py scripts.
    """
    all_symbols = {
        # Bonds
        'bonds': ['US2Y'],
        
        # Commodities
        'commodities': ['XAU/USD'],  # Gold (with others commented out in original)
        
        # Cryptocurrencies
        'crypto': ['BTC/USD', 'ETH/USD', 'XRP/USD', 'LTC/USD', 'ADA/USD'],
        
        # Forex pairs (formatted as needed)
        'forex': ['EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'USD/CAD', 'AUD/USD'],
        
        # Indices
        'indices': [
            'SPY', 'DIA', 'QQQ', 'IWM', 'EWU', 'EWJ', 'FEZ', 'DAX', 
            'EEM', 'INDA', 'MCHI', 'EWG', 'EWQ', 'EWS', 'EWA'
        ],
        
        # Sector ETFs - split into two groups like the original
        'sectors_s1': ['XLK', 'XLF', 'XLE', 'XLV', 'XLY', 'XLP', 'XLI'],
        'sectors_s2': ['XLRE', 'XLB', 'XLC'],
        
        # VIX ETFs
        'vix': ['VXX', 'UVXY']
    }
    return all_symbols

def get_next_api_key() -> str:
    """
    Get the next API key in rotation that has the lowest usage count.
    This helps distribute requests across multiple API keys.
    
    Returns:
        The API key to use for the next request
    """
    global current_api_key_index
    
    # Find the API key with the minimum usage
    min_usage_key = min(API_KEYS, key=lambda k: api_key_usage[k])
    key_to_use = min_usage_key
    
    # Update usage count
    api_key_usage[key_to_use] += 1
    
    return key_to_use

def fetch_single_symbol(symbol: str, use_rotated_key: bool = True) -> Dict[str, Any]:
    """
    Fetch data for a single symbol using the TwelveData API with retry logic.
    
    Args:
        symbol: The symbol to fetch
        use_rotated_key: Whether to use API key rotation (default: True)
        
    Returns:
        Dictionary with symbol data or error information
    """
    # Select API key
    if use_rotated_key and len(API_KEYS) > 1:
        api_key = get_next_api_key()
    else:
        # Use the primary key if only one is available or rotation is disabled
        api_key = API_KEYS[0]
    
    url = (
        f"{BASE_URL}"
        f"?symbol={symbol}&interval={INTERVAL}&outputsize={OUTPUT_SIZE}&apikey={api_key}"
    )
    
    max_retries = 3
    retry_delay = 15  # seconds to wait before retrying after a 429 error
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url)
            data = response.json()
            
            if "values" not in data:
                if data.get('code') == 429:  # Rate limit error
                    # If we get a 429, try with a different API key on the next attempt
                    if attempt < max_retries - 1 and use_rotated_key and len(API_KEYS) > 1:
                        logger.warning(f"Rate limit hit for {symbol} with key {api_key[:8]}..., trying different key...")
                        # Get a different key for retry
                        different_key = None
                        for key in API_KEYS:
                            if key != api_key and key != data.get('apikey', api_key):  # If available in response
                                different_key = key
                                break
                        if different_key:
                            logger.info(f"Retrying with different API key: {different_key[:8]}...")
                            api_key = different_key
                            api_key_usage[api_key] += 1
                            url = (
                                f"{BASE_URL}"
                                f"?symbol={symbol}&interval={INTERVAL}&outputsize={OUTPUT_SIZE}&apikey={api_key}"
                            )
                    else:
                        logger.warning(f"Rate limit hit for {symbol}, waiting {retry_delay}s before retry {attempt + 1}/{max_retries}")
                        time.sleep(retry_delay)
                    continue
                else:
                    logger.warning(f"No data for {symbol}: {data}")
                    return {"symbol": symbol, "error": data, "values": []}
            
            return {"symbol": symbol, "error": None, "values": data.get('values', [])}
        
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"Error fetching {symbol}, waiting {retry_delay}s before retry {attempt + 1}/{max_retries}: {str(e)}")
                time.sleep(retry_delay)
                continue
            else:
                logger.error(f"Error fetching {symbol} after {max_retries} attempts: {str(e)}")
                return {"symbol": symbol, "error": str(e), "values": []}

def batch_fetch_symbols(symbols: List[str], batch_size: int = 6, delay: float = 60.0) -> List[Dict[str, Any]]:
    """
    Fetch data for all symbols with support for multiple API keys to increase throughput.
    
    Args:
        symbols: List of symbols to fetch
        batch_size: Number of symbols to fetch per batch
        delay: Delay in seconds between batches (when needed)
        
    Returns:
        List of dictionaries containing symbol data
    """
    all_results = []
    
    if len(API_KEYS) > 1:
        # With multiple API keys, we can process all symbols with rotation and reduced delays
        effective_rate_limit = 8 * len(API_KEYS)  # 8 calls per minute per API key
        logger.info(f"Using {len(API_KEYS)} API keys - effective rate limit: {effective_rate_limit} calls per minute")
        
        # Process symbols with API key rotation for better throughput
        for i, symbol in enumerate(symbols):
            logger.info(f"Processing symbol {i+1}/{len(symbols)}: {symbol}")
            result = fetch_single_symbol(symbol, use_rotated_key=True)
            all_results.append(result)
            
            # With multiple keys, we can reduce individual call delay
            # The rotation will distribute across multiple rate limits
            time.sleep(1)  # Reduced from 8s to 1s with multiple keys
    else:
        # With single API key, process in batches to respect rate limits
        num_batches = len(symbols) // batch_size + (1 if len(symbols) % batch_size > 0 else 0)
        
        logger.info(f"Using single API key - processing {len(symbols)} symbols in {num_batches} batches of {batch_size} symbols each")
        
        for i in range(0, len(symbols), batch_size):
            batch = symbols[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{num_batches} with {len(batch)} symbols: {batch}")
            
            # Fetch all symbols in this batch
            batch_results = []
            for symbol in batch:
                result = fetch_single_symbol(symbol, use_rotated_key=False)  # Use same key for batch consistency
                batch_results.append(result)
                
                # Wait between API calls to respect rate limits
                logger.debug(f"Waiting 8 seconds before next API call...")
                time.sleep(8)
            
            all_results.extend(batch_results)
            
            # Wait before next batch if not the last batch
            if i + batch_size < len(symbols):
                logger.info(f"Waiting {delay} seconds before next batch...")
                time.sleep(delay)
    
    return all_results

def save_data_to_csv(results: List[Dict[str, Any]], asset_class: str) -> None:
    """
    Save the fetched data to the appropriate CSV file based on asset class.
    This replicates the logic from the original t12-*.py scripts.
    """
    # Define file paths and column mappings
    file_configs = {
        'bonds': {'path': 'data/bonds_15min.csv', 'symbol_col': 'bond', 'value_col': 'yield'},
        'commodities': {'path': 'data/commodities_15min.csv', 'symbol_col': 'commodity', 'value_col': 'close'},
        'crypto': {'path': 'data/crypto_15min.csv', 'symbol_col': 'crypto', 'value_col': 'close'},
        'forex': {'path': 'data/forex_15min.csv', 'symbol_col': 'pair', 'value_col': 'close'},
        'indices': {'path': 'data/indices_15min.csv', 'symbol_col': 'symbol', 'value_col': 'close'},
        'sectors_s1': {'path': 'data/sector_etf_15min.csv', 'symbol_col': 'sector_etf', 'value_col': 'close'},
        'sectors_s2': {'path': 'data/sector2_etf_15min.csv', 'symbol_col': 'sector_etf', 'value_col': 'close'},
        'vix': {'path': 'data/vix_15min.csv', 'symbol_col': 'vix_etf', 'value_col': 'close'}
    }
    
    if asset_class not in file_configs:
        logger.error(f"Unknown asset class: {asset_class}")
        return
    
    config = file_configs[asset_class]
    csv_path = os.path.join(os.path.dirname(__file__), config['path'])
    
    # Determine columns based on asset class
    symbol_col = config['symbol_col']
    value_col = config['value_col']
    
    # Prepare initial dataframe structure
    if asset_class == 'bonds':
        columns = [symbol_col, 'timestamp', 'yield']
    elif asset_class == 'commodities':
        columns = [symbol_col, 'timestamp', 'open', 'high', 'low', 'close']
    else:
        columns = [symbol_col, 'timestamp', 'open', 'high', 'low', 'close']
        if asset_class == 'indices':
            columns.append('volume')  # indices have volume column
    
    # Try to read existing data
    try:
        df_existing = pd.read_csv(csv_path, parse_dates=['timestamp'])
    except FileNotFoundError:
        df_existing = pd.DataFrame(columns=columns)
    
    # Prepare new data
    rows = []
    for result in results:
        if result['error'] is not None:
            continue
            
        symbol = result['symbol']
        for entry in result['values']:
            row_data = {symbol_col: symbol, 'timestamp': pd.to_datetime(entry['datetime'])}
            
            if asset_class == 'bonds':
                # Bonds typically have yield instead of OHLC
                row_data['yield'] = float(entry.get('close', entry.get('value', 0)))
            elif asset_class == 'commodities':
                # Commodities may have value or close
                row_data['open'] = float(entry['open'])
                row_data['high'] = float(entry['high'])
                row_data['low'] = float(entry['low'])
                row_data['close'] = float(entry.get('close', entry.get('value', 0)))
            else:
                # Standard OHLC format
                row_data['open'] = float(entry['open'])
                row_data['high'] = float(entry['high'])
                row_data['low'] = float(entry['low'])
                row_data['close'] = float(entry['close'])
                if 'volume' in entry and asset_class == 'indices':
                    row_data['volume'] = float(entry['volume'])
            
            rows.append(row_data)
    
    if rows:
        df_new = pd.DataFrame(rows)
        df_combined = pd.concat([df_existing, df_new]).drop_duplicates(
            subset=[symbol_col, 'timestamp']
        ).sort_values([symbol_col, 'timestamp'])
        
        # Ensure columns are in the right order
        df_combined = df_combined[columns]
        
        df_combined.to_csv(csv_path, index=False)
        logger.info(f"Saved {len(df_new)} new records to {csv_path}")
    else:
        logger.info(f"No new records to save for {asset_class}")

def process_asset_class(asset_class: str, symbols: List[str]) -> None:
    """
    Process a single asset class by fetching its symbols and saving to CSV.
    
    Args:
        asset_class: Name of the asset class
        symbols: List of symbols for this asset class
    """
    logger.info(f"Processing {asset_class} with {len(symbols)} symbols...")
    
    # Fetch data with appropriate rate limiting based on number of API keys
    if len(API_KEYS) > 1:
        # With multiple API keys, we can be more efficient
        results = batch_fetch_symbols(symbols, batch_size=6, delay=30.0)
        # Reduced delay between asset classes when using multiple API keys
        inter_asset_delay = 5  # Seconds
    else:
        # With single API key, be more conservative
        results = batch_fetch_symbols(symbols, batch_size=4, delay=62.0)
        inter_asset_delay = 20  # Seconds
    
    # Log any errors
    errors = [r for r in results if r is not None and r.get('error') is not None]
    if errors:
        logger.warning(f"Errors encountered for {asset_class}: {len(errors)} symbols failed")
        for error_result in errors:
            logger.warning(f"  - {error_result.get('symbol', 'Unknown')}: {error_result.get('error')}")
    
    # Save successful results to CSV
    successful_results = [r for r in results if r is not None and r.get('error') is None]
    if successful_results:
        save_data_to_csv(successful_results, asset_class)

    logger.info(f"Completed processing {asset_class}")
    
    # Add a delay between asset classes to further ensure we don't hit rate limits
    if len(symbols) > 0:  # Only add delay if there were symbols processed
        logger.info(f"Waiting {inter_asset_delay} seconds before processing next asset class...")
        time.sleep(inter_asset_delay)

def main():
    """
    Main function to orchestrate the batched data fetching for all asset classes.
    """
    logger.info("Starting unified data fetching process...")
    
    # Get all symbols by asset class
    all_symbols = get_all_symbols_by_asset_class()
    
    # Determine delay based on number of API keys
    inter_class_delay = 10 if len(API_KEYS) > 1 else 30
    
    # Process each asset class
    for idx, (asset_class, symbols) in enumerate(all_symbols.items()):
        logger.info(f"\nProcessing asset class: {asset_class} with {len(symbols)} symbols")
        process_asset_class(asset_class, symbols)
        
        # Add additional delay between asset classes as a safety measure
        if idx < len(all_symbols) - 1:  # Don't wait after the last asset class
            logger.info(f"Waiting {inter_class_delay} seconds before processing next asset class...")
            time.sleep(inter_class_delay)
    
    logger.info("\nAll data fetching completed!")

if __name__ == "__main__":
    main()