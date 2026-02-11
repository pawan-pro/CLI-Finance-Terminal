import pandas as pd
import duckdb
import os
import glob
from datetime import timedelta

def ingest_calendar():
    base_path = os.path.dirname(os.path.abspath(__file__))
    # Force Master Absolute Path
    db_path = "/Users/pawan/CLI-Finance-Terminal/approach-3.0/Hackathon/data/silver/market_data.duckdb"
    bronze_dir = "/Users/pawan/CLI-Finance-Terminal/approach-3.0/Hackathon/data/bronze/"
    
    files = glob.glob(os.path.join(bronze_dir, "CALENDAR_EXPORT_*.csv"))
    if not files:
        print("⚠️ No Calendar CSV found.")
        return
    
    latest_file = max(files, key=os.path.getctime)
    print(f"📂 Loading: {os.path.basename(latest_file)}")
    
    import csv
    import io

    # Read and process the CSV to handle commas within fields
    processed_rows = []
    with open(latest_file, 'r', encoding='utf-8') as f:
        # Use csv module which handles quoted fields properly
        reader = csv.reader(f)
        for row in reader:
            # If we have too many fields due to unquoted commas in event_name,
            # merge the extra fields back into the event_name field
            if len(row) > 6:
                # Reconstruct the row: time_mt5, currency, event_name (may contain commas), impact, actual, forecast
                new_row = [row[0], row[1]]  # time_mt5, currency
                # Event name is composed of fields from index 2 up to the last 3 fields (impact, actual, forecast)
                event_name = ','.join(row[2:len(row)-3])
                new_row.append(event_name)
                # Add the last 3 fields (impact, actual, forecast)
                new_row.extend(row[len(row)-3:])
                processed_rows.append(new_row)
            else:
                processed_rows.append(row)

    # Convert processed rows back to CSV format for pandas
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerows(processed_rows)
    df = pd.read_csv(io.StringIO(output.getvalue()))
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