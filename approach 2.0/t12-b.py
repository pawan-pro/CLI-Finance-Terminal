import requests
import pandas as pd

bonds = ['US2Y', 'US5Y', 'US10Y', 'US30Y']
api_key = 'd423c8d01edf48fc940b88a5a894bb2f'
csv_file = 'approach 2.0/data/bonds_15min.csv'

try:
    df_existing = pd.read_csv(csv_file, parse_dates=['timestamp'])
except FileNotFoundError:
    df_existing = pd.DataFrame(columns=['bond', 'timestamp', 'yield'])

rows = []
for symbol in bonds:
    url = (
        f"https://api.twelvedata.com/time_series"
        f"?symbol={symbol}&interval=15min&outputsize=96&apikey={api_key}"
    )
    data = requests.get(url).json()
    # Typically, bond yield data does not have "open, high, low, close", just "value" (yield)
    for entry in data.get('values', []):
        rows.append({
            'bond': symbol,
            'timestamp': pd.to_datetime(entry['datetime']),
            'yield': float(entry.get('close', entry.get('value', 0))),
        })

df_new = pd.DataFrame(rows)
df_combined = pd.concat([df_existing, df_new]).drop_duplicates(subset=['bond', 'timestamp']).sort_values(['bond', 'timestamp'])
df_combined.to_csv(csv_file, index=False)
