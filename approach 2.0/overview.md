# CLI-Finance-Terminal Project Overview

## Purpose

A fully automated, multi-asset financial market reporting system, fetching, analyzing, and generating daily quant-oriented global reports (HTML, PDF, etc.), structured for robust reproducible research and summary analytics.

## Data Sources

*   **MT5 Server (Primary):** This is the primary source for 24x5 data on major indices, FX, and commodities, fetched via `mt5_file_downloader.py`.
*   **Twelve Data API (Fallback):** This is used for assets not covered by MT5 (Bonds, VIX, Crypto, Sectors) and as a fallback for any stale MT5 assets.

## Directory Structure

```text
CLI-Finance-Terminal/
├── approach 2.0/
│   ├── src/
│   │   ├── fetchers/
│   │   │   ├── mt5_file_downloader.py  # MT5 data fetcher
│   │   │   ├── t12-comm.py             # Commodity fetcher (Twelve Data)
│   │   │   ├── t12-crypto.py           # Crypto OHLC fetcher
│   │   │   ├── t12-forex.py            # Forex OHLC fetcher
│   │   │   ├── t12-indices.py          # Indices/ETF OHLC fetcher
│   │   │   ├── t12-sec.py / t12-sec2.py# Sector ETFs fetchers
│   │   │   └── t12-vix.py              # Volatility ETF fetcher
│   ├── daily_report.py                 # Generates daily HTML report
│   ├── compute_metrics.py              # Computes cross-asset/summary metrics
│   ├── read_align_data.py              # Reads CSVs, aligns timezones, gets latest candles
│   ├── data/
│   │   ├── mt5/
│   │   │   └── mt5_data.csv            # MT5 data
│   │   ├── indices_15min.csv
│   │   ├── sector_etf_15min.csv
│   │   ├── commodities_15min.csv
│   │   ├── crypto_15min.csv
│   │   ├── forex_15min.csv
│   │   ├── bond_yields_15min.csv
│   │   ├── vix_15min.csv
│   │   ├── latest_market_data.pkl
│   │   └── market_analysis_results.pkl
│   ├── daily_report.html               # Auto-generated HTML report
│   ├── config/                         # Any API keys or settings
│   ├── economic-calendar/              # Macro event scripts/calendar (optional)
│   └── documentation/                  # Project docs, Markdown overviews, etc.
│
├── venv/                               # Python virtual environment
├── enhanced-financial-report/          # Experimental reporting, charts, etc.
├── README.md
└── overview.md                         # This overview file
```

## Main Scripts

### Data Flow

1.  **`mt5_file_downloader.py`:** Fetches the latest 24x5 data from the MT5 server.
2.  **Data Fetchers (`t12-*.py`):** Fetch OHLC/candle data for various asset classes from the Twelve Data API.
3.  **`read_align_data.py`:**
    *   Reads the MT5 CSV and all Twelve Data CSVs.
    *   Prioritizes the MT5 data for supported assets.
    *   Falls back to Twelve Data for assets not covered by MT5 or if the MT5 data is stale.
    *   Aligns timestamps, extracts the latest values, and saves the unified data to a pickle file for pipeline analysis.
4.  **`compute_metrics.py`:**
    *   Analyzes the fresh data snapshots.
    *   Computes leaders/laggards, cross-asset metrics, yield curve, and volatility highlights.
    *   Saves the analysis results to a pickle file.
5.  **`daily_report.py` and `daily_report-i.py`:**
    *   Generate formatted reports as HTML.
    *   Include per-asset-class tables with prices, 24h delta/%change, timezone conversion, and sector and regional grouping.
    *   Use the latest computed metrics and pickled analysis results.
    *   `daily_report-i.py` generates charts with 1-hour candles.

## Data Files

Each asset class is archived as a CSV in `data/`, keeping the latest 15min candles for intraday analysis and delta computation. Pickles are used for intermediate/final analysis stages.

## Utilities & Config

*   **`config/`:** For API keys, secrets, and variable overrides.
*   **`venv/`:** Isolated Python packages/environment for reproducibility.
*   **`documentation/`:** Markdown/help files (`overview.md`, `README.md`, technical documentation).

## Report Output

HTML Reports for browser viewing and PDF export. Other formats (Excel, Markdown, plot images, etc.) can be added as needed.

## Additional Notes

*   All time synchronization, error handling, and modularity is built into the pipeline.
*   Each script is robust to missing data, timezone differences, API limits, and asset variability.
*   Charting, PDF automation, and macro-event integration can be added modularly.
