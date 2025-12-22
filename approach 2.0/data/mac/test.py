# mt5_export_eurusd_m15_windows.py
from datetime import datetime, timedelta, timezone
import os

import pandas as pd
import MetaTrader5 as mt5

SYMBOL = "EURUSD"
TIMEFRAME = mt5.TIMEFRAME_M15   # 15-minute bars [web:30]
HOUR_WINDOWS = [1, 2, 4, 6, 12, 24]

OUTDIR = "mt5_exports"
os.makedirs(OUTDIR, exist_ok=True)

def fetch_window(symbol: str, hours: int) -> pd.DataFrame:
    utc_to = datetime.now(timezone.utc)
    utc_from = utc_to - timedelta(hours=hours)

    rates = mt5.copy_rates_range(symbol, TIMEFRAME, utc_from, utc_to)  # [web:23]
    if rates is None:
        code, msg = mt5.last_error()
        raise RuntimeError(f"MT5 copy_rates_range failed: {code} {msg}")

    df = pd.DataFrame(rates)
    if df.empty:
        return df

    # MT5 returns 'time' as Unix seconds -> convert to UTC datetime
    df["time_utc"] = pd.to_datetime(df["time"], unit="s", utc=True)
    df["symbol"] = symbol
    df["window_hours"] = hours
    return df

def main():
    if not mt5.initialize():
        code, msg = mt5.last_error()
        raise RuntimeError(f"mt5.initialize() failed: {code} {msg}")

    try:
        # Ensure symbol is available in Market Watch
        if not mt5.symbol_select(SYMBOL, True):
            code, msg = mt5.last_error()
            raise RuntimeError(f"symbol_select failed for {SYMBOL}: {code} {msg}")

        frames = []
        for h in HOUR_WINDOWS:
            frames.append(fetch_window(SYMBOL, h))

        out = pd.concat(frames, ignore_index=True)

        # Keep useful columns; you can add more if needed
        keep = ["symbol", "window_hours", "time_utc", "open", "high", "low", "close", "tick_volume", "spread", "real_volume"]
        out = out[keep].sort_values(["window_hours", "time_utc"])

        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        outfile = os.path.join(OUTDIR, f"{SYMBOL}_M15_windows_{ts}UTC.csv")
        out.to_csv(outfile, index=False)
        print(f"Wrote {len(out):,} rows to {outfile}")

    finally:
        mt5.shutdown()

if __name__ == "__main__":
    main()
