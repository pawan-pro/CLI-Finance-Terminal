import pandas as pd
from datetime import datetime
import pytz
import pickle
import os

def switch_to_mt5_based_on_mapping(latest_data):
    """
    Switches data source from T12 to MT5 for symbols defined in symbol_mapping.csv
    and adds new symbols as specified.
    """
    base_path = os.path.dirname(__file__)
    mapping_file = os.path.join(base_path, 'data/mt5/symbol_mapping.csv')
    if not os.path.exists(mapping_file):
        print(f"Warning: Symbol mapping file not found at {mapping_file}. Skipping data source switch.")
        return latest_data

    if 'mt5' not in latest_data or latest_data['mt5'].empty:
        print("Warning: No MT5 data available to perform the switch.")
        return latest_data

    print("Applying MT5 symbol mapping...")
    mapping_df = pd.read_csv(mapping_file, skipinitialspace=True)
    mt5_data = latest_data['mt5'].copy()

    # This mapping helps connect the descriptive name in the CSV to the T12 symbol used in the data files.
    # This is based on the SYMBOL_TO_NAME_MAP in daily_report-i.py
    name_to_t12_symbol = {
        'S&P 500': 'SPY', 'Nasdaq 100': 'QQQ', 'Dow Jones Industrial Average': 'DIA',
        'Russell 2000': 'IWM', 'United Kingdom (FTSE)': 'EWU', 'Japan (Nikkei)': 'EWJ',
        'Euro Stoxx 50': 'FEZ', 'Germany (DAX)': 'DAX', 'Emerging Markets': 'EEM',
        'India (MSCI India)': 'INDA', 'China (MSCI China)': 'MCHI', 'Germany Equity': 'EWG',
        'France': 'EWQ', 'Australia': 'EWA'
        # Forex and others can be handled by logic, e.g. 'EUR/USD' -> 'EURUSD'
    }

    asset_type_map = {
        'forex': 'forex', 'cfd': 'indices', 'commodity': 'commodities', 'crypto': 'crypto'
    }

    for _, row in mapping_df.iterrows():
        report_name = row['Report Symbol/name'].strip()
        mt5_symbol = row['Symbol']

        if mt5_symbol == 'NA' or pd.isna(mt5_symbol):
            continue

        asset_type = str(row['Asset Type']).lower().strip()
        notes = str(row['Notes'])

        mt5_row_df = mt5_data[mt5_data['symbol'] == mt5_symbol]
        if mt5_row_df.empty:
            print(f"Info: MT5 data for '{mt5_symbol}' not in latest fetch. Skipping.")
            continue

        asset_class_key = asset_type_map.get(asset_type)
        if not asset_class_key:
            print(f"Warning: Unknown asset type '{asset_type}' for '{report_name}'.")
            continue

        # Ensure the target asset class dataframe exists
        if asset_class_key not in latest_data:
            print(f"Info: Creating new asset class dataframe for '{asset_class_key}'.")
            latest_data[asset_class_key] = pd.DataFrame(columns=mt5_row_df.columns)

        # --- Add new symbols ---
        if "to be added" in notes:
            if mt5_symbol not in latest_data[asset_class_key]['symbol'].values:
                latest_data[asset_class_key] = pd.concat(
                    [latest_data[asset_class_key], mt5_row_df], ignore_index=True
                )
                print(f"✓ Added new symbol '{mt5_symbol}' to '{asset_class_key}'.")
            continue

        # --- Replace existing symbols ---
        t12_symbol_to_remove = name_to_t12_symbol.get(report_name)
        if not t12_symbol_to_remove and asset_type == 'forex':
            t12_symbol_to_remove = report_name.replace('/', '')

        if not t12_symbol_to_remove:
            print(f"Info: No T12 symbol found for '{report_name}'. Adding MT5 symbol '{mt5_symbol}' directly.")
        else:
            df = latest_data[asset_class_key]
            if t12_symbol_to_remove in df['symbol'].values:
                df = df[df['symbol'] != t12_symbol_to_remove]
                latest_data[asset_class_key] = df
                print(f"✓ Removed T12 symbol '{t12_symbol_to_remove}' from '{asset_class_key}'.")

        # Add the MT5 data, ensuring no duplicates
        if mt5_symbol not in latest_data[asset_class_key]['symbol'].values:
            latest_data[asset_class_key] = pd.concat(
                [latest_data[asset_class_key], mt5_row_df], ignore_index=True
            )
            print(f"✓ Added MT5 symbol '{mt5_symbol}' to '{asset_class_key}'.")

    latest_data.pop('mt5', None)
    print("✓ MT5 data has been integrated into respective asset classes.")

    return latest_data


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
        base_path = os.path.dirname(__file__)
        mt5_file = os.path.join(base_path, 'data/mt5/mt5_standardized.csv')
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
    # Correct file paths to be relative to the script's location
    base_path = os.path.dirname(__file__)
    data_files = {
        'bonds': {'file': os.path.join(base_path, 'data/bonds_15min.csv'), 'tz_source': 'America/New_York'},
        'commodities': {'file': os.path.join(base_path, 'data/commodities_15min.csv'), 'tz_source': 'UTC'},
        'crypto': {'file': os.path.join(base_path, 'data/crypto_15min.csv'), 'tz_source': 'UTC'},
        'forex': {'file': os.path.join(base_path, 'data/forex_15min.csv'), 'tz_source': 'UTC'},
        'indices': {'file': os.path.join(base_path, 'data/indices_15min.csv'), 'tz_source': 'America/New_York'},
        'sector_s1': {'file': os.path.join(base_path, 'data/sector_etf_15min.csv'), 'tz_source': 'America/New_York'},
        'sector_s2': {'file': os.path.join(base_path, 'data/sector2_etf_15min.csv'), 'tz_source': 'America/New_York'},
        'vix': {'file': os.path.join(base_path, 'data/vix_15min.csv'), 'tz_source': 'America/New_York'}
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

    # Process MT5 data first to make it available for switching
    latest_data = process_mt5_data(latest_data)

    # Switch data source to MT5 based on the mapping file
    latest_data = switch_to_mt5_based_on_mapping(latest_data)

    output_path = os.path.join(base_path, 'data/latest_market_data.pkl')
    with open(output_path, 'wb') as f:
        pickle.dump(latest_data, f)
    print(f"\n✓ Latest data saved to '{output_path}' for analysis")

if __name__ == "__main__":
    read_and_align_data()
