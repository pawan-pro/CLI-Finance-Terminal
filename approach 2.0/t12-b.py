import requests
import pandas as pd
from datetime import datetime
import os
from rate_limiter import APITimer

bonds = ['US2Y', 'US5Y', 'US10Y', 'US30Y']
api_key = os.getenv('TWELVE_DATA_API_KEY')
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
csv_file = os.path.join(script_dir, 'data/bonds_15min.csv')

# Initialize the timer with the shared timestamp file
timestamp_file = os.path.join(project_root, 'timestamps.json')
api_timer = APITimer(calls=8, period=60, file_path=timestamp_file)

try:
    df_existing = pd.read_csv(csv_file, parse_dates=['timestamp'])
except FileNotFoundError:
    df_existing = pd.DataFrame(columns=['bond', 'timestamp', 'yield'])

rows = []
for symbol in bonds:
    # Add the wait call inside the loop
    api_timer.wait_if_needed()

    print(f"Fetching data for {symbol}...")
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
