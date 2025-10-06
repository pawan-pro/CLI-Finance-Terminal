# script to load last 24 hours of data from mt5 for symbols in symbols.txt
# also saves to csv file
# customized for mac os, running mt5 via wine bottler
# in 15 minute intervals

#### use wine python data-mt5.py to run 


import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
import time
import os
import sys


print(f"[{datetime.now()}] Attempting to initialize MT5...")
mt5.initialize()
time.sleep(2)
if not mt5.initialize():
    print(f"[{datetime.now()}] initialize() failed, error code = {mt5.last_error()}")
    sys.exit(1)
print(f"[{datetime.now()}] MT5 initialized")
time.sleep(2)


account_info = mt5.account_info()
if account_info is None:
    print(f"[{datetime.now()}] Failed to get account info")
    mt5.shutdown()
    sys.exit(1)
print(f"[{datetime.now()}] Account info: {account_info}")
time.sleep(2)

script_dir = os.path.dirname(os.path.abspath(__file__))
symbols_file = os.path.join(script_dir, 'symbols.txt')


try:
    with open(symbols_file, 'r') as f:
        symbols = [line.strip() for line in f if line.strip()]
    print(f"[{datetime.now()}] Symbols: {symbols}")
except Exception as e:
    print(f"[{datetime.now()}] Failed to read symbols.txt: {e}")
    mt5.shutdown()
    sys.exit(1)
time.sleep(2)



now = datetime.now()
from_time = now - timedelta(days=1)
from_time_mt5 = datetime(from_time.year, from_time.month, from_time.day, from_time.hour, from_time.minute)
print(f"[{datetime.now()}] Fetching data from: {from_time_mt5} to {now}")
time.sleep(2)

# fetch data for each symbol

for symbol in symbols:
    print(f"[{datetime.now()}] Processing symbol: {symbol}")
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(f"[{datetime.now()}] Symbol {symbol} not found on MT5")
        continue
    if not symbol_info.visible:
        print(f"[{datetime.now()}] Symbol {symbol} is not visible, trying to switch on...")
        if not mt5.symbol_select(symbol, True):
            print(f"[{datetime.now()}] Failed to select symbol {symbol}")
            continue
    print(f"[{datetime.now()}] Fetching 15m bars for {symbol} from {from_time_mt5} to {now}")
    rates = mt5.copy_rates_from(symbol, mt5.TIMEFRAME_M15, from_time_mt5, 96)
    if rates is None or len(rates) == 0:
        print(f"[{datetime.now()}] No data for symbol {symbol} in the last 24 hours.")
        continue
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    print(f"[{datetime.now()}] Retrieved {len(df)} bars for {symbol}. Latest bar: {df['time'].max() if not df.empty else 'N/A'}")
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
    time.sleep(2)

# shutdown mt5 connection
mt5.shutdown()
print(f"[{datetime.now()}] MT5 shutdown")
time.sleep(2)
print(f"[{datetime.now()}] Script completed")
time.sleep(2)
sys.exit(0)