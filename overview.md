# Project Overview

This project is a CLI-based financial terminal for generating investment reports. It fetches data from various sources, processes it, and generates a daily HTML report.

## Project Structure

```
CLI-Finance-Terminal/
├── run_complete_workflow.py
├── src/
│   ├── fetchers/
│   │   ├── t12-b.py
│   │   ├── t12-comm.py
│   │   ├── t12-crypto.py
│   │   ├── t12-fx.py
│   │   ├── t12-i.py
│   │   ├── t12-sec.py
│   │   ├── t12-sec2.py
│   │   └── t12-vix.py
│   ├── processing/
│   │   ├── read_align_data.py
│   │   ├── compute_metrics.py
│   │   └── daily_report.py
│   └── utils/
├── data/
│   ├── bonds_15min.csv
│   ├── commodities_15min.csv
│   ├── crypto_15min.csv
│   ├── forex_15min.csv
│   ├── indices_15min.csv
│   ├── sector_etf_15min.csv
│   ├── sector2_etf_15min.csv
│   ├── vix_15min.csv
│   ├── latest_market_data.pkl
│   └── market_analysis_results.pkl
├── reports/
│   └── daily_report.html
├── config/
└── overview.md
```

## Execution Workflow

To run the entire data pipeline and generate the final report, execute the master script from the root directory:

```bash
python run_complete_workflow.py
```

## Component Breakdown

*   **run_complete_workflow.py**: The main entry point for the application. It orchestrates the entire data pipeline, from fetching to report generation.
*   **src/fetchers/**: This directory contains scripts responsible for gathering raw data from various APIs.
*   **src/processing/**: This directory contains scripts for cleaning, analyzing, and transforming the raw data into the final report.
    *   `read_align_data.py`: Reads all the raw CSV data, aligns timezones, and creates a pickle file with the latest data for each asset.
    *   `compute_metrics.py`: Calculates various metrics and generates a market summary, saving the results in a pickle file.
    *   `daily_report.py`: Generates the final HTML report from the analysis results.
*   **src/utils/**: This directory is for shared helper functions and classes.
*   **/data/**: This directory stores raw `.csv` and intermediate `.pkl` files.
*   **/reports/**: This is the output directory for the final `daily_report.html`.
*   **/config/**: This directory is for API keys and other sensitive settings.

## Data Flow Diagram

```
API -> src/fetchers/ -> data/*.csv
data/*.csv -> src/processing/read_align_data.py -> data/latest_market_data.pkl
data/latest_market_data.pkl -> src/processing/compute_metrics.py -> data/market_analysis_results.pkl
data/market_analysis_results.pkl -> src/processing/daily_report.py -> reports/daily_report.html
```
