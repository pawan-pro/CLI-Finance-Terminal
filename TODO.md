# TODO List for CLI Finance Terminal Updates

## Report Formatting Issues

### 1. Executive Summary Decimal Values
- [ ] Fix index values showing decimals in Executive Summary (e.g., US30Roll showing 45921.70 instead of 45922)
- [ ] Apply integer formatting consistently for all indices in Executive Summary

### 2. Market Overview Status
- [ ] Fix "Markets closed" message in Market Overview section
- [ ] Ensure correct market status is displayed based on actual trading hours

### 3. UT100Roll Formatting
- [ ] UT100Roll is Nasdaq 100 index, should not show decimal values
- [ ] Apply integer formatting specifically for UT100Roll

### 4. Missing US500 Data
- [ ] US500 is still not being fetched/displayed
- [ ] Re-implement US500 data fetching or find alternative symbol

### 5. Major Indices Performance - 24H % Change
- [ ] Add 24H % change column to Major Indices Performance table
- [ ] Calculate and display percentage change for each index

### 6. Currency Markets - 24H % Change
- [ ] Add 24H % change column to Currency Markets table
- [ ] Calculate and display percentage change for each currency pair

### 7. Commodities - 24H % Change
- [ ] Add 24H % change column to Commodities table
- [ ] Calculate and display percentage change for each commodity

### 8. Top Movers Currency Formatting
- [ ] Currencies in Top Movers should not be rounded to integers
- [ ] Maintain proper decimal precision for currency values in Top Movers

### 9. Economic Calendar Still N/A
- [x] Economic Calendar is still showing as "NA"
- [x] Read and parse CSV file from specified directory: /Users/pawan/.wine/drive_c/Users/Administrator/AppData/Roaming/MetaQuotes/Terminal/Common/Files/economic_calendar.csv
- [ ] Fix formatting and display of economic calendar events

### 10. Market Charts Issues
- [ ] Fix stretched/compressed chart appearance
- [ ] Fix x-axis to show time in IST (10:00 or 22:00) instead of just date
- [ ] Fix candlestick rendering (sticks should be within candles, not at whiskers)

## Priority Order
1. Fix critical data display issues (US500, Economic Calendar)
2. Add missing 24H % change columns to all tables
3. Fix formatting issues (decimals vs integers for specific symbols)
4. Fix chart rendering problems
5. Address Market Overview status message

## Completed Tasks
- [x] Integer Values for Indices (partially completed)
- [x] Remove Spread Values
- [x] Gold Value Issue (XAUUSD)
- [x] Decimal Values in Top Market Movers (partially completed)
- [x] Chart Updates to Candlestick Format (basic implementation)