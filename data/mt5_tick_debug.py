import MetaTrader5 as mt5
from datetime import datetime
import time

symbols = [
    'EURUSD.sd', 'GBPUSD.sd', 'AUDUSD.sd', 'USDJPY.sd', 'USDCHF.sd', 'USDCAD.sd', 'NZDUSD.sd', 'USDCNH.sd',
    'US500Roll', 'US30Roll', 'UK100Roll', 'DE40Roll', 'FRA40Roll', 'JP225Roll', 'HK50Roll', 'CHINA50Roll',
    'XAUUSD', 'XAGUSD', 'XPTUSD', 'USOILRoll', 'BRENT', 'NGAS',
    'BTCUSD.lv', 'ETHUSD.lv', 'LTCUSD.lv', 'VIXRoll'
]

print(f"[SYSTEM TIME] {datetime.now()}")
if not mt5.initialize():
    print(f"[MT5 INIT ERROR] {mt5.last_error()}")
    exit(1)
print(f"[MT5 TERMINAL INFO] {mt5.terminal_info()}")

for symbol in symbols:
    tick = mt5.symbol_info_tick(symbol)
    if tick:
        tick_time = datetime.fromtimestamp(tick.time)
        print(f"{symbol}: last tick at {tick_time} (bid={tick.bid}, ask={tick.ask})")
    else:
        print(f"{symbol}: No tick data available")
    time.sleep(0.2)

mt5.shutdown()
print("[DONE]")
