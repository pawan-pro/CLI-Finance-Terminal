import duckdb
import os
import pandas as pd

class MarketPulse:
    def __init__(self):
        # Absolute path to ensure consistency
        self.db_path = "/Users/pawan/CLI-Finance-Terminal/approach 3.0/Hackathon/data/silver/market_data.duckdb"

    def _estimate_yield(self, symbol, price):
        """
        Calibrated Yield Model using Modified Duration
        Formula: Δyield (bps) = -(ΔPrice% / Duration) × 100
        """
        # ANCHOR POINTS: Web Yield (base_y) mapped to Terminal ETF Price (ref_p)
        calibration = {
            "US02Y.px": {"base_y": 3.597, "ref_p": 82.82, "dur": 1.8},
            "US07Y.px": {"base_y": 4.073, "ref_p": 119.28, "dur": 4.6},
            "US10Y.px": {"base_y": 4.295, "ref_p": 96.30, "dur": 7.4},
            "US30Y.px": {"base_y": 4.920, "ref_p": 88.33, "dur": 16.5}
        }
        
        if symbol not in calibration:
            return price
            
        c = calibration[symbol]
        
        # Calculate percentage price change from anchor
        price_change_pct = ((price - c['ref_p']) / c['ref_p']) * 100
        
        # Convert to yield change in percentage points
        # Duration approximation: ΔY ≈ -(ΔP% / Duration)
        yield_change = -(price_change_pct / c['dur'])
        
        return c['base_y'] + yield_change

    def get_snapshot(self, limit=200):
        if not os.path.exists(self.db_path): return pd.DataFrame()
        conn = duckdb.connect(self.db_path)
        
        query = """
        WITH latest AS (
            SELECT *, 
            CASE 
                WHEN symbol LIKE '%.px' THEN 'BONDS'
                WHEN symbol IN ('XAUUSD.sd', 'XAGUSD.sd', 'XPTUSD.sd') THEN 'METALS'
                WHEN symbol LIKE '%.lv' THEN 'CRYPTO' 
                WHEN symbol LIKE '%Roll' THEN 'INDEX'
                WHEN symbol LIKE '%.sec' THEN 'SECTORS'
                WHEN symbol LIKE '%.sd' THEN 'FX'
                ELSE 'STOCK' 
            END as asset_class
            FROM m15_bars QUALIFY ROW_NUMBER() OVER(PARTITION BY symbol ORDER BY time_utc DESC) = 1
        ),
        baseline AS (
            SELECT symbol, close as price_24h_ago
            FROM m15_bars QUALIFY ROW_NUMBER() OVER(PARTITION BY symbol ORDER BY time_utc DESC) = 96
        )
        SELECT 
            l.symbol, l.close as last_price, l.asset_class, l.time_utc as sync_ist,
            ROUND(((l.close - COALESCE(b.price_24h_ago, l.close)) / NULLIF(COALESCE(b.price_24h_ago, l.close), 0)) * 100, 2) as return_24h,
            ABS(ROUND(((l.close - COALESCE(b.price_24h_ago, l.close)) / NULLIF(COALESCE(b.price_24h_ago, l.close), 0)) * 100, 2)) as return_magnitude
        FROM latest l
        LEFT JOIN baseline b ON l.symbol = b.symbol
        ORDER BY asset_class ASC, return_magnitude DESC
        """
        df = conn.execute(query).df()
        
        # Mapping Display Data
        df['display_price'] = df.apply(lambda x: self._estimate_yield(x['symbol'], x['last_price']), axis=1)
        
        names = {
            "US10Y.px": "10Y Treasury", "US02Y.px": "2Y Treasury", "US30Y.px": "30Y Treasury",
            "US07Y.px": "7Y Treasury", "XAUUSD.sd": "Gold Spot", "BTCUSD.lv": "Bitcoin",
            "ETHUSD.lv": "Ethereum", "VIXRoll": "VIX", "US500Roll": "S&P 500",
            "XPTUSD.sd": "Platinum Spot", "XAGUSD.sd": "Silver Spot",
            "TECH.sec": "Technology", "FINANCE.sec": "Financials", "ENERGY.sec": "Energy"
        }
        df['friendly_name'] = df['symbol'].map(names).fillna(df['symbol'])
        
        max_t = df['sync_ist'].max()
        df['status'] = df['sync_ist'].apply(lambda x: 'LIVE' if (max_t - x).total_seconds() < 7200 else 'Inactive')
        
        conn.close()
        return df

    def get_sparkline_data(self, symbol, limit=10):
        conn = duckdb.connect(self.db_path)
        df = conn.execute(f"SELECT close FROM m15_bars WHERE symbol = '{symbol}' ORDER BY time_utc DESC LIMIT {limit}").df()
        conn.close()
        return df['close'].tolist()[::-1] if not df.empty else []