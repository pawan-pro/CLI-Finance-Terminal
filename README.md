# Finance Terminal

A CLI for finance.

## Features

- Real-time quotes for stocks, indices, currencies, and commodities
- Charting capabilities for technical analysis
- Financial news aggregation
- Economic calendar with important events
- Market status monitoring
- Sector performance tracking
- **Daily investment reports** with comprehensive market analysis

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd CLI-Finance-Terminal
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your environment variables in a `.env` file:
   ```
   ALPHA_VANTAGE_API_KEY=your_api_key_here
   ```

## Usage

Run the CLI with:
```
python -m src.cli.main
```

Or use the available commands:
- `dashboard` - Show a comprehensive daily market report (default)
- `quote SYMBOL` - Get a quote for a specific symbol
- `chart SYMBOL` - Display a chart for a symbol
- `news [SYMBOL]` - Get financial news (optionally for a specific symbol)
- `calendar` - Show upcoming economic events
- `status` - Check market status
- `sector` - Show sector performance
- `report` - Generate a daily investment report
- `config` - Manage configuration settings

## Daily Investment Report

The daily investment report provides a comprehensive analysis of the markets including:
- Market status and key indices performance
- Currency pairs movements
- Commodity prices
- Market volatility metrics (VIX-like indices)
- Top gainers and losers
- Economic calendar events
- Technical charts for key assets

Generate a standard report with:
```
python -m src.cli.main report
```

Generate an institutional-grade report with:
```
python -m src.cli.main report --institutional
```

## MT5 Integration

This tool integrates with MetaTrader 5 (MT5) terminal for real-time market data. 
The tool supports both Windows native MT5 and Wine-based MT5 on macOS/Linux.

For Wine-based setup on macOS/Linux, see [MT5_WINE_SETUP.md](MT5_WINE_SETUP.md) for detailed instructions.

Ensure MT5 is installed and running before using the report feature. The tool will automatically
detect and use your MT5 setup, falling back to mock data if MT5 is not available.

To generate a daily investment report with real market data from MT5 through
Wine:

```bash
#venv
source .venv/bin/activate

# Generate standard report with real MT5 data from Wine
python -m src.cli.main report --format pdf --wine-mt5

# Generate institutional-grade report with real MT5 data from Wine
python -m src.cli.main report --institutional --format pdf --wine-mt5

# Specify custom save directory
python -m src.cli.main report --format pdf --wine-mt5 --save-dir ./my_reports
```
