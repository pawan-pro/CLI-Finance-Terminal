import pandas as pd
import duckdb
import os
import glob
from datetime import timedelta

def ingest_calendar():
    base_path = os.path.dirname(os.path.abspath(__file__))
    # Force Master Absolute Path
    db_path = "/Users/pawan/CLI-Finance-Terminal/approach 3.0/Hackathon/data/silver/market_data.duckdb"
    bronze_dir = "/Users/pawan/CLI-Finance-Terminal/approach 3.0/Hackathon/data/bronze/"
    
    files = glob.glob(os.path.join(bronze_dir, "CALENDAR_EXPORT_*.csv"))
    if not files:
        print("⚠️ No Calendar CSV found.")
        return
    
    latest_file = max(files, key=os.path.getctime)
    print(f"📂 Loading: {os.path.basename(latest_file)}")
    
    df = pd.read_csv(latest_file)
    df['time_utc'] = pd.to_datetime(df['time_mt5']) - timedelta(hours=2)
    df['actual'] = df['actual'].apply(lambda x: None if x == 0.0 else x)
    df['forecast'] = df['forecast'].apply(lambda x: None if x == 0.0 else x)
    df = df[['time_utc', 'currency', 'event_name', 'impact', 'actual', 'forecast']].copy()

    conn = duckdb.connect(db_path)
    
    # Initialize table if not exists
    conn.execute("""
        CREATE TABLE IF NOT EXISTS economic_events (
            time_utc TIMESTAMP,
            currency VARCHAR,
            event_name VARCHAR,
            impact VARCHAR,
            actual DOUBLE,
            forecast DOUBLE,
            PRIMARY KEY (time_utc, currency, event_name)
        )
    """)

    conn.register("temp_cal", df)
    
    try:
        # Using INSERT OR IGNORE logic to handle duplicates within the CSV
        conn.execute("""
            INSERT OR IGNORE INTO economic_events 
            SELECT DISTINCT * FROM temp_cal
        """)
        count = conn.execute("SELECT count(*) FROM economic_events").fetchone()[0]
        print(f"✅ Calendar Refreshed. {count} total events in Lake.")
    except Exception as e:
        print(f"❌ Ingestion Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    ingest_calendar()