# Report Generation Workflow - Meta-Prompt

This document outlines the state and instructions for generating the "Daily Investment Research Note." This meta-prompt is updated upon the completion of each task, allowing for seamless continuation or error recovery.

---

## Current Task Status:

- **Last Completed Task:** Report generated.
- **Next Planned Task:** Apply global formatting and content structure adjustments.
- **Errors/Notes from Last Run:** None.

---

## Global Formatting and Content Directives:

1.  **Font:**
    *   Use "Century Gothic" for all text.
    *   **Bold:** `/Users/pawan/Desktop/fonts/Century Gothic/centurygothic_bold.tff`
    *   **Regular:** `/Users/pawan/Desktop/fonts/Century Gothic/centurygothic.tff`

2.  **Case:** Do not use uppercase letters anywhere in the report, except where proper nouns or initialisms (like "ETF," "CPI," "API") naturally require them.
3.  **Title/Header:**
    *   Remove "Institutional Grade" from the main title. The quality is *implied* as institutional grade, not explicitly stated in the title.
    *   Update the main title on page 1 to reflect this change.

4.  **Market Status Line:** Remove the line indicating whether markets are open or closed (e.g., "Markets are currently Closed as of...").

5.  **Text Justification:** All textual content (executive summary, key market insight, biggest risk, conviction trade, portfolio implication) must be fully justified.

6.  **Color Coding for % Change:**
    *   Implement color coding for all percentage change values across the report (e.g., green for positive, red for negative, black/gray for no change).
    *   Ensure the actual numerical value is displayed, not `<font color="red">-0.17</font>`. The color should be applied to the text itself.

---

## Section-Specific Directives:

### 1. Executive Summary (Page 3)

*   **Content Justification:** Ensure all bullet points and paragraphs are fully justified.

### 2. Market Overview (Page 4)

*   **Market Indices Order:**
    *   Reorder the "Key Market Indices Performance" table and the "MAJOR INDICES PERFORMANCE" table.
    *   Group indices by region: Asia first, then Euro Area + UK, then Americas.
    *   Add Indian market indices (e.g., Nifty 50, Sensex) by fetching data from a public API, as they are not available on MT5. Integrate them into the "Asia" grouping.

*   **Major Indices Performance Table:**
    *   Remove the "Description" column.
    *   Rename CFD symbols to their common market names (e.g., "US500Roll" -> "S&P 500", "FRA40Roll" -> "CAC 40").
    *   Add a smaller, italicized line beneath the market name to show the CFD symbol (e.g., "CAC 40 *FRA40Roll*").
    *   Ensure "24h Change" and "24h Change %" values are correctly calculated using current price and the corresponding 24-hour prior price from MT5 data, considering timezone differences between local laptop time and MT5 server time. (Refer to the `data-mt5.py` script for data fetching logic).

### 3. Currency Markets (Page 4)

*   **Formatting:** Apply the same formatting rules as for "Major Indices Performance" to the "Currency Markets" table.
    *   Remove `<font color="...">` tags and apply color directly to the text for % change.
    *   Calculate "24h Change" and "24h Change %" accurately.

### 4. Commodities (Page 5)

*   **Formatting:** Apply the same formatting rules as for "Major Indices Performance" to the "Commodities" table.
    *   Remove `<font color="...">` tags and apply color directly to the text for % change.
    *   Calculate "24h Change" and "24h Change %" accurately.

### 5. Bonds/ETFs (Page 5)

*   **Description:** Update the "Description" column to include a concise explanation of each bond/ETF (e.g., "TLT ETF/Bond" -> "TLT (20+ Year US Treasury Bond ETF)"). The tool should research and provide appropriate descriptions where currently vague.
*   **Formatting:** Apply the same formatting rules as for "Major Indices Performance" to the "Bonds/ETFs" table.
    *   Remove `<font color="...">` tags and apply color directly to the text for % change.
    *   Calculate "24h Change" and "24h Change %" accurately.

### 6. Market Volatility (Page 5-6)

*   **VIX Description:** Add a description for the VIX index in the "Volatility Index" table.

### 7. Top Market Movers (Page 6)

*   **Color Coding:** Apply color coding to the "24h Change %" column (green for positive, red for negative).

### 8. Economic Calendar (Page 6)

*   **Data Source:** Integrate economic calendar data from the provided CSV file: `/Users/pawan/CLI-Finance-Terminal/economic-calendar/ECONOMIC_CALENDAR_DATA.csv`.
*   **Presentation:** Display the relevant economic events in a clear, formatted table, showing `DateTime`, `EventID`, `Name`, `Country`, `Currency`, `Impact`, `Actual`, `Forecast`, `Previous`.

### 9. Technical Charts (Page 7-12)

*   **Chart Titles:**
    *   Remove the chart names from being overlaid on the charts themselves.
    *   Rename chart titles to be more user-friendly (e.g., "S&P 500 Technical Analysis" instead of "US500Roll Technical Analysis").
    *   Ensure all chart titles follow this convention.

*   **Color Scheme:** Update the color scheme of all charts to use professional and aesthetically pleasing colors. (e.g., muted blues, greens, grays for lines and bars; avoid overly bright or clashing colors).
*   **Font:** All text within the charts (axis labels, legends, numbers) should use "Century Gothic" font.
*   **New Chart:** Add a VIX chart.
*   **Chart Order:** Order the charts logically:
    1.  VIX Chart
    2.  Major Global Indices (Asia, Europe+UK, Americas) in the order specified previously.
    3.  Major Currencies
    4.  Major Commodities
    5.  Major Bonds/ETFs

---

## Workflow Tracking:

*   **Stage 1: Data Acquisition & Pre-processing (Completed)**
    *   `data-mt5.py` script has run.
    *   Economic calendar CSV is available.
    *   Initial OCR on report pages is complete.

*   **Stage 2: Global Formatting (To Do)**
    *   Apply Century Gothic font.
    *   Enforce lowercase rule.
    *   Update report title.
    *   Remove market status line.
    *   Justify text content.

*   **Stage 3: Section-Specific Content & Formatting (To Do)**
    *   Update Executive Summary justification.
    *   Reorder and rename Market Overview tables, add Indian indices, update 24h change.
    *   Update Currency Markets formatting and 24h change.
    *   Update Commodities formatting and 24h change.
    *   Update Bonds/ETFs descriptions, formatting, and 24h change.
    *   Add VIX description.
    *   Color-code Top Market Movers % change.
    *   Integrate Economic Calendar data.

*   **Stage 4: Chart Generation & Refinement (To Do)**
    *   Update chart titles.
    *   Apply professional color scheme to all charts.
    *   Set Century Gothic font for all chart text.
    *   Add VIX chart.
    
    *   Reorder all technical charts.

---

**Instructions for CLI Tool:**

Process the report page by page, applying the directives above. After completing a logical block of tasks (e.g., all global formatting, or all market overview updates), update the "Current Task Status" and "Last Completed Task" in this `meta-prompt.md` to reflect progress. If an error occurs, update "Errors/Notes from Last Run" with details.