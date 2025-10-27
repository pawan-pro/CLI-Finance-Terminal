import pickle
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, time
import pytz
import plotly.graph_objects as go
import plotly.io as pio
import os

# --- Symbol to Descriptive Name Mapping ---
SYMBOL_TO_NAME_MAP = {
    # Major Indices
    'SPY': 'S&P 500', 'QQQ': 'Nasdaq 100', 'DIA': 'Dow Jones Industrial Average', 'IWM': 'Russell 2000',
    # International Indices
    'EWU': 'United Kingdom (FTSE)', 'EWJ': 'Japan (Nikkei)', 'FEZ': 'Euro Stoxx 50',
    'DAX': 'Germany (DAX)', 'EEM': 'Emerging Markets', 'INDA': 'India (MSCI India)',
    'MCHI': 'China (MSCI China)', 'EWG': 'Germany Equity', 'EWQ': 'France',
    'EWS': 'Singapore', 'EWA': 'Australia',
    # Sector ETFs
    'XLE': 'Energy Sector', 'XLF': 'Financials Sector', 'XLU': 'Utilities Sector', 'XLI': 'Industrials Sector',
    'XLK': 'Technology Sector', 'XLV': 'Health Care Sector', 'XLY': 'Consumer Discretionary Sector',
    'XLP': 'Consumer Staples Sector', 'XLB': 'Materials Sector', 'XLRE': 'Real Estate Sector',
    'XLC': 'Communication Services Sector',
    # VIX
    'VXX': 'VIX Short-Term Futures ETN', 'UVXY': 'UVXY',
    # Commodities (Examples)
    'GLD': 'Gold', 'SLV': 'Silver', 'USO': 'Crude Oil',
    # Bonds (Examples)
    'TLT': '20+ Year Treasury Bond ETF',
    # MT5 Symbols (Forex pairs)
    'EURUSDm': 'Euro vs US Dollar (MT5)', 'GBPUSDm': 'British Pound vs US Dollar (MT5)', 
    'USDJPYm': 'US Dollar vs Japanese Yen (MT5)', 'AUDUSDm': 'Australian Dollar vs US Dollar (MT5)',
    'USDCADm': 'US Dollar vs Canadian Dollar (MT5)', 'USDCHFm': 'US Dollar vs Swiss Franc (MT5)',
    'USDSEKm': 'US Dollar vs Swedish Krona (MT5)',
    'XAUUSDm': 'Gold vs US Dollar (MT5)',
    'XAGUSDm': 'Silver vs US Dollar (MT5)',
    'USOILm': 'Crude Oil WTI (MT5)',
    'XNGUSDm': 'Natural Gas vs US Dollar (MT5)',
    'BTCUSDm': 'Bitcoin vs US Dollar (MT5)', 'ETHUSDm': 'Ethereum vs US Dollar (MT5)',
    'XRPUSDm': 'Ripple vs US Dollar (MT5)', 'ADAUSDm': 'Cardano vs US Dollar (MT5)',
    'LTCUSDm': 'Litecoin vs US Dollar (MT5)', 'SOLUSDm': 'Solana vs US Dollar (MT5)',
    # MT5 Indices
    'US500m': 'US 500 Index (MT5)', 'US30m': 'US 30 Index (MT5)', 'USTECm': 'US Tech 100 Index (MT5)',
    'DE30m': 'Germany 30 Index (MT5)', 'FR40m': 'France 40 Index (MT5)', 'UK100m': 'UK 100 Index (MT5)',
    'STOXX50m': 'Euro Stoxx 50 Index (MT5)', 'AUS200m': 'Australia 200 Index (MT5)', 
    'JP225m': 'Japan 225 Index (MT5)', 'HK50m': 'Hong Kong 50 Index (MT5)', 'IN50m': 'India 50 Index (MT5)',
    # MT5 Stocks
    'AAPLm': 'Apple Inc. (MT5)', 'MSFTm': 'Microsoft Corp. (MT5)', 'GOOGLm': 'Alphabet Inc. (MT5)',
    'AMZNm': 'Amazon.com Inc. (MT5)', 'NVDAm': 'NVIDIA Corp. (MT5)', 'FBm': 'Meta Platforms Inc. (MT5)',
    'JPMm': 'JPMorgan Chase & Co. (MT5)', 'BACm': 'Bank of America Corp. (MT5)', 
    'JNJm': 'Johnson & Johnson (MT5)', 'PFEm': 'Pfizer Inc. (MT5)', 'XOMm': 'Exxon Mobil Corp. (MT5)',
    'TSLAm': 'Tesla Inc. (MT5)', 'MCDm': 'McDonald\'s Corp. (MT5)'
}


# --- Helper Functions ---

def load_analysis_results(filepath):
    """Loads analysis results from a pickle file."""
    with open(filepath, 'rb') as f:
        return pickle.load(f)

def load_historical_csv(symbol, asset, days=1):
    """
    Loads historical data for a specific symbol.
    **UPDATE**: Now handles multiple CSV files for a single asset class (e.g., 'sectors').
    """
    file_map = {
        'indices': 'indices_15min.csv',
        # **UPDATE**: 'sectors' now points to a list of files.
        'sectors': ['sector_etf_15min.csv', 'sector2_etf_15min.csv'],
        'forex': 'forex_15min.csv',
        'commodities': 'commodities_15min.csv',
        'crypto': 'crypto_15min.csv',
        # **FIX**: Corrected filename based on screenshot.
        'bonds': 'bonds_15min.csv',
        'vix': 'vix_15min.csv'
    }
    try:
        base_path = os.path.join(os.path.dirname(__file__), "data")
        
        filenames = file_map.get(asset)
        if not filenames:
            return pd.DataFrame()
        
        # Ensure filenames is a list for consistent processing
        if isinstance(filenames, str):
            filenames = [filenames]

        # Load and concatenate all relevant CSVs for the asset class
        all_dfs = []
        for fname in filenames:
            try:
                full_path = os.path.join(base_path, fname)
                temp_df = pd.read_csv(full_path, parse_dates=['timestamp'])
                all_dfs.append(temp_df)
            except FileNotFoundError:
                print(f"Warning: File not found and will be skipped: {base_path}{fname}")
        
        if not all_dfs:
            return pd.DataFrame()

        # Combine all data into a single DataFrame
        df = pd.concat(all_dfs, ignore_index=True)
        
        # --- The rest of the function proceeds as before with the combined data ---
        end_time = df['timestamp'].max()
        start_time = end_time - pd.Timedelta(days=days)
        
        symbol_col = None
        for col in ['symbol', 'pair', 'sector_etf', 'commodity', 'crypto', 'vix_etf', 'bond']:
            if col in df.columns:
                symbol_col = col
                break
        
        if symbol_col:
            fdf = df[df[symbol_col] == symbol].copy()
            fdf = fdf[(fdf['timestamp'] >= start_time) & (fdf['timestamp'] <= end_time)]
            return fdf
        else:
            return pd.DataFrame()

    except Exception as e:
        print(f"Error loading data for {symbol} in {asset}: {e}")
        return pd.DataFrame()


def value_and_pct_change(df, price_col):
    """Calculates the latest value, absolute change, and percentage change."""
    if df.empty or price_col not in df.columns:
        return np.nan, np.nan, np.nan
        
    df_sorted = df.sort_values('timestamp').dropna(subset=[price_col])
    
    if len(df_sorted) < 2:
        latest_val = df_sorted.iloc[-1][price_col] if not df_sorted.empty else np.nan
        return latest_val, np.nan, np.nan

    first_price = df_sorted.iloc[0][price_col]
    last_price = df_sorted.iloc[-1][price_col]
    
    delta = last_price - first_price
    pct_change = (delta / first_price) * 100 if first_price != 0 else 0.0
    
    return last_price, delta, pct_change

def get_price_col(asset_class, hist_df):
    """Determines the correct price/value column for a given asset class."""
    if hist_df.empty:
        return None
    col_map = {
        'bonds': ['yield', 'value'], 'commodities': ['value', 'close'],
        'indices': ['close'], 'sectors': ['close'], 'forex': ['close'],
        'crypto': ['close'], 'vix': ['close']
    }
    for col in col_map.get(asset_class, []):
        if col in hist_df.columns:
            return col
    return None

def _generate_performance_table(df, title):
    """Generates an HTML table for a performance DataFrame (leaders/laggards)."""
    if df.empty:
        return f"<h3>{title}</h3><p>No data available.</p>"
    rows = []
    for _, row in df.iterrows():
        symbol = row['symbol']
        display_name = SYMBOL_TO_NAME_MAP.get(symbol, symbol)
        pct = row['pct_change']
        pct_disp = f"{pct:+.2f}%"
        color_class = "positive" if pct > 0 else "negative" if pct < 0 else ""
        rows.append(f"""<tr><td>{display_name}</td><td>{row['asset_class'].title()}</td><td class="{color_class}">{pct_disp}</td></tr>""")
    return f"""<h3>{title}</h3><table class="data-table"><thead><tr><th>Asset</th><th>Asset Class</th><th>% Change (24h)</th></tr></thead><tbody>{''.join(rows)}</tbody></table>"""

# --- Main HTML Report Function (unchanged) ---

def generate_candle_chart_html(asset_symbol, asset_name, hist_data):
    """
    Generates an interactive Plotly candlestick chart for the given asset.
    """
    if hist_data.empty or len(hist_data) < 2 or not all(col in hist_data.columns for col in ['open', 'high', 'low', 'close', 'timestamp']):
        return f'<p>No sufficient OHLC data for {asset_name} ({asset_symbol}) chart</p>'

    hist_sorted = hist_data.sort_values('timestamp')

    fig = go.Figure(data=[go.Candlestick(
        x=hist_sorted['timestamp'],
        open=hist_sorted['open'],
        high=hist_sorted['high'],
        low=hist_sorted['low'],
        close=hist_sorted['close'],
        increasing_line_color='#2E8B57',
        decreasing_line_color='#B22222'
    )])

    # Add alternating day background highlights
    unique_days = hist_sorted['timestamp'].dt.date.unique()
    for i, day in enumerate(unique_days):
        if i % 2 != 0:
            fig.add_vrect(
                x0=datetime.combine(day, time.min),
                x1=datetime.combine(day, time.max),
                fillcolor="#f0f0f0",
                opacity=0.5,
                layer="below",
                line_width=0,
            )

    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Price",
        paper_bgcolor='#ffffff',
        plot_bgcolor='#f5f5f5',
        xaxis_rangeslider_visible=False,
        font=dict(family='Century Gothic', color='#2c3e50'),
        xaxis=dict(gridcolor='#e0e0e0'),
        yaxis=dict(gridcolor='#e0e0e0'),
        margin=dict(l=50, r=50, t=50, b=50)
    )

    return fig.to_html(full_html=False, include_plotlyjs='cdn')


def generate_sector_performance_chart(sectors_df, symbol_map):
    """Generates a Plotly horizontal bar chart for sector performance."""
    if sectors_df.empty:
        return ""

    # Calculate percentage change for each sector
    perf_data = []
    for _, row in sectors_df.iterrows():
        hist = load_historical_csv(row['symbol'], 'sectors', days=1)
        _, _, pct = value_and_pct_change(hist, 'close')
        if pd.notna(pct):
            display_name = symbol_map.get(row['symbol'], row['symbol'])
            perf_data.append({'name': display_name, 'pct_change': pct})
    
    if not perf_data:
        return "<h3>Sector Performance (24h % Change)</h3><p>No performance data available.</p>"

    # Create a DataFrame and sort by performance
    perf_df = pd.DataFrame(perf_data).sort_values('pct_change', ascending=False)
    
    # Conditional coloring
    colors = ['#2E8B57' if val >= 0 else '#B22222' for val in perf_df['pct_change']]
    
    # Create the chart
    # Create the chart
    fig = go.Figure(go.Bar(
        x=perf_df['pct_change'],
        y=perf_df['name'],
        orientation='h',
        marker_color=colors,
        text=perf_df['pct_change'].apply(lambda x: f'{x:+.2f}%'),
        textposition='outside'
    ))
    
    # Style the chart
    fig.update_layout(
        title_text='Sector Performance (24h % Change)',
        yaxis={'categoryorder': 'total ascending'},
        paper_bgcolor='#ffffff',
        plot_bgcolor='#f5f5f5',
        showlegend=False,
        xaxis_title="24h % Change",
        yaxis_title="Sector",
        margin=dict(l=150, r=20, t=50, b=50),
        xaxis=dict(gridcolor='#e0e0e0')
    )
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn')

def html_report(analysis_results):
    """Generates a professional, styled HTML financial market report."""
    latest_data = analysis_results['latest_data']
    summary = analysis_results['market_summary']
    all_assets_performance = []
    css_style = """
    <style>
        body {
            font-family: 'Century Gothic', CenturyGothic, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f8f9fa;
            color: #333333;
            font-size: 16px;
            line-height: 1.6;
        }
        .container {
            max-width: 1000px;
            margin: 40px auto;
            padding: 30px;
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        }
        h1, h2, h3 {
            color: #2c3e50;
            margin-top: 40px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid #e0e0e0;
        }
        h1 { font-size: 2.2em; }
        h2 { font-size: 1.8em; }
        h3 {
            font-size: 1.4em;
            border-bottom: none;
            background-color: #f5f5f5;
            padding: 12px;
            border-left: 5px solid #2c3e50;
        }
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        .header h1 {
            border-bottom: none;
        }
        .report-meta {
            font-size: 0.9em;
            color: #666;
        }
        .data-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        .data-table th, .data-table td {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }
        .data-table th {
            background-color: #f5f5f5;
            font-weight: bold;
            color: #2c3e50;
        }
        .data-table tbody tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        .data-table tbody tr:hover {
            background-color: #f1f1f1;
        }
        .positive { color: #2E8B57 !important; }
        .negative { color: #B22222 !important; }
        .performance-section {
            display: flex;
            justify-content: space-between;
            gap: 30px;
        }
        .performance-section > div {
            width: 48%;
        }
        .charts-section {
            margin-top: 40px;
            padding: 20px;
            background-color: #f5f5f5;
            border-radius: 5px;
        }
        .chart-container {
            margin-bottom: 20px;
            padding: 20px;
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
        }
        .geographic-header {
            background-color: #f5f5f5;
            padding: 12px;
            border-left: 5px solid #2c3e50;
            margin-top: 20px;
            margin-bottom: 15px;
        }
        .asset-class-header {
            background-color: #f5f5f5;
            padding: 12px;
            margin-top: 30px;
            margin-bottom: 15px;
            font-size: 1.5em;
            border-bottom: 1px solid #e0e0e0;
        }
    </style>
    """
    
    html_body = [f"""<div class="header"><h1>Daily Financial Market Report</h1><p class="report-meta">Report Generated: {summary['report_time'].strftime('%Y-%m-%d %H:%M:%S %Z')}</p><p class="report-meta">Total Assets Tracked: {summary['total_assets_tracked']} | Asset Classes: {', '.join(summary['asset_classes'])}</p></div>"""]
    
    # Reorganize indices by geography
    geographic_regions = {
        'Asia-Pacific': ['EWJ', 'INDA', 'MCHI', 'EWA'],
        'Europe + UK': ['FEZ', 'DAX', 'EWU', 'EWG', 'EWQ'],
        'Americas': ['SPY', 'QQQ', 'DIA', 'IWM'],
        'Global / Emerging Markets': ['EEM']
    }
    
    # Process indices first in geographic order
    if 'indices' in latest_data:
        indices_df = latest_data['indices']
        html_body.append('<div class="geographic-section">')
        html_body.append('<h2>Global Indices by Region</h2>')
        
        for region, symbols in geographic_regions.items():
            region_symbols = [s for s in symbols if s in indices_df['symbol'].values]
            if region_symbols:  # Only show region if it has data
                html_body.append(f'<div class="geographic-header"><h3>{region}</h3></div>')
                region_data = indices_df[indices_df['symbol'].isin(region_symbols)]
                
                table_rows = []
                for _, row in region_data.iterrows():
                    symbol = row['symbol']
                    display_name = SYMBOL_TO_NAME_MAP.get(symbol, symbol)
                    hist = load_historical_csv(symbol, 'indices', days=1)
                    val, delta, pct = value_and_pct_change(hist, 'close')
                    val_disp = f"{val:,.4f}" if pd.notna(val) else "-"
                    delta_disp = f"{delta:+.4f}" if pd.notna(delta) else "-"
                    pct_disp = f"{pct:+.2f}%" if pd.notna(pct) else "-"
                    color_class = ""
                    if pd.notna(pct):
                        if pct > 0: color_class = "positive"
                        elif pct < 0: color_class = "negative"
                    table_rows.append(f'<tr><td>{display_name}</td><td>{val_disp}</td><td class="{color_class}">{delta_disp}</td><td class="{color_class}">{pct_disp}</td></tr>')
                    if pd.notna(pct):
                        all_assets_performance.append({'symbol': symbol, 'asset_class': 'indices', 'pct_change': pct})
                
                html_body.append(f"""<table class="data-table"><thead><tr><th>Asset</th><th>Latest Price</th><th>Change (24h)</th><th>% Change (24h)</th></tr></thead><tbody>{''.join(table_rows)}</tbody></table>""")
        
        html_body.append('</div>')  # End geographic-section
        
        # Process remaining non-indices asset classes
        for asset_class, df in latest_data.items():
            if asset_class == 'sectors':
                # Generate and append the sector performance chart
                sector_chart_html = generate_sector_performance_chart(df, SYMBOL_TO_NAME_MAP)
                html_body.append(f'<div class="chart-container">{sector_chart_html}</div>')
            elif asset_class != 'indices':
                html_body.append(f'<h2 class="asset-class-header">{asset_class.title()}</h2>')
                table_rows = []
                for _, row in df.iterrows():
                    symbol = row['symbol']
                    display_name = SYMBOL_TO_NAME_MAP.get(symbol, symbol)
                    hist = load_historical_csv(symbol, asset_class, days=1)
                    price_col = get_price_col(asset_class, hist)
                    val, delta, pct = value_and_pct_change(hist, price_col)
                    val_disp = f"{val:,.4f}" if pd.notna(val) else "-"
                    delta_disp = f"{delta:+.4f}" if pd.notna(delta) else "-"
                    pct_disp = f"{pct:+.2f}%" if pd.notna(pct) else "-"
                    color_class = ""
                    if pd.notna(pct):
                        if pct > 0: color_class = "positive"
                        elif pct < 0: color_class = "negative"
                    table_rows.append(f'<tr><td>{display_name}</td><td>{val_disp}</td><td class="{color_class}">{delta_disp}</td><td class="{color_class}">{pct_disp}</td></tr>')
                    if pd.notna(pct):
                        all_assets_performance.append({'symbol': symbol, 'asset_class': asset_class, 'pct_change': pct})
                html_body.append(f"""<table class="data-table"><thead><tr><th>Asset</th><th>Latest Price</th><th>Change (24h)</th><th>% Change (24h)</th></tr></thead><tbody>{''.join(table_rows)}</tbody></table>""")
    else:
        # If no indices, just process all asset classes normally
        for asset_class, df in latest_data.items():
            html_body.append(f'<h2>{asset_class.title()}</h2>')
            table_rows = []
            for _, row in df.iterrows():
                symbol = row['symbol']
                display_name = SYMBOL_TO_NAME_MAP.get(symbol, symbol)
                hist = load_historical_csv(symbol, asset_class, days=1)
                price_col = get_price_col(asset_class, hist)
                val, delta, pct = value_and_pct_change(hist, price_col)
                val_disp = f"{val:,.4f}" if pd.notna(val) else "-"
                delta_disp = f"{delta:+.4f}" if pd.notna(delta) else "-"
                pct_disp = f"{pct:+.2f}%" if pd.notna(pct) else "-"
                color_class = ""
                if pd.notna(pct):
                    if pct > 0: color_class = "positive"
                    elif pct < 0: color_class = "negative"
                table_rows.append(f'<tr><td>{display_name}</td><td>{val_disp}</td><td class="{color_class}">{delta_disp}</td><td class="{color_class}">{pct_disp}</td></tr>')
                if pd.notna(pct):
                    all_assets_performance.append({'symbol': symbol, 'asset_class': asset_class, 'pct_change': pct})
            html_body.append(f"""<table class="data-table"><thead><tr><th>Asset</th><th>Latest Price</th><th>Change (24h)</th><th>% Change (24h)</th></tr></thead><tbody>{''.join(table_rows)}</tbody></table>""")
    
    html_body.append('<h2>Market Performance Highlights</h2>')
    perf_df = pd.DataFrame(all_assets_performance).sort_values('pct_change', ascending=False)
    leaders_table = _generate_performance_table(perf_df.head(5), "Top 5 Leaders")
    laggards_table = _generate_performance_table(perf_df.tail(5).sort_values('pct_change', ascending=True), "Top 5 Laggards")
    html_body.append(f'<div class="performance-section"><div>{leaders_table}</div><div>{laggards_table}</div></div>')
    
    # Add charts section at the end
    key_assets = ['SPY', 'QQQ', 'DIA', 'IWM', 'VXX', 'UVXY', 'XLE', 'XLF', 'XLK', 'XLV', 'XLU']  # Key assets for charts (including XLU - Utilities)
    html_body.append('<div class="charts-section"><h2>Key Assets 15-Min Charts</h2>')
    
    for asset in key_assets:
        for asset_class, df in latest_data.items():
            if asset in df['symbol'].values:
                display_name = SYMBOL_TO_NAME_MAP.get(asset, asset)
                # Get historical data for chart
                hist = load_historical_csv(asset, asset_class, days=7)
                chart_html = generate_candle_chart_html(asset, display_name, hist)
                html_body.append(f'<div class="chart-container"><h3>{display_name} ({asset})</h3>{chart_html}</div>')
                break
    html_body.append('</div>')
    
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Daily Financial Report</title>{css_style}</head><body><div class="container">{''.join(html_body)}</div></body></html>"""

# --- Main execution block ---
if __name__ == '__main__':
    base_path = os.path.dirname(__file__)
    fp = os.path.join(base_path, 'data/market_analysis_results.pkl')
    out_path = os.path.join(base_path, 'daily_report-i.html')
    try:
        analysis_results = load_analysis_results(fp)
        html_content = html_report(analysis_results)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✓ Report updated to handle multiple sector files: {out_path}")
    except FileNotFoundError:
        print(f"Error: The input file was not found at {fp}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")