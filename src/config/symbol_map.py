"""
Symbol Mapping Utility
This module provides mapping between internal application symbols and symbols for different data providers.
"""
from typing import Dict, Optional

# Define symbol mapping between internal application symbols and different provider symbols
# Internal symbols to Alpha Vantage symbols mapping
ALPHAVANTAGE_SYMBOL_MAPPING = {
    # Major indices
    'US500Roll': 'SPX',      # S&P 500
    'US500': 'SPX',          # S&P 500
    'SPX': 'SPX',            # S&P 500
    'ES': 'SPY',             # S&P 500 E-mini futures alternative - use SPY ETF
    
    'US30Roll': 'DJI',        # Dow Jones
    'US30': 'DJI',            # Dow Jones
    'DJI': 'DJI',             # Dow Jones
    'YM': 'DIA',              # Dow Jones E-mini futures alternative - use DIA ETF
    
    'UT100Roll': 'NDX',      # Nasdaq 100
    'UT100': 'NDX',          # Nasdaq 100
    'NDX': 'NDX',            # Nasdaq 100
    'NQ': 'QQQ',             # Nasdaq 100 E-mini futures alternative - use QQQ ETF
    
    'DE40Roll': 'DAX',      # DAX
    'DE40': 'DAX',          # DAX
    'DAX': 'DAX',           # DAX
    
    'UK100Roll': 'FTSE',      # FTSE 100
    'UK100': 'FTSE',          # FTSE 100
    'FTSE': 'FTSE',           # FTSE 100
    
    'FRA40Roll': 'FCHI',      # CAC 40
    'FRA40': 'FCHI',          # CAC 40
    'CAC40': 'FCHI',          # CAC 40
    
    'JP225Roll': 'N225',      # Nikkei 225
    'JP225': 'N225',          # Nikkei 225
    
    'HK50Roll': 'HSI',        # Hang Seng
    'HK50': 'HSI',            # Hang Seng
    
    'CHINA50Roll': '000016.SS', # CSI 500
    
    # Currencies (Alpha Vantage uses different format)
    'EURUSD.sd': 'EURUSD',     # EUR/USD
    'EURUSD': 'EURUSD',        # EUR/USD
    
    'GBPUSD.sd': 'GBPUSD',     # GBP/USD
    'GBPUSD': 'GBPUSD',        # GBP/USD
    
    'USDJPY.sd': 'USDJPY',     # USD/JPY
    'USDJPY': 'USDJPY',        # USD/JPY
    
    'AUDUSD.sd': 'AUDUSD',     # AUD/USD
    'AUDUSD': 'AUDUSD',        # AUD/USD
    
    'USDCAD.sd': 'USDCAD',     # USD/CAD
    'USDCAD': 'USDCAD',        # USD/CAD
    
    'USDCHF.sd': 'USDCHF',     # USD/CHF
    'USDCHF': 'USDCHF',        # USD/CHF
    
    'NZDUSD.sd': 'NZDUSD',     # NZD/USD
    'NZDUSD': 'NZDUSD',        # NZD/USD
    
    'USDCNH.sd': 'USDCNH',     # USD/CNH
    
    # Commodities
    'XAUUSD': 'XAU',        # Gold - Alpha Vantage uses XAU (spot gold)
    'GC=F': 'GC=F',          # Gold futures
    
    'XAGUSD': 'XAG',        # Silver - Alpha Vantage uses XAG (spot silver)
    'SIL=F': 'SIL=F',         # Silver futures
    
    'XPTUSD': 'XPT',        # Platinum - Alpha Vantage uses XPT
    
    'USOILRoll': 'CL=F',       # Crude Oil
    'USOIL': 'CL=F',           # Crude Oil
    'CL=F': 'CL=F',            # Crude Oil futures
    
    'BRENT': 'BZ=F',           # Brent Oil
    'NGAS': 'NG=F',            # Natural Gas
    
    # Volatility
    'VIXRoll': 'VIX',         # VIX
    'VIX': 'VIX',             # VIX
    
    # Crypto
    'BTCUSD.lv': 'BTC-USD',     # Bitcoin
    'BTCUSD': 'BTC-USD',        # Bitcoin
    
    'ETHUSD.lv': 'ETH-USD',     # Ethereum
    'ETHUSD': 'ETH-USD',        # Ethereum
    
    'XRPUSD.lv': 'XRP-USD',     # Ripple
    'LTCUSD.lv': 'LTC-USD',     # Litecoin
    'BCHUSD.lv': 'BCH-USD',     # Bitcoin Cash
    'EOSUSD.lv': 'EOS-USD',     # EOS
}

# Finnhub symbol mappings (for backward compatibility if needed)
FINNHUB_SYMBOL_MAPPING = {
    # Major indices
    'US500Roll': '^GSPC',      # S&P 500
    'US500': '^GSPC',          # S&P 500
    'SPX': '^GSPC',            # S&P 500
    'ES': '^GSPC',             # S&P 500 E-mini futures
    
    'US30Roll': '^DJI',        # Dow Jones
    'US30': '^DJI',            # Dow Jones
    'DJI': '^DJI',             # Dow Jones
    'YM': '^DJI',              # Dow Jones E-mini futures
    
    'UT100Roll': '^IXIC',      # Nasdaq 100
    'UT100': '^IXIC',          # Nasdaq 100
    'NDX': '^IXIC',            # Nasdaq 100
    'NQ': '^IXIC',             # Nasdaq 100 E-mini futures
    
    'DE40Roll': '^GDAXI',      # DAX
    'DE40': '^GDAXI',          # DAX
    'DAX': '^GDAXI',           # DAX
    
    'UK100Roll': '^FTSE',      # FTSE 100
    'UK100': '^FTSE',          # FTSE 100
    'FTSE': '^FTSE',           # FTSE 100
    
    'FRA40Roll': '^FCHI',      # CAC 40
    'FRA40': '^FCHI',          # CAC 40
    'CAC40': '^FCHI',          # CAC 40
    
    'JP225Roll': '^N225',      # Nikkei 225
    'JP225': '^N225',          # Nikkei 225
    
    'HK50Roll': '^HSI',        # Hang Seng
    'HK50': '^HSI',            # Hang Seng
    
    'CHINA50Roll': '000016.SS', # CSI 500
    
    # Currencies (Finnhub may use OANDA format)
    'EURUSD.sd': 'EURUSD',     # EUR/USD
    'EURUSD': 'EURUSD',        # EUR/USD
    
    'GBPUSD.sd': 'GBPUSD',     # GBP/USD
    'GBPUSD': 'GBPUSD',        # GBP/USD
    
    'USDJPY.sd': 'USDJPY',     # USD/JPY
    'USDJPY': 'USDJPY',        # USD/JPY
    
    'AUDUSD.sd': 'AUDUSD',     # AUD/USD
    'AUDUSD': 'AUDUSD',        # AUD/USD
    
    'USDCAD.sd': 'USDCAD',     # USD/CAD
    'USDCAD': 'USDCAD',        # USD/CAD
    
    'USDCHF.sd': 'USDCHF',     # USD/CHF
    'USDCHF': 'USDCHF',        # USD/CHF
    
    'NZDUSD.sd': 'NZDUSD',     # NZD/USD
    'NZDUSD': 'NZDUSD',        # NZD/USD
    
    'USDCNH.sd': 'USDCNH',     # USD/CNH
    
    # Commodities
    'XAUUSD': 'XAUUSD',        # Gold
    'GC=F': 'XAUUSD',          # Gold futures
    
    'XAGUSD': 'XAGUSD',        # Silver
    'SIL=F': 'XAGUSD',         # Silver futures
    
    'XPTUSD': 'XPTUSD',        # Platinum
    
    'USOILRoll': 'CL=F',       # Crude Oil
    'USOIL': 'CL=F',           # Crude Oil
    'CL=F': 'CL=F',            # Crude Oil futures
    
    'BRENT': 'BZ=F',           # Brent Oil
    'NGAS': 'NG=F',            # Natural Gas
    
    # Volatility
    'VIXRoll': '^VIX',         # VIX
    'VIX': '^VIX',             # VIX
    
    # Crypto
    'BTCUSD.lv': 'BTCUSD',     # Bitcoin
    'BTCUSD': 'BTCUSD',        # Bitcoin
    
    'ETHUSD.lv': 'ETHUSD',     # Ethereum
    'ETHUSD': 'ETHUSD',        # Ethereum
    
    'XRPUSD.lv': 'XRPUSD',     # Ripple
    'LTCUSD.lv': 'LTCUSD',     # Litecoin
    'BCHUSD.lv': 'BCHUSD',     # Bitcoin Cash
    'EOSUSD.lv': 'EOSUSD',     # EOS
}

def get_alphavantage_symbol(internal_symbol: str) -> Optional[str]:
    """
    Get the Alpha Vantage-compatible symbol for an internal application symbol.
    
    Args:
        internal_symbol: The symbol used internally in the application
        
    Returns:
        The corresponding Alpha Vantage symbol or None if not found
    """
    return ALPHAVANTAGE_SYMBOL_MAPPING.get(internal_symbol, internal_symbol)

def get_finnhub_symbol(internal_symbol: str) -> Optional[str]:
    """
    Get the Finnhub-compatible symbol for an internal application symbol.
    
    Args:
        internal_symbol: The symbol used internally in the application
        
    Returns:
        The corresponding Finnhub symbol or None if not found
    """
    return FINNHUB_SYMBOL_MAPPING.get(internal_symbol, internal_symbol)

def get_internal_symbol(provider_symbol: str, provider: str = "alphavantage") -> Optional[str]:
    """
    Get the internal application symbol for a provider symbol.
    This is the reverse mapping operation.
    
    Args:
        provider_symbol: The symbol used by the data provider
        provider: The data provider ('alphavantage' or 'finnhub')
        
    Returns:
        The corresponding internal application symbol or None if not found
    """
    mapping = ALPHAVANTAGE_SYMBOL_MAPPING if provider.lower() == "alphavantage" else FINNHUB_SYMBOL_MAPPING
    for internal, provider_sym in mapping.items():
        if provider_sym == provider_symbol:
            return internal
    return provider_symbol  # Return original if not found in mapping

def map_symbol_for_request(internal_symbol: str, provider: str = "alphavantage") -> str:
    """
    Map an internal symbol to a provider-compatible symbol for API requests.
    If the symbol is not in the mapping, return it as-is.
    
    Args:
        internal_symbol: The symbol used internally in the application
        provider: The data provider ('alphavantage' or 'finnhub')
        
    Returns:
        The provider-compatible symbol
    """
    if provider.lower() == "alphavantage":
        mapped = get_alphavantage_symbol(internal_symbol)
        return mapped if mapped is not None else internal_symbol
    else:  # Default to Finnhub mapping for backward compatibility
        mapped = get_finnhub_symbol(internal_symbol)
        return mapped if mapped is not None else internal_symbol