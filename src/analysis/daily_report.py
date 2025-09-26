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
    
    def __init__(self, use_wine_mt5: bool = False):
        """Initialize the report generator"""
        self.use_wine_mt5 = use_wine_mt5
        
        # Initialize data fetchers
        self.mt5_fetcher = MT5DataFetcher(use_wine_mt5=use_wine_mt5)
        self.calendar_fetcher = EconomicCalendarFetcher()
        self.mt5_calendar_fetcher = MT5CalendarFetcher()
        self.advanced_calendar_extractor = AdvancedMT5CalendarExtractor()
        self.news_fetcher = NewsAPI()
        self.volatility_calculator = VolatilityCalculator()
        self.chart_generator = MarketChartGenerator()
        self.advanced_analytics = AdvancedMarketAnalytics()
        self.institutional_analytics = InstitutionalMarketAnalytics()
        
        # Initialize LLM executive summary generator
        self.llm_generator = LLMExecutiveSummaryGenerator()
        
        # Define default symbols to track with available symbols from MT5
        self.major_indices = ['US500Roll', 'US30Roll', 'UT100Roll', 'DE40Roll', 'UK100Roll']
        self.major_currencies = ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD']
        self.commodities = ['XAUUSD', 'XAGUSD', 'USOIL', 'UKOIL']
        self.bonds = ['TLT', 'IEF', 'SHY', 'LQD']
        self.volatility_symbols = ['VIX', 'VXN', 'VXD']

    def _get_wine_symbol_info(self, symbol: str) -> Optional[Dict]:
        """Get symbol info from Wine MT5"""
        if not self.use_wine_mt5:
            return None
        
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
        
        try:
            from src.data.providers.wine_mt5_connector import wine_mt5_connector
            rates = wine_mt5_connector.copy_rates_range(symbol, timeframe, start_time, end_time)
            if rates:
                df = pd.DataFrame(rates)
                df['time'] = pd.to_datetime(df['time'], unit='s')
                return df
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol} from Wine MT5: {e}")
            return pd.DataFrame()

    def _calculate_24h_percentage_change(self, symbol: str) -> float:
        """Calculate 24-hour percentage change for a symbol"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=1)
            
            if self.use_wine_mt5:
                historical_data = self._get_wine_historical_data(symbol, mt5.TIMEFRAME_M15, start_time, end_time)
            else:
                historical_data = self.mt5_fetcher.fetch_historical_data(symbol, mt5.TIMEFRAME_M15, start_time, end_time)
            
            if not historical_data.empty and len(historical_data) > 1:
                first_price = historical_data['close'].iloc[0]
                last_price = historical_data['close'].iloc[-1]
                if first_price != 0:
                    return ((last_price - first_price) / first_price) * 100
            return 0.0
        except Exception as e:
            logger.warning(f"Error calculating 24H percentage change for {symbol}: {e}")
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
        indices_data = []
        for symbol in self.major_indices:
            info = self.mt5_fetcher.get_symbol_info(symbol)
            if info:
                info['pct_change_24h'] = self._calculate_24h_percentage_change(symbol)
                indices_data.append(info)
        df = pd.DataFrame(indices_data)
        for item in indices_data:
            item['Price'] = (item.get('ask', 0) + item.get('bid', 0)) / 2 if item.get('ask') and item.get('bid') else item.get('last', 0)
        return pd.DataFrame(indices_data)

    def get_currency_data(self) -> pd.DataFrame:
        """Get data for major currencies"""
        currency_data = []
        for symbol in self.major_currencies:
            info = self.mt5_fetcher.get_symbol_info(symbol)
            if info:
                info['pct_change_24h'] = self._calculate_24h_percentage_change(symbol)
                currency_data.append(info)
        for item in currency_data:
            item['Price'] = (item.get('ask', 0) + item.get('bid', 0)) / 2 if item.get('ask') and item.get('bid') else item.get('last', 0)
        return pd.DataFrame(currency_data)

    def get_commodities_data(self) -> pd.DataFrame:
        """Get data for commodities"""
        commodities_data = []
        for symbol in self.commodities:
            info = self.mt5_fetcher.get_symbol_info(symbol)
            if info:
                info['pct_change_24h'] = self._calculate_24h_percentage_change(symbol)
                commodities_data.append(info)
        for item in commodities_data:
            item['Price'] = (item.get('ask', 0) + item.get('bid', 0)) / 2 if item.get('ask') and item.get('bid') else item.get('last', 0)
        return pd.DataFrame(commodities_data)

    def get_bonds_data(self) -> pd.DataFrame:
        """Get data for bonds (using ETF proxies)"""
        bonds_data = []
        for symbol in self.bonds:
            info = self.mt5_fetcher.get_symbol_info(symbol)
            if info:
                info['pct_change_24h'] = self._calculate_24h_percentage_change(symbol)
                bonds_data.append(info)
        for item in bonds_data:
            item['Price'] = (item.get('ask', 0) + item.get('bid', 0)) / 2 if item.get('ask') and item.get('bid') else item.get('last', 0)
        return pd.DataFrame(bonds_data)

    def get_volatility_data(self) -> pd.DataFrame:
        """Get volatility indices data"""
        volatility_data = []
        for symbol in self.volatility_symbols:
            info = self.mt5_fetcher.get_symbol_info(symbol)
            if info:
                volatility_data.append(info)
        for item in volatility_data:
            item['Price'] = (item.get('ask', 0) + item.get('bid', 0)) / 2 if item.get('ask') and item.get('bid') else item.get('last', 0)
        return pd.DataFrame(volatility_data)

    def get_top_movers(self, data: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
        """Get top gainers and losers based on 24-hour price change."""
        if data.empty:
            return pd.DataFrame()
        data['pct_change'] = data['name'].apply(self._calculate_24h_percentage_change)
        data['abs_pct_change'] = data['pct_change'].abs()
        return data.nlargest(top_n, 'abs_pct_change')

    def generate_charts(self, save_dir: str = "./reports/charts") -> List[str]:
        """Generate key market charts for a predefined list of symbols."""
        chart_files = []
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        symbols_to_chart = [
            'US500Roll', 'US30Roll', 'UT100Roll', 'DE40Roll', 'UK100Roll',
            'GBPUSD', 'USDJPY', 'XAUUSD', 'XAGUSD'
        ]

        for symbol in symbols_to_chart:
            try:
                end_time = datetime.now()
                start_time = end_time - timedelta(days=365)
                data = self.mt5_fetcher.fetch_historical_data(symbol, mt5.TIMEFRAME_D1, start_time, end_time)

                if not data.empty and all(col in data.columns for col in ['open', 'high', 'low', 'close']):
                    chart_path = os.path.join(save_dir, f"{symbol.replace('/', '_')}_candlestick.png")
                    chart_file = self.chart_generator.generate_candlestick_chart(data, symbol, chart_path)
                    if chart_file:
                        chart_files.append(chart_file)
                else:
                    logger.warning(f"Could not generate chart for {symbol} due to missing data.")
            except Exception as e:
                logger.error(f"Failed to generate chart for {symbol}: {e}", exc_info=True)
        
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
                data = self.mt5_fetcher.fetch_historical_data(symbol, mt5.TIMEFRAME_D1, start_time, end_time)
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
        bonds_data = self.get_bonds_data()
        volatility_data = self.get_volatility_data()
        
        all_data = pd.concat([indices_data, currency_data, commodities_data, bonds_data], ignore_index=True)
        top_movers = self.get_top_movers(all_data) if not all_data.empty else pd.DataFrame()
        
        calendar_data = self.get_economic_calendar()
        financial_news = self.get_financial_news()
        volatility_summary = self.get_volatility_summary()
        
        logger.info("Generating charts...")
        chart_files = self.generate_charts(chart_dir)
        
        if format.lower() == "pdf":
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

    def shutdown(self):
        """Shutdown connections"""
        self.mt5_fetcher.shutdown()

# Example usage
if __name__ == "__main__":
    try:
        report_gen = DailyInvestmentReportGenerator(use_wine_mt5=True)
        report_path = report_gen.generate_report()
        print(f"Report generated: {report_path}")
        report_gen.shutdown()
    except Exception as e:
        print(f"Error generating report: {e}")