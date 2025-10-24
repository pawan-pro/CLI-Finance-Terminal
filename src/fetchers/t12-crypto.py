import requests
import pandas as pd

cryptos = ['BTC/USD', 'ETH/USD', 'XRP/USD', 'LTC/USD', 'ADA/USD']
api_key = 'd423c8d01edf48fc940b88a5a894bb2f'
csv_file = '../data/crypto_15min.csv'

try:
    df_existing = pd.read_csv(csv_file, parse_dates=['timestamp'])
except FileNotFoundError:
    df_existing = pd.DataFrame(columns=['crypto', 'timestamp', 'open', 'high', 'low', 'close'])

rows = []
for symbol in cryptos:
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
            'crypto': symbol,
            'timestamp': pd.to_datetime(entry['datetime']),
            'open': float(entry['open']),
            'high': float(entry['high']),
            'low': float(entry['low']),
            'close': float(entry['close'])
        })

df_new = pd.DataFrame(rows)
df_combined = pd.concat([df_existing, df_new]).drop_duplicates(subset=['crypto', 'timestamp']).sort_values(['crypto', 'timestamp'])
df_combined.to_csv(csv_file, index=False)
