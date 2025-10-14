import requests
import pandas as pd
from datetime import datetime

symbols = [
    'SPY',    # S&P 500 (US large cap)
    'DIA',    # Dow Jones Industrial Average
    'QQQ',    # Nasdaq 100
    'IWM',    # Russell 2000 (small cap)
    'EWU',    # United Kingdom (UK FTSE 100 proxy)
    'EWJ',    # Japan (Nikkei 225 proxy)
    'FEZ',    # Euro Stoxx 50
    'DAX',    # Germany (ETF: DAX)
    'EEM',    # Emerging Markets (MSCI EM)
    'INDA',   # India (MSCI India)
    'MCHI',   # China (MSCI China)
    'EWG',    # Germany Equity (alternative DAX ETF)
    'EWQ',    # France
    'EWS',    # Singapore
    'EWA',    # Australia
]

api_key = 'd423c8d01edf48fc940b88a5a894bb2f'
csv_file = 'approach 2.0/data/indices_15min.csv'
interval = '15min'

# Try to read existing data
try:
    df_existing = pd.read_csv(csv_file, parse_dates=['timestamp'])
except FileNotFoundError:
    df_existing = pd.DataFrame(columns=['symbol', 'timestamp', 'open', 'high', 'low', 'close', 'volume'])

rows = []
for symbol in symbols:
    url = (
        f"https://api.twelvedata.com/time_series?"
        f"symbol={symbol}&interval={interval}&outputsize=96&apikey={api_key}"
    )
    data = requests.get(url).json()
    for entry in data.get('values', []):
        row = {
            'symbol': symbol,
            'timestamp': pd.to_datetime(entry['datetime']),
            'open': float(entry['open']),
            'high': float(entry['high']),
            'low': float(entry['low']),
            'close': float(entry['close']),
            'volume': float(entry['volume'])
        }
        rows.append(row)

df_new = pd.DataFrame(rows)

# Combine and drop duplicate (symbol, timestamp) entries
if not df_new.empty:
    df_combined = pd.concat([df_existing, df_new]).drop_duplicates(subset=['symbol', 'timestamp']).sort_values(['symbol', 'timestamp'])
else:
    df_combined = df_existing.sort_values(['symbol', 'timestamp'])


df_combined.to_csv(csv_file, index=False)

#save the csv to file in the current folder in the directory
df_combined = df_combined.reset_index(drop=True)