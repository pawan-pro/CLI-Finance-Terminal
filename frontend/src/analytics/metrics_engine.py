import duckdb
import os
import pandas as pd
from datetime import datetime

class MarketPulse:
    def __init__(self):
        self.db_path = "/Users/pawan/CLI-Finance-Terminal/approach-3.0/Hackathon/data/silver/market_data.duckdb"
        self.meta_path = "/Users/pawan/CLI-Finance-Terminal/approach-3.0/Hackathon/data/metadata/SymbolMetadata_0_GMT.csv"

    def get_sparkline_data(self, symbol, timeframe_range="1D"):
        try:
            conn = duckdb.connect(self.db_path)

            # Map ticker back to MT5 name for database lookup
            mapping = {"AAPL": "Apple", "TSLA": "Tesla", "NVDA": "NVIDIA", "MSFT": "Microsoft",
                       "AMZN": "Amazon", "GOOGL": "Alphabet", "META": "Facebook", "C": "Citigroup"}
            lookup = mapping.get(symbol, symbol)

            # Determine the query based on the range parameter
            if timeframe_range == "1W" or timeframe_range == "TREND":
                # For TREND view: Fetch last 30 days of data using h1_bars or m15_bars with STEP 4
                df = conn.execute(f"""
                    SELECT time_utc, close
                    FROM m15_bars
                    WHERE symbol = '{lookup}'
                    AND time_utc >= (SELECT MAX(time_utc) - INTERVAL 30 DAYS FROM m15_bars WHERE symbol = '{lookup}')
                    ORDER BY time_utc ASC
                """).df()

                # Apply STEP 4 to simulate 1-hour or 4-hour candles (performance optimization)
                if not df.empty:
                    # Take every 4th row to simulate 1-hour candles from 15-min data
                    df = df.iloc[::4]
            else:  # Default to "1D" or "SESSION"
                # For SESSION view: Fetch last 14 days of data from m15_bars (~1,300 bars)
                df = conn.execute(f"""
                    SELECT time_utc, close
                    FROM m15_bars
                    WHERE symbol = '{lookup}'
                    AND time_utc >= (SELECT MAX(time_utc) - INTERVAL 14 DAYS FROM m15_bars WHERE symbol = '{lookup}')
                    ORDER BY time_utc ASC
                """).df()

            conn.close()

            # Apply time_ist conversion to the entire historical array
            if not df.empty:
                # Convert time_utc to IST by adding 5 hours and 30 minutes
                df['time_ist'] = df['time_utc'] + pd.Timedelta(hours=5, minutes=30)
                # Return both time and close data for proper charting
                result = []
                for _, row in df.iterrows():
                    result.append({
                        'time_ist': row['time_ist'],
                        'close': row['close']
                    })
                return result
            else:
                return []
        except Exception as e:
            print(f"Error in get_sparkline_data: {e}")
            return []

    def get_snapshot(self, limit=200):
        if not os.path.exists(self.db_path): return pd.DataFrame()
        conn = duckdb.connect(self.db_path)
        
        query = f"""
        WITH market_context AS (SELECT MAX(time_utc) as global_max_time FROM m15_bars),
        latest_prices AS (
            SELECT symbol as raw_symbol, close as last_price, time_utc as last_time
            FROM m15_bars
            QUALIFY ROW_NUMBER() OVER(PARTITION BY symbol ORDER BY time_utc DESC) = 1
        ),
        baseline_prices AS (
            SELECT symbol, close as price_24h_ago
            FROM m15_bars, market_context
            WHERE time_utc <= market_context.global_max_time - INTERVAL 24 HOURS
            QUALIFY ROW_NUMBER() OVER(PARTITION BY symbol ORDER BY time_utc DESC) = 1
        )
        SELECT 
            CASE 
                WHEN lp.raw_symbol = 'Apple' THEN 'AAPL'
                WHEN lp.raw_symbol = 'Tesla' THEN 'TSLA'
                WHEN lp.raw_symbol = 'NVIDIA' THEN 'NVDA'
                WHEN lp.raw_symbol = 'Microsoft' THEN 'MSFT'
                WHEN lp.raw_symbol = 'Amazon' THEN 'AMZN'
                WHEN lp.raw_symbol = 'Alphabet' THEN 'GOOGL'
                WHEN lp.raw_symbol = 'Facebook' THEN 'META'
                WHEN lp.raw_symbol = 'Citigroup' THEN 'C'
                ELSE lp.raw_symbol
            END as symbol,
            lp.raw_symbol as name,
            CASE 
                WHEN lp.raw_symbol IN ('XAUUSD.sd', 'XAGUSD.sd', 'XPTUSD.sd') THEN 'METALS'
                WHEN lp.raw_symbol LIKE '%.px' THEN 'BONDS'
                WHEN lp.raw_symbol LIKE '%.sec' THEN 'SECTORS'
                WHEN lp.raw_symbol LIKE '%.lv' THEN 'CRYPTO' 
                WHEN lp.raw_symbol LIKE '%Roll' THEN 'INDEX'
                ELSE 'STOCK' 
            END as asset_class,
            CASE 
                WHEN lp.raw_symbol = 'US02Y.px' THEN ROUND(3.590 + (82.80 - lp.last_price) * 0.15, 3)
                WHEN lp.raw_symbol = 'US10Y.px' THEN ROUND(4.360 + (95.94 - lp.last_price) * 0.10, 3)
                WHEN lp.raw_symbol = 'US30Y.px' THEN ROUND(4.990 + (87.80 - lp.last_price) * 0.05, 3)
                ELSE lp.last_price 
            END as price,
            ROUND(((lp.last_price - bp.price_24h_ago) / bp.price_24h_ago) * 100, 2) as change_24h,
            (lp.last_time + INTERVAL 5 HOURS + INTERVAL 30 MINUTES) as last_sync,
            CASE WHEN (EXTRACT(EPOCH FROM (SELECT global_max_time FROM market_context)) - EXTRACT(EPOCH FROM lp.last_time)) > 3600 THEN 'Inactive' ELSE 'LIVE' END as status
        FROM latest_prices lp
        LEFT JOIN baseline_prices bp ON lp.raw_symbol = bp.symbol
        ORDER BY ABS(change_24h) DESC LIMIT {limit}
        """
        try:
            return conn.execute(query).df()
        except:
            return pd.DataFrame()
        finally:
            conn.close()