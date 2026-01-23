import duckdb
import os
import pandas as pd
from datetime import datetime

class MarketPulse:
    def __init__(self):
        self.db_path = "/Users/pawan/CLI-Finance-Terminal/approach 3.0/Hackathon/data/silver/market_data.duckdb"
        self.meta_path = "/Users/pawan/CLI-Finance-Terminal/approach 3.0/Hackathon/data/metadata/SymbolMetadata_0_GMT.csv"

    def get_sparkline_data(self, symbol):
        try:
            conn = duckdb.connect(self.db_path)
            # Map ticker back to MT5 name for database lookup
            mapping = {"AAPL": "Apple", "TSLA": "Tesla", "NVDA": "NVIDIA", "MSFT": "Microsoft", 
                       "AMZN": "Amazon", "GOOGL": "Alphabet", "META": "Facebook", "C": "Citigroup"}
            lookup = mapping.get(symbol, symbol)
            df = conn.execute(f"SELECT close FROM m15_bars WHERE symbol = '{lookup}' ORDER BY time_utc DESC LIMIT 20").df()
            conn.close()
            return df['close'].values[::-1].tolist() if not df.empty else []
        except:
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