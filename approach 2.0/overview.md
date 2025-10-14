CLI-Finance-Terminal Project Overview
Purpose
A fully automated, multi-asset financial market reporting system, fetching, analyzing, and generating daily quant-oriented global reports (HTML, PDF, etc.), structured for robust reproducible research and summary analytics.

Directory Structure
text
CLI-Finance-Terminal/
├── approach 2.0/
│   ├── daily_report.py           # Generates daily HTML report
│   ├── compute_metrics.py        # Computes cross-asset/summary metrics
│   ├── read_align_data.py        # Reads CSVs, aligns timezones, gets latest candles
│   ├── t12-comm.py               # Commodity fetcher (Twelve Data)
│   ├── t12-crypto.py             # Crypto OHLC fetcher
│   ├── t12-forex.py              # Forex OHLC fetcher
│   ├── t12-indices.py            # Indices/ETF OHLC fetcher
│   ├── t12-sec.py / t12-sec2.py  # Sector ETFs fetchers (split for rate limits)
│   ├── t12-vix.py                # Volatility ETF fetcher
│   ├── data/
│       ├── indices_15min.csv
│       ├── sector_etf_15min.csv
│       ├── commodities_15min.csv
│       ├── crypto_15min.csv
│       ├── forex_15min.csv
│       ├── bond_yields_15min.csv
│       ├── vix_15min.csv
│       ├── latest_market_data.pkl
│       ├── market_analysis_results.pkl
│   ├── daily_report.html         # Auto-generated HTML report
│   ├── config/                   # Any API keys or settings
│   ├── economic-calendar/        # Macro event scripts/calendar (optional)
│   ├── documentation/            # Project docs, Markdown overviews, etc.
│
├── venv/                         # Python virtual environment
├── enhanced-financial-report/    # Experimental reporting, charts, etc.
├── README.md
├── overview.md                   # This overview file
Main Scripts
Data Fetchers (t12-*.py):

Fetch OHLC/candle data for indices, commodities, forex, crypto, VIX, sector ETFs.

Save as CSV for next-stage processing.

read_align_data.py:

Reads all CSVs, aligns timestamps (per asset zone), extracts latest values, saves to pickle for pipeline analysis.

compute_metrics.py:

Analyzes fresh snapshots; computes leaders/laggards, cross-asset metrics, yield curve, volatility highlights.

Saves analysis results to pickle.

daily_report.py:

Generates formatted report as HTML (and optionally PDF), including per-asset-class tables with prices, 24h delta/%change, timezone conversion, sector and regional grouping.

Uses latest computed metrics and pickled analysis results.

Data Files
Each asset class is archived as a CSV in data/, keeping latest 15min candles for intraday analysis and delta computation. Pickles are used for intermediate/final analysis stages.

Utilities & Config
config/: For API keys, secrets, variable overrides.

venv/: Isolated Python packages/environment for reproducibility.

documentation/: Markdown/help files (overview.md, README.md, technical documentation).

Report Output
HTML Reports for browser viewing and PDF export

Other formats (Excel, Markdown, plot images, etc.) can be added as needed.

Additional Notes
All time synchronization, error handling, and modularity is built into the pipeline.

Each script is robust to missing data, timezone differences, API limits, and asset variability.

Charting, PDF automation, and macro-event integration can be added modularly.

