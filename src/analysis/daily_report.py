import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Local imports
from src.data.providers.alphavantage_data import AlphaVantageDataFetcher
from src.analysis.volatility import VolatilityCalculator
from src.analysis.charts import MarketChartGenerator
from src.analysis.professional_pdf_report import ProfessionalPDFReportGenerator
from src.analysis.advanced_analytics import AdvancedMarketAnalytics
from src.analysis.institutional_analytics import InstitutionalMarketAnalytics
from src.analysis.enhanced_institutional_pdf import EnhancedInstitutionalPDFReportGenerator
from src.analysis.llm_integration import LLMExecutiveSummaryGenerator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DailyInvestmentReportGenerator:
    """Class to generate daily investment reports using Alpha Vantage data."""

    def __init__(self):
        """Initialize the report generator."""
        self.av_fetcher = AlphaVantageDataFetcher()
        self.volatility_calculator = VolatilityCalculator()
        self.chart_generator = MarketChartGenerator()
        self.advanced_analytics = AdvancedMarketAnalytics()
        self.institutional_analytics = InstitutionalMarketAnalytics()
        self.llm_generator = LLMExecutiveSummaryGenerator()

        # These symbols will be mapped by the fetcher using symbol_map.py
        self.major_indices = ['US500Roll', 'US30Roll', 'UK100Roll', 'DE40Roll', 'JP225Roll']
        self.major_currencies = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD']
        self.commodities = ['XAUUSD', 'USOILRoll']
        self.bonds = ['TLT', 'IEF', 'SHY', 'LQD']
        self.crypto = ['BTCUSD', 'ETHUSD']
        self.volatility_symbols = ['VIXRoll']
        
    def _fetch_data(self, symbols: List[str]) -> pd.DataFrame:
        """Fetch and process data for a list of symbols from Alpha Vantage."""
        data_list = []
        for symbol in symbols:
            try:
                # Using GLOBAL_QUOTE as per instructions
                quote = self.av_fetcher.get_global_quote(symbol)
                if quote:
                    price_str = quote.get('price', '0')
                    price = float(price_str) if price_str and price_str != 'N/A' else 0.0

                    pct_change_str = str(quote.get('change_percent', '0%')).strip('%')
                    pct_change = float(pct_change_str) if pct_change_str and pct_change_str != 'N/A' else 0.0

                    volume_str = str(quote.get('volume', '0'))
                    volume = int(volume_str) if volume_str and volume_str.isdigit() else 0

                    data_list.append({
                        'name': symbol,
                        'Price': price,
                        'last': price,
                        'ask': price,
                        'bid': price,
                        'pct_change_24h': pct_change,
                        'volume': volume
                    })
            except Exception as e:
                logger.warning(f"Error fetching data for {symbol} via GLOBAL_QUOTE: {e}")
        return pd.DataFrame(data_list)

    def get_market_status(self) -> Dict:
        """Get current market status (placeholder)."""
        return {
            'status': 'Open' if 9 <= datetime.now().hour <= 16 else 'Closed',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'timezone': 'UTC'
        }

    def get_major_indices_data(self) -> pd.DataFrame:
        return self._fetch_data(self.major_indices)

    def get_currency_data(self) -> pd.DataFrame:
        return self._fetch_data(self.major_currencies)

    def get_commodities_data(self) -> pd.DataFrame:
        return self._fetch_data(self.commodities)

    def get_crypto_data(self) -> pd.DataFrame:
        return self._fetch_data(self.crypto)

    def get_bonds_data(self) -> pd.DataFrame:
        return self._fetch_data(self.bonds)

    def get_volatility_data(self) -> pd.DataFrame:
        return self._fetch_data(self.volatility_symbols)

    def get_top_movers(self, data: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
        """Get top gainers and losers based on 24-hour price change."""
        if data.empty or 'pct_change_24h' not in data.columns:
            return pd.DataFrame()
        data['abs_pct_change'] = data['pct_change_24h'].abs()
        return data.nlargest(top_n, 'abs_pct_change')

    def generate_charts(self, save_dir: str = "./reports/charts") -> List[str]:
        """Generate key market charts for all major asset classes using Alpha Vantage data."""
        chart_files = []
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        all_symbols = self.major_indices + self.major_currencies + self.commodities
        for symbol in all_symbols:
            try:
                data = self.av_fetcher.get_intraday_data(symbol, interval='60min')
                if not data.empty:
                    chart_path = os.path.join(save_dir, f"{symbol.replace('/', '_')}_candlestick.png")
                    chart_file = self.chart_generator.generate_candlestick_chart(data, symbol, chart_path)
                    if chart_file and os.path.exists(chart_file):
                        chart_files.append(chart_file)
            except Exception as e:
                logger.error(f"Failed to generate chart for {symbol}: {e}")
        return chart_files

    def get_economic_calendar(self) -> pd.DataFrame:
        """Get today's economic calendar from Alpha Vantage."""
        try:
            calendar_df = self.av_fetcher.get_economic_calendar()
            return calendar_df if not calendar_df.empty else pd.DataFrame()
        except Exception as e:
            logger.error(f"Error fetching economic calendar: {e}")
            return pd.DataFrame()

    def get_financial_news(self) -> Optional[List[Dict]]:
        """Fetches financial news headlines from Alpha Vantage."""
        try:
            news = self.av_fetcher.get_news_sentiment()
            return news if news else None
        except Exception as e:
            logger.error(f"Error fetching financial news: {e}")
            return None

    def get_volatility_summary(self) -> pd.DataFrame:
        """Get volatility summary for the benchmark asset (SPY)."""
        volatility_summary = []
        benchmark_symbol = 'US500Roll'  # Mapped to SPY
        try:
            data = self.av_fetcher.get_historical_data(benchmark_symbol, days=100)
            if not data.empty:
                summary = self.volatility_calculator.get_volatility_summary(data, benchmark_symbol)
                if summary:
                    volatility_summary.append(summary)
        except Exception as e:
            logger.warning(f"Error calculating volatility for {benchmark_symbol}: {e}")
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
            # Text report generation is not a priority, but keeping the structure
            report_path = os.path.join(report_dir, f"daily_report_{timestamp}.txt")
            with open(report_path, 'w') as f:
                f.write("Text report generation is being refactored.")
        
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
            executive_summary_points = ["⚠️ LLM EXECUTIVE SUMMARY UNAVAILABLE ⚠️"]
        
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
        pdf_path = os.path.join(report_dir, f"daily_report_{timestamp}_institutional.pdf")
        pdf_gen = EnhancedInstitutionalPDFReportGenerator(pdf_path)
        
        pdf_gen.add_cover_page()
        pdf_gen.add_table_of_contents()
        pdf_gen.add_title("DAILY INVESTMENT REPORT - INSTITUTIONAL GRADE")
        
        try:
            executive_summary_points = self.llm_generator.generate_executive_summary(
                indices_data, currency_data, commodities_data, top_movers, calendar_data
            )
        except Exception as e:
            logger.warning(f"Failed to generate AI executive summary: {e}")
            executive_summary_points = ["⚠️ LLM EXECUTIVE SUMMARY UNAVAILABLE ⚠️"]
        
        pdf_gen.add_executive_summary(executive_summary_points)
        pdf_gen.add_market_overview(market_status, indices_data)
        pdf_gen.add_indices_table(indices_data)
        pdf_gen.add_currencies_table(currency_data)
        pdf_gen.add_commodities_table(commodities_data)
        pdf_gen.add_bonds_table(bonds_data)
        pdf_gen.add_volatility_table(volatility_data)
        pdf_gen.add_top_movers_table(top_movers)
        pdf_gen.add_calendar_events(calendar_data)
        pdf_gen.add_volatility_summary(volatility_summary)
        
        # Risk Metrics using benchmark asset
        historical_data = self.av_fetcher.get_historical_data('US500Roll', days=90)
        risk_metrics = self._calculate_comprehensive_risk_metrics(historical_data)
        pdf_gen.add_risk_metrics(risk_metrics)
        
        pdf_gen.add_charts(chart_files)
        pdf_gen.add_disclaimer()
        pdf_gen.generate()
        return pdf_path

    def _calculate_comprehensive_risk_metrics(self, historical_data: pd.DataFrame) -> Dict:
        """Calculate comprehensive risk metrics for institutional reports from historical data."""
        risk_metrics = {
            'sharpe_ratio': 'N/A', 'sortino_ratio': 'N/A', 'max_drawdown': 'N/A',
            'value_at_risk_95': 'N/A', 'conditional_var_95': 'N/A'
        }
        if historical_data.empty:
            return risk_metrics

        try:
            returns = historical_data['close'].pct_change().dropna()
            if len(returns) > 1:
                # Sharpe Ratio (annualized, risk-free rate = 0)
                sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252)
                risk_metrics['sharpe_ratio'] = f"{sharpe_ratio:.2f}"

                # Sortino Ratio (annualized, risk-free rate = 0)
                downside_returns = returns[returns < 0]
                if len(downside_returns) > 1:
                    downside_std = np.std(downside_returns)
                    if downside_std > 0:
                        sortino_ratio = np.mean(returns) / downside_std * np.sqrt(252)
                        risk_metrics['sortino_ratio'] = f"{sortino_ratio:.2f}"

                # Max Drawdown
                cumulative_returns = (1 + returns).cumprod()
                peak = cumulative_returns.expanding(min_periods=1).max()
                drawdown = (cumulative_returns - peak) / peak
                risk_metrics['max_drawdown'] = f"{drawdown.min():.2%}"
                
                # VaR and CVaR
                risk_metrics['value_at_risk_95'] = f"{returns.quantile(0.05):.2%}"
                risk_metrics['conditional_var_95'] = f"{returns[returns <= returns.quantile(0.05)].mean():.2%}"

        except Exception as e:
            logger.warning(f"Could not calculate risk metrics: {e}")
        
        return risk_metrics

    def shutdown(self):
        """Shutdown connections if any."""
        pass

if __name__ == "__main__":
    try:
        report_gen = DailyInvestmentReportGenerator()
        # Example: Generate institutional PDF report
        report_path = report_gen.generate_report(format="pdf", institutional_grade=True)
        print(f"Report generated: {report_path}")
    except Exception as e:
        print(f"Error generating report: {e}", file=sys.stderr)