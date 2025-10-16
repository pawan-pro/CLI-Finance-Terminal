import pickle
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
import plotly.graph_objects as go

def load_analysis_results(filepath):
    with open(filepath, 'rb') as f:
        return pickle.load(f)

def load_historical_csv(symbol, asset, days=1):
    file_map = {
        'indices': 'indices_15min.csv',
        'sectors': 'sector_etf_15min.csv',
        'forex': 'forex_15min.csv',
        'commodities': 'commodities_15min.csv',
        'crypto': 'crypto_15min.csv',
        'bonds': 'bond_yields_15min.csv',
        'vix': 'vix_15min.csv'
    }
    try:
        df = pd.read_csv(f"approach 2.0/data/{file_map[asset]}", parse_dates=['timestamp'])
        end_time = df['timestamp'].max()
        start_time = pd.to_datetime(end_time) - pd.Timedelta(days=days)
        for col in ['symbol', 'pair', 'sector_etf', 'commodity', 'crypto', 'vix_etf', 'bond']:
            if col in df.columns:
                fdf = df[df[col] == symbol]
                break
        else:
            fdf = pd.DataFrame()
        if 'timestamp' in fdf.columns:
            fdf = fdf[(fdf['timestamp'] >= start_time) & (fdf['timestamp'] <= end_time)]
        return fdf
    except Exception as e:
        return pd.DataFrame()

def value_and_pct_change(df, price_col, asset_class):
    if df.empty or 'timestamp' not in df.columns or price_col is None or price_col not in df.columns:
        return np.nan, np.nan, np.nan
    df_sorted = df.sort_values('timestamp')
    if df_sorted.empty or len(df_sorted) < 2:
        return np.nan, np.nan, np.nan
    first_row = df_sorted.iloc[0]
    last_row = df_sorted.iloc[-1]
    val = last_row[price_col]
    prev = first_row[price_col]
    delta = val - prev
    pct = (delta / prev) * 100 if prev != 0 else np.nan
    return val, delta, pct

def get_price_col(asset_class, hist):
    if hist.empty:
        return None
    if asset_class == 'bonds':
        if 'yield' in hist.columns:
            return 'yield'
        elif 'value' in hist.columns:
            return 'value'
    elif asset_class == 'commodities':
        if 'value' in hist.columns:
            return 'value'
        elif 'close' in hist.columns:
            return 'close'
    elif asset_class in ['indices', 'sectors', 'forex', 'crypto', 'vix']:
        if 'close' in hist.columns:
            return 'close'
    return None

def generate_chart(symbol, asset_class, days=1):
    df = load_historical_csv(symbol, asset_class, days)
    if df.empty or not all(col in df.columns for col in ['open', 'high', 'low', 'close']):
        return ""

    fig = go.Figure(data=[go.Candlestick(x=df['timestamp'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'])])
    fig.update_layout(title=f'{symbol} 24-Hour Performance',
                      xaxis_title='Timestamp',
                      yaxis_title='Price',
                      xaxis_rangeslider_visible=False)
    return fig.to_html(full_html=False, include_plotlyjs='cdn')

def html_report(analysis_results):
    latest_data = analysis_results['latest_data']
    summary = analysis_results['market_summary']
    html = ["<html><head><title>Daily Financial Report</title></head><body>"]
    html.append("<h1>Daily Financial Market Report</h1>")
    html.append(f"<h3>Report Generated: {summary['report_time'].strftime('%Y-%m-%d %H:%M:%S %Z')}</h3>")

    html.append('<h2>Key Market Charts</h2>')
    html.append(generate_chart('SPY', 'indices'))
    html.append(generate_chart('XAU/USD', 'commodities'))
    html.append(generate_chart('BTC/USD', 'crypto'))

    html.append('<h2>Market Overview</h2>')
    html.append(f"Total Assets Tracked: {summary['total_assets_tracked']}<br/>Asset Classes: {', '.join(summary['asset_classes'])}")

    # Define index categories
    index_categories = {
        "Asia & Pacific Markets": ['EWJ', 'INDA', 'MCHI', 'EWS', 'EWA'],
        "European Markets": ['EWU', 'FEZ', 'DAX', 'EWG', 'EWQ'],
        "American Markets": ['SPY', 'DIA', 'QQQ', 'IWM'],
        "Global Markets": ['EEM']
    }

    # Section: Asset Classes Details
    for asset_class, df in latest_data.items():
        if asset_class == 'indices':
            for category, symbols in index_categories.items():
                html.append(f'<h2>{category}</h2>')
                table = ['<table border=\"1\"><tr><th>Symbol</th><th>Latest Price</th><th>Change (24h)</th><th>% Change (24h)</th></tr>']
                for symbol in symbols:
                    row = df[df['symbol'] == symbol]
                    if not row.empty:
                        hist = load_historical_csv(symbol, asset_class, days=1)
                        price_col = get_price_col(asset_class, hist)
                        val, delta, pct = value_and_pct_change(hist, price_col, asset_class)
                        delta_disp = f"{delta:.4f}" if not np.isnan(delta) else "-"
                        pct_disp = f"{pct:.2f}" if not np.isnan(pct) else "-"
                        val_disp = f"{val:.4f}" if not np.isnan(val) else "-"
                        table.append(f'<tr><td>{symbol}</td><td>{val_disp}</td><td>{delta_disp}</td><td>{pct_disp}</td></tr>')
                table.append('</table>')
                html.append(''.join(table))
        else:
            html.append(f'<h2>{asset_class.title()}</h2>')
            table = ['<table border=\"1\"><tr><th>Symbol</th><th>Latest Price</th><th>Change (24h)</th><th>% Change (24h)</th></tr>']
            for _, row in df.iterrows():
                hist = load_historical_csv(row['symbol'], asset_class, days=1)
                price_col = get_price_col(asset_class, hist)
                val, delta, pct = value_and_pct_change(hist, price_col, asset_class)
                delta_disp = f"{delta:.4f}" if not np.isnan(delta) else "-"
                pct_disp = f"{pct:.2f}" if not np.isnan(pct) else "-"
                val_disp = f"{val:.4f}" if not np.isnan(val) else "-"
                table.append(f'<tr><td>{row["symbol"]}</td><td>{val_disp}</td><td>{delta_disp}</td><td>{pct_disp}</td></tr>')
            table.append('</table>')
            html.append(''.join(table))

    html.append('<h2>Leaders & Laggards</h2>')
    html.append('<p>(See script output, or extend this function to add leader/laggard tables.)</p>')
    html.append('<h2>Further Analysis</h2>')
    html.append('<p>(See script output for cross-asset metrics, yield curve, etc. - can be extended to table/summary here.)</p>')
    html.append('</body></html>')
    return ''.join(html)

if __name__ == '__main__':
    fp = 'approach 2.0/data/market_analysis_results.pkl'
    analysis_results = load_analysis_results(fp)
    html = html_report(analysis_results)
    out_path = 'approach 2.0/daily_report.html'
    with open(out_path, 'w') as f:
        f.write(html)
    print(f"✓ HTML report generated: {out_path}")
