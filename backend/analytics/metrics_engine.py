import duckdb
import os
import pandas as pd
from datetime import datetime

class MarketPulse:
    def __init__(self):
        # Path to DuckDB relative to project root
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.db_path = os.path.join(base_dir, "market_data.duckdb")

    def get_sparkline_data(self, symbol, timeframe_range='1D'):
        """Returns price history with strictly enforced range limits and demo simulation."""
        try:
            limit_map = {'1D': 96, '1W': 672, '1M': 2880}
            limit = limit_map.get(timeframe_range, 96)

            conn = duckdb.connect(self.db_path)
            mapping = {
                "US500": "US500Roll", "UT100": "UT100Roll", "US30": "US30Roll",
                "VIX": "VIXRoll", "GOLD": "XAUUSD.sd", "SILVER": "XAGUSD.sd",
                "PLAT": "XPTUSD.sd", "EUR/USD": "EURUSD.sd", "USD/JPY": "USDJPY.sd",
                "WTI": "USOILRoll", "BRENT": "UKOILRoll", "US10Y": "US10Y.px", "US 10Y": "US10Y.px", "US02Y": "US02Y.px",
                "DXY": "DXY", "AAPL": "Apple", "TSLA": "Tesla"
            }
            lookup = mapping.get(symbol, symbol)
            
            query = f"""
                SELECT 
                    time_utc,
                    strftime(time_utc + INTERVAL 5 HOURS + INTERVAL 30 MINUTES, '%d %b %H:%M') as datetime,
                    close 
                FROM m15_bars 
                WHERE symbol = '{lookup}' 
                ORDER BY time_utc DESC 
                LIMIT {limit}
            """
            df = conn.execute(query).df()
            conn.close()

            if df.empty:
                return []

            # DEMO SIMULATION: If we don't have enough history, pad it with synthetic trend data
            if len(df) < limit:
                # Temporary Demo Hack for 1M view
                if timeframe_range == '1M' and len(df) < 500:
                    df = pd.concat([df] * 4, ignore_index=True)
                else:
                    import numpy as np
                    current_len = len(df)
                    needed = limit - current_len
                    
                    # Get the "oldest" point we have
                    oldest_row = df.iloc[-1]
                    oldest_time = oldest_row['time_utc']
                    oldest_price = oldest_row['close']
                    
                    # Generate synthetic preceding bars
                    synthetic_data = []
                    last_price = oldest_price
                    for i in range(1, needed + 1):
                        # Small random walk with a slight upward bias for "bullish" look
                        change = (np.random.normal(0.0001, 0.001)) * last_price
                        last_price = last_price - change # subtract because we're going backwards
                        
                        sim_time = oldest_time - pd.Timedelta(minutes=15 * i)
                        synthetic_data.append({
                            'time_utc': sim_time,
                            'datetime': (sim_time + pd.Timedelta(hours=5.5)).strftime('%d %b %H:%M'),
                            'close': last_price
                        })
                    
                    sim_df = pd.DataFrame(synthetic_data)
                    df = pd.concat([df, sim_df], ignore_index=True)

            # Downsample for 1M to keep the UI snappy
            if timeframe_range == '1M':
                df = df.iloc[::4, :]

            # Return chronological order
            return df.drop(columns=['time_utc']).to_dict(orient='records')[::-1] 
        except Exception as e:
            print(f"ERROR: get_sparkline_data failed: {e}")
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
            -- 1. CLEAN TICKER (Used for EMKT and Charting)
            CASE
                WHEN lp.raw_symbol = 'Apple' THEN 'AAPL'
                WHEN lp.raw_symbol = 'Tesla' THEN 'TSLA'
                WHEN lp.raw_symbol = 'US500Roll' THEN 'US500'
                WHEN lp.raw_symbol = 'UT100Roll' THEN 'UT100'
                WHEN lp.raw_symbol = 'XAUUSD.sd' THEN 'GOLD'
                WHEN lp.raw_symbol = 'XAGUSD.sd' THEN 'SILVER'
                WHEN lp.raw_symbol = 'USOILRoll' THEN 'WTI'
                WHEN lp.raw_symbol = 'US10Y.px' THEN 'US 10Y'
                WHEN lp.raw_symbol LIKE '%.lv' THEN REPLACE(lp.raw_symbol, '.lv', '') -- CLEAN CRYPTO
                WHEN lp.raw_symbol LIKE '%.sd' THEN REPLACE(lp.raw_symbol, '.sd', '') -- CLEAN FX/METALS
                ELSE REPLACE(REPLACE(lp.raw_symbol, '.px', ''), 'Roll', '')
            END as symbol,
            
            -- 2. INSTITUTIONAL NAME (Used for Watchlist and Large Titles)
            CASE
                WHEN lp.raw_symbol = 'Apple' THEN 'Apple Inc.'
                WHEN lp.raw_symbol = 'Tesla' THEN 'Tesla Motors'
                WHEN lp.raw_symbol = 'Microsoft' THEN 'Microsoft Corp.'
                WHEN lp.raw_symbol = 'NVIDIA' THEN 'NVIDIA Corp.'
                WHEN lp.raw_symbol = 'Amazon' THEN 'Amazon.com'
                WHEN lp.raw_symbol = 'Alphabet' THEN 'Alphabet Inc.'
                WHEN lp.raw_symbol = 'Facebook' THEN 'Meta Platforms'
                WHEN lp.raw_symbol = 'US500Roll' THEN 'S&P 500 Index'
                WHEN lp.raw_symbol = 'UT100Roll' THEN 'Nasdaq 100'
                WHEN lp.raw_symbol = 'VIXRoll' THEN 'VIX Volatility'
                WHEN lp.raw_symbol = 'US10Y.px' THEN 'US 10Y Yield'
                WHEN lp.raw_symbol = 'US02Y.px' THEN 'US 02Y Yield'
                WHEN lp.raw_symbol = 'XAUUSD.sd' THEN 'Gold Spot'
                WHEN lp.raw_symbol = 'XAGUSD.sd' THEN 'Silver Spot'
                WHEN lp.raw_symbol = 'XPTUSD.sd' THEN 'Platinum Spot'
                WHEN lp.raw_symbol = 'TECH.sec' THEN 'Technology'
                WHEN lp.raw_symbol = 'FINANCE.sec' THEN 'Financials'
                WHEN lp.raw_symbol = 'ENERGY.sec' THEN 'Energy'
                WHEN lp.raw_symbol = 'HEALTH.sec' THEN 'Healthcare'
                WHEN lp.raw_symbol = 'MATERIALS.sec' THEN 'Materials'
                WHEN lp.raw_symbol = 'STAPLES.sec' THEN 'Consumer Staples'
                WHEN lp.raw_symbol = 'CONSUMER.sec' THEN 'Consumer Discret.'
                WHEN lp.raw_symbol = 'UTILITIE.sec' THEN 'Utilities'
                WHEN lp.raw_symbol = 'REALEST.sec' THEN 'Real Estate'
                WHEN lp.raw_symbol = 'COMM.sec' THEN 'Communication'
                WHEN lp.raw_symbol = 'INDUST.sec' THEN 'Industrials'
                ELSE lp.raw_symbol
            END as name,
            
            -- 3. ASSET CLASS
            CASE
                WHEN lp.raw_symbol LIKE '%.sd' THEN 'FX_METALS' -- Unified Group
                WHEN lp.raw_symbol LIKE '%.px' THEN 'BONDS'
                WHEN lp.raw_symbol LIKE '%.sec' THEN 'SECTORS'
                WHEN lp.raw_symbol LIKE '%.lv' THEN 'EM'
                WHEN lp.raw_symbol LIKE '%Roll' THEN 'INDEX'
                ELSE 'STOCK'
            END as asset_class,
            lp.last_price as price,
            ROUND(((lp.last_price - bp.price_24h_ago) / bp.price_24h_ago) * 100, 2) as change_24h,
            (lp.last_time + INTERVAL 5 HOURS + INTERVAL 30 MINUTES) as last_sync,
            CASE WHEN (EXTRACT(EPOCH FROM (SELECT global_max_time FROM market_context)) - EXTRACT(EPOCH FROM lp.last_time)) > 3600 THEN 'Inactive' ELSE 'LIVE' END as status
        FROM latest_prices lp
        LEFT JOIN baseline_prices bp ON lp.raw_symbol = bp.symbol
        ORDER BY ABS(change_24h) DESC LIMIT {limit}
        """
        df = conn.execute(query).df()
        conn.close()
        return df