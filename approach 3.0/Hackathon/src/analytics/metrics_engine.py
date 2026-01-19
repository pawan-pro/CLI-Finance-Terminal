import duckdb
import os
import pandas as pd
from datetime import datetime

class MarketPulse:
    def __init__(self):
        # EXACT ABSOLUTE PATHS
        self.db_path = "/Users/pawan/CLI-Finance-Terminal/approach 3.0/Hackathon/data/silver/market_data.duckdb"
        self.meta_path = "/Users/pawan/CLI-Finance-Terminal/approach 3.0/Hackathon/data/metadata/SymbolMetadata_0_GMT.csv"

    def _ensure_metadata_loaded(self, conn):
        if not os.path.exists(self.meta_path): return
        conn.execute(f"CREATE TABLE IF NOT EXISTS symbol_metadata AS SELECT * FROM read_csv_auto('{self.meta_path}')")

    def get_snapshot(self, limit=200):
        if not os.path.exists(self.db_path): return pd.DataFrame()
        conn = duckdb.connect(self.db_path)
        self._ensure_metadata_loaded(conn)
        
        query = f"""
        WITH market_context AS (
            SELECT MAX(time_utc) as global_max_time FROM m15_bars
        ),
        latest_prices AS (
            SELECT symbol, close as last_price, time_utc as last_time
            FROM m15_bars
            QUALIFY ROW_NUMBER() OVER(PARTITION BY symbol ORDER BY time_utc DESC) = 1
        ),
        baseline_prices AS (
            SELECT symbol, close as price_24h_ago, time_utc as baseline_time
            FROM m15_bars, market_context
            WHERE time_utc <= market_context.global_max_time - INTERVAL 24 HOURS
            QUALIFY ROW_NUMBER() OVER(PARTITION BY symbol ORDER BY time_utc DESC) = 1
        ),
        fallback_prices AS (
            SELECT symbol, close as first_price, time_utc as first_time
            FROM m15_bars
            QUALIFY ROW_NUMBER() OVER(PARTITION BY symbol ORDER BY time_utc ASC) = 1
        )
        SELECT 
            lp.symbol, 
            CASE 
                WHEN lp.symbol IN ('XAUUSD.sd', 'XAGUSD.sd', 'XPTUSD.sd') THEN 'METALS'
                WHEN lp.symbol LIKE '%.px' THEN 'BONDS'
                WHEN lp.symbol LIKE '%.lv' THEN 'CRYPTO' 
                WHEN lp.symbol LIKE '%OILRoll' THEN 'ENERGY'
                WHEN lp.symbol LIKE '%Roll' THEN 'INDEX'
                WHEN lp.symbol LIKE '%.sd' THEN 'FX'
                ELSE COALESCE(sm.asset_class, 'STOCK') 
            END as asset_class,
            lp.last_price, 
            ROUND(((lp.last_price - COALESCE(bp.price_24h_ago, fp.first_price)) / 
                   COALESCE(bp.price_24h_ago, fp.first_price)) * 100, 2) as return_24h,
            ABS(ROUND(((lp.last_price - COALESCE(bp.price_24h_ago, fp.first_price)) / 
                   COALESCE(bp.price_24h_ago, fp.first_price)) * 100, 2)) as return_magnitude,
            (lp.last_time + INTERVAL 5 HOURS + INTERVAL 30 MINUTES) as sync_ist,
            CASE 
                WHEN (EXTRACT(EPOCH FROM (SELECT global_max_time FROM market_context)) - 
                      EXTRACT(EPOCH FROM lp.last_time)) > 3600 
                THEN 'Inactive' 
                ELSE 'LIVE' 
            END as status
        FROM latest_prices lp
        LEFT JOIN symbol_metadata sm ON lp.symbol = sm.symbol
        LEFT JOIN baseline_prices bp ON lp.symbol = bp.symbol
        LEFT JOIN fallback_prices fp ON lp.symbol = fp.symbol
        ORDER BY return_magnitude DESC
        LIMIT {limit}
        """
        try:
            df = conn.execute(query).df()
        except Exception as e:
            print(f"Metrics Error: {e}")
            df = pd.DataFrame()
        finally:
            conn.close()
        return df