import pandas as pd
from datetime import datetime
import pytz
import pickle
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

MT5_SYMBOL_MAP = {
    'US500m': 'S&P 500',
    'US30m': 'Dow Jones Industrial Average',
    'USTECm': 'Nasdaq 100',
    'DE30m': 'DAX',
    'UK100m': 'UK 100',
    'JP225m': 'Japan (Nikkei)',
    'XAUUSDm': 'XAU/USD',
    'EURUSDm': 'EUR/USD',
    'GBPUSDm': 'GBP/USD',
    'USDJPYm': 'USD/JPY',
    'AUDUSDm': 'AUD/USD',
    'USDCADm': 'USD/CAD',
    'USDCHFm': 'USD/CHF',
    'NZDUSDm': 'NZD/USD'
}

T12_TO_NAME_MAP = {
    'SPY': 'S&P 500', 'QQQ': 'Nasdaq 100', 'DIA': 'Dow Jones Industrial Average', 'IWM': 'Russell 2000',
    'EWU': 'United Kingdom (FTSE)', 'EWJ': 'Japan (Nikkei)', 'FEZ': 'Euro Stoxx 50',
    'DAX': 'Germany (DAX)', 'EEM': 'Emerging Markets', 'INDA': 'India (MSCI India)',
    'MCHI': 'China (MSCI China)', 'EWG': 'Germany Equity', 'EWQ': 'France',
    'EWS': 'Singapore', 'EWA': 'Australia',
    'GLD': 'Gold', 'SLV': 'Silver', 'USO': 'Crude Oil',
    'EUR/USD': 'EUR/USD', 'GBP/USD': 'GBP/USD', 'USD/JPY': 'USD/JPY', 'AUD/USD': 'AUD/USD',
    'USD/CAD': 'USD/CAD', 'USD/CHF': 'USD/CHF', 'NZD/USD': 'NZD/USD'
}

def load_mt5_data(directory="data/mt5/"):
    """
    Loads the latest MT5 CSV, renames symbols, and checks for staleness.
    """
    try:
        files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.csv')]
        if not files:
            logger.warning("No MT5 CSV files found.")
            return None

        latest_file = max(files, key=os.path.getctime)
        logger.info(f"Loading MT5 data from {latest_file}")

        df = pd.read_csv(latest_file)

        # Check for staleness
        df['timestamp'] = pd.to_datetime(df['time'])
        latest_timestamp = df['timestamp'].max()
        if (datetime.now() - latest_timestamp).total_seconds() > 24 * 3600:
            logger.warning("MT5 data is stale (older than 24 hours).")
            return None

        df['symbol'] = df['symbol'].map(MT5_SYMBOL_MAP)
        df = df.dropna(subset=['symbol']) # Drop symbols not in the map

        return df
    except Exception as e:
        logger.error(f"Error loading MT5 data: {e}")
        return None

def read_and_align_data():
    """
    Read all asset class CSVs, align timezones, and select the latest data for each asset.
    Returns a dictionary with latest data for each asset class.
    """
    mt5_data = load_mt5_data()
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
    mt5_covered_assets = ['indices', 'forex', 'commodities']

    for asset_class, info in data_files.items():
        if asset_class in mt5_covered_assets and mt5_data is not None:
            # Use MT5 data for this asset class
            asset_symbols = mt5_data[mt5_data['symbol'].isin(MT5_SYMBOL_MAP.values())]

            # Get the symbols for the current asset class
            # This is a bit of a simplification, you might need a more robust way to map symbols to asset classes
            if asset_class == 'indices':
                symbols_in_class = [s for s in T12_TO_NAME_MAP.values() if s in MT5_SYMBOL_MAP.values()]
            elif asset_class == 'forex':
                symbols_in_class = [s for s in T12_TO_NAME_MAP.values() if s in MT5_SYMBOL_MAP.values() and '/' in s and 'XAU' not in s]
            elif asset_class == 'commodities':
                symbols_in_class = [s for s in T12_TO_NAME_MAP.values() if s in MT5_SYMBOL_MAP.values() and ('Gold' in s or 'Silver' in s or 'Crude' in s)]

            class_df = mt5_data[mt5_data['symbol'].isin(symbols_in_class)].copy()
            class_df['timestamp'] = class_df['timestamp'].dt.tz_localize('UTC').dt.tz_convert(target_tz)
            latest = class_df.loc[class_df.groupby('symbol')['timestamp'].idxmax()]
            latest_data[asset_class] = latest[['symbol', 'timestamp', 'open', 'high', 'low', 'close']]
            logger.info(f"Using 24x5 MT5 data for {asset_class}")

            # Fallback for symbols not in MT5
            try:
                t12_df = pd.read_csv(info['file'], parse_dates=['timestamp'])
                if t12_df.empty:
                    continue

                # Determine the symbol column
                symbol_col = None
                if asset_class == 'indices': symbol_col = 'symbol'
                elif asset_class == 'forex': symbol_col = 'pair'
                elif asset_class == 'commodities': symbol_col = 'commodity'

                if symbol_col:
                    # Create a reverse map from report name to T12 symbol
                    name_to_t12_map = {v: k for k, v in T12_TO_NAME_MAP.items()}

                    t12_df['report_symbol'] = t12_df[symbol_col].map(T12_TO_NAME_MAP)

                    missing_symbols = [s for s in t12_df['report_symbol'].unique() if s not in latest_data[asset_class]['symbol'].values]

                    if missing_symbols:
                        logger.warning(f"MT5 data for {missing_symbols} not found. Falling back to Twelve Data.")

                        if t12_df['timestamp'].dt.tz is None:
                           t12_df['timestamp'] = t12_df['timestamp'].dt.tz_localize(info['tz_source'])
                        t12_df['timestamp'] = t12_df['timestamp'].dt.tz_convert(target_tz)

                        fallback_df = t12_df[t12_df['report_symbol'].isin(missing_symbols)]
                        latest_fallback = fallback_df.loc[fallback_df.groupby('report_symbol')['timestamp'].idxmax()]
                        latest_fallback = latest_fallback.rename(columns={'report_symbol': 'symbol'})

                        latest_data[asset_class] = pd.concat([latest_data[asset_class], latest_fallback[['symbol', 'timestamp', 'open', 'high', 'low', 'close']]], ignore_index=True)

            except FileNotFoundError:
                logger.warning(f"{info['file']} not found for fallback, skipping.")
            except Exception as e:
                logger.error(f"Error processing fallback for {asset_class}: {e}")

        else:
            # Process non-MT5 asset classes as before
            try:
                df = pd.read_csv(info['file'], parse_dates=['timestamp'])
                if df.empty:
                    logger.warning(f"{info['file']} is empty")
                    continue
                if df['timestamp'].dt.tz is None:
                    df['timestamp'] = df['timestamp'].dt.tz_localize(info['tz_source'])
                df['timestamp'] = df['timestamp'].dt.tz_convert(target_tz)

                if asset_class == 'bonds':
                    latest = df.loc[df.groupby('bond')['timestamp'].idxmax()]
                    latest_data[asset_class] = latest[['bond', 'timestamp', 'yield']].rename(columns={'bond': 'symbol', 'yield': 'value'})
                elif asset_class == 'crypto':
                    latest = df.loc[df.groupby('crypto')['timestamp'].idxmax()]
                    latest_data[asset_class] = latest[['crypto', 'timestamp', 'open', 'high', 'low', 'close']].rename(columns={'crypto': 'symbol'})
                elif asset_class.startswith('sector'):
                    latest = df.loc[df.groupby('sector_etf')['timestamp'].idxmax()]
                    latest_data[asset_class] = latest[['sector_etf', 'timestamp', 'open', 'high', 'low', 'close']].rename(columns={'sector_etf': 'symbol'})
                elif asset_class == 'vix':
                    latest = df.loc[df.groupby('vix_etf')['timestamp'].idxmax()]
                    latest_data[asset_class] = latest[['vix_etf', 'timestamp', 'open', 'high', 'low', 'close']].rename(columns={'vix_etf': 'symbol'})

            except FileNotFoundError:
                logger.warning(f"{info['file']} not found, skipping {asset_class}")
            except Exception as e:
                logger.error(f"Error processing {asset_class}: {e}")

    # Combine sector_s1 and sector_s2
    if 'sector_s1' in latest_data and 'sector_s2' in latest_data:
        sectors_combined = pd.concat([latest_data['sector_s1'], latest_data['sector_s2']], ignore_index=True)
        # Remove duplicates by keeping the most recent timestamp for each symbol
        sectors_combined = sectors_combined.loc[sectors_combined.groupby('symbol')['timestamp'].idxmax()]
        latest_data['sectors'] = sectors_combined
        latest_data.pop('sector_s1', None)
        latest_data.pop('sector_s2', None)

    output_path = 'data/latest_market_data.pkl'
    with open(output_path, 'wb') as f:
        pickle.dump(latest_data, f)
    print(f"\n✓ Latest data saved to '{output_path}' for analysis")

if __name__ == "__main__":
    read_and_align_data()
