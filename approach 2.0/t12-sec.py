import requests
import pandas as pd

sector_etfs = [
    'XLK',  # Technology
    'XLF',  # Financials
    'XLE',  # Energy
    'XLV',  # Health Care
    'XLY',  # Consumer Discretionary
    'XLP',  # Consumer Staples
    'XLI',  # Industrials
]
api_key = 'd423c8d01edf48fc940b88a5a894bb2f'
csv_file = 'approach 2.0/data/sector_etf_15min.csv'

try:
    df_existing = pd.read_csv(csv_file, parse_dates=['timestamp'])
except FileNotFoundError:
    df_existing = pd.DataFrame(columns=['sector_etf', 'timestamp', 'open', 'high', 'low', 'close'])

rows = []
for symbol in sector_etfs:
    url = (
        f"https://api.twelvedata.com/time_series"
        f"?symbol={symbol}&interval=15min&outputsize=96&apikey={api_key}"
    )
    data = requests.get(url).json()
    if "values" not in data:
        print(f"No data for {symbol}: {data}")
        continue
    for entry in data.get('values', []):
        rows.append({
            'sector_etf': symbol,
            'timestamp': pd.to_datetime(entry['datetime']),
            'open': float(entry['open']),
            'high': float(entry['high']),
            'low': float(entry['low']),
            'close': float(entry['close'])
        })

df_new = pd.DataFrame(rows)
df_combined = pd.concat([df_existing, df_new]).drop_duplicates(subset=['sector_etf', 'timestamp']).sort_values(['sector_etf', 'timestamp'])
df_combined.to_csv(csv_file, index=False)
