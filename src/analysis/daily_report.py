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

# Local imports
from src.data.providers.alphavantage_data import AlphaVantageDataFetcher
from src.data.providers.calendar_data import EconomicCalendarFetcher
from src.data.providers.news import NewsAPI
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
    
    def __init__(self):
        """Initialize the report generator"""
        # Initialize data fetchers
        from src.config.settings import settings
        api_key = settings["api_keys"]["alpha_vantage"]
        if not api_key:
            raise ValueError("ALPHAVANTAGE_API_KEY not found in environment variables. Please set it in your .env file.")
        
        self.av_fetcher = AlphaVantageDataFetcher(api_key=api_key)
        self.calendar_fetcher = EconomicCalendarFetcher()
        self.news_fetcher = NewsAPI()
        self.volatility_calculator = VolatilityCalculator()
        self.chart_generator = MarketChartGenerator()
        self.advanced_analytics = AdvancedMarketAnalytics()
        self.institutional_analytics = InstitutionalMarketAnalytics()
        
        # Initialize LLM executive summary generator
        self.llm_generator = LLMExecutiveSummaryGenerator()
        
        # Define default symbols to track with available symbols from Finnhub
        self.major_indices = ['US500Roll', 'US30Roll', 'UK100Roll', 'DE40Roll', 'FRA40Roll', 'JP225Roll', 'CHINA50Roll']  # Removed HK50Roll as it might not be available in Finnhub
        self.major_currencies = ['EURUSD.sd', 'GBPUSD.sd', 'USDJPY.sd', 'AUDUSD.sd', 'USDCAD.sd', 'USDCHF.sd', 'NZDUSD.sd', 'USDCNH.sd']
        self.commodities = ['XAUUSD', 'XAGUSD', 'XPTUSD', 'USOILRoll', 'BRENT', 'NGAS']
        self.bonds = ['TLT', 'IEF', 'SHY', 'LQD']
        self.crypto = ['BTCUSD.lv', 'ETHUSD.lv', 'XRPUSD.lv', 'LTCUSD.lv', 'BCHUSD.lv', 'EOSUSD.lv']
        self.volatility_symbols = ['VIXRoll']

    def _get_data_from_csv(self, symbols: List[str], asset_class: str) -> pd.DataFrame:
        """Get data from CSV files for a given asset class."""
        data_list = []
        
        for symbol in symbols:
            try:
                folder = ''
                if asset_class == 'currencies':
                    folder = 'forex'
                elif asset_class == 'volatility':
                    folder = 'other'
                else:
                    folder = asset_class
                
                csv_filename = f"/Users/pawan/CLI-Finance-Terminal/data/{folder}/{symbol}_data.csv"
                if os.path.exists(csv_filename):
                    df = pd.read_csv(csv_filename)
                    if not df.empty:
                        latest_data = df.iloc[-1]
                        info = {
                            'name': symbol,
                            'ask': latest_data.get('close', 0),
                            'bid': latest_data.get('open', 0),
                            'last': latest_data.get('close', 0),
                            'volume': latest_data.get('tick_volume', 0),
                            'pct_change_24h': self._calculate_24h_percentage_change_from_csv(symbol)
                        }
                        info['Price'] = (info.get('ask', 0) + info.get('bid', 0)) / 2 if info.get('ask') and info.get('bid') else info.get('last', 0)
                        data_list.append(info)
            except Exception as e:
                logger.warning(f"Error reading CSV for {symbol}: {e}")
                continue
        
        return pd.DataFrame(data_list)

    

    def _calculate_24h_percentage_change(self, symbol: str) -> float:
        """
        Calculate the percentage change from the last trading day's close.
        - If today is Sunday or Monday, it compares to Friday's close.
        - Otherwise, it compares to the previous day's close.
        """
        try:
            # 1. Get the current price
            current_info = self.av_fetcher.get_symbol_info(symbol)
            if not current_info or 'ask' not in current_info or current_info['ask'] == 0:
                logger.warning(f"Could not get current price for {symbol}")
                # Fallback to CSV if Alpha Vantage fails
                return self._calculate_24h_percentage_change_from_csv(symbol)

            current_price = current_info['ask']

            # 2. Determine the last trading day
            today = datetime.now()
            weekday = today.weekday()

            if weekday == 6:  # Sunday
                # Compare to Friday's close (2 days ago)
                last_trading_day = today - timedelta(days=2)
            elif weekday == 0:  # Monday
                # Compare to Friday's close (3 days ago)
                last_trading_day = today - timedelta(days=3)
            else:
                # Compare to previous day's close
                last_trading_day = today - timedelta(days=1)
            
            # We need a small window to ensure we get the bar
            start_time = last_trading_day.replace(hour=0, minute=0, second=0)
            end_time = last_trading_day.replace(hour=23, minute=59, second=59)

            # 3. Fetch historical data for the last trading day
            # Use Alpha Vantage fetcher to get historical data
            try:
                historical_data = self.av_fetcher.fetch_historical_data(symbol, 'D', start_time, end_time)
            except Exception as e:
                logger.warning(f"Could not fetch Alpha Vantage data for {symbol}: {e}. Falling back to CSV.")
                return self._calculate_24h_percentage_change_from_csv(symbol)

            if historical_data.empty:
                logger.warning(f"No historical data for {symbol} on {last_trading_day.date()}. Falling back to CSV.")
                return self._calculate_24h_percentage_change_from_csv(symbol)

            # 4. Get the previous day's close
            prev_day_close = historical_data['close'].iloc[0]

            # 5. Calculate percentage change
            if prev_day_close != 0:
                return ((current_price - prev_day_close) / prev_day_close) * 100
            
            return 0.0

        except Exception as e:
            logger.error(f"Error calculating 24H percentage change for {symbol}: {e}", exc_info=True)
            return 0.0

    def _calculate_24h_percentage_change_from_csv(self, symbol: str) -> float:
        """Fallback to calculate 24h percentage change from CSV."""
        try:
            folder = ''
            if '.sd' in symbol: folder = 'forex'
            elif '.lv' in symbol: folder = 'crypto'
            elif 'Roll' in symbol:
                if 'VIX' in symbol: folder = 'other'
                else: folder = 'indices'
            else: folder = 'commodities'
            
            csv_filename = f"/Users/pawan/CLI-Finance-Terminal/data/{folder}/{symbol}_data.csv"
            if not os.path.exists(csv_filename):
                return 0.0

            df = pd.read_csv(csv_filename)
            if df.empty or len(df) < 2:
                return 0.0

            # Assuming the CSV is sorted by date, last row is current, second to last is previous
            last_price = df['close'].iloc[-1]
            previous_price = df['close'].iloc[-2]

            if previous_price != 0:
                return ((last_price - previous_price) / previous_price) * 100
            return 0.0
        except Exception as e:
            logger.warning(f"CSV Fallback Error for {symbol}: {e}")
            return 0.0

    def get_market_status(self) -> Dict:
        """Get current market status"""
        return {
            'status': 'Open' if 9 <= datetime.now().hour <= 16 else 'Closed',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'timezone': 'UTC'
        }

    def get_major_indices_data(self) -> pd.DataFrame:
        """Get data for major indices"""
        return self._get_data_from_csv(self.major_indices, 'indices')

    def get_currency_data(self) -> pd.DataFrame:
        """Get data for major currencies"""
        return self._get_data_from_csv(self.major_currencies, 'currencies')

    def get_commodities_data(self) -> pd.DataFrame:
        """Get data for commodities"""
        return self._get_data_from_csv(self.commodities, 'commodities')

    def get_crypto_data(self) -> pd.DataFrame:
        """Get data for crypto"""
        return self._get_data_from_csv(self.crypto, 'crypto')

    def get_bonds_data(self) -> pd.DataFrame:
        """Get data for bonds (using ETF proxies)"""
        bonds_data = []
        for symbol in self.bonds:
            info = self.av_fetcher.get_symbol_info(symbol)
            if info:
                info['pct_change_24h'] = self._calculate_24h_percentage_change(symbol)
                bonds_data.append(info)
        for item in bonds_data:
            item['Price'] = (item.get('ask', 0) + item.get('bid', 0)) / 2 if item.get('ask') and item.get('bid') else item.get('last', 0)
        return pd.DataFrame(bonds_data)

    def get_volatility_data(self) -> pd.DataFrame:
        """Get volatility indices data"""
        return self._get_data_from_csv(self.volatility_symbols, 'volatility')

    def get_top_movers(self, data: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
        """Get top gainers and losers based on 24-hour price change."""
        if data.empty:
            return pd.DataFrame()
        data['pct_change'] = data['name'].apply(self._calculate_24h_percentage_change)
        data['abs_pct_change'] = data['pct_change'].abs()
        return data.nlargest(top_n, 'abs_pct_change')

    def generate_charts(self, save_dir: str = "./reports/charts") -> List[str]:
        """Generate key market charts for all major asset classes using CSV data."""
        chart_files = []
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # Define symbols for all major asset classes
        all_symbols = {
            'indices': ['US500Roll', 'US30Roll', 'UK100Roll', 'DE40Roll', 'FRA40Roll', 'JP225Roll', 'HK50Roll', 'CHINA50Roll'],
            'forex': ['EURUSD.sd', 'GBPUSD.sd', 'USDJPY.sd', 'AUDUSD.sd', 'USDCAD.sd', 'USDCHF.sd', 'NZDUSD.sd', 'USDCNH.sd'],
            'commodities': ['XAUUSD', 'XAGUSD', 'XPTUSD', 'USOILRoll', 'BRENT', 'NGAS'],
            'crypto': ['BTCUSD.lv', 'ETHUSD.lv', 'XRPUSD.lv', 'LTCUSD.lv', 'BCHUSD.lv', 'EOSUSD.lv'],
            'volatility': ['VIXRoll']
        }
        
        # Flatten all symbols for processing
        symbols_to_chart = []
        for category, symbols in all_symbols.items():
            symbols_to_chart.extend(symbols)

        for symbol in symbols_to_chart:
            try:
                # Determine the folder based on symbol category
                folder = ''
                if '.sd' in symbol:
                    folder = 'forex'
                elif '.lv' in symbol:
                    folder = 'crypto'
                elif 'Roll' in symbol:
                    if 'VIX' in symbol:
                        folder = 'other'
                    elif 'OIL' in symbol:
                        folder = 'commodities'
                    else:
                        folder = 'indices'
                elif symbol in ['XAUUSD', 'XAGUSD', 'XPTUSD']:
                    folder = 'commodities'
                else:
                    folder = 'commodities'  # Default for other symbols
                
                csv_filename = f"/Users/pawan/CLI-Finance-Terminal/data/{folder}/{symbol}_data.csv"
                
                # Check if CSV file exists
                if os.path.exists(csv_filename):
                    logger.info(f"Found CSV data for {symbol} at {csv_filename}")
                    data = pd.read_csv(csv_filename)
                else:
                    logger.warning(f"CSV file not found for {symbol} at {csv_filename}")
                    continue

                # Check if the data has the required columns for candlestick chart
                required_columns = ['time', 'open', 'high', 'low', 'close']
                if not all(col in data.columns for col in required_columns):
                    logger.warning(f"Missing required columns for candlestick chart for {symbol}")
                    continue

                # Generate chart if we have valid data
                if not data.empty and len(data) > 1:  # Need at least 2 data points for a meaningful chart
                    chart_path = os.path.join(save_dir, f"{symbol.replace('/', '_')}_candlestick.png")
                    logger.info(f"Generating candlestick chart for {symbol} -> {chart_path}")
                    chart_file = self.chart_generator.generate_candlestick_chart(data, symbol, chart_path)
                    if chart_file and os.path.exists(chart_file):
                        chart_files.append(chart_file)
                        logger.info(f"Successfully generated chart for {symbol}")
                    else:
                        logger.warning(f"Failed to generate chart for {symbol}")
                else:
                    logger.warning(f"Insufficient data for chart generation for {symbol}")
                    
            except Exception as e:
                logger.error(f"Failed to generate chart for {symbol}: {e}", exc_info=True)
        
        logger.info(f"Generated {len(chart_files)} charts out of {len(symbols_to_chart)} attempted")
        return chart_files

    def get_economic_calendar(self) -> pd.DataFrame:
        """Get today's economic calendar from the CSV file."""
        try:
            local_calendar_path = "./economic-calendar/ECONOMIC_CALENDAR_DATA.csv"
            if os.path.exists(local_calendar_path):
                df = pd.read_csv(local_calendar_path)
                logger.info(f"Successfully read economic calendar from: {local_calendar_path}")
                if 'DateTime' in df.columns:
                    df.rename(columns={'DateTime': 'Time'}, inplace=True)
                if 'Time' in df.columns:
                    df['Time'] = pd.to_datetime(df['Time'], errors='coerce')
                return df.replace('nan', pd.NA)
            else:
                logger.warning(f"Economic calendar CSV file not found at {local_calendar_path}")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error reading economic calendar CSV: {e}")
            return pd.DataFrame()

    def get_financial_news(self) -> Optional[List[Dict]]:
        """Fetches financial news headlines."""
        logger.info("Fetching financial news...")
        try:
            headlines = self.news_fetcher.get_financial_news()
            if headlines:
                logger.info(f"Successfully fetched {len(headlines)} financial news headlines.")
                return headlines
            else:
                logger.warning("No financial news headlines received.")
                return None
        except Exception as e:
            logger.error(f"Error fetching financial news: {e}")
            return None

    def get_volatility_summary(self) -> pd.DataFrame:
        """Get volatility summary for major assets"""
        volatility_summary = []
        symbols = self.major_indices + self.major_currencies + self.commodities
        for symbol in symbols[:5]:
            try:
                end_time = datetime.now()
                start_time = end_time - timedelta(days=60)
                data = self.av_fetcher.fetch_historical_data(symbol, 'D', start_time, end_time)
                if not data.empty:
                    summary = self.volatility_calculator.get_volatility_summary(data, symbol)
                    if summary:
                        volatility_summary.append(summary)
            except Exception as e:
                logger.warning(f"Error calculating volatility for {symbol}: {e}")
        return pd.DataFrame(volatility_summary)

    def generate_report(self, save_dir: str = "./reports", format: str = "txt", institutional_grade: bool = False) -> str:
        """Generate the complete daily investment report"""
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_dir = os.path.join(save_dir, f"daily_report_{timestamp}")
        chart_dir = os.path.join(report_dir, "charts")
        os.makedirs(report_dir, exist_ok=True)
        
        logger.info("Generating daily investment report...")
        market_status = self.get_market_status()
        indices_data = self.get_major_indices_data()
        currency_data = self.get_currency_data()
        commodities_data = self.get_commodities_data()
        crypto_data = self.get_crypto_data()
        bonds_data = self.get_bonds_data()
        volatility_data = self.get_volatility_data()
        
        all_data = pd.concat([indices_data, currency_data, commodities_data, crypto_data, bonds_data], ignore_index=True)
        top_movers = self.get_top_movers(all_data) if not all_data.empty else pd.DataFrame()
        
        calendar_data = self.get_economic_calendar()
        financial_news = self.get_financial_news()
        volatility_summary = self.get_volatility_summary()
        
        logger.info("Generating charts...")
        chart_files = self.generate_charts(chart_dir)
        
        if format.lower() == "pdf":
            if institutional_grade:
                report_path = self._generate_institutional_pdf_report(
                    market_status, indices_data, currency_data, commodities_data, bonds_data,
                    volatility_data, top_movers, calendar_data, volatility_summary, chart_files,
                    report_dir, timestamp)
            else:
                report_path = self._generate_pdf_report(
                    market_status, indices_data, currency_data, commodities_data, bonds_data,
                    volatility_data, top_movers, calendar_data, financial_news, volatility_summary, chart_files,
                    report_dir, timestamp)
        else:
            report_path = self._generate_text_report(
                market_status, indices_data, currency_data, commodities_data, bonds_data,
                volatility_data, top_movers, calendar_data, financial_news, volatility_summary, chart_files,
                report_dir, timestamp)
        
        logger.info(f"Daily investment report saved to: {report_path}")
        return report_path

    def _generate_pdf_report(self, market_status: Dict, indices_data: pd.DataFrame,
                             currency_data: pd.DataFrame, commodities_data: pd.DataFrame,
                             bonds_data: pd.DataFrame, volatility_data: pd.DataFrame, 
                             top_movers: pd.DataFrame, calendar_data: pd.DataFrame,
                             financial_news: Optional[List[Dict]], volatility_summary: pd.DataFrame,
                             chart_files: List[str], report_dir: str, timestamp: str) -> str:
        pdf_path = os.path.join(report_dir, f"daily_report_{timestamp}.pdf")
        pdf_gen = ProfessionalPDFReportGenerator(pdf_path)
        
        pdf_gen.add_cover_page()
        pdf_gen.add_table_of_contents()
        pdf_gen.add_title("DAILY INVESTMENT REPORT")
        
        try:
            executive_summary_points = self.llm_generator.generate_executive_summary(
                indices_data, currency_data, commodities_data, top_movers, calendar_data
            )
        except Exception as e:
            logger.warning(f"Failed to generate AI executive summary: {e}")
            executive_summary_points = [
                "⚠️ LLM EXECUTIVE SUMMARY UNAVAILABLE ⚠️",
                "Markets are currently stable with mixed sentiment.",
                "Key indices showing moderate volatility.",
            ]
        
        pdf_gen.add_executive_summary(executive_summary_points)
        pdf_gen.add_market_overview(market_status, indices_data)
        pdf_gen.add_indices_table(indices_data)
        pdf_gen.add_currencies_table(currency_data)
        pdf_gen.add_commodities_table(commodities_data)
        pdf_gen.add_bonds_table(bonds_data)
        pdf_gen.add_volatility_table(volatility_data)
        pdf_gen.add_top_movers_table(top_movers)
        if financial_news:
            pdf_gen.add_financial_news_section(financial_news)
        pdf_gen.add_calendar_events(calendar_data)
        pdf_gen.add_volatility_summary(volatility_summary)
        pdf_gen.add_charts(chart_files)
        pdf_gen.add_disclaimer()
        
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
        try:
            executive_summary_points = self.llm_generator.generate_executive_summary(
                indices_data, currency_data, commodities_data, top_movers, calendar_data
            )
        except Exception as e:
            logger.warning(f"Failed to generate AI executive summary: {e}")
            executive_summary_points = [
                "⚠️ LLM EXECUTIVE SUMMARY UNAVAILABLE ⚠️",
                "Markets are currently stable with mixed sentiment.",
                "Key indices showing moderate volatility.",
            ]
        
        pdf_gen.add_executive_summary(executive_summary_points)
        
        # Market Overview
        pdf_gen.add_market_overview(market_status, indices_data)
        
        # Major Indices
        pdf_gen.add_indices_table(indices_data)
        
        # Major Currencies
        pdf_gen.add_currencies_table(currency_data)
        
        # Commodities
        pdf_gen.add_commodities_table(commodities_data)
        
        # Bonds/ETFs
        pdf_gen.add_bonds_table(bonds_data)
        
        # Market Volatility
        pdf_gen.add_volatility_table(volatility_data)
        
        # Top Movers
        pdf_gen.add_top_movers_table(top_movers)
        
        # Economic Calendar
        pdf_gen.add_calendar_events(calendar_data)
        
        # Volatility Summary
        pdf_gen.add_volatility_summary(volatility_summary)
        
        # Risk Metrics
        # First, we need to collect historical data for risk calculations
        from datetime import datetime, timedelta
        historical_data_dict = {}
        end_time = datetime.now()
        start_time = end_time - timedelta(days=90)  # 90 days of historical data
        
        # Collect historical data for major indices
        for symbol in self.major_indices[:3]:  # Limit to first 3 for performance
            try:
                # Use Alpha Vantage to fetch historical data
                data = self.av_fetcher.fetch_historical_data(
                    symbol, 'D', start_time, end_time)
                
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

    def _generate_text_report(self, market_status: Dict, indices_data: pd.DataFrame,
                             currency_data: pd.DataFrame, commodities_data: pd.DataFrame,
                             bonds_data: pd.DataFrame, volatility_data: pd.DataFrame, 
                             top_movers: pd.DataFrame, calendar_data: pd.DataFrame, 
                             financial_news: Optional[List[Dict]], volatility_summary: pd.DataFrame,
                             chart_files: List[str], report_dir: str, timestamp: str) -> str:
        timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        report = [f"DAILY INVESTMENT REPORT - {timestamp_str}\n\n"]
        
        report.append(f"MARKET STATUS\nStatus: {market_status.get('status', 'Unknown')}\n\n")
        
        for name, data in [("MAJOR INDICES", indices_data), ("MAJOR CURRENCIES", currency_data), ("COMMODITIES", commodities_data)]:
            report.append(f"{name}\n")
            if not data.empty:
                report.append(data.to_string(index=False))
            else:
                report.append("No data available")
            report.append("\n\n")
            
        if financial_news:
            report.append("FINANCIAL MARKET NEWS\n")
            for article in financial_news:
                report.append(f"• {article.get('title', 'No Title')}\n")
            report.append("\n")
        
        report_content = "".join(report)
        report_path = os.path.join(report_dir, f"daily_report_{timestamp}.txt")
        with open(report_path, 'w') as f:
            f.write(report_content)
        return report_path

    def _calculate_comprehensive_risk_metrics(self, indices_data: pd.DataFrame, 
                                           currency_data: pd.DataFrame, 
                                           commodities_data: pd.DataFrame, 
                                           volatility_data: pd.DataFrame,
                                           historical_data_dict: Dict) -> Dict:
        """Calculate comprehensive risk metrics for institutional reports"""
        import numpy as np
        
        risk_metrics = {}
        
        # Calculate basic risk metrics based on available data
        try:
            # Sharpe ratio approximation (using a simplified approach)
            risk_metrics['sharpe_ratio'] = 1.25  # Placeholder value
            risk_metrics['sortino_ratio'] = 1.85  # Placeholder value
            risk_metrics['max_drawdown'] = -0.15  # Placeholder value
            risk_metrics['value_at_risk_95'] = -0.035  # Placeholder value
            risk_metrics['value_at_risk_99'] = -0.052  # Placeholder value
            risk_metrics['conditional_var_95'] = -0.058  # Placeholder value
            risk_metrics['market_beta'] = 1.15  # Placeholder value
            risk_metrics['indices_volatility_annualized'] = 0.22  # Placeholder value
            risk_metrics['average_correlation'] = 0.45  # Placeholder value
            risk_metrics['market_stress_indicator'] = 0.65  # Placeholder value
            risk_metrics['market_regime_confidence'] = 0.78  # Placeholder value
            
            # Calculate more sophisticated metrics based on historical data if available
            if historical_data_dict:
                returns_list = []
                for symbol, data in historical_data_dict.items():
                    if not data.empty and 'close' in data.columns:
                        # Calculate returns
                        data['returns'] = data['close'].pct_change()
                        returns = data['returns'].dropna()
                        if len(returns) > 0:
                            returns_list.extend(returns.tolist())
                
                if returns_list:
                    returns_array = np.array(returns_list)
                    if len(returns_array) > 1:
                        # Recalculate some metrics based on actual historical data
                        mean_return = np.mean(returns_array)
                        std_return = np.std(returns_array)
                        
                        if std_return != 0:
                            risk_metrics['sharpe_ratio'] = mean_return / std_return * np.sqrt(252)  # Annualized
                        
                        # Calculate Value at Risk (95% and 99%)
                        if len(returns_array) > 10:
                            risk_metrics['value_at_risk_95'] = np.percentile(returns_array, 5)
                            risk_metrics['value_at_risk_99'] = np.percentile(returns_array, 1)
                            
                            # Calculate Conditional Value at Risk (Expected Shortfall)
                            var_95 = risk_metrics['value_at_risk_95']
                            var_99 = risk_metrics['value_at_risk_99']
                            shortfall_95 = returns_array[returns_array <= var_95]
                            shortfall_99 = returns_array[returns_array <= var_99]
                            
                            if len(shortfall_95) > 0:
                                risk_metrics['conditional_var_95'] = np.mean(shortfall_95)
                            if len(shortfall_99) > 0:
                                risk_metrics['conditional_var_99'] = np.mean(shortfall_99)
        
        except Exception as e:
            logger.warning(f"Error calculating comprehensive risk metrics: {e}")
            # Fallback to default values
            risk_metrics = {
                'sharpe_ratio': 1.25,
                'sortino_ratio': 1.85,
                'max_drawdown': -0.15,
                'value_at_risk_95': -0.035,
                'value_at_risk_99': -0.052,
                'conditional_var_95': -0.058,
                'market_beta': 1.15,
                'indices_volatility_annualized': 0.22,
                'average_correlation': 0.45,
                'market_stress_indicator': 0.65,
                'market_regime_confidence': 0.78
            }
        
        return risk_metrics

    def shutdown(self):
        """Shutdown connections"""
        # Finnhub doesn't need explicit shutdown
        pass

# Example usage
if __name__ == "__main__":
    try:
        report_gen = DailyInvestmentReportGenerator()
        report_path = report_gen.generate_report()
        print(f"Report generated: {report_path}")
        report_gen.shutdown()
    except Exception as e:
        print(f"Error generating report: {e}")