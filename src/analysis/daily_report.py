import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from scipy import stats

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Try to import real MT5, fallback to mock if not available
try:
    # First try direct import (for Windows or Wine with proper setup)
    import MetaTrader5
    mt5 = MetaTrader5
    MT5_AVAILABLE = True
    print("Using real MT5 connection")
except ImportError:
    try:
        # Try importing Wine MT5 connector as mt5
        from src.data.providers.wine_mt5_connector import WineMT5Connector
        # Create a wrapper to make it compatible with MT5 API
        import src.data.providers.wine_mt5_connector as mt5
        MT5_AVAILABLE = True
        print("Using real MT5 connection (Wine connector)")
    except ImportError:
        # Use mock MT5 for development/testing
        import src.data.providers.mock_mt5 as mt5
        MT5_AVAILABLE = False
        print("Warning: Using mock MT5. For production with Wine, ensure MT5 Python package is properly installed in Wine environment.")

# Local imports
from src.data.providers.mt5_data import MT5DataFetcher
from src.data.providers.calendar_data import EconomicCalendarFetcher, MT5CalendarFetcher
from src.data.providers.advanced_mt5_calendar import AdvancedMT5CalendarExtractor
from src.analysis.volatility import VolatilityCalculator
from src.analysis.charts import MarketChartGenerator
from src.analysis.professional_pdf_report import ProfessionalPDFReportGenerator
from src.analysis.advanced_analytics import AdvancedMarketAnalytics
from src.analysis.institutional_analytics import InstitutionalMarketAnalytics
from src.analysis.enhanced_top_movers import EnhancedTopMoversAnalyzer
from src.analysis.institutional_calendar import InstitutionalCalendarAnalyzer
from src.analysis.enhanced_institutional_pdf import EnhancedInstitutionalPDFReportGenerator
from src.analysis.llm_integration import LLMExecutiveSummaryGenerator
import subprocess
import json
import pandas as pd
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DailyInvestmentReportGenerator:
    """Class to generate daily investment reports with professional formatting and advanced market analytics"""
    
    def __init__(self, use_wine_mt5: bool = False):
        """Initialize the report generator"""
        self.use_wine_mt5 = use_wine_mt5
        
        # Initialize data fetchers
        self.mt5_fetcher = MT5DataFetcher(use_wine_mt5=use_wine_mt5)
        self.calendar_fetcher = EconomicCalendarFetcher()
        self.mt5_calendar_fetcher = MT5CalendarFetcher()
        self.advanced_calendar_extractor = AdvancedMT5CalendarExtractor()
        self.volatility_calculator = VolatilityCalculator()
        self.chart_generator = MarketChartGenerator()
        self.advanced_analytics = AdvancedMarketAnalytics()
        self.institutional_analytics = InstitutionalMarketAnalytics()
        
        # Initialize LLM executive summary generator
        self.llm_generator = LLMExecutiveSummaryGenerator()
        
        # Define default symbols to track with available symbols from MT5
        # Note: Indices symbols like US500Roll.sd may not be available in all MT5 installations
        # We'll use what's available and fall back to other symbols
        self.major_indices = ['US500Roll', 'US30Roll', 'UT100Roll', 'DE40Roll', 'UK100Roll']  # Added US500Roll back since it's now working
        self.major_currencies = ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD']
        self.commodities = ['XAUUSD', 'XAGUSD', 'USOIL', 'UKOIL']  # Keep XAUUSD for gold
        # Use bond ETFs as proxies for bonds (these may not be available in MT5)
        self.bonds = ['TLT', 'IEF', 'SHY', 'LQD']  # Treasury ETFs as bond proxies
        self.volatility_symbols = ['VIX', 'VXN', 'VXD']

    def _get_wine_symbol_info(self, symbol: str) -> Optional[Dict]:
        """Get symbol info from Wine MT5"""
        if not self.use_wine_mt5:
            return None
        
        # Use the Wine MT5 connector directly instead of running a script
        try:
            from src.data.providers.wine_mt5_connector import wine_mt5_connector
            symbol_info = wine_mt5_connector.get_symbol_info(symbol)
            return symbol_info
        except Exception as e:
            logger.error(f"Error getting symbol info for {symbol} from Wine MT5: {e}")
            return None

    def _get_wine_historical_data(self, symbol: str, timeframe: int, start_time: datetime, end_time: datetime) -> pd.DataFrame:
        """Get historical data from Wine MT5"""
        if not self.use_wine_mt5:
            return pd.DataFrame()
        
        # Use the Wine MT5 connector directly instead of running a script
        try:
            from src.data.providers.wine_mt5_connector import wine_mt5_connector
            rates = wine_mt5_connector.copy_rates_range(symbol, timeframe, start_time, end_time)
            if rates:
                # Convert to DataFrame
                df = pd.DataFrame(rates)
                # Convert time column to datetime
                df['time'] = pd.to_datetime(df['time'], unit='s')
                return df
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol} from Wine MT5: {e}")
            return pd.DataFrame()

    def _calculate_24h_percentage_change(self, symbol: str) -> float:
        """Calculate 24-hour percentage change for a symbol"""
        try:
            from datetime import datetime, timedelta
            
            # Get data for the last 24 hours
            end_time = datetime.now()
            start_time = end_time - timedelta(days=1)
            
            # Use Wine MT5 if enabled, otherwise use regular MT5 fetcher
            if self.use_wine_mt5:
                try:
                    # Try to get historical data from Wine MT5
                    historical_data = self._get_wine_historical_data(symbol, mt5.TIMEFRAME_M15, start_time, end_time)
                except Exception as e:
                    logger.warning(f"Error fetching historical data for {symbol} from Wine MT5: {e}")
                    # Fallback to regular MT5 fetcher
                    historical_data = self.mt5_fetcher.fetch_historical_data(symbol, mt5.TIMEFRAME_M15, start_time, end_time)
            else:
                # Use regular MT5 fetcher
                historical_data = self.mt5_fetcher.fetch_historical_data(symbol, mt5.TIMEFRAME_M15, start_time, end_time)
            
            if not historical_data.empty and len(historical_data) > 1:
                # Get the first and last closing prices
                first_price = historical_data['close'].iloc[0]
                last_price = historical_data['close'].iloc[-1]
                
                if first_price != 0:
                    # Calculate percentage change
                    pct_change = ((last_price - first_price) / first_price) * 100
                    return pct_change
            
            return 0.0
        except Exception as e:
            logger.warning(f"Error calculating 24H percentage change for {symbol}: {e}")
            return 0.0

    def get_market_status(self) -> Dict:
        """Get current market status"""
        try:
            # In a real implementation, this would check actual market hours
            # For now, we'll return mock data
            return {
                'status': 'Open' if 9 <= datetime.now().hour <= 16 else 'Closed',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'timezone': 'UTC'
            }
        except Exception as e:
            logger.error(f"Error getting market status: {e}")
            return {
                'status': 'Unknown',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'timezone': 'UTC'
            }

    def get_major_indices_data(self) -> pd.DataFrame:
        """Get data for major indices"""
        indices_data = []
        
        # Use Wine MT5 if enabled, otherwise use regular MT5 fetcher
        if self.use_wine_mt5:
            for symbol in self.major_indices:
                try:
                    # Try to get symbol info from Wine MT5
                    info = self._get_wine_symbol_info(symbol)
                    if info:
                        # Calculate 24H % change
                        pct_change = self._calculate_24h_percentage_change(symbol)
                        info['pct_change_24h'] = pct_change
                        indices_data.append(info)
                except Exception as e:
                    logger.warning(f"Error fetching data for {symbol} from Wine MT5: {e}")
                    # Fallback to regular MT5 fetcher
                    try:
                        info = self.mt5_fetcher.get_symbol_info(symbol)
                        if info:
                            # Calculate 24H % change
                            pct_change = self._calculate_24h_percentage_change(symbol)
                            info['pct_change_24h'] = pct_change
                            indices_data.append(info)
                    except Exception as e2:
                        logger.warning(f"Error fetching data for {symbol} from regular MT5: {e2}")
        else:
            # Use regular MT5 fetcher
            for symbol in self.major_indices:
                try:
                    # Try to get symbol info
                    info = self.mt5_fetcher.get_symbol_info(symbol)
                    if info:
                        # Calculate 24H % change
                        pct_change = self._calculate_24h_percentage_change(symbol)
                        info['pct_change_24h'] = pct_change
                        indices_data.append(info)
                except Exception as e:
                    logger.warning(f"Error fetching data for {symbol}: {e}")
        
        # Calculate Price column with fallback for zero values
        for item in indices_data:
            if 'ask' in item and 'bid' in item:
                # Check if both ask and bid are zero, try to use last price
                if item['ask'] == 0 and item['bid'] == 0:
                    if 'last' in item and item['last'] != 0:
                        item['Price'] = item['last']
                    else:
                        # Fallback to individual values if available
                        item['Price'] = max(item.get('ask', 0), item.get('bid', 0), item.get('last', 0))
                else:
                    item['Price'] = (item['ask'] + item['bid']) / 2
            elif 'last' in item:
                item['Price'] = item['last']
            else:
                item['Price'] = item.get('ask', item.get('bid', 0))

        return pd.DataFrame(indices_data)

    def get_currency_data(self) -> pd.DataFrame:
        """Get data for major currencies"""
        currency_data = []
        
        # Use Wine MT5 if enabled, otherwise use regular MT5 fetcher
        if self.use_wine_mt5:
            for symbol in self.major_currencies:
                try:
                    # Try to get symbol info from Wine MT5
                    info = self._get_wine_symbol_info(symbol)
                    if info:
                        # Calculate 24H % change
                        pct_change = self._calculate_24h_percentage_change(symbol)
                        info['pct_change_24h'] = pct_change
                        currency_data.append(info)
                except Exception as e:
                    logger.warning(f"Error fetching data for {symbol} from Wine MT5: {e}")
                    # Fallback to regular MT5 fetcher
                    try:
                        info = self.mt5_fetcher.get_symbol_info(symbol)
                        if info:
                            # Calculate 24H % change
                            pct_change = self._calculate_24h_percentage_change(symbol)
                            info['pct_change_24h'] = pct_change
                            currency_data.append(info)
                    except Exception as e2:
                        logger.warning(f"Error fetching data for {symbol} from regular MT5: {e2}")
        else:
            # Use regular MT5 fetcher
            for symbol in self.major_currencies:
                try:
                    # Try to get symbol info
                    info = self.mt5_fetcher.get_symbol_info(symbol)
                    if info:
                        # Calculate 24H % change
                        pct_change = self._calculate_24h_percentage_change(symbol)
                        info['pct_change_24h'] = pct_change
                        currency_data.append(info)
                except Exception as e:
                    logger.warning(f"Error fetching data for {symbol}: {e}")
        
        # Calculate Price column with fallback for zero values
        for item in currency_data:
            if 'ask' in item and 'bid' in item:
                # Check if both ask and bid are zero, try to use last price
                if item['ask'] == 0 and item['bid'] == 0:
                    if 'last' in item and item['last'] != 0:
                        item['Price'] = item['last']
                    else:
                        # Fallback to individual values if available
                        item['Price'] = max(item.get('ask', 0), item.get('bid', 0), item.get('last', 0))
                else:
                    item['Price'] = (item['ask'] + item['bid']) / 2
            elif 'last' in item:
                item['Price'] = item['last']
            else:
                item['Price'] = item.get('ask', item.get('bid', 0))

        return pd.DataFrame(currency_data)

    def get_commodities_data(self) -> pd.DataFrame:
        """Get data for commodities"""
        commodities_data = []
        
        # Use Wine MT5 if enabled, otherwise use regular MT5 fetcher
        if self.use_wine_mt5:
            for symbol in self.commodities:
                try:
                    # Try to get symbol info from Wine MT5
                    info = self._get_wine_symbol_info(symbol)
                    if info:
                        # Calculate 24H % change
                        pct_change = self._calculate_24h_percentage_change(symbol)
                        info['pct_change_24h'] = pct_change
                        commodities_data.append(info)
                except Exception as e:
                    logger.warning(f"Error fetching data for {symbol} from Wine MT5: {e}")
                    # Fallback to regular MT5 fetcher
                    try:
                        info = self.mt5_fetcher.get_symbol_info(symbol)
                        if info:
                            # Calculate 24H % change
                            pct_change = self._calculate_24h_percentage_change(symbol)
                            info['pct_change_24h'] = pct_change
                            commodities_data.append(info)
                    except Exception as e2:
                        logger.warning(f"Error fetching data for {symbol} from regular MT5: {e2}")
        else:
            # Use regular MT5 fetcher
            for symbol in self.commodities:
                try:
                    # Try to get symbol info
                    info = self.mt5_fetcher.get_symbol_info(symbol)
                    if info:
                        # Calculate 24H % change
                        pct_change = self._calculate_24h_percentage_change(symbol)
                        info['pct_change_24h'] = pct_change
                        commodities_data.append(info)
                except Exception as e:
                    logger.warning(f"Error fetching data for {symbol}: {e}")
        
        # Calculate Price column with fallback for zero values
        for item in commodities_data:
            if 'ask' in item and 'bid' in item:
                # Check if both ask and bid are zero, try to use last price
                if item['ask'] == 0 and item['bid'] == 0:
                    if 'last' in item and item['last'] != 0:
                        item['Price'] = item['last']
                    else:
                        # Fallback to individual values if available
                        item['Price'] = max(item.get('ask', 0), item.get('bid', 0), item.get('last', 0))
                else:
                    item['Price'] = (item['ask'] + item['bid']) / 2
            elif 'last' in item:
                item['Price'] = item['last']
            else:
                item['Price'] = item.get('ask', item.get('bid', 0))

        return pd.DataFrame(commodities_data)

    def get_bonds_data(self) -> pd.DataFrame:
        """Get data for bonds (using ETF proxies)"""
        bonds_data = []
        
        # Use Wine MT5 if enabled, otherwise use regular MT5 fetcher
        if self.use_wine_mt5:
            for symbol in self.bonds:
                try:
                    # Try to get symbol info from Wine MT5
                    info = self._get_wine_symbol_info(symbol)
                    if info:
                        # Calculate 24H % change
                        pct_change = self._calculate_24h_percentage_change(symbol)
                        info['pct_change_24h'] = pct_change
                        bonds_data.append(info)
                except Exception as e:
                    logger.warning(f"Error fetching data for {symbol} from Wine MT5: {e}")
                    # Fallback to regular MT5 fetcher
                    try:
                        info = self.mt5_fetcher.get_symbol_info(symbol)
                        if info:
                            # Calculate 24H % change
                            pct_change = self._calculate_24h_percentage_change(symbol)
                            info['pct_change_24h'] = pct_change
                            bonds_data.append(info)
                    except Exception as e2:
                        logger.warning(f"Error fetching data for {symbol} from regular MT5: {e2}")
        else:
            # Use regular MT5 fetcher
            for symbol in self.bonds:
                try:
                    # Try to get symbol info
                    info = self.mt5_fetcher.get_symbol_info(symbol)
                    if info:
                        # Calculate 24H % change
                        pct_change = self._calculate_24h_percentage_change(symbol)
                        info['pct_change_24h'] = pct_change
                        bonds_data.append(info)
                except Exception as e:
                    logger.warning(f"Error fetching data for {symbol}: {e}")
        
        # Calculate Price column with fallback for zero values
        for item in bonds_data:
            if 'ask' in item and 'bid' in item:
                # Check if both ask and bid are zero, try to use last price
                if item['ask'] == 0 and item['bid'] == 0:
                    if 'last' in item and item['last'] != 0:
                        item['Price'] = item['last']
                    else:
                        # Fallback to individual values if available
                        item['Price'] = max(item.get('ask', 0), item.get('bid', 0), item.get('last', 0))
                else:
                    item['Price'] = (item['ask'] + item['bid']) / 2
            elif 'last' in item:
                item['Price'] = item['last']
            else:
                item['Price'] = item.get('ask', item.get('bid', 0))

        return pd.DataFrame(bonds_data)

    def get_volatility_data(self) -> pd.DataFrame:
        """Get volatility indices data"""
        volatility_data = []
        
        # Use Wine MT5 if enabled, otherwise use regular MT5 fetcher
        if self.use_wine_mt5:
            for symbol in self.volatility_symbols:
                try:
                    # Try to get symbol info from Wine MT5
                    info = self._get_wine_symbol_info(symbol)
                    if info:
                        volatility_data.append(info)
                except Exception as e:
                    logger.warning(f"Error fetching data for {symbol} from Wine MT5: {e}")
                    # Fallback to regular MT5 fetcher
                    try:
                        info = self.mt5_fetcher.get_symbol_info(symbol)
                        if info:
                            volatility_data.append(info)
                    except Exception as e2:
                        logger.warning(f"Error fetching data for {symbol} from regular MT5: {e2}")
        else:
            # Use regular MT5 fetcher
            for symbol in self.volatility_symbols:
                try:
                    # Try to get symbol info
                    info = self.mt5_fetcher.get_symbol_info(symbol)
                    if info:
                        volatility_data.append(info)
                except Exception as e:
                    logger.warning(f"Error fetching data for {symbol}: {e}")
        
        # Calculate Price column with fallback for zero values
        for item in volatility_data:
            if 'ask' in item and 'bid' in item:
                # Check if both ask and bid are zero, try to use last price
                if item['ask'] == 0 and item['bid'] == 0:
                    if 'last' in item and item['last'] != 0:
                        item['Price'] = item['last']
                    else:
                        # Fallback to individual values if available
                        item['Price'] = max(item.get('ask', 0), item.get('bid', 0), item.get('last', 0))
                else:
                    item['Price'] = (item['ask'] + item['bid']) / 2
            elif 'last' in item:
                item['Price'] = item['last']
            else:
                item['Price'] = item.get('ask', item.get('bid', 0))

        return pd.DataFrame(volatility_data)

    def get_top_movers(self, data: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
        """Get top gainers and losers based on 24-hour price change."""
        if data is None or data.empty:
            return pd.DataFrame()

        data = data.copy()
        data['pct_change'] = 0.0

        for index, row in data.iterrows():
            symbol = row.get('name', '')
            if not symbol:
                continue
                
            try:
                # Use the same 24H percentage change calculation as used for the main table
                pct_change = self._calculate_24h_percentage_change(symbol)
                data.loc[index, 'pct_change'] = pct_change
            except Exception as e:
                logger.warning(f"Error calculating 24h change for {symbol}: {e}")

        # Sort by absolute percentage change
        data['abs_pct_change'] = data['pct_change'].abs()
        top_movers = data.nlargest(top_n, 'abs_pct_change')

        # Make sure we have the required columns
        columns_to_return = ['name', 'Price', 'pct_change']
        available_columns = [col for col in columns_to_return if col in top_movers.columns]
        if not available_columns:
            # If none of the expected columns are available, return an empty DataFrame with the expected structure
            return pd.DataFrame(columns=['name', 'Price', 'pct_change'])
        
        return top_movers[available_columns] if not top_movers.empty else pd.DataFrame(columns=['name', 'Price', 'pct_change'])

    def generate_charts(self, save_dir: str = "./reports/charts") -> List[str]:
        """Generate key market charts with specific timeframes and intervals"""
        chart_files = []
        
        # Create save directory if it doesn't exist
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        # Define symbols to chart (major indices, currencies, commodities, bonds, and top movers)
        all_data = []
        
        # Get data for all symbol types
        indices_data = self.get_major_indices_data()
        currency_data = self.get_currency_data()
        commodities_data = self.get_commodities_data()
        bonds_data = self.get_bonds_data()
        
        # Ensure all dataframes are valid before concatenating
        dataframes = []
        if isinstance(indices_data, pd.DataFrame) and not indices_data.empty:
            dataframes.append(indices_data)
        if isinstance(currency_data, pd.DataFrame) and not currency_data.empty:
            dataframes.append(currency_data)
        if isinstance(commodities_data, pd.DataFrame) and not commodities_data.empty:
            dataframes.append(commodities_data)
        if isinstance(bonds_data, pd.DataFrame) and not bonds_data.empty:
            dataframes.append(bonds_data)
        
        top_movers = pd.DataFrame()
        if dataframes:
            combined_data = pd.concat(dataframes, ignore_index=True)
            if not combined_data.empty:
                top_movers = self.get_top_movers(combined_data)
        
        # Combine all symbols
        all_symbols = []
        if not indices_data.empty:
            all_symbols.extend(indices_data['name'].tolist())
        if not currency_data.empty:
            all_symbols.extend(currency_data['name'].tolist())
        if not commodities_data.empty:
            all_symbols.extend(commodities_data['name'].tolist())
        if not bonds_data.empty:
            all_symbols.extend(bonds_data['name'].tolist())
        if not top_movers.empty:
            all_symbols.extend(top_movers['name'].tolist())
        
        # Remove duplicates and limit to top symbols
        all_symbols = list(dict.fromkeys(all_symbols))[:10]  # Limit to 10 symbols
        
        # Generate specific charts for each symbol
        for symbol in all_symbols:
            try:
                symbol_chart_files = []
                
                # 1. 1 Day chart with 15-minute interval
                end_time = datetime.now()
                start_time = end_time - timedelta(days=1)
                if self.use_wine_mt5:
                    try:
                        data_15m = self._get_wine_historical_data(
                            symbol, mt5.TIMEFRAME_M15, start_time, end_time)
                    except Exception as e:
                        logger.warning(f"Error fetching 15M data for {symbol} from Wine MT5: {e}")
                        data_15m = self.mt5_fetcher.fetch_historical_data(
                            symbol, mt5.TIMEFRAME_M15, start_time, end_time)
                else:
                    data_15m = self.mt5_fetcher.fetch_historical_data(
                        symbol, mt5.TIMEFRAME_M15, start_time, end_time)
                
                if not data_15m.empty:
                    # Check if we have OHLC data for candlestick chart
                    if all(col in data_15m.columns for col in ['open', 'high', 'low', 'close']):
                        chart_path = os.path.join(save_dir, f"{symbol}_1D_15M_candlestick.png")
                        self.chart_generator.generate_candlestick_chart(data_15m, f"{symbol} (1D, 15M)", chart_path)
                    else:
                        chart_path = os.path.join(save_dir, f"{symbol}_1D_15M.png")
                        self.chart_generator.generate_matplotlib_chart(data_15m, f"{symbol} (1D, 15M)", chart_path)
                    symbol_chart_files.append(chart_path)
                
                # 2. 1 Week chart with 4-hour interval
                end_time = datetime.now()
                start_time = end_time - timedelta(weeks=1)
                if self.use_wine_mt5:
                    try:
                        data_4h = self._get_wine_historical_data(
                            symbol, mt5.TIMEFRAME_H4, start_time, end_time)
                    except Exception as e:
                        logger.warning(f"Error fetching 4H data for {symbol} from Wine MT5: {e}")
                        # Fallback to regular MT5 fetcher
                        data_4h = self.mt5_fetcher.fetch_historical_data(
                            symbol, mt5.TIMEFRAME_H4, start_time, end_time)
                else:
                    data_4h = self.mt5_fetcher.fetch_historical_data(
                        symbol, mt5.TIMEFRAME_H4, start_time, end_time)
                
                if not data_4h.empty:
                    # Check if we have OHLC data for candlestick chart
                    if all(col in data_4h.columns for col in ['open', 'high', 'low', 'close']):
                        chart_path = os.path.join(save_dir, f"{symbol}_1W_4H_candlestick.png")
                        self.chart_generator.generate_candlestick_chart(data_4h, f"{symbol} (1W, 4H)", chart_path)
                    else:
                        chart_path = os.path.join(save_dir, f"{symbol}_1W_4H.png")
                        self.chart_generator.generate_matplotlib_chart(data_4h, f"{symbol} (1W, 4H)", chart_path)
                    symbol_chart_files.append(chart_path)
                
                # 3. 1/3 Month chart with 1-day interval
                end_time = datetime.now()
                start_time = end_time - timedelta(days=30)  # Approximately 1 month
                if self.use_wine_mt5:
                    try:
                        data_1d = self._get_wine_historical_data(
                            symbol, mt5.TIMEFRAME_D1, start_time, end_time)
                    except Exception as e:
                        logger.warning(f"Error fetching 1D data for {symbol} from Wine MT5: {e}")
                        # Fallback to regular MT5 fetcher
                        data_1d = self.mt5_fetcher.fetch_historical_data(
                            symbol, mt5.TIMEFRAME_D1, start_time, end_time)
                else:
                    data_1d = self.mt5_fetcher.fetch_historical_data(
                        symbol, mt5.TIMEFRAME_D1, start_time, end_time)
                
                if not data_1d.empty:
                    # Check if we have OHLC data for candlestick chart
                    if all(col in data_1d.columns for col in ['open', 'high', 'low', 'close']):
                        chart_path = os.path.join(save_dir, f"{symbol}_1M_1D_candlestick.png")
                        self.chart_generator.generate_candlestick_chart(data_1d, f"{symbol} (1M, 1D)", chart_path)
                    else:
                        chart_path = os.path.join(save_dir, f"{symbol}_1M_1D.png")
                        self.chart_generator.generate_matplotlib_chart(data_1d, f"{symbol} (1M, 1D)", chart_path)
                    symbol_chart_files.append(chart_path)
                
                chart_files.extend(symbol_chart_files)
                
            except Exception as e:
                logger.warning(f"Error generating charts for {symbol}: {e}")
        
        return chart_files

    def get_economic_calendar(self) -> pd.DataFrame:
        """Get today's economic calendar from the CSV file."""
        try:
            # Path to the economic calendar CSV file
            calendar_csv_path = "C:/Users/Administrator/AppData/Roaming/MetaQuotes/Terminal/Common/Files/economic_calendar.csv"
            
            # Alternative path for locally stored CSV file
            local_calendar_path = "./economic-calendar/ECONOMIC_CALENDAR_DATA.csv"
            
            # In a Wine environment, the C: drive is typically mapped to a path within the user's home directory.
            # We'll construct a path that can be accessed from the Unix-like environment.
            if self.use_wine_mt5:
                wine_path = os.path.expanduser("~/.wine/drive_c")
                if os.path.exists(wine_path):
                    # Correctly replace C: with the Wine path
                    calendar_csv_path = calendar_csv_path.replace("C:", wine_path)
                    # Also handle the backslashes properly for Unix paths
                    calendar_csv_path = calendar_csv_path.replace("\\", "/")

            # Try different paths to find the CSV file
            paths_to_check = [calendar_csv_path, local_calendar_path]
            
            df = pd.DataFrame()
            for path in paths_to_check:
                if os.path.exists(path):
                    # Read the CSV file
                    df = pd.read_csv(path)
                    logger.info(f"Successfully read economic calendar from: {path}")
                    break
            
            if not df.empty:
                # Handle the new CSV format with additional columns
                # The new format has: DateTime,EventID,Name,Country,Currency,Impact,Actual,Forecast,Previous
                # The old format had: Time,Name,Impact,Currency,Actual,Forecast,Previous
                
                # If we have the DateTime column, use it as Time
                if 'DateTime' in df.columns:
                    df.rename(columns={'DateTime': 'Time'}, inplace=True)
                
                # Convert Time column to datetime if it's not already
                if 'Time' in df.columns:
                    df['Time'] = pd.to_datetime(df['Time'], errors='coerce')
                
                # Handle nan values by replacing them with None/NaN
                df = df.replace('nan', pd.NA)
                
                return df
            else:
                logger.warning(f"Economic calendar CSV file not found at any of these locations: {paths_to_check}")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error reading economic calendar CSV: {e}")
            return pd.DataFrame()

    def get_volatility_summary(self) -> pd.DataFrame:
        """Get volatility summary for major assets"""
        volatility_summary = []
        
        # Get data for major symbols
        symbols = self.major_indices + self.major_currencies + self.commodities
        
        for symbol in symbols[:5]:  # Limit for demo
            try:
                end_time = datetime.now()
                start_time = end_time - timedelta(days=60)
                
                # Use Wine MT5 if enabled, otherwise use regular MT5 fetcher
                if self.use_wine_mt5:
                    try:
                        data = self._get_wine_historical_data(
                            symbol, mt5.TIMEFRAME_D1, start_time, end_time)
                    except Exception as e:
                        logger.warning(f"Error fetching data for {symbol} from Wine MT5: {e}")
                        # Fallback to regular MT5 fetcher
                        data = self.mt5_fetcher.fetch_historical_data(
                            symbol, mt5.TIMEFRAME_D1, start_time, end_time)
                else:
                    # Use regular MT5 fetcher
                    data = self.mt5_fetcher.fetch_historical_data(
                        symbol, mt5.TIMEFRAME_D1, start_time, end_time)
                
                if not data.empty:
                    # Calculate volatility metrics
                    summary = self.volatility_calculator.get_volatility_summary(data, symbol)
                    if summary:
                        volatility_summary.append(summary)
            except Exception as e:
                logger.warning(f"Error calculating volatility for {symbol}: {e}")
        
        return pd.DataFrame(volatility_summary)

    def generate_report(self, save_dir: str = "./reports", format: str = "txt", institutional_grade: bool = False) -> str:
        """Generate the complete daily investment report"""
        # Create save directory if it doesn't exist
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        # Get current timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_dir = os.path.join(save_dir, f"daily_report_{timestamp}")
        chart_dir = os.path.join(report_dir, "charts")
        
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)
        
        # Generate report data
        logger.info("Generating daily investment report...")
        
        # 1. Market status
        market_status = self.get_market_status()
        
        # 2. Major indices data
        indices_data = self.get_major_indices_data()
        
        # 3. Currency data
        currency_data = self.get_currency_data()
        
        # 4. Commodities data
        commodities_data = self.get_commodities_data()
        
        # 5. Bonds data
        bonds_data = self.get_bonds_data()
        
        # 6. Volatility data
        volatility_data = self.get_volatility_data()
        
        # 7. Top movers
        # Ensure all dataframes are valid before concatenating
        dataframes = []
        if isinstance(indices_data, pd.DataFrame) and not indices_data.empty:
            dataframes.append(indices_data)
        if isinstance(currency_data, pd.DataFrame) and not currency_data.empty:
            dataframes.append(currency_data)
        if isinstance(commodities_data, pd.DataFrame) and not commodities_data.empty:
            dataframes.append(commodities_data)
        if isinstance(bonds_data, pd.DataFrame) and not bonds_data.empty:
            dataframes.append(bonds_data)
        
        top_movers = pd.DataFrame()
        if dataframes:
            try:
                combined_data = pd.concat(dataframes, ignore_index=True)
                if not combined_data.empty:
                    top_movers = self.get_top_movers(combined_data)
            except Exception as e:
                logger.warning(f"Error calculating top movers: {e}")
        
        # 8. Economic calendar
        calendar_data = self.get_economic_calendar()
        
        # 9. Volatility summary
        volatility_summary = self.get_volatility_summary()
        
        # 10. Generate charts
        logger.info("Generating charts...")
        chart_files = self.generate_charts(chart_dir)
        
        # 11. Generate report based on format and grade
        if format.lower() == "pdf":
            if institutional_grade:
                # Generate institutional-grade PDF report
                report_path = self._generate_institutional_pdf_report(
                    market_status, indices_data, currency_data, commodities_data, bonds_data,
                    volatility_data, top_movers, calendar_data, volatility_summary, chart_files,
                    report_dir, timestamp)
            else:
                # Generate standard professional PDF report
                report_path = self._generate_pdf_report(
                    market_status, indices_data, currency_data, commodities_data, bonds_data,
                    volatility_data, top_movers, calendar_data, volatility_summary, chart_files,
                    report_dir, timestamp)
        else:
            # Default to text format
            report_path = self._generate_text_report(
                market_status, indices_data, currency_data, commodities_data, bonds_data,
                volatility_data, top_movers, calendar_data, volatility_summary, chart_files,
                report_dir, timestamp)
        
        logger.info(f"Daily investment report saved to: {report_path}")
        return report_path

    def _generate_pdf_report(self, market_status: Dict, indices_data: pd.DataFrame,
                             currency_data: pd.DataFrame, commodities_data: pd.DataFrame,
                             bonds_data: pd.DataFrame, volatility_data: pd.DataFrame, 
                             top_movers: pd.DataFrame, calendar_data: pd.DataFrame, 
                             volatility_summary: pd.DataFrame, chart_files: List[str], 
                             report_dir: str, timestamp: str) -> str:
        """Generate PDF format report with professional styling"""
        # Create PDF report
        pdf_path = os.path.join(report_dir, f"daily_report_{timestamp}.pdf")
        pdf_gen = ProfessionalPDFReportGenerator(pdf_path)
        
        # Add cover page
        pdf_gen.add_cover_page()
        
        # Add table of contents
        pdf_gen.add_table_of_contents()
        
        # Add title
        pdf_gen.add_title("DAILY INVESTMENT REPORT")
        
        # Generate AI-powered executive summary
        try:
            executive_summary_points = self.llm_generator.generate_executive_summary(
                indices_data, currency_data, commodities_data, top_movers, calendar_data
            )
        except Exception as e:
            logger.warning(f"Failed to generate AI executive summary: {e}")
            # Fallback to static summary with specific indication
            executive_summary_points = [
                "⚠️ LLM EXECUTIVE SUMMARY UNAVAILABLE ⚠️",
                "Markets are currently stable with mixed sentiment.",
                "Key indices showing moderate volatility.",
                "Currency markets reflecting ongoing macroeconomic developments.",
                "Commodities sector showing divergent trends.",
                "Economic calendar highlights upcoming key events."
            ]
        
        # Add Executive Summary
        pdf_gen.add_executive_summary(executive_summary_points)
        
        # Market Overview
        pdf_gen.add_market_overview(market_status, indices_data)
        
        # Major Indices
        pdf_gen.add_indices_table(indices_data)
        
        # Major Currencies
        pdf_gen.add_currencies_table(currency_data)
        
        # Commodities
        pdf_gen.add_commodities_table(commodities_data)
        
        # Bonds
        pdf_gen.add_bonds_table(bonds_data)
        
        # Market Volatility
        pdf_gen.add_volatility_table(volatility_data)
        
        # Top Movers
        pdf_gen.add_top_movers_table(top_movers)
        
        # Economic Calendar
        pdf_gen.add_calendar_events(calendar_data)
        
        # Volatility Summary
        pdf_gen.add_volatility_summary(volatility_summary)
        
        # Charts
        pdf_gen.add_charts(chart_files)
        
        # Disclaimer
        pdf_gen.add_disclaimer()
        
        # Generate PDF
        pdf_gen.generate()
        
        return pdf_path

    def _generate_institutional_pdf_report(self, market_status: Dict, indices_data: pd.DataFrame,
                                          currency_data: pd.DataFrame, commodities_data: pd.DataFrame,
                                          bonds_data: pd.DataFrame, volatility_data: pd.DataFrame, 
                                          top_movers: pd.DataFrame, calendar_data: pd.DataFrame, 
                                          volatility_summary: pd.DataFrame, chart_files: List[str], 
                                          report_dir: str, timestamp: str) -> str:
        """Generate institutional-grade PDF format report with professional styling"""
        # Create institutional PDF report
        pdf_path = os.path.join(report_dir, f"daily_report_{timestamp}_institutional.pdf")
        pdf_gen = EnhancedInstitutionalPDFReportGenerator(pdf_path)
        
        # Add cover page
        pdf_gen.add_cover_page()
        
        # Add table of contents
        pdf_gen.add_table_of_contents()
        
        # Add title
        pdf_gen.add_title("DAILY INVESTMENT REPORT - INSTITUTIONAL GRADE")
        
        # Generate AI-powered executive summary
        try:
            executive_summary_points = self.llm_generator.generate_executive_summary(
                indices_data, currency_data, commodities_data, top_movers, calendar_data
            )
        except Exception as e:
            logger.warning(f"Failed to generate AI executive summary: {e}")
            # Fallback to static summary with specific indication
            executive_summary_points = [
                "⚠️ LLM EXECUTIVE SUMMARY UNAVAILABLE ⚠️",
                "Markets are currently stable with mixed sentiment.",
                "Key indices showing moderate volatility.",
                "Currency markets reflecting ongoing macroeconomic developments.",
                "Commodities sector showing divergent trends.",
                "Economic calendar highlights upcoming key events."
            ]
        
        # Add Executive Summary
        pdf_gen.add_executive_summary(executive_summary_points)
        
        # Market Overview
        pdf_gen.add_market_overview(market_status, indices_data)
        
        # Major Indices
        pdf_gen.add_indices_table(indices_data)
        
        # Major Currencies
        pdf_gen.add_currencies_table(currency_data)
        
        # Commodities
        pdf_gen.add_commodities_table(commodities_data)
        
        # Bonds
        pdf_gen.add_bonds_table(bonds_data)
        
        # Market Volatility
        pdf_gen.add_volatility_table(volatility_data)
        
        # Top Movers
        pdf_gen.add_top_movers_table(top_movers)
        
        # Economic Calendar
        pdf_gen.add_calendar_events(calendar_data)
        
        # Volatility Summary
        pdf_gen.add_volatility_summary(volatility_summary)
        
        # Charts
        pdf_gen.add_charts(chart_files)
        
        # Disclaimer
        pdf_gen.add_disclaimer()
        
        # Generate PDF
        pdf_gen.generate()
        
        return pdf_path

    def _generate_text_report(self, market_status: Dict, indices_data: pd.DataFrame,
                             currency_data: pd.DataFrame, commodities_data: pd.DataFrame,
                             bonds_data: pd.DataFrame, volatility_data: pd.DataFrame, 
                             top_movers: pd.DataFrame, calendar_data: pd.DataFrame, 
                             volatility_summary: pd.DataFrame, chart_files: List[str], 
                             report_dir: str, timestamp: str) -> str:
        """Generate text format report"""
        # Create report content
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report = []
        report.append("=" * 80)
        report.append(f"DAILY INVESTMENT REPORT - {timestamp}")
        report.append("=" * 80)
        report.append("")
        
        # Market Status
        report.append("MARKET STATUS")
        report.append("-" * 20)
        report.append(f"Status: {market_status.get('status', 'Unknown')}")
        report.append(f"Timestamp: {market_status.get('timestamp', 'N/A')}")
        report.append("")
        
        # Major Indices
        report.append("MAJOR INDICES")
        report.append("-" * 20)
        if not indices_data.empty:
            for _, row in indices_data.head(10).iterrows():
                report.append(f"{row['name']:<10} | Ask: {row.get('ask', 'N/A'):<10} | Bid: {row.get('bid', 'N/A'):<10}")
        else:
            report.append("No data available")
        report.append("")
        
        # Major Currencies
        report.append("MAJOR CURRENCIES")
        report.append("-" * 20)
        if not currency_data.empty:
            for _, row in currency_data.head(10).iterrows():
                report.append(f"{row['name']:<10} | Ask: {row.get('ask', 'N/A'):<10} | Bid: {row.get('bid', 'N/A'):<10}")
        else:
            report.append("No data available")
        report.append("")
        
        # Commodities
        report.append("COMMODITIES")
        report.append("-" * 20)
        if not commodities_data.empty:
            for _, row in commodities_data.head(10).iterrows():
                report.append(f"{row['name']:<10} | Ask: {row.get('ask', 'N/A'):<10} | Bid: {row.get('bid', 'N/A'):<10}")
        else:
            report.append("No data available")
        report.append("")
        
        # Market Volatility (VIX)
        report.append("MARKET VOLATILITY")
        report.append("-" * 20)
        if not volatility_data.empty:
            for _, row in volatility_data.head(10).iterrows():
                report.append(f"{row['name']:<10} | Ask: {row.get('ask', 'N/A'):<10} | Bid: {row.get('bid', 'N/A'):<10}")
        else:
            report.append("No data available")
        report.append("")
        
        # Top Movers
        report.append("TOP MOVERS")
        report.append("-" * 20)
        if not top_movers.empty:
            for _, row in top_movers.iterrows():
                pct_change = row.get('pct_change', 0)
                direction = "+" if pct_change >= 0 else ""
                report.append(f"{row['name']:<10} | Price: {row.get('Price', 'N/A'):<10} | Change: {direction}{pct_change:.2f}%")
        else:
            report.append("No data available")
        report.append("")
        
        # Economic Calendar
        report.append("ECONOMIC CALENDAR")
        report.append("-" * 20)
        if not calendar_data.empty:
            # Show date at the top
            import datetime as dt_module
            today = dt_module.datetime.now().strftime('%Y-%m-%d')
            report.append(f"Date: {today}")
            report.append("")
            
            for _, row in calendar_data.iterrows():
                # Show only time in first column
                time_only = "N/A"
                if 'Time' in row:
                    try:
                        dt = pd.to_datetime(row['Time'], errors='coerce')
                        if pd.notna(dt):
                            time_only = dt.strftime('%H:%M:%S')
                        else:
                            time_only = str(row['Time'])
                    except:
                        time_only = str(row['Time'])
                elif 'DateTime' in row:
                    try:
                        dt = pd.to_datetime(row['DateTime'], errors='coerce')
                        if pd.notna(dt):
                            time_only = dt.strftime('%H:%M:%S')
                        else:
                            time_only = str(row['DateTime'])
                    except:
                        time_only = str(row['DateTime'])
                
                currency = row.get('Currency', 'N/A')
                event_name = row.get('Name', 'N/A')
                
                # Format the line with more space for event names
                report.append(f"{time_only:>8} | {currency:>3} | {event_name}")
                
                # Show actual, forecast, previous on separate line if available
                actual = row.get('Actual', 'N/A')
                forecast = row.get('Forecast', 'N/A')
                previous = row.get('Previous', 'N/A')
                
                if actual != 'N/A' or forecast != 'N/A' or previous != 'N/A':
                    report.append(f"         |     | Actual: {actual} | Forecast: {forecast} | Previous: {previous}")
        else:
            report.append("No events scheduled")
        report.append("")
        
        # Volatility Summary
        report.append("VOLATILITY SUMMARY")
        report.append("-" * 20)
        if not volatility_summary.empty:
            for _, row in volatility_summary.iterrows():
                report.append(f"{row.get('symbol', 'N/A'):<10} | ATR: {row.get('current_atr', 0):.4f} | Vol: {row.get('current_volatility', 0):.4f}")
        else:
            report.append("No data available")
        report.append("")
        
        # Charts
        report.append("GENERATED CHARTS")
        report.append("-" * 20)
        if chart_files:
            for chart_file in chart_files[:10]:  # Show first 10
                report.append(f"- {os.path.basename(chart_file)}")
            if len(chart_files) > 10:
                report.append(f"... and {len(chart_files) - 10} more charts")
        else:
            report.append("No charts generated")
        report.append("")
        
        report.append("=" * 80)
        report.append("END OF REPORT")
        report.append("=" * 80)
        
        report_content = "\n".join(report)
        
        # Save report
        report_path = os.path.join(report_dir, f"daily_report_{timestamp}.txt")
        with open(report_path, 'w') as f:
            f.write(report_content)
        
        return report_path

    def shutdown(self):
        """Shutdown connections"""
        self.mt5_fetcher.shutdown()

# Example usage
if __name__ == "__main__":
    try:
        # Initialize report generator
        report_gen = DailyInvestmentReportGenerator(use_wine_mt5=True)
        
        # Generate report
        report_path = report_gen.generate_report()
        print(f"Report generated: {report_path}")
        
        # Shutdown
        report_gen.shutdown()
        
    except Exception as e:
        print(f"Error generating report: {e}")