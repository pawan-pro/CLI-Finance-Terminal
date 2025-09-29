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
- **Status:** In Progress

