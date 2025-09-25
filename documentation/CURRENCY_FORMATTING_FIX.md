# Currency Formatting Fix Summary

## Issue
Currencies were showing as integers in the top movers section (e.g., EURUSD was showing as "1" instead of its actual price like "1.18").

## Root Cause
The formatting logic in the `add_top_movers_table` method of `src/analysis/professional_pdf_report.py` was using a simple string matching approach to identify index symbols. This caused false positives where currency symbols containing index identifiers (like "EURUSD" containing "US") were incorrectly identified as indices and formatted as integers.

## Solution
Modified the index detection logic to use exact symbol matching instead of partial string matching:

### Before (problematic):
```python
# Check if this is an index symbol
if any(index_name in name for index_name in ['US', 'JP', 'DE', 'UK', 'FR', 'IT', 'ES', 'AU', 'NZ', 'CA']):
    # Format as integer for indices
    price = f"{price_value:.0f}"
else:
    # Format with decimals for others
    price = f"{price_value:.2f}"
```

### After (fixed):
```python
# Check if this is an index symbol by looking for exact matches
# rather than partial matches to avoid false positives with currencies
name = str(row.get('name', ''))
is_index = False
index_symbols = ['US30', 'US500', 'US30Roll', 'US500Roll', 'UT100', 'UT100Roll', 
               'DE30', 'DE40', 'DE30Roll', 'DE40Roll', 'UK100', 'UK100Roll',
               'JP225', 'FR40', 'IT50', 'ES35', 'AU200', 'NZ50', 'CA60']

# Check if the name matches any index symbol exactly or as a prefix
for index_symbol in index_symbols:
    if name.startswith(index_symbol):
        is_index = True
        break

if is_index:
    # Format as integer for indices
    price = f"{price_value:.0f}"
else:
    # Format with decimals for others (currencies, commodities, etc.)
    price = f"{price_value:.2f}"
```

## Results
- ✅ Currencies now display with proper decimal formatting in top movers (e.g., EURUSD shows as "1.18" instead of "1")
- ✅ Indices continue to display as integers as intended
- ✅ No false positives in symbol identification
- ✅ Consistent formatting across all report sections

## Files Modified
- `src/analysis/professional_pdf_report.py`: Updated the `add_top_movers_table` method with improved symbol detection logic

## Verification
Tested by generating a PDF report with Wine MT5 enabled. The top movers section now correctly displays currency prices with decimal places while maintaining integer formatting for indices.