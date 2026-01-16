import requests
import duckdb
import os
import pandas as pd
from datetime import datetime
import io

def ingest_yields():
    base_path = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.normpath(os.path.join(base_path, "../../data/silver/market_data.duckdb"))
    
    # FRED Series: DGS10 (10-Year Treasury), DGS2 (2-Year Treasury)
    series = {"DGS10": "US10Y", "DGS2": "US02Y"}
    conn = duckdb.connect(db_path)
    
    print("🌐 Fetching Yields from FRED (Federal Reserve)...")
    for fred_id, internal_name in series.items():
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={fred_id}"
        try:
            response = requests.get(url)
            df = pd.read_csv(io.StringIO(response.text))
            latest_val = df.iloc[-1][fred_id]
            
            # If data is '.', take previous row (handles holidays)
            if latest_val == '.': latest_val = df.iloc[-2][fred_id]
            
            val = float(latest_val)
            time_utc = datetime.now()

            conn.execute("""
                INSERT INTO m15_bars (symbol, time_utc, open, high, low, close, volume, spread, ingested_at)
                VALUES (?, ?, ?, ?, ?, ?, 0, 0, ?)
                ON CONFLICT (symbol, time_utc) DO UPDATE SET close = excluded.close
            """, (internal_name, time_utc, val, val, val, val, datetime.now()))
            print(f"✅ {internal_name} Synced: {val}%")
        except Exception as e:
            print(f"❌ Error fetching {fred_id}: {e}")
            
    conn.close()

if __name__ == "__main__":
    ingest_yields()