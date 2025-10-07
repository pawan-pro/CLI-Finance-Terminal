# CLI Finance Terminal

A comprehensive command-line interface for financial market analysis and reporting. This tool generates daily investment reports with institutional-grade formatting and analytics using Alpha Vantage API data.

## Features

- Real-time market data from Alpha Vantage API
- Daily investment reports (text and PDF format)
- Professional market analysis with charts
- Economic calendar integration
- Financial news aggregation
- Top market movers identification
- Institutional-grade risk metrics

## Prerequisites

- Python 3.8+
- Alpha Vantage API Key (free tier available - 25 requests per day)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd CLI-Finance-Terminal
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Setup

### Get Alpha Vantage API Key

1. Go to [Alpha Vantage](https://www.alphavantage.co/support/#api-key) and sign up for a free account
2. Check your email for the API key or find it in your account dashboard
3. Copy your API key

### Configuration

1. Create a `.env` file in the project root:
```bash
cp .env.example .env
```

2. Edit the `.env` file to add your Alpha Vantage API key:
```bash
ALPHAVANTAGE_API_KEY=your_actual_alpha_vantage_api_key_here
```

**Note:** If you don't have an Alpha Vantage API key, the system will still work but will rely on CSV file data for charts and fallback mechanisms. For full real-time functionality, you'll need a valid API key. Note that the free tier allows 25 requests per day, so use the API judiciously.

### Testing without API Key

You can test the system functionality without an Alpha Vantage API key by running:
```bash
python -m src.cli.main report --format pdf
```

The system will generate reports using CSV data files (for charts) and fallback functionality. You'll see 401 errors for API calls, which is expected without a valid key.

## Usage

### Generate Daily Report

```bash
python -m src.cli.main report --format pdf
```

Available options:
- `--format`: Output format (txt or pdf) [default: pdf]
- `--save-dir`: Directory to save the report [default: ./reports]
- `--institutional`: Generate institutional-grade report
- `--verbose`: Enable verbose output

### Other Commands

```bash
# View dashboard
python -m src.cli.main dashboard

# Get quote for a symbol
python -m src.cli.main quote AAPL

# Get financial news
python -m src.cli.main news

# Get economic calendar
python -m src.cli.main calendar

# View market status
python -m src.cli.main status
```

## Symbol Mapping

The system uses internal symbols that are mapped to Alpha Vantage-compatible symbols. Some examples:

- US500Roll → SPX (S&P 500)
- US30Roll → DJI (Dow Jones)
- EURUSD → EURUSD (EUR/USD)
- XAUUSD → XAU (Gold)
- BTCUSD.lv → BTC-USD (Bitcoin)

See `src/config/symbol_map.py` for the complete mapping.

## Directory Structure

```
CLI-Finance-Terminal/
├── src/
│   ├── analysis/           # Report generation and analytics
│   ├── cli/               # Command-line interface components
│   ├── config/            # Configuration settings
│   ├── data/              # Data fetching and providers
│   └── __init__.py
├── reports/               # Generated reports output
├── LLM/                   # LLM integration components
├── config/                # Configuration files
└── requirements.txt       # Dependencies
```

## Data Sources

- Market data: Alpha Vantage API
- Financial news: API-based (with fallbacks)
- Economic calendar: API-based or CSV fallback

## Output Formats

- **PDF**: Professional institutional-grade reports with cover pages, TOC, and styling
- **Text**: Simple text format for quick review
- **Charts**: Technical analysis charts in various formats

## API Rate Limits

The Alpha Vantage free tier provides 25 requests per day. The system uses caching to minimize API calls and maximize the efficiency of your daily allowance. To stay within limits:
- Avoid repeatedly running the report generation in quick succession
- Be mindful when testing individual symbol queries
- The system includes 12-second delays between API requests to stay well under the 5-calls-per-minute limit

## Troubleshooting

- If reports fail to generate, ensure your Alpha Vantage API key is valid and has sufficient daily quota
- Check the logs in your terminal for error messages
- Verify that all dependencies are properly installed
- If you see rate limit errors, wait until the next day for your quota to reset

## License

This project is licensed under the terms specified in the LICENSE file.