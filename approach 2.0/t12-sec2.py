import requests
import pandas as pd
from datetime import datetime
import os
from rate_limiter import APITimer
from dotenv import load_dotenv

load_dotenv()

sector_etfs = [
    'XLRE', # Real Estate
    'XLB',  # Materials
    'XLC'   # Communication Services
]
api_key = os.getenv('TWELVE_DATA_API_KEY')
csv_file = 'approach 2.0/data/sector2_etf_15min.csv'

# Initialize the timer
api_timer = APITimer(calls=8, period=60)

try:
    df_existing = pd.read_csv(csv_file, parse_dates=['timestamp'])
except FileNotFoundError:
    df_existing = pd.DataFrame(columns=['sector_etf', 'timestamp', 'open', 'high', 'low', 'close'])

rows = []
for symbol in sector_etfs:
    # Add the wait call inside the loop
    api_timer.wait_if_needed()

    print(f"Fetching data for {symbol}...")
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
