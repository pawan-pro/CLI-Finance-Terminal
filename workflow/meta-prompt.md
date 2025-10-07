

# meta-prompt.md  
**Report Generation Workflow — Meta-Prompt: Data Source Migration to Alpha Vantage API**

This document outlines the state and instructions for migrating the CLI-Finance-Terminal’s data source from Finnhub (or MetaTrader 5) to the **Alpha Vantage API**. This meta-prompt is the primary directive for the development agent and will be used to track the overall migration progress.

***

## Primary Objective:  
**Replace Finnhub (or MT5) with Alpha Vantage API as the Primary Data Provider**  
All system reliance on Finnhub/MT5 for market data (quotes, historical data), news, and economic events needs to be replaced with a robust, API-first integration with Alpha Vantage. This will simplify the setup process and maximize free tier usage (within 25 request/day limits).

***

### Current Task Status:  
**Last Completed Task:** Project initialization; ready to begin Alpha Vantage migration.  
**Next Planned Task:** Stage 1: Foundational Setup & Configuration. Skeleton for new Alpha Vantage data provider.

### Errors/Notes from Last Run:  
N/A

***

## Global Directives & Migration Plan:

**1. API Key Management**

**Action:** The system must manage an `ALPHAVANTAGE_API_KEY`.

**Implementation:**
- Modify config loader to read `ALPHAVANTAGE_API_KEY` from .env file.
- Update README.md with instructions for getting and setting an Alpha Vantage API key.


**2. Symbol Naming Convention & Mapping**

**Critical:** Alpha Vantage uses specific ticker formats differing from Finnhub (e.g., symbol, exchange, etc).
**Action:** Build a centralized symbol mapping utility (`src/config/symbol_map.py` or JSON).
**Implementation:**
- The map must translate app symbols to Alpha Vantage format.
- Example mappings:
    - `^GSPC` → S&P 500 → `SPY` or `^GSPC`
    - `EURUSD` → `EURUSD`
    - `XAUUSD` → `XAUUSD`
    - `CL=F` → WTI Crude
    - Index/ETF differentiation as needed.
- Data provider must use this symbol map for all API calls. User-facing reports should retain common names (“S&P 500” etc).


**3. Data Provider Abstraction**

**Action:** Create a new, dedicated Alpha Vantage data provider to replace Finnhub code (`src/data/providers/finnhub_data.py`).
**Implementation:**
- Create: `src/data/providers/alphavantage_data.py`
- Inside, define class `AlphaVantageDataFetcher`
- Handles all API requests, including key management, symbol mapping, parsing, and Alpha Vantage rate limits.
- Must integrate with existing cache manager (to minimize API calls).


**4. Removal of Obsolete Finnhub/MT5 Code**

**Action:** After stable Alpha Vantage integration, remove Finnhub/MT5 code, configs, and CLI args.
**Implementation:**
- Delete `src/data/providers/finnhub_data.py` and/or `mt5_data.py`
- Remove all Finnhub/MT5 CLI arguments from `src/cli/main.py`
- Update README.md to remove references to Finnhub/MT5 and document Alpha Vantage setup.

***

## Section-Specific Directives (Implementation Plan):

**1. New Data Provider (`src/data/providers/alphavantage_data.py`)**
- Methods to implement:
    - `get_quote(symbol)`: Fetch latest price
    - `get_historical_data(symbol, days, interval)`: Fetch historical OHLCV, must match previous provider’s DataFrame structure
    - `get_24h_change(symbol)`: Calculate 24-hour pct change using Alpha Vantage historical data
    - `get_financial_news()`: Fetch general financial news — use Alpha Vantage news endpoints if available, else NewsAPI fallback
    - `get_economic_calendar()`: Fetch economic events (Alpha Vantage supports US, some macro indicators)

**2. Report Orchestrator (`src/analysis/daily_report.py`)**
- Change import from Finnhub provider to Alpha Vantage
- In main report generator init, instantiate `AlphaVantageDataFetcher`
- Review upstream data access; ensure all calls and structures match new provider

**3. PDF Generators (`professional_pdf_report.py`, `enhanced_institutional_pdf.py`)**
- Verify data formats (DataFrames, dicts) are kept consistent by new provider
- If formats match, no changes needed; perform post-integration check

**4. Top Market Movers (`src/analysis/enhanced_top_movers.py`)**
- Update logic to source symbol universe from new map file
- Update to call `get_24h_change` from Alpha Vantage
- Ensure percent change logic matches old structure

**5. CLI & Configuration (`src/cli/main.py` & `config/`)**
- Remove Finnhub/MT5 user-facing CLI components
- Remove old CLI arguments
- Ensure `ALPHAVANTAGE_API_KEY` environment variable is loaded
- Update help text

***

## Workflow Tracking:

### Stage 1: Foundational Setup (To Do)
- Add ALPHAVANTAGE_API_KEY to environment/config
- Create `src/data/providers/alphavantage_data.py` with skeleton class
- Build initial symbol mapping file/dictionary (`src/config/symbol_map.py`)
- Update README.md for Alpha Vantage instructions

### Stage 2: Core Provider Implementation (To Do)
- Implement quote/historical/candle logic in `AlphaVantageDataFetcher`
- Implement 24h change using historical endpoint
- Implement news and economic event fetch logic
- Integrate caching

### Stage 3: Integration & Refactoring (To Do)
- Wire up report generator to use new provider
- Test population of all report sections (Indices, FX, Commodities, Movers)
- Test dynamic Economic Calendar section

### Stage 4: Cleanup & Documentation (To Do)
- Delete Finnhub/MT5 provider scripts
- Remove Finnhub/MT5 CLI args and logic
- Clean README.md

### Stage 5: Final Verification (To Do)
- Generate normal & institutional reports to confirm full migration
- Check for data formatting, symbol mapping, user-facing naming conventions

***

**Note:**  
Carefully monitor the Alpha Vantage daily request quota (25/day) and optimize the caching/utilization logic for report generation within free limits.

***

**End meta-prompt.**

[1](https://finnhub.io/docs/api/forex-rates)