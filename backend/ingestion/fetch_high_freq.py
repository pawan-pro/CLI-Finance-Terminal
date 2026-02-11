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
    
    DB_PATH = "/Users/pawan/CLI-Finance-Terminal/approach-3.0/Hackathon/data/silver/market_data.duckdb"
    
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
    
    # CALIBRATION PARAMETERS: Based on current market data (Jan 27, 2026)
    # Using real-time web data: US2Y=3.593%, US7Y=4.021%, US10Y=4.221%, US30Y=4.813%
    bond_calibration = {
        "US02Y.px": {
            "reference_price": 82.80,  # Current SHY price
            "reference_yield": 3.593,  # Current 2Y yield from web
            "duration": 1.9,           # Approximate modified duration
            "conversion_factor": -0.19  # Sensitivity factor
        },
        "US07Y.px": {
            "reference_price": 119.17,  # Current IEI price from your data
            "reference_yield": 4.021,   # Current 7Y yield from web
            "duration": 6.5,            # Approximate modified duration
            "conversion_factor": -0.065
        },
        "US10Y.px": {
            "reference_price": 95.94,   # Current IEF price
            "reference_yield": 4.221,   # Current 10Y yield from web
            "duration": 8.5,            # Approximate modified duration
            "conversion_factor": -0.085
        },
        "US30Y.px": {
            "reference_price": 87.80,   # Current TLT price
            "reference_yield": 4.813,   # Current 30Y yield from web
            "duration": 18.0,           # Approximate modified duration
            "conversion_factor": -0.055
        }
    }
    
    def convert_etf_price_to_yield(etf_price, bond_label):
        """
        Convert ETF price to Treasury yield using calibrated parameters.
        Formula: Yield = Reference_Yield + (Reference_Price - Current_Price) * Conversion_Factor
        """
        if bond_label not in bond_calibration:
            return etf_price  # Return as-is for non-bond symbols
        
        cal = bond_calibration[bond_label]
        price_change = cal["reference_price"] - etf_price
        yield_value = cal["reference_yield"] + (price_change * cal["conversion_factor"])
        
        return round(yield_value, 3)
    
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
            
            # Convert ETF prices to yields for bond symbols
            is_bond = label.endswith('.px')
            
            if is_bond:
                # Store YIELDS for bonds (not ETF prices)
                df['close'] = df['close'].astype(float).apply(lambda x: convert_etf_price_to_yield(x, label))
                df['open'] = df['open'].astype(float).apply(lambda x: convert_etf_price_to_yield(x, label))
                df['high'] = df['high'].astype(float).apply(lambda x: convert_etf_price_to_yield(x, label))
                df['low'] = df['low'].astype(float).apply(lambda x: convert_etf_price_to_yield(x, label))
            else:
                # Keep regular prices for sectors
                df['close'] = df['close'].astype(float)
                df['open'] = df['open'].astype(float)
                df['high'] = df['high'].astype(float)
                df['low'] = df['low'].astype(float)
            
            formatted_df = pd.DataFrame({
                'symbol': label,
                'time_utc': df['time_utc'],
                'open': df['open'],
                'high': df['high'],
                'low': df['low'],
                'close': df['close'],
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
            
            if is_bond:
                print(f"✅ {label}: Synced as YIELD (using key {i % num_keys + 1}) - Latest: {df['close'].iloc[0]:.3f}%")
            else:
                print(f"✅ {label}: Synced (using key {i % num_keys + 1})")
            
            # SAFETY DELAY: 2 seconds between calls to stay under the 8-calls-per-minute-per-key limit
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Failed {ticker}: {e}")

    conn.close()
    print("🏁 High-Frequency Sync Complete.")

if __name__ == "__main__":
    fetch_high_freq()