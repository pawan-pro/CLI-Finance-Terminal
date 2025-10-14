import pickle
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz

# --- Symbol to Descriptive Name Mapping ---
SYMBOL_TO_NAME_MAP = {
    # Major Indices
    'SPY': 'S&P 500', 'QQQ': 'Nasdaq 100', 'DIA': 'Dow Jones Industrial Average', 'IWM': 'Russell 2000',
    # Sector ETFs
    'XLE': 'Energy Sector', 'XLF': 'Financials Sector', 'XLU': 'Utilities Sector', 'XLI': 'Industrials Sector',
    'XLK': 'Technology Sector', 'XLV': 'Health Care Sector', 'XLY': 'Consumer Discretionary Sector',
    'XLP': 'Consumer Staples Sector', 'XLB': 'Materials Sector', 'XLRE': 'Real Estate Sector',
    'XLC': 'Communication Services Sector',
    # VIX
    'VXX': 'VIX Short-Term Futures ETN',
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

def html_report(analysis_results):
    """Generates a professional, styled HTML financial market report."""
    latest_data = analysis_results['latest_data']
    summary = analysis_results['market_summary']
    all_assets_performance = []
    css_style = """<style>body{font-family:'Century Gothic',CenturyGothic,sans-serif;margin:0;padding:0;background-color:#f9f9f9;color:#333;font-size:16px;line-height:1.6}.container{max-width:960px;margin:20px auto;padding:20px;background-color:#fff;border:1px solid #e0e0e0;box-shadow:0 2px 5px rgba(0,0,0,.05)}h1,h2,h3{color:#2c3e50;border-bottom:2px solid #e0e0e0;padding-bottom:10px;margin-top:30px}h1{font-size:2em}h2{font-size:1.75em}h3{font-size:1.25em;border-bottom:none}.header{text-align:center;margin-bottom:40px}.header h1{border-bottom:none}.report-meta{font-size:.9em;color:#777}.data-table{width:100%;border-collapse:collapse;margin-bottom:30px}.data-table th,.data-table td{padding:12px;text-align:left;border-bottom:1px solid #ddd}.data-table th{background-color:#f2f2f2;font-weight:700;color:#555}.data-table tbody tr:nth-child(even){background-color:#f9f9f9}.data-table tbody tr:hover{background-color:#f1f1f1}.positive{color:#27ae60!important}.negative{color:#c0392b!important}.performance-section{display:flex;justify-content:space-between;gap:20px}.performance-section>div{width:48%}</style>"""
    html_body = [f"""<div class="header"><h1>Daily Financial Market Report</h1><p class="report-meta">Report Generated: {summary['report_time'].strftime('%Y-%m-%d %H:%M:%S %Z')}</p><p class="report-meta">Total Assets Tracked: {summary['total_assets_tracked']} | Asset Classes: {', '.join(summary['asset_classes'])}</p></div>"""]
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