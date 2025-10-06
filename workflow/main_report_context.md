# CLI Finance Terminal - Main Report Generation Context

## Overview
The CLI-Finance-Terminal is a sophisticated financial reporting system that generates daily investment reports using MT5 (MetaTrader 5) data feeds. The main report provides comprehensive market analysis across multiple asset classes with professional-grade reporting, focusing on standard market data without the enhanced institutional analytics.

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

## Main Report Generation Architecture

### Core Components

#### 1. Daily Report Generator (`src/analysis/daily_report.py`)
- **Primary Responsibility**: Main report orchestration for standard reports
- **Key Functions**:
  - Coordinates data fetching from MT5
  - Generates all standard report sections
  - Handles both text and PDF format generation
  - Manages chart generation for main report
  - Calls `_generate_pdf_report` method for PDF generation
  - Processes reports when `institutional_grade=False`

#### 2. Professional PDF Generator (`src/analysis/professional_pdf_report.py`)
- **Primary Responsibility**: Professional PDF formatting and styling for main reports
- **Key Functions**:
  - Applies institutional-grade styling
  - Formats each report section
  - Generates cover pages, TOC, and disclaimers
  - Handles table and chart integration for main reports
  - Implements standard market analysis presentation

#### 3. Chart Generator (`src/analysis/charts.py`)
- **Primary Responsibility**: Technical analysis chart generation for main reports
- **Key Functions**:
  - Generates ASCII charts for terminal display
  - Creates matplotlib price charts
  - Produces professional candlestick charts with technical indicators (SMA, RSI)
  - Includes volume and RSI subplots
  - Supports dashboard generation with multiple chart types

#### 4. Data Provider (`src/data/providers/mt5_data.py`)
- **Primary Responsibility**: MT5 data fetching and caching
- **Key Functions**:
  - Establishes MT5 connections (real, Wine or mock)
  - Fetches real-time market data
  - Handles historical data requests
  - Implements caching mechanisms
  - Supports Wine MT5 connector for cross-platform compatibility

## Main Report Sections Breakdown

### 1. Executive Summary
- **Scripts**: `src/analysis/daily_report.py`, `src/analysis/llm_integration.py`
- **Data Source**: Market data from MT5 combined with LLM analysis
- **Functionality**:
  - Uses LLM to generate AI-powered insights
  - Analyzes major market movements
  - Creates concise bullet-point summary
  - Includes fallback mechanisms if LLM fails

### 2. Market Overview
- **Scripts**: `src/analysis/daily_report.py`, `src/analysis/professional_pdf_report.py`
- **Data Source**: MT5 market status and key indices data
- **Functionality**:
  - Provides current market status
  - Shows market opening/closing information
  - Includes standard commentary
  - Displays key indices performance

### 3. Major Indices Performance (Price & 24H Change)
- **Scripts**: `src/analysis/daily_report.py`, `src/analysis/professional_pdf_report.py`
- **Symbols**: `US500Roll`, `US30Roll`, `UT100Roll`, `DE40Roll`, `UK100Roll`
- **Functionality**:
  - Fetches current prices for major indices
  - Calculates 24-hour percentage changes
  - Formats data in professional tables
  - Applies specific formatting rules for different index types

### 4. Currency Markets
- **Scripts**: `src/analysis/daily_report.py`, `src/analysis/professional_pdf_report.py`
- **Symbols**: `EURUSD`, `GBPUSD`, `USDJPY`, `USDCHF`, `AUDUSD`
- **Functionality**:
  - Retrieves major currency pair data
  - Calculates 24-hour percentage changes
  - Applies 4-decimal formatting for currencies
  - Integrates into professional tables

### 5. Commodities
- **Scripts**: `src/analysis/daily_report.py`, `src/analysis/professional_pdf_report.py`
- **Symbols**: `XAUUSD`, `XAGUSD`, `USOIL`, `UKOIL`
- **Functionality**:
  - Fetches commodity market data
  - Calculates percentage changes
  - Applies specific formatting (e.g., 2 decimals for gold)
  - Generates professional commodity tables

### 6. Top Market Movers
- **Scripts**: `src/analysis/daily_report.py`, `src/analysis/enhanced_top_movers.py`, `src/analysis/professional_pdf_report.py`
- **Functionality**:
  - Identifies top gainers and losers based on 24-hour changes
  - Provides basic attribution analysis
  - Includes volume metrics
  - Generates commentary on move attribution

### 7. Financial Market News
- **Scripts**: `src/analysis/daily_report.py`, `src/data/providers/news.py`
- **Data Source**: NewsAPI integration
- **Functionality**:
  - Fetches financial news headlines
  - Formats news in professional section
  - Includes source and publication timestamps
  - Implements caching for performance

### 8. Economic Calendar
- **Scripts**: `src/analysis/daily_report.py`, `src/analysis/professional_pdf_report.py`
- **Data Source**: CSV files in economic-calendar directory
- **Functionality**:
  - Filters for today's events
  - Shows only medium and high importance events
  - Provides timezone conversion (IST)
  - Displays actual vs forecast vs previous values
  - Special handling for CFTC and Japanese events

## Key Data Fetching Components

### LLM Integration (`src/analysis/llm_integration.py`)
- **Purpose**: AI-powered executive summary generation for main reports
- **Provider**: Krutrim's Phi-4-reasoning-plus model
- **Functionality**:
  - Formats market data for LLM processing
  - Creates structured prompts for analysis
  - Extracts and formats bullet-point summaries
  - Implements fallback mechanisms

### Chart Generator (`src/analysis/charts.py`)
- **Purpose**: Technical analysis chart generation
- **Functionality**:
  - Generates ASCII charts for terminal display
  - Creates matplotlib price charts
  - Produces professional candlestick charts with technical indicators (SMA, RSI)
  - Includes volume and RSI subplots for comprehensive analysis
  - Supports dashboard generation with multiple chart types
  - Integrates with main report generation in `daily_report.py`

### Enhanced Top Movers (`src/analysis/enhanced_top_movers.py`)
- **Purpose**: Standard top movers analysis
- **Functionality**:
  - Identifies significant market moves
  - Provides basic attribution analysis
  - Generates fundamental and technical commentary

### Volatility Calculator (`src/analysis/volatility.py`)
- **Purpose**: Volatility analysis for risk metrics
- **Functionality**:
  - Calculates ATR and volatility measures
  - Provides volatility summary tables
  - Supports basic risk metric calculations

## Configuration and Setup

### MT5 Integration
- Supports both real MT5 and mock data environments
- Implements Wine MT5 connector for cross-platform compatibility
- Includes fallback mechanisms when MT5 is unavailable
- Command: `python -m src.cli.main report --format pdf --wine-mt5`

### Caching Layer
- Implemented through `cache_manager` in `src/data/cache_manager.py`
- Reduces API calls and improves performance
- Applies TTL (time-to-live) for fresh data

## Output Formats
- **PDF**: Professional reports with cover pages, TOC, and styling
- **Text**: Simple text format for quick review
- **Charts**: Technical analysis charts in various formats including:
  - ASCII charts for terminal display
  - Matplotlib line charts showing price trends
  - Professional candlestick charts with technical indicators (SMA, RSI)
  - Volume and RSI subplots for comprehensive analysis
  - Dashboard charts combining multiple chart types

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

## Development Notes
- The system can run with mock MT5 data for development
- All data fetching is cached with configurable TTL
- Error handling includes graceful fallbacks for all external services
- Professional styling follows institutional investment bank standards
- Main reports use the `_generate_pdf_report` method in `daily_report.py`