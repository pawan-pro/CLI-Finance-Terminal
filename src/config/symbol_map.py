"""
Symbol Mapping Utility
This module provides mapping from internal application symbols to Alpha Vantage API tickers.
"""
from typing import Dict

# This map is the single source of truth for symbol translation.
# It primarily targets symbols usable with the GLOBAL_QUOTE endpoint, which means
# using ETFs as proxies for indices and commodities where necessary.
# For Forex and Crypto, a different endpoint is required, so the mapping
# provides the necessary symbol components.
ALPHAVANTAGE_SYMBOL_MAPPING = {
    # Indices -> ETFs or AV Index Tickers for GLOBAL_QUOTE
    'US500Roll': 'SPY',
    'US30Roll': 'DIA',
    'UT100Roll': 'QQQ',      # Using QQQ as a proxy for Nasdaq 100
    'DE40Roll': '^GDAXI',    # German DAX index
    'UK100Roll': '^FTSE',    # UK FTSE 100 index
    'JP225Roll': '^N225',    # Japan Nikkei 225 index

    # Commodities -> ETFs for GLOBAL_QUOTE
    'XAUUSD': 'GLD',         # Gold ETF
    'USOILRoll': 'USO',      # WTI Crude Oil ETF

    # Volatility Index
    'VIXRoll': '^VIX',

    # Bonds (ETFs, direct mapping, no change needed)
    'TLT': 'TLT',
    'IEF': 'IEF',
    'SHY': 'SHY',
    'LQD': 'LQD',

    # Forex (from_currency/to_currency, handled by fetcher)
    'EURUSD': 'EUR/USD',
    'GBPUSD': 'GBP/USD',
    'USDJPY': 'USD/JPY',
    'AUDUSD': 'AUD/USD',
    'USDCAD': 'USD/CAD',

    # Crypto (symbol, handled by fetcher)
    'BTCUSD': 'BTC',
    'ETHUSD': 'ETH',
}

# A reverse map to get internal symbols from provider symbols
REVERSE_ALPHAVANTAGE_SYMBOL_MAPPING = {v: k for k, v in ALPHAVANTAGE_SYMBOL_MAPPING.items()}

# Lists to identify asset classes
FOREX_SYMBOLS = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD']
CRYPTO_SYMBOLS = ['BTCUSD', 'ETHUSD']

def map_symbol_for_request(internal_symbol: str) -> str:
    """
    Map an internal symbol to the Alpha Vantage-compatible symbol.
    If the symbol is not in the mapping, it is returned as-is,
    assuming it's a direct ticker (like for stocks or other ETFs).
    """
    return ALPHAVANTAGE_SYMBOL_MAPPING.get(internal_symbol, internal_symbol)

def get_internal_symbol(provider_symbol: str) -> str:
    """
    Get the internal application symbol from an Alpha Vantage symbol.
    Returns the original symbol if no reverse mapping is found.
    """
    return REVERSE_ALPHAVANTAGE_SYMBOL_MAPPING.get(provider_symbol, provider_symbol)