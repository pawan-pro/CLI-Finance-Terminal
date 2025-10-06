# Prompt Updates for enhanced_institutional_pdf.py

This file tracks the progress of updates based on the user's prompt.md.

## Current Status:

### Task 1: Central alignment for "Daily Investment Research Note"
- **Status:** Completed
- **Description:** The "Daily Investment Research Note" on the cover page needs to be centrally aligned.
- **Action:** Modified the `subtitle_style` in `add_cover_page` method to set `alignment=1` (center).

### Task 2: Remove "CONFIDENTIAL - FOR AUTHORIZED PERSONNEL ONLY"
- **Status:** Completed
- **Description:** Removed the confidentiality notice from the cover page.
- **Action:** Removed the `conf_style` and the corresponding `Paragraph` from `add_cover_page`.

### Task 3: Remove "Institutional Grade" and CAPS from title on page 3
- **Status:** Completed
- **Description:** Removed "Institutional Grade" and converted the title to sentence case on page 3.
- **Action:** Modified the `add_title` method to use `title.title()` and ensured `subtitle_style` is centrally aligned.

### Task 4: Executive Summary - Justified alignment and gap between points
- **Status:** Completed
- **Description:** The Executive Summary text needs to have justified alignment and a gap between each point.
- **Action:** Modified `executive_summary_style` to set `alignment=4` (justified) and added `Spacer` between points.

### Task 5: Update Key Market Insight, Biggest Risk, Conviction Trade, Portfolio Implication
- **Status:** Completed
- **Description:** Updated the content of these sections to reflect different trading perspectives (prop trading, day trading, swing trading, position trading, portfolio management).
- **Action:** Modified the `insights_boxes` content in `add_executive_summary`.

### Task 6: Market Overview - Adjust time to UTC
- **Status:** Completed
- **Description:** The time shown in the Market Overview is in IST but mentioned as UTC. It has been adjusted to display correctly in UTC.
- **Action:** Modified the `market_status` dictionary creation in the example usage to use `datetime.utcnow()`.

### Task 7: Resolve coloring issue in "Key Market Indices Performance"
- **Status:** Completed
- **Description:** The `font color` tags in the "Key Market Indices Performance" table are not being applied, resulting in uncolored text.
- **Action:** Modified the `add_market_overview` method to apply colors directly through `ParagraphStyle` for table cells.

### Task 8: Correct calculation of Chg % (24H change)
- **Status:** Completed
- **Description:** The calculation of `Chg %` is always 0.01%. It needs to be the change % over the last 24 hours (weekday to weekday, and Friday-Monday change over the timestamp).
- **Action:** Added `get_24h_change` method to `src/data/providers/mt5_data.py` and integrated it into `add_market_overview` in `enhanced_institutional_pdf.py`.

### Task 9: Rename symbols and add change/change % to tables
- **Status:** Completed
- **Description:** Replace MT5 symbols with user-friendly names (e.g., "US500Roll" with "S&P 500 CFD") and include 24H change and change % for major indices, currency markets, and commodities.
- **Action:** 
    1. Defined a symbol mapping dictionary.
    2. Updated `add_market_overview`, `add_indices_table`, `add_currencies_table`, and `add_commodities_table` to use the new names and include change/change %.
    3. Added a note about CFDs where appropriate.

### Task 10: Use Alpha Vantage for Bonds/ETFs Data
- **Status:** Completed
- **Description:** Use Alpha Vantage API to fetch major bonds and ETFs data instead of using MT5 data.
- **Action:** 
    1. Integrated `AlphaVantageData` class to fetch bonds/ETFs data from Alpha Vantage API
    2. Updated `add_bonds_table` method to prioritize Alpha Vantage data with MT5 as fallback
    3. Added comprehensive list of bond/ETF symbols including Treasury ETFs, corporate bond ETFs, international bond ETFs, and commodity ETFs
    4. Ensured 24H change data is included for all bond/ETF instruments

### Task 11: Use economic calendar data from CSV file
- **Status:** Completed
- **Description:** Use data from "/Users/pawan/CLI-Finance-Terminal/economic-calendar/ECONOMIC_CALENDAR_DATA.csv" file to create the calendar.
- **Action:** Verified that the `add_calendar_events` function already properly reads from the specified CSV file with appropriate filtering for date and importance level.

### Task 12: Fix chart creation issues
- **Status:** Completed
- **Description:** Ensure charts are properly created and displayed in the report.
- **Action:** Enhanced the `add_charts` method with robust error handling for missing chart files and improved display logic to handle various file types gracefully.

### Task 13: Ensure 24H Change % consistency across the whole report
- **Status:** Completed
- **Description:** Ensure 24H Change % is consistent across all sections of the report.
- **Action:** Applied consistent color coding and calculation methodology across all financial data tables (market overview, indices, currencies, commodities, bonds) using the same `get_24h_change` method with appropriate styling.

### Task 14: Enhanced chart debugging and logging
- **Status:** Completed
- **Description:** Added comprehensive debug logging to track chart creation and embedding issues as per prompt.md requirements.
- **Action:** Enhanced the `add_charts` method with detailed logging at every stage:
    1. After chart creation (confirmation of file existence)
    2. Before embedding in PDF (logging attempted file path)
    3. On error (precise error logging with skip-only-that-chart behavior)
    4. Added summary logging to prompt-updates.md for chart embedding attempts

### Task 15: Enhanced MT5 Symbol Mapping and Debugging
- **Status:** Completed
- **Description:** Implemented comprehensive debugging and symbol mapping as per meta-prompt.md requirements to handle MT5 symbol suffixes (.sd, .USD, etc.) and provide fallback options when symbols are not found.
- **Action:** 
    1. Enhanced `get_symbol_info` method in `MT5DataFetcher` to try common suffixes (.sd, .USD, etc.) when original symbol is not found in MT5
    2. Enhanced `get_symbol_info` method to also try known alternative symbol mappings (e.g., US500Roll -> SPX500)
    3. Enhanced `get_24h_change` method to also try alternative symbol suffixes and mappings when historical data is not available
    4. Enhanced `add_charts` method with additional debugging for missing chart files that includes symbol verification and warnings in PDF for symbol mapping issues
    5. Added logging to track symbol attempted, available symbols in MT5, and found/not found status
    6. Added PDF warnings for missing charts due to symbol mapping issues as per meta-prompt.md


### Chart Embedding Summary
- **Status:** Successfully embedded 22 out of 22 requested chart files
- **Files processed:** ['./reports/daily_report_20250930_231411/charts/US500Roll_candlestick.png', './reports/daily_report_20250930_231411/charts/US30Roll_candlestick.png', './reports/daily_report_20250930_231411/charts/UK100Roll_candlestick.png', './reports/daily_report_20250930_231411/charts/DE40Roll_candlestick.png', './reports/daily_report_20250930_231411/charts/FRA40Roll_candlestick.png', './reports/daily_report_20250930_231411/charts/JP225Roll_candlestick.png', './reports/daily_report_20250930_231411/charts/HK50Roll_candlestick.png', './reports/daily_report_20250930_231411/charts/CHINA50Roll_candlestick.png', './reports/daily_report_20250930_231411/charts/EURUSD.sd_candlestick.png', './reports/daily_report_20250930_231411/charts/GBPUSD.sd_candlestick.png', './reports/daily_report_20250930_231411/charts/USDJPY.sd_candlestick.png', './reports/daily_report_20250930_231411/charts/AUDUSD.sd_candlestick.png', './reports/daily_report_20250930_231411/charts/USDCAD.sd_candlestick.png', './reports/daily_report_20250930_231411/charts/USDCHF.sd_candlestick.png', './reports/daily_report_20250930_231411/charts/NZDUSD.sd_candlestick.png', './reports/daily_report_20250930_231411/charts/XAUUSD_candlestick.png', './reports/daily_report_20250930_231411/charts/XAGUSD_candlestick.png', './reports/daily_report_20250930_231411/charts/XPTUSD_candlestick.png', './reports/daily_report_20250930_231411/charts/BTCUSD.lv_candlestick.png', './reports/daily_report_20250930_231411/charts/ETHUSD.lv_candlestick.png', './reports/daily_report_20250930_231411/charts/LTCUSD.lv_candlestick.png', './reports/daily_report_20250930_231411/charts/VIXRoll_candlestick.png']
- **Date:** 2025-09-30 23:16:42

### Chart Embedding Summary
- **Status:** Successfully embedded 22 out of 22 requested chart files
- **Files processed:** ['./reports/daily_report_20250930_232217/charts/US500Roll_candlestick.png', './reports/daily_report_20250930_232217/charts/US30Roll_candlestick.png', './reports/daily_report_20250930_232217/charts/UK100Roll_candlestick.png', './reports/daily_report_20250930_232217/charts/DE40Roll_candlestick.png', './reports/daily_report_20250930_232217/charts/FRA40Roll_candlestick.png', './reports/daily_report_20250930_232217/charts/JP225Roll_candlestick.png', './reports/daily_report_20250930_232217/charts/HK50Roll_candlestick.png', './reports/daily_report_20250930_232217/charts/CHINA50Roll_candlestick.png', './reports/daily_report_20250930_232217/charts/EURUSD.sd_candlestick.png', './reports/daily_report_20250930_232217/charts/GBPUSD.sd_candlestick.png', './reports/daily_report_20250930_232217/charts/USDJPY.sd_candlestick.png', './reports/daily_report_20250930_232217/charts/AUDUSD.sd_candlestick.png', './reports/daily_report_20250930_232217/charts/USDCAD.sd_candlestick.png', './reports/daily_report_20250930_232217/charts/USDCHF.sd_candlestick.png', './reports/daily_report_20250930_232217/charts/NZDUSD.sd_candlestick.png', './reports/daily_report_20250930_232217/charts/XAUUSD_candlestick.png', './reports/daily_report_20250930_232217/charts/XAGUSD_candlestick.png', './reports/daily_report_20250930_232217/charts/XPTUSD_candlestick.png', './reports/daily_report_20250930_232217/charts/BTCUSD.lv_candlestick.png', './reports/daily_report_20250930_232217/charts/ETHUSD.lv_candlestick.png', './reports/daily_report_20250930_232217/charts/LTCUSD.lv_candlestick.png', './reports/daily_report_20250930_232217/charts/VIXRoll_candlestick.png']
- **Date:** 2025-09-30 23:24:39

### Chart Embedding Summary
- **Status:** Successfully embedded 22 out of 22 requested chart files
- **Files processed:** ['./reports/daily_report_20250930_232647/charts/US500Roll_candlestick.png', './reports/daily_report_20250930_232647/charts/US30Roll_candlestick.png', './reports/daily_report_20250930_232647/charts/UK100Roll_candlestick.png', './reports/daily_report_20250930_232647/charts/DE40Roll_candlestick.png', './reports/daily_report_20250930_232647/charts/FRA40Roll_candlestick.png', './reports/daily_report_20250930_232647/charts/JP225Roll_candlestick.png', './reports/daily_report_20250930_232647/charts/HK50Roll_candlestick.png', './reports/daily_report_20250930_232647/charts/CHINA50Roll_candlestick.png', './reports/daily_report_20250930_232647/charts/EURUSD.sd_candlestick.png', './reports/daily_report_20250930_232647/charts/GBPUSD.sd_candlestick.png', './reports/daily_report_20250930_232647/charts/USDJPY.sd_candlestick.png', './reports/daily_report_20250930_232647/charts/AUDUSD.sd_candlestick.png', './reports/daily_report_20250930_232647/charts/USDCAD.sd_candlestick.png', './reports/daily_report_20250930_232647/charts/USDCHF.sd_candlestick.png', './reports/daily_report_20250930_232647/charts/NZDUSD.sd_candlestick.png', './reports/daily_report_20250930_232647/charts/XAUUSD_candlestick.png', './reports/daily_report_20250930_232647/charts/XAGUSD_candlestick.png', './reports/daily_report_20250930_232647/charts/XPTUSD_candlestick.png', './reports/daily_report_20250930_232647/charts/BTCUSD.lv_candlestick.png', './reports/daily_report_20250930_232647/charts/ETHUSD.lv_candlestick.png', './reports/daily_report_20250930_232647/charts/LTCUSD.lv_candlestick.png', './reports/daily_report_20250930_232647/charts/VIXRoll_candlestick.png']
- **Date:** 2025-09-30 23:29:15

### Chart Embedding Summary
- **Status:** Successfully embedded 22 out of 22 requested chart files
- **Files processed:** ['./reports/daily_report_20250930_232938/charts/US500Roll_candlestick.png', './reports/daily_report_20250930_232938/charts/US30Roll_candlestick.png', './reports/daily_report_20250930_232938/charts/UK100Roll_candlestick.png', './reports/daily_report_20250930_232938/charts/DE40Roll_candlestick.png', './reports/daily_report_20250930_232938/charts/FRA40Roll_candlestick.png', './reports/daily_report_20250930_232938/charts/JP225Roll_candlestick.png', './reports/daily_report_20250930_232938/charts/HK50Roll_candlestick.png', './reports/daily_report_20250930_232938/charts/CHINA50Roll_candlestick.png', './reports/daily_report_20250930_232938/charts/EURUSD.sd_candlestick.png', './reports/daily_report_20250930_232938/charts/GBPUSD.sd_candlestick.png', './reports/daily_report_20250930_232938/charts/USDJPY.sd_candlestick.png', './reports/daily_report_20250930_232938/charts/AUDUSD.sd_candlestick.png', './reports/daily_report_20250930_232938/charts/USDCAD.sd_candlestick.png', './reports/daily_report_20250930_232938/charts/USDCHF.sd_candlestick.png', './reports/daily_report_20250930_232938/charts/NZDUSD.sd_candlestick.png', './reports/daily_report_20250930_232938/charts/XAUUSD_candlestick.png', './reports/daily_report_20250930_232938/charts/XAGUSD_candlestick.png', './reports/daily_report_20250930_232938/charts/XPTUSD_candlestick.png', './reports/daily_report_20250930_232938/charts/BTCUSD.lv_candlestick.png', './reports/daily_report_20250930_232938/charts/ETHUSD.lv_candlestick.png', './reports/daily_report_20250930_232938/charts/LTCUSD.lv_candlestick.png', './reports/daily_report_20250930_232938/charts/VIXRoll_candlestick.png']
- **Date:** 2025-09-30 23:32:15

### Chart Embedding Summary
- **Status:** Successfully embedded 22 out of 22 requested chart files
- **Files processed:** ['./reports/daily_report_20251001_000804/charts/US500Roll_candlestick.png', './reports/daily_report_20251001_000804/charts/US30Roll_candlestick.png', './reports/daily_report_20251001_000804/charts/UK100Roll_candlestick.png', './reports/daily_report_20251001_000804/charts/DE40Roll_candlestick.png', './reports/daily_report_20251001_000804/charts/FRA40Roll_candlestick.png', './reports/daily_report_20251001_000804/charts/JP225Roll_candlestick.png', './reports/daily_report_20251001_000804/charts/HK50Roll_candlestick.png', './reports/daily_report_20251001_000804/charts/CHINA50Roll_candlestick.png', './reports/daily_report_20251001_000804/charts/EURUSD.sd_candlestick.png', './reports/daily_report_20251001_000804/charts/GBPUSD.sd_candlestick.png', './reports/daily_report_20251001_000804/charts/USDJPY.sd_candlestick.png', './reports/daily_report_20251001_000804/charts/AUDUSD.sd_candlestick.png', './reports/daily_report_20251001_000804/charts/USDCAD.sd_candlestick.png', './reports/daily_report_20251001_000804/charts/USDCHF.sd_candlestick.png', './reports/daily_report_20251001_000804/charts/NZDUSD.sd_candlestick.png', './reports/daily_report_20251001_000804/charts/XAUUSD_candlestick.png', './reports/daily_report_20251001_000804/charts/XAGUSD_candlestick.png', './reports/daily_report_20251001_000804/charts/XPTUSD_candlestick.png', './reports/daily_report_20251001_000804/charts/BTCUSD.lv_candlestick.png', './reports/daily_report_20251001_000804/charts/ETHUSD.lv_candlestick.png', './reports/daily_report_20251001_000804/charts/LTCUSD.lv_candlestick.png', './reports/daily_report_20251001_000804/charts/VIXRoll_candlestick.png']
- **Date:** 2025-10-01 00:10:23

### Chart Embedding Summary
- **Status:** Successfully embedded 22 out of 22 requested chart files
- **Files processed:** ['./reports/daily_report_20251001_051641/charts/US500Roll_candlestick.png', './reports/daily_report_20251001_051641/charts/US30Roll_candlestick.png', './reports/daily_report_20251001_051641/charts/UK100Roll_candlestick.png', './reports/daily_report_20251001_051641/charts/DE40Roll_candlestick.png', './reports/daily_report_20251001_051641/charts/FRA40Roll_candlestick.png', './reports/daily_report_20251001_051641/charts/JP225Roll_candlestick.png', './reports/daily_report_20251001_051641/charts/HK50Roll_candlestick.png', './reports/daily_report_20251001_051641/charts/CHINA50Roll_candlestick.png', './reports/daily_report_20251001_051641/charts/EURUSD.sd_candlestick.png', './reports/daily_report_20251001_051641/charts/GBPUSD.sd_candlestick.png', './reports/daily_report_20251001_051641/charts/USDJPY.sd_candlestick.png', './reports/daily_report_20251001_051641/charts/AUDUSD.sd_candlestick.png', './reports/daily_report_20251001_051641/charts/USDCAD.sd_candlestick.png', './reports/daily_report_20251001_051641/charts/USDCHF.sd_candlestick.png', './reports/daily_report_20251001_051641/charts/NZDUSD.sd_candlestick.png', './reports/daily_report_20251001_051641/charts/XAUUSD_candlestick.png', './reports/daily_report_20251001_051641/charts/XAGUSD_candlestick.png', './reports/daily_report_20251001_051641/charts/XPTUSD_candlestick.png', './reports/daily_report_20251001_051641/charts/BTCUSD.lv_candlestick.png', './reports/daily_report_20251001_051641/charts/ETHUSD.lv_candlestick.png', './reports/daily_report_20251001_051641/charts/LTCUSD.lv_candlestick.png', './reports/daily_report_20251001_051641/charts/VIXRoll_candlestick.png']
- **Date:** 2025-10-01 05:19:35

### Chart Embedding Summary
- **Status:** Successfully embedded 22 out of 22 requested chart files
- **Files processed:** ['./reports/daily_report_20251002_052131/charts/US500Roll_candlestick.png', './reports/daily_report_20251002_052131/charts/US30Roll_candlestick.png', './reports/daily_report_20251002_052131/charts/UK100Roll_candlestick.png', './reports/daily_report_20251002_052131/charts/DE40Roll_candlestick.png', './reports/daily_report_20251002_052131/charts/FRA40Roll_candlestick.png', './reports/daily_report_20251002_052131/charts/JP225Roll_candlestick.png', './reports/daily_report_20251002_052131/charts/HK50Roll_candlestick.png', './reports/daily_report_20251002_052131/charts/CHINA50Roll_candlestick.png', './reports/daily_report_20251002_052131/charts/EURUSD.sd_candlestick.png', './reports/daily_report_20251002_052131/charts/GBPUSD.sd_candlestick.png', './reports/daily_report_20251002_052131/charts/USDJPY.sd_candlestick.png', './reports/daily_report_20251002_052131/charts/AUDUSD.sd_candlestick.png', './reports/daily_report_20251002_052131/charts/USDCAD.sd_candlestick.png', './reports/daily_report_20251002_052131/charts/USDCHF.sd_candlestick.png', './reports/daily_report_20251002_052131/charts/NZDUSD.sd_candlestick.png', './reports/daily_report_20251002_052131/charts/XAUUSD_candlestick.png', './reports/daily_report_20251002_052131/charts/XAGUSD_candlestick.png', './reports/daily_report_20251002_052131/charts/XPTUSD_candlestick.png', './reports/daily_report_20251002_052131/charts/BTCUSD.lv_candlestick.png', './reports/daily_report_20251002_052131/charts/ETHUSD.lv_candlestick.png', './reports/daily_report_20251002_052131/charts/LTCUSD.lv_candlestick.png', './reports/daily_report_20251002_052131/charts/VIXRoll_candlestick.png']
- **Date:** 2025-10-02 05:29:36

### Chart Embedding Summary
- **Status:** Successfully embedded 22 out of 22 requested chart files
- **Files processed:** ['./reports/daily_report_20251002_053745/charts/US500Roll_candlestick.png', './reports/daily_report_20251002_053745/charts/US30Roll_candlestick.png', './reports/daily_report_20251002_053745/charts/UK100Roll_candlestick.png', './reports/daily_report_20251002_053745/charts/DE40Roll_candlestick.png', './reports/daily_report_20251002_053745/charts/FRA40Roll_candlestick.png', './reports/daily_report_20251002_053745/charts/JP225Roll_candlestick.png', './reports/daily_report_20251002_053745/charts/HK50Roll_candlestick.png', './reports/daily_report_20251002_053745/charts/CHINA50Roll_candlestick.png', './reports/daily_report_20251002_053745/charts/EURUSD.sd_candlestick.png', './reports/daily_report_20251002_053745/charts/GBPUSD.sd_candlestick.png', './reports/daily_report_20251002_053745/charts/USDJPY.sd_candlestick.png', './reports/daily_report_20251002_053745/charts/AUDUSD.sd_candlestick.png', './reports/daily_report_20251002_053745/charts/USDCAD.sd_candlestick.png', './reports/daily_report_20251002_053745/charts/USDCHF.sd_candlestick.png', './reports/daily_report_20251002_053745/charts/NZDUSD.sd_candlestick.png', './reports/daily_report_20251002_053745/charts/XAUUSD_candlestick.png', './reports/daily_report_20251002_053745/charts/XAGUSD_candlestick.png', './reports/daily_report_20251002_053745/charts/XPTUSD_candlestick.png', './reports/daily_report_20251002_053745/charts/BTCUSD.lv_candlestick.png', './reports/daily_report_20251002_053745/charts/ETHUSD.lv_candlestick.png', './reports/daily_report_20251002_053745/charts/LTCUSD.lv_candlestick.png', './reports/daily_report_20251002_053745/charts/VIXRoll_candlestick.png']
- **Date:** 2025-10-02 05:45:32

### Chart Embedding Summary
- **Status:** Successfully embedded 23 out of 23 requested chart files
- **Files processed:** ['./reports/daily_report_20251003_220257/charts/US500Roll_candlestick.png', './reports/daily_report_20251003_220257/charts/US30Roll_candlestick.png', './reports/daily_report_20251003_220257/charts/UK100Roll_candlestick.png', './reports/daily_report_20251003_220257/charts/DE40Roll_candlestick.png', './reports/daily_report_20251003_220257/charts/FRA40Roll_candlestick.png', './reports/daily_report_20251003_220257/charts/JP225Roll_candlestick.png', './reports/daily_report_20251003_220257/charts/HK50Roll_candlestick.png', './reports/daily_report_20251003_220257/charts/CHINA50Roll_candlestick.png', './reports/daily_report_20251003_220257/charts/EURUSD.sd_candlestick.png', './reports/daily_report_20251003_220257/charts/GBPUSD.sd_candlestick.png', './reports/daily_report_20251003_220257/charts/USDJPY.sd_candlestick.png', './reports/daily_report_20251003_220257/charts/AUDUSD.sd_candlestick.png', './reports/daily_report_20251003_220257/charts/USDCAD.sd_candlestick.png', './reports/daily_report_20251003_220257/charts/USDCHF.sd_candlestick.png', './reports/daily_report_20251003_220257/charts/NZDUSD.sd_candlestick.png', './reports/daily_report_20251003_220257/charts/XAUUSD_candlestick.png', './reports/daily_report_20251003_220257/charts/XAGUSD_candlestick.png', './reports/daily_report_20251003_220257/charts/XPTUSD_candlestick.png', './reports/daily_report_20251003_220257/charts/USOILRoll_candlestick.png', './reports/daily_report_20251003_220257/charts/BTCUSD.lv_candlestick.png', './reports/daily_report_20251003_220257/charts/ETHUSD.lv_candlestick.png', './reports/daily_report_20251003_220257/charts/LTCUSD.lv_candlestick.png', './reports/daily_report_20251003_220257/charts/VIXRoll_candlestick.png']
- **Date:** 2025-10-03 22:05:35

### Chart Embedding Summary
- **Status:** Successfully embedded 23 out of 23 requested chart files
- **Files processed:** ['./reports/daily_report_20251004_051321/charts/US500Roll_candlestick.png', './reports/daily_report_20251004_051321/charts/US30Roll_candlestick.png', './reports/daily_report_20251004_051321/charts/UK100Roll_candlestick.png', './reports/daily_report_20251004_051321/charts/DE40Roll_candlestick.png', './reports/daily_report_20251004_051321/charts/FRA40Roll_candlestick.png', './reports/daily_report_20251004_051321/charts/JP225Roll_candlestick.png', './reports/daily_report_20251004_051321/charts/HK50Roll_candlestick.png', './reports/daily_report_20251004_051321/charts/CHINA50Roll_candlestick.png', './reports/daily_report_20251004_051321/charts/EURUSD.sd_candlestick.png', './reports/daily_report_20251004_051321/charts/GBPUSD.sd_candlestick.png', './reports/daily_report_20251004_051321/charts/USDJPY.sd_candlestick.png', './reports/daily_report_20251004_051321/charts/AUDUSD.sd_candlestick.png', './reports/daily_report_20251004_051321/charts/USDCAD.sd_candlestick.png', './reports/daily_report_20251004_051321/charts/USDCHF.sd_candlestick.png', './reports/daily_report_20251004_051321/charts/NZDUSD.sd_candlestick.png', './reports/daily_report_20251004_051321/charts/XAUUSD_candlestick.png', './reports/daily_report_20251004_051321/charts/XAGUSD_candlestick.png', './reports/daily_report_20251004_051321/charts/XPTUSD_candlestick.png', './reports/daily_report_20251004_051321/charts/USOILRoll_candlestick.png', './reports/daily_report_20251004_051321/charts/BTCUSD.lv_candlestick.png', './reports/daily_report_20251004_051321/charts/ETHUSD.lv_candlestick.png', './reports/daily_report_20251004_051321/charts/LTCUSD.lv_candlestick.png', './reports/daily_report_20251004_051321/charts/VIXRoll_candlestick.png']
- **Date:** 2025-10-04 05:15:36
