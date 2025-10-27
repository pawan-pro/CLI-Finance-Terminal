import pandas as pd
import numpy as np
import pickle
from datetime import datetime, timedelta
import pytz

def load_latest_data():
    try:
        with open('data/latest_market_data.pkl', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        print("Error: latest_market_data.pkl not found. Run data alignment script first.")
        return None

def calculate_daily_changes(latest_data):
    changes = {}
    for asset_class, df in latest_data.items():
        df_copy = df.copy()
        if asset_class == 'bonds':
            df_copy['daily_change_bps'] = 0
        elif all(c in df.columns for c in ['open', 'high', 'low']):
            df_copy['intraday_range_pct'] = ((df_copy['high'] - df_copy['low']) / df_copy['open'] * 100).round(2)
            df_copy['daily_change_pct'] = 0
        else:
            # For asset classes without OHLC data like commodities
            df_copy['daily_change_pct'] = 0
        changes[asset_class] = df_copy
    return changes

def identify_market_leaders_laggards(latest_data):
    print("\n" + "="*60)
    print("MARKET LEADERS & LAGGARDS ANALYSIS")
    print("="*60)
    if 'sectors' in latest_data:
        sectors_df = latest_data['sectors'].copy()
        sectors_df['intraday_range'] = ((sectors_df['high'] - sectors_df['low']) / sectors_df['open'] * 100)
        print("\nSECTOR VOLATILITY (Intraday Range %):")
        print("-" * 40)
        sector_volatility = sectors_df.nlargest(5, 'intraday_range')[['symbol', 'intraday_range', 'close']]
        for _, row in sector_volatility.iterrows():
            print(f"{row['symbol']}: {row['intraday_range']:.2f}% range, Close: ${row['close']:.2f}")
    if 'crypto' in latest_data:
        crypto_df = latest_data['crypto'].copy()
        crypto_df['intraday_range'] = ((crypto_df['high'] - crypto_df['low']) / crypto_df['open'] * 100)
        print("\nCRYPTO VOLATILITY (Intraday Range %):")
        print("-" * 40)
        crypto_volatility = crypto_df.nlargest(3, 'intraday_range')[['symbol', 'intraday_range', 'close']]
        for _, row in crypto_volatility.iterrows():
            print(f"{row['symbol']}: {row['intraday_range']:.2f}% range, Price: ${row['close']:.2f}")

def calculate_cross_asset_metrics(latest_data):
    print("\n" + "="*60)
    print("CROSS-ASSET METRICS & RATIOS")
    print("="*60)
    metrics = {}
    if 'bonds' in latest_data:
        bonds_df = latest_data['bonds']
        if len(bonds_df) >= 2:
            us2y = bonds_df[bonds_df['symbol'] == 'US2Y']['value'].iloc[0] if 'US2Y' in bonds_df['symbol'].values else None
            us10y = bonds_df[bonds_df['symbol'] == 'US10Y']['value'].iloc[0] if 'US10Y' in bonds_df['symbol'].values else None
            if us2y is not None and us10y is not None:
                yield_spread = us10y - us2y
                metrics['yield_curve_2s10s'] = yield_spread
                curve_status = "Normal" if yield_spread > 0 else "Inverted" if yield_spread < -0.1 else "Flat"
                print(f"\nYIELD CURVE ANALYSIS:")
                print(f"2Y-10Y Spread: {yield_spread:.2f} bps ({curve_status})")
    if 'vix' in latest_data:
        vix_df = latest_data['vix']
        if len(vix_df) > 0:
            vix_level = vix_df['close'].iloc[0]
            vix_sentiment = "Low" if vix_level < 30 else "Elevated" if vix_level < 40 else "High"
            metrics['vix_level'] = vix_level
            print(f"\nVOLATILITY GAUGE:")
            print(f"VIX Proxy Level: ${vix_level:.2f} ({vix_sentiment} Fear)")
    if 'forex' in latest_data:
        forex_df = latest_data['forex']
        usd_pairs = forex_df[forex_df['symbol'].str.contains('USD')]
        if len(usd_pairs) > 0:
            print(f"\nUSD CROSS-RATES (Latest):")
            for _, row in usd_pairs.iterrows():
                print(f"{row['symbol']}: {row['close']:.4f}")
    if 'commodities' in latest_data:
        commodities_df = latest_data['commodities']
        print(f"\nCOMMODITIES:")
        for _, row in commodities_df.iterrows():
            print(f"{row['symbol']}: ${row['value']:.2f}")
    if 'mt5' in latest_data:
        mt5_df = latest_data['mt5']
        print(f"\nMT5 REAL-TIME DATA (Latest):")
        # Show top 10 MT5 symbols by timestamp
        mt5_recent = mt5_df.sort_values('timestamp', ascending=False).head(10)
        for _, row in mt5_recent.iterrows():
            symbol = row['symbol']
            close_price = row['close']
            print(f"{symbol}: {close_price:.5f}")
    return metrics

def generate_market_summary(latest_data):
    current_time = datetime.now(pytz.timezone('Asia/Kolkata'))
    print("\n" + "="*60)
    print("EXECUTIVE MARKET SUMMARY")
    print("="*60)
    print(f"Report Time: {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    summary = {
        'report_time': current_time,
        'total_assets_tracked': sum(len(df) for df in latest_data.values()),
        'asset_classes': list(latest_data.keys())
    }
    print(f"\nMARKET SNAPSHOT:")
    print(f"• Total Assets Tracked: {summary['total_assets_tracked']}")
    print(f"• Asset Classes: {', '.join(summary['asset_classes']).title()}")
    if 'indices' in latest_data:
        indices_df = latest_data['indices']
        spy_data = indices_df[indices_df['symbol'] == 'SPY']
        if len(spy_data) > 0:
            spy_level = spy_data['close'].iloc[0]
            print(f"• S&P 500 (SPY): ${spy_level:.2f}")
    if 'forex' in latest_data:
        forex_df = latest_data['forex']
        dxy_proxy = forex_df[forex_df['symbol'] == 'EUR/USD']
        if len(dxy_proxy) > 0:
            eurusd = dxy_proxy['close'].iloc[0]
            print(f"• EUR/USD: {eurusd:.4f}")
    return summary

def save_analysis_results(latest_data, metrics, summary):
    analysis_results = {
        'latest_data': latest_data,
        'cross_asset_metrics': metrics,
        'market_summary': summary,
        'analysis_timestamp': datetime.now(pytz.timezone('Asia/Kolkata'))
    }
    output_path = 'data/market_analysis_results.pkl'
    with open(output_path, 'wb') as f:
        pickle.dump(analysis_results, f)
    print(f"\n✓ Analysis results saved to '{output_path}'")

if __name__ == "__main__":
    latest_data = load_latest_data()
    if latest_data is None:
        exit(1)
    changes = calculate_daily_changes(latest_data)
    identify_market_leaders_laggards(latest_data)
    metrics = calculate_cross_asset_metrics(latest_data)
    summary = generate_market_summary(latest_data)
    save_analysis_results(latest_data, metrics, summary)
