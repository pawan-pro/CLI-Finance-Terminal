import requests
import pandas as pd

# List of major commodities available for free (check docs/API for symbol support)
commodities = ['XAU/USD',  # Gold
               #'XAG/USD',  # Silver
               #'WTI/USD',  # Crude oil West Texas Intermediate
               #'BRENT/USD',# Crude oil Brent
               #'NATGAS/USD' # Natural gas
              ]
api_key = 'd423c8d01edf48fc940b88a5a894bb2f'
csv_file = '../data/commodities_15min.csv'

try:

    df_existing = pd.read_csv(csv_file, parse_dates=['timestamp'])
except FileNotFoundError:
    df_existing = pd.DataFrame(columns=['commodity', 'timestamp', 'open', 'high', 'low', 'close'])

rows = []
for symbol in commodities:
    url = (
        f"https://api.twelvedata.com/time_series"
        f"?symbol={symbol}&interval=15min&outputsize=96&apikey={api_key}"
    )
    data = requests.get(url).json()
    for entry in data.get('values', []):
        rows.append({
            'commodity': symbol,
            'timestamp': pd.to_datetime(entry['datetime']),
            'open': float(entry['open']),
            'high': float(entry['high']),
            'low': float(entry['low']),
            'close': float(entry['close'])
        })

df_new = pd.DataFrame(rows)
df_combined = pd.concat([df_existing, df_new]).drop_duplicates(subset=['commodity', 'timestamp']).sort_values(['commodity', 'timestamp'])
df_combined.to_csv(csv_file, index=False)
