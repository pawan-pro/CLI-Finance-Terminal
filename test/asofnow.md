✦ Now I understand the core issue! The problem is:

   1. No historical data is being fetched: The fetch_historical_data method is
      returning empty DataFrames (0 data points for all symbols).

   2. The symbol info is being found: The get_symbol_info method works fine
      (as seen in the first test), but the fetch_historical_data method is
      failing to fetch historical price data.

   3. The Wine MT5 connector is being used: As seen by the "Using Wine MT5
      connector" logs, but it's falling back to mock because the Wine MT5 may
      not be working properly.

  The issue is in the fetch_historical_data method when using the Wine MT5
  connector. The historical data fetching is the key issue preventing chart
  generation. The error shows the system is falling back to mock MT5, which
  means the Wine MT5 fetch is failing.