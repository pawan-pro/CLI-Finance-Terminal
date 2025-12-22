# Market Overview Report – Quantwater Tech

## 1. Report Objective

The **Quantwater Tech Market Overview** is a twice‑daily, systematic snapshot of global markets built on our internal MT5‑driven data lake.  
The goal is to provide a **research‑grade, model‑ready view** of key assets for:

- Intraday and swing **trading decisions** (FX, indices, commodities, equities, ETFs).  
- **Macro and event‑driven** monitoring around economic releases and central‑bank communication.  
- Continuous **factor, regime, and volatility diagnostics** feeding into strategy research.

The report is designed to be:

- **Consistent:** same methodology and coverage every run.  
- **Explainable:** all metrics traceable back to MT5 M15 bar data.  
- **Composable:** directly usable in notebooks, dashboards, and PPT research decks.

---

## 2. Data Foundations

**Source:**  
- Live and historical prices from the **MetaTrader 5 (MT5)** terminal (Equiti demo to start, production brokers later).  
- Bar frequency: **15‑minute (M15)** as canonical intraday view, with optional aggregation to H1/D1.  

**Universe (initial):**

- **FX Majors & Crosses**  
  - EURUSD.sd, GBPUSD.sd, USDJPY.sd, AUDUSD.sd, USDCAD.sd, USDCHF.sd, NZDUSD.sd  
  - Selected crosses: EURGBP.sd, EURJPY.sd, GBPJPY.sd, etc.

- **Equity Indices (CFDs)**  
  - US500, NAS100, US30, GER40, UK100, JP225, HK50, etc. (exact broker symbols)

- **Commodities**  
  - XAUUSD.sd (Gold), XAGUSD.sd (Silver), USOILRoll (WTI), UKOILRoll (Brent), others as needed.

- **Single Stocks / ETFs (CFDs)**  
  - Large‑cap US names relevant to strategy research (e.g. AAPL, MSFT, NVDA, TSLA, SPY, QQQ equivalents).

**Data Model (target lake schema):**

Each row represents a single bar:

- `symbol` – MT5 symbol.  
- `asset_class` – FX / Index / Commodity / Equity / ETF.  
- `timeframe` – M15 (canonical), with derived H1/D1.  
- `bar_time_utc` – end time of bar in UTC (MT5 server ≈ GMT).  
- `open, high, low, close` – bar prices.  
- `tick_volume` – MT5 tick volume.  
- `spread` – average/close spread on the bar (as given by MT5).  
- `source_run_ts` – timestamp of export run (morning/evening snapshot).  

Raw MT5 CSVs live as the **bronze layer**; cleaned and deduplicated tables (parquet / DuckDB / SQLite) form **silver/gold layers** for analysis.

---

## 3. Report Structure (Twice Daily)

Each run produces a **Morning Overview** and **Evening Overview**.

### 3.1 FX Dashboard

**Objective:** Track intraday FX regimes, volatility, and event responses.

Key sections:

- **FX Heatmap**  
  - Spot change over last 24h and since previous run (pips and %).  
  - Ranked movers for majors and key crosses.

- **Volatility & Range Metrics**  
  - Realized range over last 4h, 8h, 24h (high–low, normalized by spot).  
  - Rolling ATR or similar measure on M15/H1.  
  - Spread diagnostics (current spread vs typical spread by pair).

- **Event Windows (where applicable)**  
  - For scheduled events (NFP, CPI, CB meetings, etc.), attach:  
    - Pre‑event vs post‑event price change.  
    - Max/min move in units of ATR+spread (linking to existing ATR event framework).

### 3.2 Indices & Risk Sentiment

**Objective:** Summarize global risk‑on/risk‑off tone.

Key sections:

- **Index Performance**  
  - 24h and session‑to‑date moves for US, Europe, and Asia indices.  
  - Gap vs prior close, intraday high/low ranges.

- **Breadth & Volatility Proxies**  
  - Simple breadth (indices up vs down).  
  - Range‑based realized volatility per index.

- **Correlation Snapshot (lite)**  
  - Rolling correlation (e.g. last 3–5 days H1) between key indices and FX risk proxies (e.g., AUDJPY, NZDJPY).

### 3.3 Commodities

**Objective:** Monitor macro‑sensitive commodities relevant to FX and index strategies.

Key sections:

- **Energy & Metals Moves**  
  - 24h and session moves for Gold, Silver, WTI, Brent.  
  - Intraday high/low and realized range.

- **Macro Linkages**  
  - Simple commentary hooks (e.g. “Gold up, USD down / real yields proxy via DXY later”).

### 3.4 Equities & ETFs (Selected)

**Objective:** Follow key thematic names that interact with macro trades.

Key sections:

- **Top Movers List**  
  - Ranked by 1‑day and intraday % move among selected names.  

- **Volatility & Gaps**  
  - Gap vs prior close, intraday range, rough realized vol.

---

## 4. Workflow & Artifacts

### 4.1 Data Generation (MT5 Layer)

- Attach **Export_MarketSnapshot.mq5** script to any MT5 chart.  
- At each scheduled run (morning/evening):  
  - Script loops through configured symbol list (~50 symbols).  
  - For each symbol, exports M15 bars for the last 24h into:  
    - `<SYMBOL>_M15_windows_<YYYYMMDD_HHMM>GMT.csv` in `MQL5/Files`.  
- Files are synced to the host folder (e.g. `~/MarketData/MT5_exports`) on the Mac.

### 4.2 Ingestion & Lake Update

- Python script `ingest_mt5_exports.py`:

  - Discovers new CSVs, parses `time_gmt` as `bar_time_utc` (UTC).  
  - Adds `asset_class` and `source_run_ts` from metadata.  
  - Writes to a partitioned **parquet** or **DuckDB/SQLite** table.  
  - Dedupes using `(symbol, timeframe, bar_time_utc)`.

This creates a stable **time‑series panel** that can be queried by symbol, asset class, date, and snapshot.

### 4.3 Report Generation

- Python script `market_overview.py`:

  - Takes `run_ts` (or “latest”) as input.  
  - Pulls last 24h of data from the lake for the relevant symbols.  
  - Computes all summary metrics and rankings.  
  - Outputs:
    - **Console/markdown** view for quick inspection.  
    - Optional **PPTX deck** by reusing the existing matplotlib + pptx layout pipeline for Quantwater Tech research reports.

---

## 5. Alignment with Quantwater Tech Strategy

The overview is designed to serve as a **front door to the data lake** and as a **daily operating dashboard** for Quantwater Tech:

- Gives a **consistent macro and cross‑asset context** before running trading systems or manual interventions.  
- Feeds directly into **research notebooks** (factor construction, event studies, cross‑sectional signals).  
- Provides an auditable trail from **live broker prices → MT5 export → lake → report**, supporting robust strategy evaluation and eventual production deployment.

Over the next 1–2 weeks, the plan is to stabilize this pipeline (export → ingest → overview), then extend it with:

- Event‑aligned slices (your ATR/event framework).  
- Factor‑like derived features (carry, momentum, volatility regimes).  
- Hooks into automated trading and risk dashboards as Quantwater Tech infrastructure matures.
