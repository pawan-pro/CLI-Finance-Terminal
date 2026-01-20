import requests
import pandas as pd
import duckdb
import os
import warnings
import time
from dotenv import load_dotenv
from datetime import datetime

warnings.filterwarnings("ignore", category=UserWarning, module='urllib3')
load_dotenv()

def fetch_high_freq():
    # Load and Parse Multiple Keys
    keys_raw = os.getenv("API_KEYS")
    if not keys_raw:
        print("❌ Error: API_KEYS missing from .env (Format: key1,key2,key3)")
        return
    
    api_keys = [k.strip() for k in keys_raw.split(",")]
    num_keys = len(api_keys)
    
    DB_PATH = "/Users/pawan/CLI-Finance-Terminal/approach 3.0/Hackathon/data/silver/market_data.duckdb"
    
    # Combined Universe: Bonds (.px) + All 11 Sectors (.sec)
    symbols = {
        # Treasury Bonds
        "SHY": "US02Y.px", "IEI": "US07Y.px", "IEF": "US10Y.px", "TLT": "US30Y.px",
        # S&P 500 Sectors
        "XLK": "TECH.sec", "XLF": "FINANCE.sec", "XLE": "ENERGY.sec",
        "XLV": "HEALTH.sec", "XLY": "CONSUMER.sec", "XLP": "STAPLES.sec",
        "XLI": "INDUST.sec", "XLRE": "REALEST.sec", "XLB": "MATERIALS.sec",
        "XLC": "COMM.sec", "XLU": "UTILITIES.sec"
    }
    
    conn = duckdb.connect(DB_PATH)
    print(f"⚡ Syncing High-Freq Macro with {num_keys} Rotational Keys...")

    for i, (ticker, label) in enumerate(symbols.items()):
        # ROTATION LOGIC: Pick key based on index
        current_key = api_keys[i % num_keys]
        
        url = "https://api.twelvedata.com/time_series"
        params = {
            "symbol": ticker, "interval": "15min", "outputsize": 96,
            "timezone": "UTC", "apikey": current_key
        }
        
        try:
            r = requests.get(url, params=params).json()
            
            if "values" not in r:
                error_msg = r.get('message', 'Unknown Error')
                print(f"⚠️ {ticker} skip: {error_msg}")
                # If we hit a rate limit even with rotation, wait longer
                if "API credits" in error_msg:
                    print("⏳ Rate limit reached. Sleeping 10 seconds...")
                    time.sleep(10)
                continue
                
            df = pd.DataFrame(r["values"])
            df['time_utc'] = pd.to_datetime(df['datetime'])
            
            formatted_df = pd.DataFrame({
                'symbol': label,
                'time_utc': df['time_utc'],
                'open': df['open'].astype(float),
                'high': df['high'].astype(float),
                'low': df['low'].astype(float),
                'close': df['close'].astype(float),
                'volume': df['volume'].astype(int),
                'spread': 0,
                'ingested_at': datetime.now()
            })

            conn.register("temp_td", formatted_df)
            conn.execute("""
                INSERT INTO m15_bars 
                SELECT symbol, time_utc, open, high, low, close, volume, spread, ingested_at 
                FROM temp_td ON CONFLICT (symbol, time_utc) DO UPDATE SET close = excluded.close
            """)
            print(f"✅ {label}: Synced (using key {i % num_keys + 1})")
            
            # SAFETY DELAY: 2 seconds between calls to stay under the 8-calls-per-minute-per-key limit
            time.sleep(0.05)
            
        except Exception as e:
            print(f"❌ Failed {ticker}: {e}")

    conn.close()
    print("🏁 High-Frequency Sync Complete.")

if __name__ == "__main__":
    fetch_high_freq()