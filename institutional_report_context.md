# CLI Finance Terminal - Institutional Report Generation Context

## Overview
The CLI-Finance-Terminal is a sophisticated financial reporting system that generates institutional-grade daily investment reports using MT5 (MetaTrader 5) data feeds. The institutional report provides comprehensive market analysis with enhanced institutional-grade analytics, deeper risk metrics, and detailed attribution modeling.

## Project Structure
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

## Institutional Report Generation Architecture

### Core Components

#### 1. Daily Report Generator (`src/analysis/daily_report.py`)
- **Primary Responsibility**: Institutional report orchestration
- **Key Functions**:
  - Coordinates data fetching from MT5
  - Generates all institutional report sections with enhanced analytics
  - Handles both text and PDF format generation
  - Manages chart generation for institutional reports
  - Calls `_generate_institutional_pdf_report` method for PDF generation when `institutional_grade=True`
  - Implements comprehensive risk metrics calculation

#### 2. Enhanced Institutional PDF Generator (`src/analysis/enhanced_institutional_pdf.py`)
- **Primary Responsibility**: Advanced institutional PDF formatting and styling
- **Key Functions**:
  - Applies institutional-grade styling with enhanced color schemes
  - Formats each report section with deeper analysis
  - Generates cover pages, TOC, and disclaimers
  - Handles table and chart integration for institutional reports
  - Implements enhanced market regime analysis
  - Creates institutional commentary boxes with conviction levels

#### 3. Chart Generator (`src/analysis/charts.py`)
- **Primary Responsibility**: Technical analysis chart generation for institutional reports
- **Key Functions**:
  - Generates ASCII charts for terminal display
  - Creates matplotlib price charts
  - Produces professional candlestick charts with advanced technical indicators (SMA, RSI)
  - Includes volume and RSI subplots
  - Supports dashboard generation with multiple chart types
  - Integrates with institutional report generation in `daily_report.py`

#### 4. Data Provider (`src/data/providers/mt5_data.py`)
- **Primary Responsibility**: MT5 data fetching and caching for institutional analysis
- **Key Functions**:
  - Establishes MT5 connections (real, Wine or mock)
  - Fetches real-time market data
  - Handles extended historical data requests (90+ days for risk metrics)
  - Implements caching mechanisms
  - Supports Wine MT5 connector for cross-platform compatibility

## Institutional Report Sections Breakdown

### 1. Executive Summary
- **Scripts**: `src/analysis/daily_report.py`, `src/analysis/llm_integration.py`
- **Data Source**: Market data from MT5 combined with LLM analysis
- **Functionality**:
  - Uses LLM to generate AI-powered institutional insights
  - Analyzes major market movements with attribution
  - Creates concise bullet-point summary with institutional commentary
  - Includes key market insight, biggest risk, conviction trade and portfolio implication boxes
  - Includes fallback mechanisms if LLM fails

### 2. Market Overview
- **Scripts**: `src/analysis/daily_report.py`, `src/analysis/enhanced_institutional_pdf.py`
- **Data Source**: MT5 market status and key indices data
- **Functionality**:
  - Provides current market status
  - Shows market opening/closing information
  - Includes enhanced institutional commentary with market sentiment analysis
  - Displays key indices performance with confidence levels
  - Provides institutional market commentary with directional bias

### 3. Major Indices Performance (Price & 24H Change)
- **Scripts**: `src/analysis/daily_report.py`, `src/analysis/enhanced_institutional_pdf.py`
- **Symbols**: `US500Roll`, `US30Roll`, `UT100Roll`, `DE40Roll`, `UK100Roll`
- **Functionality**:
  - Fetches current prices for major indices
  - Calculates 24-hour percentage changes
  - Formats data in professional tables with color coding
  - Applies specific formatting rules for different index types
  - Provides institutional commentary on index movements

### 4. Currency Markets
- **Scripts**: `src/analysis/daily_report.py`, `src/analysis/enhanced_institutional_pdf.py`
- **Symbols**: `EURUSD`, `GBPUSD`, `USDJPY`, `USDCHF`, `AUDUSD`
- **Functionality**:
  - Retrieves major currency pair data
  - Calculates 24-hour percentage changes
  - Applies 4-decimal formatting for currencies
  - Integrates into professional tables with enhanced styling
  - Provides institutional analysis of currency movements

### 5. Commodities
- **Scripts**: `src/analysis/daily_report.py`, `src/analysis/enhanced_institutional_pdf.py`
- **Symbols**: `XAUUSD`, `XAGUSD`, `USOIL`, `UKOIL`
- **Functionality**:
  - Fetches commodity market data
  - Calculates percentage changes
  - Applies specific formatting (e.g., 2 decimals for gold)
  - Generates professional commodity tables with institutional commentary
  - Provides demand-supply analysis and safe-haven flow insights

### 6. Top Market Movers
- **Scripts**: `src/analysis/daily_report.py`, `src/analysis/enhanced_top_movers.py`, `src/analysis/enhanced_institutional_pdf.py`
- **Functionality**:
  - Identifies top gainers and losers based on 24-hour changes with enhanced attribution
  - Provides detailed attribution analysis using `EnhancedTopMoversAnalyzer`
  - Includes volume, confidence metrics and attribution factors
  - Generates institutional commentary on move attribution with conviction levels
  - Provides fundamental impact, technical signals and cross-asset impact analysis

### 7. Market Regime Analysis
- **Scripts**: `src/analysis/daily_report.py`, `src/analysis/enhanced_institutional_pdf.py`
- **Functionality**:
  - Analyzes current market regime (Risk-On, Risk-Off, High Volatility, Range-Bound)
  - Calculates regime confidence levels
  - Provides institutional commentary on market behavior
  - Offers tactical positioning recommendations based on regime

### 8. Economic Calendar
- **Scripts**: `src/analysis/daily_report.py`, `src/analysis/enhanced_institutional_pdf.py`
- **Data Source**: CSV files in economic-calendar directory
- **Functionality**:
  - Filters for today's events
  - Shows only medium and high importance events
  - Provides timezone conversion (IST)
  - Displays actual vs forecast vs previous values
  - Special handling for CFTC and Japanese events
  - Includes institutional analysis of economic impact

### 9. Risk Metrics
- **Scripts**: `src/analysis/daily_report.py`, `src/analysis/enhanced_institutional_pdf.py`
- **Functionality**:
  - Calculates Sharpe Ratio with institutional methodology
  - Computes Sortino Ratio for downside risk-adjusted returns
  - Determines Maximum Drawdown
  - Computes Value at Risk (95% and 99%)
  - Calculates Conditional Value at Risk
  - Measures market Beta and correlation metrics
  - Provides volatility metrics and stress indicators

## Key Data Fetching Components

### LLM Integration (`src/analysis/llm_integration.py`)
- **Purpose**: AI-powered executive summary generation for institutional reports
- **Provider**: Krutrim's Phi-4-reasoning-plus model
- **Functionality**:
  - Formats market data for LLM processing with institutional focus
  - Creates structured prompts for advanced analysis
  - Extracts and formats institutional-level bullet-point summaries
  - Implements fallback mechanisms

### Chart Generator (`src/analysis/charts.py`)
- **Purpose**: Technical analysis chart generation for institutional reports
- **Functionality**:
  - Generates ASCII charts for terminal display
  - Creates matplotlib price charts
  - Produces professional candlestick charts with advanced technical indicators (SMA, RSI)
  - Includes volume and RSI subplots for comprehensive analysis
  - Supports dashboard generation with multiple chart types
  - Integrates with institutional report generation in `daily_report.py`

### Enhanced Top Movers (`src/analysis/enhanced_top_movers.py`)
- **Purpose**: Advanced institutional top movers analysis with detailed attribution
- **Functionality**:
  - Identifies significant market moves with comprehensive attribution analysis
  - Provides detailed attribution breakdown (economic data, technical factors, fundamentals, etc.)
  - Calculates statistical confidence levels
  - Generates fundamental and technical commentary with conviction levels
  - Implements cross-asset impact analysis

### Enhanced Institutional Analytics (`src/analysis/institutional_analytics.py`)
- **Purpose**: Advanced institutional market analysis
- **Functionality**:
  - Provides enhanced market analysis tools
  - Implements sophisticated statistical models
  - Offers institutional-level market insights

### Enhanced Institutional Calendar Analysis (`src/analysis/institutional_calendar.py`)
- **Purpose**: Advanced economic calendar analysis for institutional reports
- **Functionality**:
  - Provides enhanced calendar event analysis
  - Implements impact assessment modeling
  - Offers institutional commentary on economic events

### Volatility Calculator (`src/analysis/volatility.py`)
- **Purpose**: Volatility analysis for institutional risk metrics
- **Functionality**:
  - Calculates advanced ATR and volatility measures
  - Provides enhanced volatility summary tables
  - Supports comprehensive risk metric calculations
  - Implements institutional-grade volatility modeling

## Configuration and Setup

### MT5 Integration
- Supports both real MT5 and mock data environments
- Implements Wine MT5 connector for cross-platform compatibility
- Includes fallback mechanisms when MT5 is unavailable
- Command: `python -m src.cli.main report --institutional --format pdf --wine-mt5`

### Historical Data Fetching
- Retrieves 90+ days of historical data for comprehensive risk metrics
- Calculates advanced risk metrics based on extended timeframes
- Implements enhanced correlation analysis

### Caching Layer
- Implemented through `cache_manager` in `src/data/cache_manager.py`
- Reduces API calls and improves performance
- Applies TTL (time-to-live) for fresh data
- Optimized for institutional report data requirements

## Output Formats
- **PDF**: Professional institutional-grade reports with enhanced cover pages, detailed TOC, advanced styling, and institutional commentary boxes
- **Text**: Simple text format for quick review
- **Charts**: Technical analysis charts in various formats including:
  - ASCII charts for terminal display
  - Matplotlib line charts showing price trends
  - Professional candlestick charts with advanced technical indicators (SMA, RSI)
  - Volume and RSI subplots for comprehensive analysis
  - Dashboard charts combining multiple chart types with institutional focus

## Key Dependencies
- `MetaTrader5` or mock implementation
- `pandas` for data manipulation
- `matplotlib` for chart generation
- `plotille` for ASCII charts
- `pandas_ta` for technical indicators
- `reportlab` for PDF generation
- `requests` for API calls
- `NewsAPI` for financial news feeds
- `LLM` integration for AI summaries
- `numpy` for numerical computations
- `scipy` for scientific computing
- `scikit-learn` for advanced analytics

## Development Notes
- The system can run with mock MT5 data for development
- All data fetching is cached with configurable TTL
- Error handling includes graceful fallbacks for all external services
- Professional styling follows institutional investment bank standards
- Institutional reports use the `_generate_institutional_pdf_report` method in `daily_report.py`
- Enhanced risk metrics require extended historical data (90+ days)
- Requires more computational resources due to enhanced analytics