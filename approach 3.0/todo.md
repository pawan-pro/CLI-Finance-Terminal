# TODO: MT5 → Market Data Lake (M1 Mac)

## 1. Scope & Universe (Day 1)

- [ ] Enumerate **key assets** with exact MT5 symbols  
  - [ ] FX majors/minors  
  - [ ] Indices  
  - [ ] Commodities  
  - [ ] Stocks & ETFs  
- [ ] Decide canonical bar spec  
  - [ ] Primary timeframe: **M15**  
  - [ ] Optional: add H1 / D1 later  
  - [ ] Treat MT5 timestamps as **UTC/GMT** and convert to IST only at reporting layer  
- [ ] Define naming conventions  
  - [ ] Export files: `<SYMBOL>_M15_windows_<YYYYMMDD_HHMM>GMT.csv`  
  - [ ] Target lake schema:  
    - `symbol, asset_class, timeframe, bar_time_utc, open, high, low, close, tick_volume, spread, source_run_ts`

## 2. MT5 Multi‑Symbol Exporter (Days 1–3)

- [ ] Implement **multi‑symbol MQL5 script**  
  - [ ] `input string SymbolsList = "EURUSD.sd,GBPUSD.sd,USDJPY.sd,..."`  
  - [ ] Use timeframe `PERIOD_M15`  
  - [ ] Use windows `{1,2,4,6,12,24}` or only `{24}` if shorter windows handled in Python  
  - [ ] For each symbol:  
    - [ ] `SymbolSelect(sym, true)`  
    - [ ] `CopyRates(sym, PERIOD_M15, t_from, t_to, rates[])`  
    - [ ] Write **one CSV per symbol per run** to `MQL5/Files`  
- [ ] Add error handling & logging  
  - [ ] Log `GetLastError()` for `SymbolSelect` and `CopyRates`  
  - [ ] Skip symbols cleanly on failure  
- [ ] Test on 3–5 symbols  
  - [ ] Run once (evening)  
  - [ ] Verify timestamps, continuity, and columns in exported CSVs  
- [ ] Extend `SymbolsList` to full **50‑symbol universe** when stable

## 3. Operational Setup on Mac (Days 3–5)

- [ ] Locate MT5 **data folder** under Wine  
  - [ ] Confirm exact path to `MQL5/Files`  
- [ ] Create host‑side folder for exports  
  - [ ] e.g. `~/MarketData/MT5_exports`  
- [ ] Create simple sync step  
  - [ ] Manual: copy from `MQL5/Files` → host folder  
  - [ ] Optional: small script (shell/Python) to automate copying  
- [ ] Define initial manual **run schedule**  
  - [ ] Morning export (e.g. 07:00 IST)  
  - [ ] Evening export (e.g. 19:00 IST)  
- [ ] For 1 week, run exporter manually at both times and observe logs

## 4. Python Ingestion Pipeline (Days 5–8)

- [ ] Create `ingest_mt5_exports.py`  
  - [ ] Configs:  
    - [ ] `EXPORT_DIR` (host exports folder)  
    - [ ] File pattern: `*_M15_windows_*.csv`  
- [ ] Implement ingestion logic  
  - [ ] Track already‑ingested files (e.g. `ingested_files.txt` or DB table)  
  - [ ] For each new CSV:  
    - [ ] Load via pandas  
    - [ ] Parse `time_gmt` → `bar_time_utc` (set tz UTC)  
    - [ ] Map `symbol` → `asset_class` (FX, index, commodity, equity, ETF)  
    - [ ] Extract `source_run_ts` from filename  
  - [ ] Append to local store:  
    - [ ] Phase 1: **parquet** files partitioned by date or symbol  
    - [ ] Phase 2 (optional): **DuckDB** or **SQLite** table for fast queries  
- [ ] Add basic data QA  
  - [ ] Check expected rows per symbol/day (≈96 bars)  
  - [ ] Detect duplicates on `(symbol, timeframe, bar_time_utc)`

## 5. First Market Overview Report (Days 8–10)

- [ ] Create `market_overview.py`  
  - [ ] Input: run timestamp or “latest”  
  - [ ] Load last 24h of M15 bars from ingested store  
  - [ ] Per symbol, compute:  
    - [ ] Last close & change vs previous close  
    - [ ] Intraday high, low, range  
    - [ ] Simple realized vol (e.g. std of returns or range‑based proxy)  
  - [ ] Aggregate metrics by **asset_class**  
- [ ] Output formats  
  - [ ] Terminal/markdown summary  
  - [ ] Optional: plots + PPTX using existing matplotlib/PPTX pipeline

## 6. Automation & Reliability (Days 10–14)

- [ ] Add logging  
  - [ ] MT5 script: per‑run log with symbols exported and bar counts  
  - [ ] Python ingestion: per‑run log with files ingested and row counts  
- [ ] Light automation / reminders  
  - [ ] macOS cron/launchd or reminder to:  
    - [ ] Run MT5 export script (morning & evening)  
    - [ ] Sync `MQL5/Files` → host folder  
    - [ ] Run `ingest_mt5_exports.py` and `market_overview.py`  
- [ ] Start **historical backfill** for priority symbols  
  - [ ] Manually adjust `t_from`/`t_to` in exporter script to pull older data in chunks  
  - [ ] Ingest into same lake with appropriate `source_run_ts`

## 7. Data Lake Hardening (Ongoing)

- [ ] After a week of stable operations:  
  - [ ] Freeze schema & filename conventions  
  - [ ] Add tests/checks:  
    - [ ] No missing bars per day per symbol  
    - [ ] No duplicate `(symbol, timeframe, bar_time_utc)` rows  
- [ ] Define “bronze/silver/gold” layers  
  - [ ] Bronze: raw MT5 CSV exports (immutable)  
  - [ ] Silver: cleaned parquet/DuckDB/SQLite tables  
  - [ ] Gold: derived features (returns, vol, factors) for research & reporting
