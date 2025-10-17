import pandas as pd
from datetime import datetime
import pytz

def read_and_align_data():
    """
    Read all asset class CSVs, align timezones, and select the latest data for each asset.
    Returns a dictionary with latest data for each asset class.
    """
    data_files = {
        'bonds': {'file': '/Users/pawan/CLI-Finance-Terminal/approach 2.0/data/bonds_15min.csv', 'tz_source': 'America/New_York'},
        'commodities': {'file': '/Users/pawan/CLI-Finance-Terminal/approach 2.0/data/commodities_15min.csv', 'tz_source': 'UTC'},
        'crypto': {'file': '/Users/pawan/CLI-Finance-Terminal/approach 2.0/data/crypto_15min.csv', 'tz_source': 'UTC'},
        'forex': {'file': '/Users/pawan/CLI-Finance-Terminal/approach 2.0/data/forex_15min.csv', 'tz_source': 'UTC'},
        'indices': {'file': '/Users/pawan/CLI-Finance-Terminal/approach 2.0/data/indices_15min.csv', 'tz_source': 'America/New_York'},
        'sector_s1': {'file': '/Users/pawan/CLI-Finance-Terminal/approach 2.0/data/sector_etf_15min.csv', 'tz_source': 'America/New_York'},
        'sector_s2': {'file': '/Users/pawan/CLI-Finance-Terminal/approach 2.0/data/sector2_etf_15min.csv', 'tz_source': 'America/New_York'},
        'vix': {'file': '/Users/pawan/CLI-Finance-Terminal/approach 2.0/data/vix_15min.csv', 'tz_source': 'America/New_York'}
    }

    latest_data = {}
    target_tz = 'Asia/Kolkata'  # Target timezone (IST)

    for asset_class, info in data_files.items():
        try:
            df = pd.read_csv(info['file'], parse_dates=['timestamp'])
            if df.empty:
                print(f"Warning: {info['file']} is empty")
                continue
            if df['timestamp'].dt.tz is None:
                df['timestamp'] = df['timestamp'].dt.tz_localize(info['tz_source'])
            df['timestamp'] = df['timestamp'].dt.tz_convert(target_tz)

            # Latest data for each symbol in the asset class
            if asset_class == 'bonds':
                latest = df.loc[df.groupby('bond')['timestamp'].idxmax()]
                latest_data[asset_class] = latest[['bond', 'timestamp', 'yield']].rename(columns={'bond': 'symbol', 'yield': 'value'})
            elif asset_class == 'commodities':
                latest = df.loc[df.groupby('commodity')['timestamp'].idxmax()]
                latest_data[asset_class] = latest[['commodity', 'timestamp', 'close']].rename(columns={'commodity': 'symbol', 'close': 'value'})
            elif asset_class == 'crypto':
                latest = df.loc[df.groupby('crypto')['timestamp'].idxmax()]
                latest_data[asset_class] = latest[['crypto', 'timestamp', 'open', 'high', 'low', 'close']].rename(columns={'crypto': 'symbol'})
            elif asset_class == 'forex':
                latest = df.loc[df.groupby('pair')['timestamp'].idxmax()]
                latest_data[asset_class] = latest[['pair', 'timestamp', 'open', 'high', 'low', 'close']].rename(columns={'pair': 'symbol'})
            elif asset_class == 'indices':
                latest = df.loc[df.groupby('symbol')['timestamp'].idxmax()]
                latest_data[asset_class] = latest[['symbol', 'timestamp', 'open', 'high', 'low', 'close']]
            elif asset_class.startswith('sector'):
                latest = df.loc[df.groupby('sector_etf')['timestamp'].idxmax()]
                latest_data[asset_class] = latest[['sector_etf', 'timestamp', 'open', 'high', 'low', 'close']].rename(columns={'sector_etf': 'symbol'})
            elif asset_class == 'vix':
                latest = df.loc[df.groupby('vix_etf')['timestamp'].idxmax()]
                latest_data[asset_class] = latest[['vix_etf', 'timestamp', 'open', 'high', 'low', 'close']].rename(columns={'vix_etf': 'symbol'})
        except FileNotFoundError:
            print(f"Warning: {info['file']} not found, skipping {asset_class}")
        except Exception as e:
            print(f"Error processing {asset_class}: {str(e)}")

    # Combine sector_s1 and sector_s2
    if 'sector_s1' in latest_data and 'sector_s2' in latest_data:
        sectors_combined = pd.concat([latest_data['sector_s1'], latest_data['sector_s2']], ignore_index=True)
        # Remove duplicates by keeping the most recent timestamp for each symbol
        sectors_combined = sectors_combined.loc[sectors_combined.groupby('symbol')['timestamp'].idxmax()]
        latest_data['sectors'] = sectors_combined
        latest_data.pop('sector_s1', None)
        latest_data.pop('sector_s2', None)

    import pickle
    output_path = '/Users/pawan/CLI-Finance-Terminal/approach 2.0/data/latest_market_data.pkl'
    with open(output_path, 'wb') as f:
        pickle.dump(latest_data, f)
    print(f"\n✓ Latest data saved to '{output_path}' for analysis")

if __name__ == "__main__":
    read_and_align_data()
