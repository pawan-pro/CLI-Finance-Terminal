import pandas as pd
import duckdb
import glob
import os
from datetime import datetime, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BRONZE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../../data/bronze"))
SILVER_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../../data/silver"))
SILVER_DB = os.path.join(SILVER_DIR, "market_data.duckdb")

def initialize_lake():
    if not os.path.exists(SILVER_DIR): os.makedirs(SILVER_DIR)
    conn = duckdb.connect(SILVER_DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS m15_bars (
            symbol VARCHAR, time_utc TIMESTAMP, open DOUBLE, high DOUBLE, 
            low DOUBLE, close DOUBLE, volume BIGINT, spread INTEGER, 
            ingested_at TIMESTAMP, PRIMARY KEY (symbol, time_utc)
        )
    """)
    conn.close()

def ingest_snapshots():
    conn = duckdb.connect(SILVER_DB)
    files = glob.glob(os.path.join(BRONZE_DIR, "*.csv"))
    print(f"🚀 Processing {len(files)} snapshots...")

    for f in files:
        fname = os.path.basename(f)
        # FILTER: Ignore non-price data
        if any(x in fname for x in ["CALENDAR", "Metadata", "SymbolsList", "signals"]):
            continue
        
        try:
            df = pd.read_csv(f)
            symbol = fname.split('_')[0]
            df.columns = [c.lower().replace('vol', 'volume').strip() for c in df.columns]
            df['symbol'] = symbol
            # MT5 is GMT+2. Subtract 2 to get UTC.
            df['time_utc'] = pd.to_datetime(df['time_gmt']) - timedelta(hours=2)
            df['ingested_at'] = datetime.now()

            # Using standard insert logic
            conn.register("temp_df", df)
            conn.execute("""
                INSERT INTO m15_bars 
                SELECT symbol, time_utc, open, high, low, close, volume, spread, ingested_at 
                FROM temp_df ON CONFLICT (symbol, time_utc) DO NOTHING
            """)
            print(f"✅ {symbol}: Synced.")
        except Exception as e:
            print(f"❌ Error in {f}: {e}")
    conn.close()

if __name__ == "__main__":
    initialize_lake()
    ingest_snapshots()