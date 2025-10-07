# Currency Formatting Fix in Top Movers Section

## Issue
Currency symbols in the top movers section were showing prices with excessive decimal places, affecting readability and professional presentation.

## Solution Implemented
- Modified the top movers display to use symbol-specific formatting
- Added logic to detect currency symbols and format with 4 decimal places
- For other assets, maintained clean formatting (2 decimals for indices, 3 for precious metals, etc.)

## Code Changes
- Updated formatting logic in src/analysis/enhanced_top_movers.py
- Added symbol detection to distinguish currencies from other asset types
- Ensured consistent formatting across all report sections

## Testing
Verified by generating a PDF report with Alpha Vantage data. The top movers section now correctly displays currency prices with appropriate decimal places while maintaining integer formatting for indices.