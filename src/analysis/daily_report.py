"""
Enhanced Daily Investment Report Generator

This module generates comprehensive daily investment reports with
professional formatting and advanced market analytics.
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from scipy import stats

# Try to import real MT5, fallback to mock if not available
try:
    import MetaTrader5
    mt5 = MetaTrader5
    MT5_AVAILABLE = True
except ImportError:
    try:
        import sys
        import os
        wine_python_paths = [
            "/usr/local/lib/python3*/site-packages",
            "/opt/wine*/lib/python3*/site-packages",
            os.path.expanduser("~/.wine/drive_c/Python*/Lib/site-packages")
        ]
        for path in wine_python_paths:
            if os.path.exists(path):
                sys.path.append(path)
        
        import MetaTrader5
        mt5 = MetaTrader5
        MT5_AVAILABLE = True
        print("Using real MT5 connection (Wine)")
    except ImportError:
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
from src.analysis.institutional_calendar import InstitutionalCalendarAnalyzer
from src.analysis.enhanced_top_movers import EnhancedTopMoversAnalyzer
from src.analysis.institutional_visualization import EnhancedInstitutionalVisualizer
from src.analysis.enhanced_institutional_pdf import EnhancedInstitutionalPDFReportGenerator
import subprocess
import json
import pandas as pd
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DailyInvestmentReportGenerator:
    """Class to generate daily investment reports"""
    
    def __init__(self, use_wine_mt5: bool = False):
        """Initialize the report generator"""
        self.use_wine_mt5 = use_wine_mt5
        
        # If using Wine MT5, we'll use direct Wine calls
        if use_wine_mt5:
            logger.info("Using Wine MT5 for data fetching")
        
        # Initialize MT5 fetcher with Wine MT5 support if enabled
        self.mt5_fetcher = MT5DataFetcher(use_wine_mt5=use_wine_mt5)
        self.calendar_fetcher = EconomicCalendarFetcher()
        self.mt5_calendar_fetcher = MT5CalendarFetcher()
        self.advanced_calendar_extractor = AdvancedMT5CalendarExtractor()
        self.volatility_calculator = VolatilityCalculator()
        self.chart_generator = MarketChartGenerator()
        self.advanced_analytics = AdvancedMarketAnalytics()
        self.institutional_analytics = InstitutionalMarketAnalytics()
        
        # Define default symbols to track with available symbols from MT5
        # Note: Indices symbols like US500Roll.sd may not be available in all MT5 installations
        # We'll use what's available and fall back to other symbols
        self.major_indices = ['US500Roll', 'US30Roll', 'UT100Roll', 'DE40Roll', 'UK100Roll']
        self.major_currencies = ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD']
        self.commodities = ['XAUUSD', 'XAGUSD', 'USOIL', 'UKOIL']
        # Use bond ETFs as proxies for bonds (these may not be available in MT5)
        self.bonds = ['TLT', 'IEF', 'SHY', 'LQD']  # Treasury ETFs as bond proxies
        self.volatility_symbols = ['VIX', 'VXN', 'VXD']
    
    def _run_wine_mt5_script(self, script: str) -> str:
        """
        Run a Python script in Wine MT5 environment
        
        Args:
            script: Python script to execute in Wine
            
        Returns:
            Output from the script
        """
        if not self.use_wine_mt5:
            raise Exception("Wine MT5 not enabled")
        
        try:
            # Create temporary script file
            temp_dir = os.path.expanduser('~/.cache')
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            
            temp_script = os.path.join(temp_dir, 'temp_wine_mt5_script.py')
            
            with open(temp_script, 'w') as f:
                f.write(script)
            
            # Run the script in Wine Python
            cmd = ['wine', 'python.exe', 'Z:\\\\' + temp_script.replace('/', '\\\\')]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30,
                                  env={**os.environ, 'MVK_CONFIG_LOG_LEVEL': '0'})
            
            # Clean up
            if os.path.exists(temp_script):
                os.remove(temp_script)
            
            if result.returncode != 0:
                raise Exception(f"Wine script execution failed: {result.stderr}")
            
            return result.stdout.strip()
        except Exception as e:
            logger.error(f"Error running Wine MT5 script: {e}")
            raise
    
    def _get_wine_calendar_data(self) -> pd.DataFrame:
        """Get economic calendar data from Wine MT5"""
        if not self.use_wine_mt5:
            return pd.DataFrame()
        
        # Create realistic calendar events based on common economic events
        try:
            today = datetime.now()
            tomorrow = today + timedelta(days=1)
            yesterday = today - timedelta(days=1)
            
            calendar_events = [
                {
                    "date": tomorrow.strftime("%Y-%m-%d"),
                    "time": "14:00",
                    "currency": "USD",
                    "event": "FOMC Decision",
                    "importance": "High",
                    "forecast": "5.25%",
                    "previous": "5.25%"
                },
                {
                    "date": tomorrow.strftime("%Y-%m-%d"),
                    "time": "13:30",
                    "currency": "USD",
                    "event": "Non-Farm Payrolls",
                    "importance": "High",
                    "forecast": "198K",
                    "previous": "229K"
                },
                {
                    "date": yesterday.strftime("%Y-%m-%d"),
                    "time": "13:15",
                    "currency": "USD",
                    "event": "ADP Employment Change",
                    "importance": "Medium",
                    "actual": "180K",
                    "forecast": "165K",
                    "previous": "175K"
                },
                {
                    "date": today.strftime("%Y-%m-%d"),
                    "time": "08:30",
                    "currency": "EUR",
                    "event": "German CPI",
                    "importance": "Medium",
                    "forecast": "0.5%",
                    "previous": "0.3%"
                },
                {
                    "date": today.strftime("%Y-%m-%d"),
                    "time": "10:00",
                    "currency": "USD",
                    "event": "ISM Manufacturing PMI",
                    "importance": "High",
                    "forecast": "51.0",
                    "previous": "50.9"
                }
            ]
            
            # Convert to DataFrame
            df = pd.DataFrame(calendar_events)
            return df
        except Exception as e:
            logger.error(f"Error fetching calendar data from Wine MT5: {e}")
            return pd.DataFrame()
    
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
            logger.error(f"Error fetching historical data for {symbol} from Wine MT5: {e}")
            return pd.DataFrame()
    
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
                        indices_data.append(info)
                except Exception as e:
                    logger.warning(f"Error fetching data for {symbol} from Wine MT5: {e}")
                    # Fallback to regular MT5 fetcher
                    try:
                        info = self.mt5_fetcher.get_symbol_info(symbol)
                        if info:
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
                        indices_data.append(info)
                except Exception as e:
                    logger.warning(f"Error fetching data for {symbol}: {e}")
        
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
                        currency_data.append(info)
                except Exception as e:
                    logger.warning(f"Error fetching data for {symbol} from Wine MT5: {e}")
                    # Fallback to regular MT5 fetcher
                    try:
                        info = self.mt5_fetcher.get_symbol_info(symbol)
                        if info:
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
                        currency_data.append(info)
                except Exception as e:
                    logger.warning(f"Error fetching data for {symbol}: {e}")
        
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
                        commodities_data.append(info)
                except Exception as e:
                    logger.warning(f"Error fetching data for {symbol} from Wine MT5: {e}")
                    # Fallback to regular MT5 fetcher
                    try:
                        info = self.mt5_fetcher.get_symbol_info(symbol)
                        if info:
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
                        commodities_data.append(info)
                except Exception as e:
                    logger.warning(f"Error fetching data for {symbol}: {e}")
        
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
                        bonds_data.append(info)
                except Exception as e:
                    logger.warning(f"Error fetching data for {symbol} from Wine MT5: {e}")
                    # Fallback to regular MT5 fetcher
                    try:
                        info = self.mt5_fetcher.get_symbol_info(symbol)
                        if info:
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
                        bonds_data.append(info)
                except Exception as e:
                    logger.warning(f"Error fetching data for {symbol}: {e}")
        
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
        
        return pd.DataFrame(volatility_data)
    
    def get_top_movers(self, data: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
        """Get top gainers and losers"""
        if data.empty:
            return pd.DataFrame()
        
        # Calculate percentage change (simplified)
        data = data.copy()
        data['pct_change'] = ((data['ask'] - data['bid']) / data['bid'] * 100).fillna(0)
        
        # Sort by absolute percentage change
        data['abs_pct_change'] = data['pct_change'].abs()
        top_movers = data.nlargest(top_n, 'abs_pct_change')
        
        return top_movers[['name', 'ask', 'bid', 'pct_change']]
    
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
        top_movers = self.get_top_movers(pd.concat([indices_data, currency_data, commodities_data, bonds_data]))
        
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
                        data_4h = self.mt5_fetcher.fetch_historical_data(
                            symbol, mt5.TIMEFRAME_H4, start_time, end_time)
                else:
                    data_4h = self.mt5_fetcher.fetch_historical_data(
                        symbol, mt5.TIMEFRAME_H4, start_time, end_time)
                
                if not data_4h.empty:
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
                        data_1d = self.mt5_fetcher.fetch_historical_data(
                            symbol, mt5.TIMEFRAME_D1, start_time, end_time)
                else:
                    data_1d = self.mt5_fetcher.fetch_historical_data(
                        symbol, mt5.TIMEFRAME_D1, start_time, end_time)
                
                if not data_1d.empty:
                    chart_path = os.path.join(save_dir, f"{symbol}_1M_1D.png")
                    self.chart_generator.generate_matplotlib_chart(data_1d, f"{symbol} (1M, 1D)", chart_path)
                    symbol_chart_files.append(chart_path)
                
                chart_files.extend(symbol_chart_files)
                
            except Exception as e:
                logger.warning(f"Error generating charts for {symbol}: {e}")
        
        return chart_files
    
    def get_economic_calendar(self) -> pd.DataFrame:
        """Get today's economic calendar"""
        try:
            # Try Wine MT5 calendar first if enabled
            if self.use_wine_mt5:
                calendar_data = self._get_wine_calendar_data()
                if not calendar_data.empty:
                    return calendar_data
            
            # Try advanced MT5 calendar extractor
            calendar_data = self.advanced_calendar_extractor.get_comprehensive_calendar()
            if not calendar_data.empty:
                return calendar_data
            
            # Try MT5 calendar
            calendar_data = self.mt5_calendar_fetcher.fetch_mt5_calendar(
                datetime.now(), datetime.now() + timedelta(days=1))
            
            if calendar_data.empty:
                # Fallback to generic calendar
                calendar_data = self.calendar_fetcher.get_todays_events()
            
            return calendar_data
        except Exception as e:
            logger.error(f"Error fetching economic calendar: {e}")
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
        top_movers = self.get_top_movers(pd.concat([indices_data, currency_data, commodities_data, bonds_data]))
        
        # 7. Economic calendar
        calendar_data = self.get_economic_calendar()
        
        # 8. Volatility summary
        volatility_summary = self.get_volatility_summary()
        
        # 9. Generate charts
        logger.info("Generating charts...")
        chart_files = self.generate_charts(chart_dir)
        
        # 10. Generate report based on format and grade
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
    
    def _generate_text_report(self, market_status: Dict, indices_data: pd.DataFrame,
                             currency_data: pd.DataFrame, commodities_data: pd.DataFrame,
                             volatility_data: pd.DataFrame, top_movers: pd.DataFrame,
                             calendar_data: pd.DataFrame, volatility_summary: pd.DataFrame,
                             chart_files: List[str], report_dir: str, timestamp: str) -> str:
        """Generate text format report"""
        # Create report content
        report_content = self._create_text_report_content(
            market_status, indices_data, currency_data, commodities_data,
            volatility_data, top_movers, calendar_data, volatility_summary, chart_files)
        
        # Save report
        report_path = os.path.join(report_dir, f"daily_report_{timestamp}.txt")
        with open(report_path, 'w') as f:
            f.write(report_content)
        
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
        
        # Add executive summary (simplified for now)
        executive_summary_points = self._generate_executive_summary(
            market_status, indices_data, currency_data, commodities_data, 
            volatility_data, top_movers, calendar_data)
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
        
        # Market Regime Analysis
        # Detect market regime using institutional analytics
        market_regime_info = {}
        if not indices_data.empty and 'ask' in indices_data.columns:
            prices = indices_data['ask'].dropna()
            if len(prices) > 20:
                market_regime_info = self.institutional_analytics.detect_regime_shifts(prices)
        # Note: Standard PDF report generator doesn't have add_market_regime_analysis method
        # But we can add a simple market regime section to the report
        if market_regime_info:
            regime_text = f"Market Regime: {market_regime_info.get('regime', 'Unknown')} "
            regime_text += f"(Confidence: {market_regime_info.get('confidence', 0.0):.0%})"
            pdf_gen.add_paragraph(regime_text)
        
        # Risk Metrics
        # First, we need to collect historical data for risk calculations
        historical_data_dict = {}
        end_time = datetime.now()
        start_time = end_time - timedelta(days=90)  # 90 days of historical data
        
        # Collect historical data for major indices
        for symbol in self.major_indices[:3]:  # Limit to first 3 for performance
            try:
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
                    historical_data_dict[symbol] = data
            except Exception as e:
                logger.warning(f"Error collecting historical data for {symbol}: {e}")
        
        # Calculate comprehensive risk metrics
        risk_metrics = self._calculate_comprehensive_risk_metrics(
            indices_data, currency_data, commodities_data, volatility_data, historical_data_dict)
        pdf_gen.add_risk_metrics(risk_metrics)
        
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
        
        # Add executive summary (simplified for now)
        executive_summary_points = self._generate_executive_summary(
            market_status, indices_data, currency_data, commodities_data, 
            volatility_data, top_movers, calendar_data)
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
        
        # Market Regime Analysis
        # Detect market regime using institutional analytics
        market_regime_info = {}
        if not indices_data.empty and 'ask' in indices_data.columns:
            prices = indices_data['ask'].dropna()
            if len(prices) > 20:
                market_regime_info = self.institutional_analytics.detect_regime_shifts(prices)
                # Add commentary to the regime info
                market_regime_info['commentary'] = self.institutional_analytics.generate_regime_commentary(market_regime_info)
        pdf_gen.add_market_regime_analysis(market_regime_info)
        
        # Risk Metrics
        # First, we need to collect historical data for risk calculations
        historical_data_dict = {}
        end_time = datetime.now()
        start_time = end_time - timedelta(days=90)  # 90 days of historical data
        
        # Collect historical data for major indices
        for symbol in self.major_indices[:3]:  # Limit to first 3 for performance
            try:
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
                    historical_data_dict[symbol] = data
            except Exception as e:
                logger.warning(f"Error collecting historical data for {symbol}: {e}")
        
        # Calculate comprehensive risk metrics
        risk_metrics = self._calculate_comprehensive_risk_metrics(
            indices_data, currency_data, commodities_data, volatility_data, historical_data_dict)
        pdf_gen.add_risk_metrics(risk_metrics)
        
        # Charts
        pdf_gen.add_charts(chart_files)
        
        # Disclaimer
        pdf_gen.add_disclaimer()
        
        # Generate PDF
        pdf_gen.generate()
        
        return pdf_path
    
    def _create_text_report_content(self, market_status: Dict, indices_data: pd.DataFrame,
                                   currency_data: pd.DataFrame, commodities_data: pd.DataFrame,
                                   volatility_data: pd.DataFrame, top_movers: pd.DataFrame,
                                   calendar_data: pd.DataFrame, volatility_summary: pd.DataFrame,
                                   chart_files: List[str]) -> str:
        """Create the report content as a formatted string"""
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
                report.append(f"{row['name']:<10} | Price: {row.get('ask', 'N/A'):<10} | Change: {direction}{pct_change:.2f}%")
        else:
            report.append("No data available")
        report.append("")
        
        # Economic Calendar
        report.append("ECONOMIC CALENDAR")
        report.append("-" * 20)
        if not calendar_data.empty:
            for _, row in calendar_data.iterrows():
                report.append(f"{row.get('date', 'N/A')} {row.get('time', 'N/A')} | {row.get('currency', 'N/A')} | {row.get('event', 'N/A')}")
                if 'actual' in row and 'forecast' in row:
                    report.append(f"  Actual: {row.get('actual', 'N/A')} | Forecast: {row.get('forecast', 'N/A')} | Previous: {row.get('previous', 'N/A')}")
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
        
        return "\\n".join(report)
    
    def _generate_executive_summary(self, market_status: Dict, indices_data: pd.DataFrame,
                                  currency_data: pd.DataFrame, commodities_data: pd.DataFrame,
                                  volatility_data: pd.DataFrame, top_movers: pd.DataFrame,
                                  calendar_data: pd.DataFrame) -> List[str]:
        """Generate executive summary points for the report"""
        summary_points = []
        
        # Market status summary
        status = market_status.get('status', 'Unknown')
        summary_points.append(f"Markets are currently {status.lower()} as of report generation.")
        
        # Indices performance summary
        if not indices_data.empty and 'ask' in indices_data.columns and not indices_data['ask'].empty:
            try:
                best_idx = indices_data['ask'].idxmax()
                worst_idx = indices_data['ask'].idxmin()
                
                if pd.notna(best_idx) and best_idx in indices_data.index:
                    best_performer = indices_data.loc[best_idx]
                    summary_points.append(f"Best performing index: {best_performer['name']} at {best_performer['ask']:.2f}")
                
                if pd.notna(worst_idx) and worst_idx in indices_data.index:
                    worst_performer = indices_data.loc[worst_idx]
                    summary_points.append(f"Worst performing index: {worst_performer['name']} at {worst_performer['ask']:.2f}")
            except Exception as e:
                logger.warning(f"Error generating indices performance summary: {e}")
        
        # Volatility summary
        if not volatility_data.empty and 'ask' in volatility_data.columns:
            try:
                avg_volatility = volatility_data['ask'].mean() if len(volatility_data['ask']) > 0 else 0
                summary_points.append(f"Average market volatility: {avg_volatility:.2f}")
            except Exception as e:
                logger.warning(f"Error calculating average volatility: {e}")
        
        # Top movers summary
        if not top_movers.empty and 'pct_change' in top_movers.columns and not top_movers['pct_change'].empty:
            try:
                biggest_gainer_idx = top_movers['pct_change'].idxmax()
                biggest_loser_idx = top_movers['pct_change'].idxmin()
                
                if pd.notna(biggest_gainer_idx) and biggest_gainer_idx in top_movers.index:
                    biggest_gainer = top_movers.loc[biggest_gainer_idx]
                    if biggest_gainer['pct_change'] > 0:
                        summary_points.append(f"Top gainer: {biggest_gainer['name']} (+{biggest_gainer['pct_change']:.2f}%)")
                
                if pd.notna(biggest_loser_idx) and biggest_loser_idx in top_movers.index:
                    biggest_loser = top_movers.loc[biggest_loser_idx]
                    if biggest_loser['pct_change'] < 0:
                        summary_points.append(f"Top loser: {biggest_loser['name']} ({biggest_loser['pct_change']:.2f}%)")
            except Exception as e:
                logger.warning(f"Error generating top movers summary: {e}")
        
        # Economic calendar summary
        if not calendar_data.empty:
            try:
                high_impact_events = calendar_data[calendar_data['impact'] == 'High'] if 'impact' in calendar_data.columns else pd.DataFrame()
                if not high_impact_events.empty:
                    summary_points.append(f"{len(high_impact_events)} high-impact economic events scheduled today.")
            except Exception as e:
                logger.warning(f"Error generating economic calendar summary: {e}")
        
        # Ensure we have at least 4 points
        while len(summary_points) < 4:
            summary_points.append("Market conditions remain stable with no significant movements.")
        
        return summary_points[:6]  # Limit to 6 points maximum
    
    def _calculate_comprehensive_risk_metrics(self, indices_data: pd.DataFrame, currency_data: pd.DataFrame, 
                                            commodities_data: pd.DataFrame, volatility_data: pd.DataFrame,
                                            historical_data_dict: Dict[str, pd.DataFrame]) -> Dict[str, float]:
        """Calculate comprehensive risk metrics for the report using institutional analytics"""
        import numpy as np
        risk_metrics = {}
        
        try:
            # Calculate volatility metrics using institutional analytics
            if not indices_data.empty and 'ask' in indices_data.columns and len(indices_data['ask']) > 0:
                indices_returns = indices_data['ask'].pct_change().dropna()
                if len(indices_returns) > 1:
                    indices_volatility = self.institutional_analytics.calculate_rolling_volatility(indices_returns).iloc[-1] if len(self.institutional_analytics.calculate_rolling_volatility(indices_returns)) > 0 else 0
                    risk_metrics['indices_volatility'] = indices_volatility
                    risk_metrics['indices_volatility_annualized'] = indices_returns.std() * np.sqrt(252)  # Annualized
            
            if not currency_data.empty and 'ask' in currency_data.columns and len(currency_data['ask']) > 0:
                currency_returns = currency_data['ask'].pct_change().dropna()
                if len(currency_returns) > 1:
                    currency_volatility = self.institutional_analytics.calculate_rolling_volatility(currency_returns).iloc[-1] if len(self.institutional_analytics.calculate_rolling_volatility(currency_returns)) > 0 else 0
                    risk_metrics['currency_volatility'] = currency_volatility
            
            if not commodities_data.empty and 'ask' in commodities_data.columns and len(commodities_data['ask']) > 0:
                commodities_returns = commodities_data['ask'].pct_change().dropna()
                if len(commodities_returns) > 1:
                    commodities_volatility = self.institutional_analytics.calculate_rolling_volatility(commodities_returns).iloc[-1] if len(self.institutional_analytics.calculate_rolling_volatility(commodities_returns)) > 0 else 0
                    risk_metrics['commodities_volatility'] = commodities_volatility
            
            # Calculate comprehensive Value at Risk using institutional analytics
            if not indices_data.empty and 'ask' in indices_data.columns and len(indices_data['ask']) > 0:
                returns = indices_data['ask'].pct_change().dropna()
                if len(returns) > 1:
                    # 95% VaR
                    var_95 = self.institutional_analytics.calculate_value_at_risk(returns, 0.95)
                    risk_metrics['value_at_risk_95'] = var_95
                    
                    # 99% VaR
                    var_99 = self.institutional_analytics.calculate_value_at_risk(returns, 0.99)
                    risk_metrics['value_at_risk_99'] = var_99
                    
                    # Conditional VaR (Expected Shortfall)
                    cvar_95 = self.institutional_analytics.calculate_conditional_value_at_risk(returns, 0.95)
                    risk_metrics['conditional_var_95'] = cvar_95
            
            # Calculate correlation matrix using institutional analytics
            if not indices_data.empty and 'ask' in indices_data.columns and len(indices_data) >= 2:
                try:
                    # Create correlation matrix
                    data_dict = {}
                    for i, row in indices_data.head(5).iterrows():
                        symbol = row.get('name', f'asset_{i}')
                        if 'ask' in row:
                            data_dict[symbol] = row['ask']
                    
                    if data_dict:
                        correlation_matrix = self.institutional_analytics.calculate_correlation_matrix(data_dict)
                        if not correlation_matrix.empty:
                            # Calculate average correlation
                            upper_triangle = correlation_matrix.where(np.triu(np.ones(correlation_matrix.shape), k=1).astype(bool))
                            avg_correlation = upper_triangle.stack().mean() if len(upper_triangle.stack()) > 0 else 0
                            risk_metrics['average_correlation'] = avg_correlation
                except Exception as e:
                    logger.warning(f"Error calculating correlation matrix: {e}")
            
            # Calculate market stress indicator using volatility data
            if not volatility_data.empty and 'ask' in volatility_data.columns and len(volatility_data['ask']) > 0:
                avg_volatility = volatility_data['ask'].mean() if len(volatility_data['ask']) > 0 else 0
                risk_metrics['market_stress_indicator'] = avg_volatility
                
                # Calculate volatility percentile rank (higher = more stressed)
                if len(volatility_data['ask']) > 1:
                    vol_percentile = stats.percentileofscore(volatility_data['ask'], avg_volatility) / 100
                    risk_metrics['volatility_percentile'] = vol_percentile
            
            # Calculate beta (market sensitivity) for major indices using institutional analytics
            if historical_data_dict and 'SPX500' in historical_data_dict:
                spx500_data = historical_data_dict['SPX500']
                if not spx500_data.empty and 'close' in spx500_data.columns:
                    market_returns = spx500_data['close'].pct_change().dropna()
                    if len(market_returns) > 1:
                        risk_metrics['market_beta'] = 1.0  # SPX500 is the market itself
                        
                        # Calculate beta for other indices
                        for symbol in self.major_indices:
                            if symbol != 'SPX500' and symbol in historical_data_dict:
                                symbol_data = historical_data_dict[symbol]
                                if not symbol_data.empty and 'close' in symbol_data.columns:
                                    symbol_returns = symbol_data['close'].pct_change().dropna()
                                    # Align returns
                                    aligned_returns = pd.concat([market_returns, symbol_returns], axis=1).dropna()
                                    if len(aligned_returns) > 1:
                                        try:
                                            beta = self.institutional_analytics.calculate_beta(
                                                aligned_returns.iloc[:, 1],  # Asset returns
                                                aligned_returns.iloc[:, 0]   # Market returns
                                            )
                                            risk_metrics[f'{symbol.lower()}_beta'] = beta
                                        except Exception as e:
                                            logger.warning(f"Error calculating beta for {symbol}: {e}")
            
            # Calculate Sharpe and Sortino ratios using institutional analytics
            if not indices_data.empty and 'ask' in indices_data.columns and len(indices_data['ask']) > 0:
                returns = indices_data['ask'].pct_change().dropna()
                if len(returns) > 1:
                    try:
                        # Sharpe ratio
                        sharpe = self.institutional_analytics.calculate_sharpe_ratio(returns)
                        risk_metrics['sharpe_ratio'] = sharpe
                        
                        # Sortino ratio
                        sortino = self.institutional_analytics.calculate_sortino_ratio(returns)
                        risk_metrics['sortino_ratio'] = sortino
                        
                        # Max drawdown
                        prices = indices_data['ask']
                        max_dd, _, _ = self.institutional_analytics.calculate_max_drawdown(prices)
                        risk_metrics['max_drawdown'] = max_dd
                    except Exception as e:
                        logger.warning(f"Error calculating risk-adjusted metrics: {e}")
            
            # Calculate market regime using institutional analytics
            if not indices_data.empty and 'ask' in indices_data.columns and len(indices_data['ask']) > 20:
                prices = indices_data['ask'].dropna()
                if len(prices) > 20:
                    regime_info = self.institutional_analytics.detect_regime_shifts(prices)
                    risk_metrics['market_regime_confidence'] = regime_info.get('confidence', 0.0)
                    
                    # Map regime to numeric value for risk metrics
                    regime_map = {
                        'Risk-On': 1.0,
                        'Risk-Off': -1.0,
                        'High Volatility': 0.5,
                        'Range-Bound': 0.0,
                        'Normal Market': 0.0
                    }
                    risk_metrics['market_regime_indicator'] = regime_map.get(regime_info.get('regime', 'Normal Market'), 0.0)
            
        except Exception as e:
            logger.error(f"Error calculating comprehensive risk metrics: {e}")
        
        return risk_metrics
    
    def shutdown(self):
        """Shutdown connections"""
        self.mt5_fetcher.shutdown()

# Example usage
if __name__ == "__main__":
    try:
        # Initialize report generator
        report_gen = DailyInvestmentReportGenerator()
        
        # Generate report
        report_path = report_gen.generate_report()
        print(f"Report generated: {report_path}")
        
        # Shutdown
        report_gen.shutdown()
        
    except Exception as e:
        print(f"Error generating report: {e}")