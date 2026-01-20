import duckdb
import os
import pandas as pd
from datetime import datetime

class MarketPulse:
    def __init__(self):
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
        -- CALC DOLLAR INDEX (DXY) SYNTHETICALLY
        dxy_calc AS (
            SELECT 
                'DXY' as symbol,
                50.14348112 * 
                POWER((SELECT last_price FROM latest_prices WHERE symbol = 'EURUSD.sd'), -0.576) *
                POWER((SELECT last_price FROM latest_prices WHERE symbol = 'USDJPY.sd'), 0.136) *
                POWER((SELECT last_price FROM latest_prices WHERE symbol = 'GBPUSD.sd'), -0.119) *
                POWER((SELECT last_price FROM latest_prices WHERE symbol = 'USDCAD.sd'), 0.091) *
                POWER((SELECT last_price FROM latest_prices WHERE symbol = 'USDSEK.sd'), 0.042) *
                POWER((SELECT last_price FROM latest_prices WHERE symbol = 'USDCHF.sd'), 0.036) as last_price,
                (SELECT last_time FROM latest_prices WHERE symbol = 'EURUSD.sd') as last_time
        ),
        combined_prices AS (
            SELECT * FROM latest_prices UNION ALL SELECT * FROM dxy_calc
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
                WHEN lp.symbol = 'DXY' THEN 'US Dollar Index'
                WHEN lp.symbol = 'US02Y.px' THEN '2Y Treasury'
                WHEN lp.symbol = 'US07Y.px' THEN '7Y Treasury'
                WHEN lp.symbol = 'US10Y.px' THEN '10Y Treasury'
                WHEN lp.symbol = 'US30Y.px' THEN '30Y Treasury'
                WHEN lp.symbol = 'TECH.sec' THEN 'Technology'
                WHEN lp.symbol = 'FINANCE.sec' THEN 'Financials'
                WHEN lp.symbol = 'ENERGY.sec' THEN 'Energy'
                WHEN lp.symbol = 'HEALTH.sec' THEN 'Health Care'
                WHEN lp.symbol = 'CONSUMER.sec' THEN 'Cons Discret'
                WHEN lp.symbol = 'STAPLES.sec' THEN 'Cons Staples'
                WHEN lp.symbol = 'INDUST.sec' THEN 'Industrials'
                WHEN lp.symbol = 'REALEST.sec' THEN 'Real Estate'
                WHEN lp.symbol = 'MATERIALS.sec' THEN 'Materials'
                WHEN lp.symbol = 'COMM.sec' THEN 'Comm Services'
                WHEN lp.symbol = 'UTILITIES.sec' THEN 'Utilities'
                WHEN lp.symbol = 'XAUUSD.sd' THEN 'Gold Spot'
                WHEN lp.symbol = 'XAGUSD.sd' THEN 'Silver Spot'
                WHEN lp.symbol = 'XPTUSD.sd' THEN 'Platinum Spot'
                WHEN lp.symbol = 'BTCUSD.lv' THEN 'Bitcoin'
                WHEN lp.symbol = 'ETHUSD.lv' THEN 'Ethereum'
                ELSE REPLACE(REPLACE(REPLACE(REPLACE(lp.symbol, '.sd', ''), '.lv', ''), '.px', ''), 'Roll', '')
            END as friendly_name,
            
            CASE 
                WHEN lp.symbol = 'DXY' THEN 'INDEX'
                WHEN lp.symbol IN ('XAUUSD.sd', 'XAGUSD.sd', 'XPTUSD.sd') THEN 'METALS'
                WHEN lp.symbol LIKE '%.px' THEN 'BONDS'
                WHEN lp.symbol LIKE '%.sec' THEN 'SECTORS'
                WHEN lp.symbol LIKE '%.lv' THEN 'CRYPTO' 
                WHEN lp.symbol LIKE '%OILRoll' THEN 'ENERGY'
                WHEN lp.symbol LIKE '%Roll' THEN 'INDEX'
                WHEN lp.symbol LIKE '%.sd' THEN 'FX'
                ELSE COALESCE(sm.asset_class, 'STOCK') 
            END as asset_class,
            
            -- RECALIBRATED YIELD CONVERSION (Anchor: 10Y @ 4.15%)
            CASE 
                WHEN lp.symbol = 'US02Y.px' THEN ROUND(4.150 + (82.80 - lp.last_price) * 0.25, 3)
                WHEN lp.symbol = 'US10Y.px' THEN ROUND(4.150 + (95.94 - lp.last_price) * 0.12, 3)
                WHEN lp.symbol = 'US30Y.px' THEN ROUND(4.450 + (87.80 - lp.last_price) * 0.08, 3)
                WHEN lp.symbol = 'US07Y.px' THEN ROUND(4.100 + (119.07 - lp.last_price) * 0.10, 3)
                ELSE lp.last_price 
            END as display_price,
            
            lp.last_price as raw_close,
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
        FROM combined_prices lp
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