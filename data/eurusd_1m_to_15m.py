import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
import time
import sys

symbol = 'EURUSD'

print(f"[SYSTEM TIME] {datetime.now()}")
if not mt5.initialize():
    print(f"[MT5 INIT ERROR] {mt5.last_error()}")
    sys.exit(1)

now = datetime.now()
from_time = now - timedelta(days=1)
from_time_mt5 = datetime(from_time.year, from_time.month, from_time.day, from_time.hour, from_time.minute)

print(f"Fetching 1M bars for {symbol} from {from_time_mt5} to {now}")

rates = mt5.copy_rates_from(symbol, mt5.TIMEFRAME_M1, from_time_mt5, 1440)  # 1440 minutes in 24 hours
if rates is None or len(rates) == 0:
    print(f"No 1M data for {symbol}")
    mt5.shutdown()
    sys.exit(1)

df = pd.DataFrame(rates)
df['time'] = pd.to_datetime(df['time'], unit='s')
print(f"Retrieved {len(df)} 1M bars. Latest bar: {df['time'].max() if not df.empty else 'N/A'}")

# Resample to 15M bars
if not df.empty:
    df.set_index('time', inplace=True)
    df_15m = df.resample('15T').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'tick_volume': 'sum',
        'spread': 'mean',
        'real_volume': 'sum'
    }).dropna()
    df_15m.reset_index(inplace=True)
    print(f"Resampled to {len(df_15m)} 15M bars. Latest bar: {df_15m['time'].max() if not df_15m.empty else 'N/A'}")
    # Save to CSV
    csv_filename = f"EURUSD.sd_15m_resampled.csv"
    df_15m.to_csv(csv_filename, index=False)
    print(f"15M bars saved to {csv_filename}")
else:
    print("No data to resample.")

mt5.shutdown()
print("[DONE]")
