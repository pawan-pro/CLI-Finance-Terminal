import pandas as pd
from datetime import datetime
import pytz
import pickle
import os

def process_mt5_data(latest_data):
    """
    Process MT5 data and integrate it with existing data.
    MT5 data can override existing data for the same symbols.
    
    Args:
        latest_data (dict): Dictionary with existing asset class data
        
    Returns:
        dict: Updated latest_data with MT5 data integrated
    """
    try:
        # Check if MT5 standardized data exists
        mt5_file = 'data/mt5/mt5_standardized.csv'
        if not os.path.exists(mt5_file):
            print("MT5 data not found, continuing with existing data...")
            return latest_data
            
        print("Processing MT5 data...")
        mt5_df = pd.read_csv(mt5_file, parse_dates=['timestamp'])
        
        if mt5_df.empty:
            print("MT5 data file is empty, continuing with existing data...")
            return latest_data
            
        # Process MT5 data similar to other asset classes
        # For now, we'll treat all MT5 data as forex/indices depending on symbol patterns
        # Later we can categorize more precisely
        
        # Add timezone if not present
        if mt5_df['timestamp'].dt.tz is None:
            # Assume MT5 data is in UTC (common for financial data)
            mt5_df['timestamp'] = mt5_df['timestamp'].dt.tz_localize('UTC')
        
        # Convert to target timezone
        target_tz = 'Asia/Kolkata'
        mt5_df['timestamp'] = mt5_df['timestamp'].dt.tz_convert(target_tz)
        
        # Create MT5 dataframes in the same format as existing data
        mt5_latest = mt5_df.loc[mt5_df.groupby('symbol')['timestamp'].idxmax()]
        mt5_formatted = mt5_latest[['symbol', 'timestamp', 'open', 'high', 'low', 'close']]
        
        # For now, we'll add MT5 data as a separate category
        # Later we can merge it with existing categories
        latest_data['mt5'] = mt5_formatted
        
        print(f"✓ Processed MT5 data for {len(mt5_formatted)} symbols")
        return latest_data
        
    except Exception as e:
        print(f"Warning: Error processing MT5 data: {str(e)}")
        return latest_data

def read_and_align_data():
    """
    Read all asset class CSVs, align timezones, and select the latest data for each asset.
    Returns a dictionary with latest data for each asset class.
    """
    data_files = {
        'bonds': {'file': 'data/bonds_15min.csv', 'tz_source': 'America/New_York'},
        'commodities': {'file': 'data/commodities_15min.csv', 'tz_source': 'UTC'},
        'crypto': {'file': 'data/crypto_15min.csv', 'tz_source': 'UTC'},
        'forex': {'file': 'data/forex_15min.csv', 'tz_source': 'UTC'},
        'indices': {'file': 'data/indices_15min.csv', 'tz_source': 'America/New_York'},
        'sector_s1': {'file': 'data/sector_etf_15min.csv', 'tz_source': 'America/New_York'},
        'sector_s2': {'file': 'data/sector2_etf_15min.csv', 'tz_source': 'America/New_York'},
        'vix': {'file': 'data/vix_15min.csv', 'tz_source': 'America/New_York'}
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

    # Process MT5 data and integrate it
    latest_data = process_mt5_data(latest_data)

    output_path = 'data/latest_market_data.pkl'
    with open(output_path, 'wb') as f:
        pickle.dump(latest_data, f)
    print(f"\n✓ Latest data saved to '{output_path}' for analysis")

if __name__ == "__main__":
    read_and_align_data()
