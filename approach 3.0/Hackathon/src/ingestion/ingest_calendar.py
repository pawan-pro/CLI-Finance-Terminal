import pandas as pd
import duckdb
import os
import glob
from datetime import timedelta

def ingest_calendar():
    # Path Resolution
    base_path = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.normpath(os.path.join(base_path, "../../data/silver/market_data.duckdb"))
    bronze_dir = os.path.normpath(os.path.join(base_path, "../../data/bronze/"))
    
    # Find latest calendar export
    files = glob.glob(os.path.join(bronze_dir, "CALENDAR_EXPORT_*.csv"))
    if not files:
        print("⚠️ No Calendar CSV found in bronze folder.")
        return
    
    latest_file = max(files, key=os.path.getctime)
    print(f"📂 Loading: {os.path.basename(latest_file)}")
    
    df = pd.read_csv(latest_file)
    
    # 1. Normalization: MT5 Time (GMT+2) to UTC (Subtract 2 hours)
    df['time_utc'] = pd.to_datetime(df['time_mt5']) - timedelta(hours=2)
    
    # 2. Handle 'Zero' data logic
    df['actual'] = df['actual'].apply(lambda x: None if x == 0.0 else x)
    df['forecast'] = df['forecast'].apply(lambda x: None if x == 0.0 else x)

    # 3. CRITICAL: Select exactly the 6 columns in the correct order
    # and explicitly drop the pandas index to avoid the '7th column' binder error.
    df = df[['time_utc', 'currency', 'event_name', 'impact', 'actual', 'forecast']].copy()

    conn = duckdb.connect(db_path)
    
    # 4. HARD RESET: Drop and Recreate to fix the Binder Error
    conn.execute("DROP TABLE IF EXISTS economic_events")
    conn.execute("""
        CREATE TABLE economic_events (
            time_utc TIMESTAMP,
            currency VARCHAR,
            event_name VARCHAR,
            impact VARCHAR,
            actual DOUBLE,
            forecast DOUBLE,
            PRIMARY KEY (time_utc, currency, event_name)
        )
    """)

    # 5. Register and Insert
    conn.register("temp_cal", df)
    
    try:
        # We use a simple INSERT here because we dropped the table first.
        # This is the most reliable way to fix Binder Errors.
        conn.execute("INSERT INTO economic_events SELECT * FROM temp_cal")
        print(f"✅ Successfully ingested {len(df)} events into the Silver Layer.")
    except Exception as e:
        print(f"❌ Ingestion Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    ingest_calendar()