#!/usr/bin/env python3
# script to load last 24 hours of data from alternative source (yfinance) 
# for symbols in symbols.txt, also saves to csv file
# This is a native macOS compatible version of the data-mt5.py script

import pandas as pd
from datetime import datetime, timedelta
import time
import os
import sys
import yfinance as yf

print(f"[{datetime.now()}] Starting data collection script...")
time.sleep(2)

script_dir = os.path.dirname(os.path.abspath(__file__))
symbols_file = os.path.join(script_dir, 'symbols.txt')

try:
    with open(symbols_file, 'r') as f:
        lines = f.readlines()
        symbols = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):  # Skip empty lines and comments
                symbols.append(line)
    print(f"[{datetime.now()}] Symbols to fetch: {symbols}")
except Exception as e:
    print(f"[{datetime.now()}] Failed to read symbols.txt: {e}")
    sys.exit(1)

time.sleep(2)

# Create folders if they don't exist
for folder in ['forex', 'indices', 'commodities', 'crypto', 'other']:
    folder_path = os.path.join(script_dir, folder)
    os.makedirs(folder_path, exist_ok=True)

now = datetime.now()
from_time = now - timedelta(days=1)
print(f"[{datetime.now()}] Fetching data from: {from_time} to {now}")
time.sleep(2)

# Mapping of MT5 symbols to Yahoo Finance symbols
symbol_mapping = {
    # Forex - Yahoo Finance doesn't have all the same symbols, using common ones
    'EURUSD.sd': 'EURUSD=X',
    'GBPUSD.sd': 'GBPUSD=X',
    'USDJPY.sd': 'USDJPY=X',
    'AUDUSD.sd': 'AUDUSD=X',
    'USDCAD.sd': 'USDCAD=X',
    'USDCHF.sd': 'USDCHF=X',
    'NZDUSD.sd': 'NZDUSD=X',
    # Indices - some may need adjustment
    'US500Roll': '^GSPC',  # S&P 500
    'US30Roll': '^DJI',    # Dow Jones
    'UK100Roll': '^FTSE',  # FTSE 100
    'DE40Roll': '^GDAXI',  # DAX
    'FRA40Roll': '^FCHI',  # CAC 40
    'JP225Roll': '^N225',  # Nikkei 225
    'HK50Roll': '^HSI',    # Hang Seng
    # Commodities
    'XAUUSD': 'GC=F',      # Gold
    'XAGUSD': 'SI=F',      # Silver
    'USOILRoll': 'CL=F',   # Crude Oil
    # Crypto
    'BTCUSD.lv': 'BTC-USD',
    'ETHUSD.lv': 'ETH-USD',
    'LTCUSD.lv': 'LTC-USD',
    # VIX
    'VIXRoll': '^VIX'
}

# fetch data for each symbol
for symbol in symbols:
    if symbol.strip() == '':  # Skip empty lines
        continue
        
    print(f"[{datetime.now()}] Processing symbol: {symbol}")
    
    # Map the MT5 symbol to Yahoo Finance symbol
    yf_symbol = symbol_mapping.get(symbol, symbol)
    
    try:
        # Create a ticker object
        ticker = yf.Ticker(yf_symbol)
        
        # Fetch historical data for the last day with 15-minute intervals
        hist = ticker.history(period="1d", interval="15m")
        
        if hist.empty:
            print(f"[{datetime.now()}] No data for symbol {symbol} (Yahoo symbol: {yf_symbol}).")
            continue
            
        # Convert the index to a 'time' column like in the original script
        df = hist.reset_index()
        df.rename(columns={'Datetime': 'time'}, inplace=True)
        
        print(f"[{datetime.now()}] Retrieved {len(df)} bars for {symbol}. Latest bar: {df['time'].max() if not df.empty else 'N/A'}")
        
        # Determine folder based on original categories
        forex = ['EURUSD.sd', 'GBPUSD.sd', 'USDJPY.sd', 'AUDUSD.sd', 'USDCAD.sd', 'USDCHF.sd', 'NZDUSD.sd', 'USDCNH.sd']
        crypto = ['BTCUSD.lv', 'ETHUSD.lv', 'XRPUSD.lv', 'LTCUSD.lv', 'BCHUSD.lv', 'EOSUSD.lv']
        indices = ['US500Roll', 'US30Roll', 'UK100Roll', 'DE40Roll', 'FRA40Roll', 'JP225Roll', 'HK50Roll', 'CHINA50Roll']
        commodities = ['XAUUSD', 'XAGUSD', 'XPTUSD', 'USOILRoll', 'BRENT', 'NGAS']
        other = ['VIXRoll']
        
        if symbol in forex:
            folder = 'forex'
        elif symbol in crypto:
            folder = 'crypto'
        elif symbol in indices:
            folder = 'indices'
        elif symbol in commodities:
            folder = 'commodities'
        else:
            folder = 'other'
            
        csv_filename = os.path.join(script_dir, folder, f"{symbol}_data.csv")
        try:
            df.to_csv(csv_filename, index=False)
            print(f"[{datetime.now()}] Data for {symbol} saved to {csv_filename}")
        except Exception as e:
            print(f"[{datetime.now()}] Failed to save data for {symbol} to {csv_filename}: {e}")
    except Exception as e:
        print(f"[{datetime.now()}] Failed to fetch data for {symbol} (Yahoo symbol: {yf_symbol}): {e}")
        
    time.sleep(2)

print(f"[{datetime.now()}] Script completed")
time.sleep(2)
sys.exit(0)