import requests
import pandas as pd
import duckdb
import os
import warnings
from dotenv import load_dotenv
from datetime import datetime

warnings.filterwarnings("ignore", category=UserWarning, module='urllib3')
load_dotenv()

def fetch_bond_proxies():
    API_KEY = os.getenv("TWELVEDATA_API_KEY")
    # UNIFIED PATH
    DB_PATH = "/Users/pawan/CLI-Finance-Terminal/approach 3.0/data/silver/market_data.duckdb"
    
    if not API_KEY:
        print("❌ Error: TWELVEDATA_API_KEY missing from .env")
        return

    # Tenor mapping
    symbols = {
        "SHY": "US02Y_Proxy",
        "IEI": "US07Y_Proxy",
        "IEF": "US10Y_Proxy",
        "TLT": "US30Y_Proxy"
    }
    
    conn = duckdb.connect(DB_PATH)
    # Ensure table exists with correct schema
    conn.execute("""
        CREATE TABLE IF NOT EXISTS m15_bars (
            symbol VARCHAR, time_utc TIMESTAMP, open DOUBLE, high DOUBLE, 
            low DOUBLE, close DOUBLE, volume BIGINT, spread INTEGER, 
            ingested_at TIMESTAMP, PRIMARY KEY (symbol, time_utc)
        )
    """)
    
    print(f"⚡ Syncing 24h History (96 bars) for Bonds...")

    for ticker, label in symbols.items():
        url = "https://api.twelvedata.com/time_series"
        params = {
            "symbol": ticker, "interval": "15min", "outputsize": 96,
            "timezone": "Asia/Kolkata", "apikey": API_KEY
        }
        
        try:
            r = requests.get(url, params=params).json()
            if "values" not in r:
                print(f"⚠️ {ticker} skip: {r.get('message')}")
                continue
                
            df = pd.DataFrame(r["values"])
            df['datetime'] = pd.to_datetime(df['datetime'])
            
            formatted_df = pd.DataFrame({
                'symbol': label,
                'time_utc': df['datetime'],
                'open': df['open'].astype(float),
                'high': df['high'].astype(float),
                'low': df['low'].astype(float),
                'close': df['close'].astype(float),
                'volume': df['volume'].astype(int),
                'spread': 0,
                'ingested_at': datetime.now()
            })

            conn.register("temp_td", formatted_df)
            # UPSERT: Prevents duplicates, keeps history intact
            conn.execute("""
                INSERT INTO m15_bars 
                SELECT symbol, time_utc, open, high, low, close, volume, spread, ingested_at 
                FROM temp_td ON CONFLICT (symbol, time_utc) DO UPDATE SET close = excluded.close
            """)
            print(f"✅ {label}: 96 bars synced.")
        except Exception as e:
            print(f"❌ Failed {ticker}: {e}")

    conn.close()

if __name__ == "__main__":
    fetch_bond_proxies()