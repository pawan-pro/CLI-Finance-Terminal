High-Priority Critical Bugs

ModuleNotFoundError: No module named 'MetaTrader5' in Wine Environment: The logs show that the Python script being executed inside Wine is missing the MetaTrader5 library. This is the root cause for all +0.00% change calculations failing. The script cannot fetch historical data and defaults to zero.

Data Fetching Timeouts for US Indices: The logs show a 60-second timeout when trying to fetch data for US30Roll. This is why US30Roll and likely US500Roll are completely missing from the report tables and charts.
Data & Calculation Fixes

Fix 24H % Change Calculation: This is directly caused by the ModuleNotFoundError. Once the library is installed in the Wine environment, this calculation should work. Verify across all tables (Indices, Currencies, Commodities).

Restore Missing US500 & US30 Data: This is directly caused by the timeout error. Investigate the connector script to optimize it or increase the timeout duration.
Formatting & Display Issues

Top Movers Currency Formatting: There is a major formatting regression. Currency prices in the "Top Movers" table are being rounded to whole numbers (e.g., EURUSD is 1, USDCHF is 1). These must be displayed with their proper decimal precision.

Executive Summary & Index Formatting: Index values are still showing decimals in some places. Ensure all index values (UT100Roll, DE40Roll, etc.) are consistently formatted as integers throughout the report.
Chart Enhancements

Fix Chart Appearance: Address the stretched/compressed look of the candlestick charts.

Improve Chart X-Axis: The x-axis should show time intervals relevant to the trading day (e.g., HH:MM), not just the date.
Completed Tasks

Economic Calendar Integration: The calendar is now successfully reading and displaying events from the CSV file. This is a major success.

Chart Type Upgrade: Charts have been successfully converted to the candlestick format.

Integer Values for Indices: Partially complete, but needs consistent application.

Remove Spread Values: Completed.

Gold Value Issue (XAUUSD): The price is now being fetched correctly.