# CLI Finance Terminal - Automated Data Fetching

## Overview

This solution addresses the issue of individual script execution and API rate limiting by providing:

1. **Unified data fetching**: All market data is fetched through a single script
2. **Rate limiting**: Implements proper rate limiting to avoid API errors (429)
3. **Automated workflow**: Complete workflow from data fetching to report generation
4. **Batch processing**: Processes symbols in safe batches to respect API limits

## Problem Solved

Previously, the system had two main issues:
- All t12-*.py scripts had to be run individually
- Multiple symbols caused API rate limit errors (429): "You have run out of API credits for the current minute"

## Solution Components

### 1. fetch_all_data_batched.py

Main script that:
- Collects all symbols from all asset classes
- Processes symbols in batches (max 4 per minute to stay well under 8/min limit)
- Implements retry logic for transient errors
- Saves data to appropriate CSV files
- Adds delays between batches and asset classes

### 2. run_complete_workflow.py

Orchestrator script that runs the complete workflow:
1. Fetches all market data with rate limiting
2. Aligns data from all asset classes
3. Computes market metrics
4. Generates daily reports (both standard and enhanced versions)

## Usage

### Run the Complete Workflow (Recommended)

```bash
cd /Users/pawan/CLI-Finance-Terminal/approach 2.0
python run_complete_workflow.py
```

**Note**: The workflow takes approximately 20-25 minutes to complete due to API rate limiting, as it needs to respect the 8 calls per minute limit across all symbols.

This will:
- Fetch all market data respecting API limits
- Run data alignment
- Compute metrics
- Generate both daily reports

### Run Data Fetching Only

```bash
cd /Users/pawan/CLI-Finance-Terminal/approach 2.0
python fetch_all_data_batched.py
```

## Expected Runtime

- **Complete workflow**: ~20-25 minutes (due to API rate limiting)
- **Data fetching step**: ~18-20 minutes (most time-consuming due to rate limits)
- **Other steps**: ~1-2 minutes combined (alignment, metrics, reports)

## Verification

After successful execution, you should see:
- Updated CSV files in `/approach 2.0/data/` for each asset class
- Updated pickle files: `latest_market_data.pkl` and `market_analysis_results.pkl`
- Generated reports: `daily_report.html` and `daily_report-i.html`

## Technical Details

### Rate Limiting Strategy

**Single API Key:**
- **Batch size**: 4 API calls per batch (well under the 8 calls/minute limit)
- **Delay between calls**: 8 seconds between individual API calls
- **Delay between batches**: 62 seconds between batches
- **Delay between asset classes**: 20 seconds

**Multiple API Keys (Enhanced Performance):**
- **API Key Rotation**: Automatically rotates between multiple API keys to increase effective rate limits
- **Effective Rate Limit**: With N API keys, effective limit becomes 8*N calls per minute
- **Delay between calls**: 1 second (with key rotation across multiple limits)
- **Delay between asset classes**: 5-10 seconds (with multiple keys)
- **Retry Logic**: Automatic retries (up to 3 times) with 15-second delays for 429 errors, with automatic key switching on rate limit errors

**To add additional API keys**: Edit the `API_KEYS` list in `fetch_all_data_batched.py` to include more API keys.

### Asset Classes Handled

- Bonds: `US2Y`
- Commodities: `XAU/USD` 
- Cryptocurrencies: `BTC/USD`, `ETH/USD`, `XRP/USD`, `LTC/USD`, `ADA/USD`
- Forex: `EUR/USD`, `GBP/USD`, `USD/JPY`, `USD/CHF`, `USD/CAD`, `AUD/USD`
- Indices: `SPY`, `DIA`, `QQQ`, `IWM`, `EWU`, `EWJ`, `FEZ`, `DAX`, `EEM`, `INDA`, `MCHI`, `EWG`, `EWQ`, `EWS`, `EWA`
- Sector ETFs (S1): `XLK`, `XLF`, `XLE`, `XLV`, `XLY`, `XLP`, `XLI`
- Sector ETFs (S2): `XLRE`, `XLB`, `XLC`
- VIX: `VXX`, `UVXY`

## Error Handling

- Proper exception handling for network and API errors
- Automatic retry logic for rate limit errors (429)
- Logging of all errors and successful operations
- Graceful degradation when individual symbols fail

## Files Generated

- Updated CSV files in `/approach 2.0/data/` for each asset class
- Market data pickle file: `/approach 2.0/data/latest_market_data.pkl`
- Analysis results: `/approach 2.0/data/market_analysis_results.pkl`
- Reports: `/approach 2.0/daily_report.html` and `/approach 2.0/daily_report-i.html`

## Best Practices Implemented

- Rate limit adherence: Respects the API's 8 calls per minute limit
- Error handling: Implements retry logic for transient errors
- Caching: Optimized by batching requests to reduce redundant calls
- Secure storage: API key is stored in code (should be moved to environment variables in production)