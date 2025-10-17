import pickle
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz

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
    'TLT': '20+ Year Treasury Bond ETF'
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
        base_path = "/Users/pawan/CLI-Finance-Terminal/approach 2.0/data/"
        
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
                temp_df = pd.read_csv(f"{base_path}{fname}", parse_dates=['timestamp'])
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
    Generate HTML for a professional candlestick chart for the given asset using 15-min data.
    
    Args:
        asset_symbol: The symbol of the asset (e.g., 'SPY')
        asset_name: The display name of the asset (e.g., 'S&P 500')
        hist_data: Historical data for the asset
        
    Returns:
        HTML string for the candlestick chart
    """
    if hist_data.empty or len(hist_data) < 2:
        return f'<p>No sufficient data for {asset_name} ({asset_symbol}) chart</p>'
    
    # Sort by timestamp to ensure proper order
    hist_sorted = hist_data.sort_values('timestamp')
    
    # Get the required columns for OHLC
    if not all(col in hist_sorted.columns for col in ['open', 'high', 'low', 'close']):
        return f'<p>Insufficient OHLC data for {asset_name} ({asset_symbol}) chart</p>'
    
    # Limit to the most recent 40 data points for 15-min candles (10 hours of 15-min data)
    hist_recent = hist_sorted.tail(40)
    
    # Prepare chart data
    timestamps = hist_recent['timestamp'].tolist()
    opens = hist_recent['open'].tolist()
    highs = hist_recent['high'].tolist()
    lows = hist_recent['low'].tolist()
    closes = hist_recent['close'].tolist()
    
    # Find min and max for scaling
    all_prices = opens + highs + lows + closes
    min_price = min(all_prices) * 0.995  # Slightly tighter margin for institutional look
    max_price = max(all_prices) * 1.005  # Slightly tighter margin for institutional look
    price_range = max_price - min_price
    
    # Create SVG-based institutional-style candlestick chart
    chart_html = f'''
    <div class="candle-chart" style="position:relative;height:200px;margin:10px 0;">
        <svg width="100%" height="100%" viewBox="0 0 1000 200" preserveAspectRatio="none">
    '''
    
    # Draw background grid (institutional style)
    chart_html += '''<rect x="0" y="0" width="1000" height="200" fill="#f8f9fa"/>'''
    
    # Draw horizontal grid lines
    for i in range(5):
        y = 40 + i * 40  # Horizontal grid lines
        chart_html += f'<line x1="0" y1="{y}" x2="1000" y2="{y}" stroke="#e9ecef" stroke-width="0.5"/>'
    
    # Draw candles with more professional spacing
    candle_width = 15
    spacing = 5
    total_width = (candle_width + spacing) * len(timestamps)
    start_x = max(20, (1000 - total_width) // 2)  # Center the chart
    
    for i, (timestamp, open_price, high_price, low_price, close_price) in enumerate(zip(timestamps, opens, highs, lows, closes)):
        x = start_x + i * (candle_width + spacing)
        
        # Calculate y positions (inverted because SVG y=0 is at top)
        high_y = 10 + ((max_price - high_price) / price_range) * 180
        low_y = 10 + ((max_price - low_price) / price_range) * 180
        open_y = 10 + ((max_price - open_price) / price_range) * 180
        close_y = 10 + ((max_price - close_price) / price_range) * 180
        
        # Determine candle color (green for up, red for down)
        is_up = close_price >= open_price
        body_color = "#27ae60" if is_up else "#e74c3c"  # Professional green/red
        wick_color = body_color
        
        # Draw high-low line (wick)
        chart_html += f'<line x1="{x + candle_width//2}" y1="{min(high_y, low_y)}" x2="{x + candle_width//2}" y2="{max(high_y, low_y)}" stroke="{wick_color}" stroke-width="1"/>'
        
        # Draw candle body
        body_top = min(open_y, close_y)
        body_height = abs(close_y - open_y)
        if body_height < 1:  # If open and close are nearly equal, make it visible as a thin line
            body_height = 1
            body_top = open_y
        
        chart_html += f'<rect x="{x}" y="{body_top}" width="{candle_width}" height="{body_height}" fill="{body_color}" stroke="#333" stroke-width="0.1"/>'
    
    chart_html += '</svg>'
    chart_html += f'<div style="text-align:center;font-size:14px;margin-top:5px;font-weight:bold;">15-Min OHLC Chart for {asset_name}</div>'
    chart_html += '</div>'
    
    return chart_html


def html_report(analysis_results):
    """Generates a professional, styled HTML financial market report."""
    latest_data = analysis_results['latest_data']
    summary = analysis_results['market_summary']
    all_assets_performance = []
    css_style = """<style>body{font-family:'Century Gothic',CenturyGothic,sans-serif;margin:0;padding:0;background-color:#f9f9f9;color:#333;font-size:16px;line-height:1.6}.container{max-width:960px;margin:20px auto;padding:20px;background-color:#fff;border:1px solid #e0e0e0;box-shadow:0 2px 5px rgba(0,0,0,.05)}h1,h2,h3{color:#2c3e50;border-bottom:2px solid #e0e0e0;padding-bottom:10px;margin-top:30px}h1{font-size:2em}h2{font-size:1.75em}h3{font-size:1.25em;border-bottom:none}.header{text-align:center;margin-bottom:40px}.header h1{border-bottom:none}.report-meta{font-size:.9em;color:#777}.data-table{width:100%;border-collapse:collapse;margin-bottom:30px}.data-table th,.data-table td{padding:12px;text-align:left;border-bottom:1px solid #ddd}.data-table th{background-color:#f2f2f2;font-weight:700;color:#555}.data-table tbody tr:nth-child(even){background-color:#f9f9f9}.data-table tbody tr:hover{background-color:#f1f1f1}.positive{color:#27ae60!important}.negative{color:#c0392b!important}.performance-section{display:flex;justify-content:space-between;gap:20px}.performance-section>div{width:48%}.charts-section{margin:20px 0;padding:15px;background-color:#f8f9fa;border-radius:5px}.chart-container{margin:10px 0;padding:10px;background-color:#fff;border:1px solid #ddd;border-radius:4px;position:relative;overflow:hidden}.key-assets{margin:20px 0}.candle-chart{border:1px solid #eee;border-radius:4px;padding:5px;}.geographic-section{margin:30px 0;}.geographic-header{background-color:#e9ecef;padding:10px;border-left:4px solid #2c3e50;}.asset-class-header{background-color:#f1f3f5;padding:8px;margin-top:15px;}</style>"""
    
    html_body = [f"""<div class="header"><h1>Daily Financial Market Report</h1><p class="report-meta">Report Generated: {summary['report_time'].strftime('%Y-%m-%d %H:%M:%S %Z')}</p><p class="report-meta">Total Assets Tracked: {summary['total_assets_tracked']} | Asset Classes: {', '.join(summary['asset_classes'])}</p></div>"""]
    
    # Reorganize indices by geography
    geographic_regions = {
        'Asia-Pacific': ['EWJ', 'INDA', 'MCHI'],  # Japan, India, China
        'Europe + UK': ['FEZ', 'DAX', 'EWU', 'EWG', 'EWQ'],  # Euro Stoxx 50, Germany, UK, etc.
        'Americas': ['SPY', 'QQQ', 'DIA', 'IWM', 'EEM', 'EWA']  # US and other Americas
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
            if asset_class != 'indices':
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
                hist = load_historical_csv(asset, asset_class, days=1)
                chart_html = generate_candle_chart_html(asset, display_name, hist)
                html_body.append(f'<div class="chart-container"><h3>{display_name} ({asset})</h3>{chart_html}</div>')
                break
    html_body.append('</div>')
    
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Daily Financial Report</title>{css_style}</head><body><div class="container">{''.join(html_body)}</div></body></html>"""

# --- Main execution block ---
if __name__ == '__main__':
    fp = '/Users/pawan/CLI-Finance-Terminal/approach 2.0/data/market_analysis_results.pkl'
    out_path = '/Users/pawan/CLI-Finance-Terminal/approach 2.0/daily_report-i.html'
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