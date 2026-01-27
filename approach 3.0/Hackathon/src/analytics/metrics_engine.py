import duckdb
import os
import pandas as pd
from datetime import datetime

class MarketPulse:
    def __init__(self):
        # Master Absolute Paths
        self.db_path = "/Users/pawan/CLI-Finance-Terminal/approach 3.0/Hackathon/data/silver/market_data.duckdb"
        self.meta_path = "/Users/pawan/CLI-Finance-Terminal/approach 3.0/Hackathon/data/metadata/SymbolMetadata_0_GMT.csv"

    def _ensure_metadata_loaded(self, conn):
        if not os.path.exists(self.meta_path): return
        conn.execute(f"CREATE TABLE IF NOT EXISTS symbol_metadata AS SELECT * FROM read_csv_auto('{self.meta_path}')")

    def get_sparkline_data(self, symbol):
        """Returns raw price history for the web UI charts, mapping tickers back to MT5 names."""
        try:
            conn = duckdb.connect(self.db_path)
            # REVERSE MAPPING: UI asks for 'AAPL', we look for 'Apple'
            mapping = {
                "AAPL": "Apple", "TSLA": "Tesla", "NVDA": "NVIDIA", 
                "MSFT": "Microsoft", "AMZN": "Amazon", "GOOGL": "Alphabet", 
                "META": "Facebook", "C": "Citigroup", "US02Y": "US02Y.px",
                "US10Y": "US10Y.px", "US30Y": "US30Y.px"
            }
            lookup = mapping.get(symbol, symbol)
            
            df = conn.execute(f"""
                SELECT close 
                FROM m15_bars 
                WHERE symbol = '{lookup}' 
                ORDER BY time_utc DESC 
                LIMIT 20
            """).df()
            conn.close()
            return df['close'].values[::-1].tolist() if not df.empty else []
        except Exception as e:
            print(f"Sparkline Data Error: {e}")
            return []

    def get_snapshot(self, limit=200):
        """Fetches the latest market state with tickers forced as primary IDs."""
        if not os.path.exists(self.db_path): return pd.DataFrame()
        conn = duckdb.connect(self.db_path)
        self._ensure_metadata_loaded(conn)
        
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
        ),
        fallback_prices AS (
            SELECT symbol, close as first_price
            FROM m15_bars
            QUALIFY ROW_NUMBER() OVER(PARTITION BY symbol ORDER BY time_utc ASC) = 1
        )
        SELECT
            -- 1. TICKER COLUMN (The primary key for the React UI Watchlist)
            CASE
                WHEN lp.raw_symbol = 'Apple' THEN 'AAPL'
                WHEN lp.raw_symbol = 'Tesla' THEN 'TSLA'
                WHEN lp.raw_symbol = 'NVIDIA' THEN 'NVDA'
                WHEN lp.raw_symbol = 'Microsoft' THEN 'MSFT'
                WHEN lp.raw_symbol = 'Amazon' THEN 'AMZN'
                WHEN lp.raw_symbol = 'Alphabet' THEN 'GOOGL'
                WHEN lp.raw_symbol = 'Facebook' THEN 'META'
                WHEN lp.raw_symbol = 'Citigroup' THEN 'C'
                WHEN lp.raw_symbol = 'US02Y.px' THEN 'US02Y'
                WHEN lp.raw_symbol = 'US07Y.px' THEN 'US07Y'
                WHEN lp.raw_symbol = 'US10Y.px' THEN 'US10Y'
                WHEN lp.raw_symbol = 'US30Y.px' THEN 'US30Y'
                ELSE REPLACE(REPLACE(REPLACE(lp.raw_symbol, '.sd', ''), '.lv', ''), 'Roll', '')
            END as symbol,
            
            -- 2. DESCRIPTIVE NAME
            lp.raw_symbol as name,

            -- 3. ASSET CLASSIFICATION
            CASE
                WHEN lp.raw_symbol IN ('XAUUSD.sd', 'XAGUSD.sd', 'XPTUSD.sd') THEN 'METALS'
                WHEN lp.raw_symbol LIKE '%.px' THEN 'BONDS'
                WHEN lp.raw_symbol LIKE '%.sec' THEN 'SECTORS'
                WHEN lp.raw_symbol LIKE '%.lv' THEN 'CRYPTO'
                WHEN lp.raw_symbol LIKE '%Roll' THEN 'INDEX'
                WHEN lp.raw_symbol LIKE '%.sd' THEN 'FX'
                ELSE 'STOCK'
            END as asset_class,

            -- 4. PRICE / YIELD DISPLAY
            -- For bonds (.px), the 'close' field now stores the ACTUAL YIELD (already converted in fetch script)
            -- So we just display it directly without any calculation
            ROUND(lp.last_price, 
                CASE 
                    WHEN lp.raw_symbol LIKE '%.px' THEN 3  -- 3 decimals for bond yields
                    ELSE 2  -- 2 decimals for everything else
                END
            ) as price,

            -- 5. PERFORMANCE
            ROUND(((lp.last_price - COALESCE(bp.price_24h_ago, fp.first_price)) / 
                   COALESCE(bp.price_24h_ago, fp.first_price)) * 100, 2) as change_24h,

            -- 6. STATUS & METADATA
            (lp.last_time + INTERVAL 5 HOURS + INTERVAL 30 MINUTES) as last_sync,
            CASE 
                WHEN (EXTRACT(EPOCH FROM (SELECT global_max_time FROM market_context)) - 
                      EXTRACT(EPOCH FROM lp.last_time)) > 3600 
                THEN 'Inactive' ELSE 'LIVE' 
            END as status

        FROM latest_prices lp
        LEFT JOIN baseline_prices bp ON lp.raw_symbol = bp.symbol
        LEFT JOIN fallback_prices fp ON lp.raw_symbol = fp.symbol
        ORDER BY ABS(change_24h) DESC
        LIMIT {limit}
        """
        try:
            return conn.execute(query).df()
        except Exception as e:
            print(f"Metrics Engine Critical Error: {e}")
            return pd.DataFrame()
        finally:
            conn.close()