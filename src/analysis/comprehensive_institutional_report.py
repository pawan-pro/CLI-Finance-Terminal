# /Users/pawan/CLI-Finance-Terminal/src/analysis/comprehensive_institutional_report.py

import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from reportlab.platypus import Paragraph, Spacer


# Correct import: MarketChartGenerator is defined in src.analysis.charts
from src.analysis.charts import MarketChartGenerator

# Local imports
from src.analysis.enhanced_institutional_pdf import EnhancedInstitutionalPDFReportGenerator
from src.analysis.enhanced_top_movers import EnhancedTopMoversAnalyzer
from src.analysis.institutional_analytics import InstitutionalMarketAnalytics
from src.analysis.institutional_calendar import InstitutionalCalendarAnalyzer
from src.data.providers.alphavantage_data import AlphaVantageDataFetcher

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ReportType(Enum):
    DAILY_MARKET_REPORT = "Daily Market Report"

@dataclass
class InstitutionalReportConfig:
    report_type: ReportType = ReportType.DAILY_MARKET_REPORT
    include_charts: bool = True
    include_detailed_analysis: bool = True
    include_risk_metrics: bool = True
    include_calendar_analysis: bool = True
    include_portfolio_impact: bool = False
    portfolio_exposures: List[str] = field(default_factory=list)
    output_directory: str = "./reports/institutional/"
    confidentiality_level: str = "CONFIDENTIAL - FOR AUTHORIZED PERSONNEL ONLY"

class ComprehensiveInstitutionalReportGenerator:
    """Comprehensive institutional report generator with all enhanced features"""
    
    def __init__(self, config: Optional[InstitutionalReportConfig] = None):
        self.config = config or InstitutionalReportConfig()
        self.analytics = InstitutionalMarketAnalytics()
        self.top_movers_analyzer = EnhancedTopMoversAnalyzer()
        self.calendar_analyzer = InstitutionalCalendarAnalyzer()
        
        # --- MODIFICATION: Instantiate the real chart generator ---
        self.chart_generator = MarketChartGenerator()
        
        # Use AlphaVantageDataFetcher instead of MT5DataFetcher
        from src.config.settings import settings
        api_key = settings["api_keys"]["alpha_vantage"]
        if not api_key:
            raise ValueError("ALPHAVANTAGE_API_KEY not found in environment variables.")
        self.data_fetcher = AlphaVantageDataFetcher(api_key=api_key)
        
        os.makedirs(self.config.output_directory, exist_ok=True)
        self.generated_charts = []
        
    def generate_comprehensive_report(self, symbols: Optional[List[str]] = None) -> str:
        logger.info(f"Generating comprehensive {self.config.report_type.value}...")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = os.path.join(
            self.config.output_directory,
            f"institutional_{self.config.report_type.name.lower()}_{timestamp}.pdf"
        )
        pdf_generator = EnhancedInstitutionalPDFReportGenerator(report_filename)
        
        self._add_report_structure(pdf_generator)
        market_data = self._fetch_comprehensive_market_data(symbols)
        self._add_executive_summary(pdf_generator, market_data)
        self._add_market_overview(pdf_generator, market_data)
        
        if self.config.include_detailed_analysis:
            self._add_detailed_analysis(pdf_generator, market_data)
        
        self._add_top_movers_analysis(pdf_generator, market_data)
        
        if self.config.include_calendar_analysis:
            self._add_calendar_analysis(pdf_generator, market_data)
        
        if self.config.include_risk_metrics:
            self._add_risk_metrics(pdf_generator, market_data)
        
        if self.config.include_charts:
            self._add_technical_charts(pdf_generator, market_data)
        
        self._add_compliance_sections(pdf_generator)
        pdf_generator.generate()
        logger.info(f"Comprehensive institutional report generated: {report_filename}")
        return report_filename

    # --- MODIFICATION: REPLACED CHART GENERATION LOGIC ---
    def _add_technical_charts(self, pdf_generator, market_data: Dict):
        """Generates and adds technical charts to the report by reading from CSV files."""
        logger.info("Generating and adding technical charts to report...")
        chart_files = self._generate_institutional_charts(market_data)
        
        if chart_files:
            pdf_generator.add_charts(chart_files)
            logger.info(f"Successfully queued {len(chart_files)} charts for the PDF report.")
        else:
            logger.warning("No chart files were generated to add to the PDF report.")

    def _generate_institutional_charts(self, market_data: Dict) -> List[str]:
        """
        Generates charts by reading CSV data for top symbols using the real MarketChartGenerator.
        """
        all_chart_files = []
        max_charts_in_report = 9 # Limit to a reasonable number for the report

        logger.info("Generating charts from pre-fetched CSV data...")

        chart_dir = os.path.join(self.config.output_directory, "charts", datetime.now().strftime('%Y%m%d_%H%M%S'))
        base_data_path = "/Users/pawan/CLI-Finance-Terminal/data" 

        asset_classes_to_chart = ['indices', 'currencies', 'commodities', 'crypto']

        symbols_to_chart = []
        for asset_class in asset_classes_to_chart:
            if asset_class in market_data and not market_data[asset_class].empty:
                # Get top 3 symbols from each class to prioritize them
                symbols_to_chart.extend(market_data[asset_class].head(3)['name'].tolist())

        # Ensure we don't exceed the max chart limit
        symbols_to_chart = symbols_to_chart[:max_charts_in_report]

        for symbol in symbols_to_chart:
            try:
                # Find the asset class for the current symbol to locate the folder
                folder = None
                for ac, data_df in market_data.items():
                    if not data_df.empty and 'name' in data_df.columns and symbol in data_df['name'].values:
                        folder = 'forex' if ac == 'currencies' else ac
                        break
                
                if not folder:
                    logger.warning(f"Could not determine data folder for symbol '{symbol}'. Skipping.")
                    continue

                csv_filename = os.path.join(base_data_path, folder, f"{symbol}_data.csv")

                if not os.path.exists(csv_filename):
                    logger.warning(f"CSV data file not found for {symbol} at '{csv_filename}'. Skipping chart.")
                    continue

                df = pd.read_csv(csv_filename)
                if df.empty:
                    logger.warning(f"Data file for {symbol} is empty. Skipping chart.")
                    continue

                safe_symbol_name = symbol.replace('.', '_').replace('/', '_')
                output_base_path = os.path.join(chart_dir, safe_symbol_name)

                generated_files = self.chart_generator.generate_dashboard(
                    df=df, symbol=symbol, save_path_base=output_base_path
                )
                
                png_file = next((f for f in generated_files if f.endswith('.png')), None)
                if png_file:
                    all_chart_files.append(png_file)
                    logger.info(f"Successfully generated chart for {symbol}.")
                else:
                    logger.warning(f"A PNG chart was not generated for {symbol}.")

            except Exception as e:
                logger.error(f"An unexpected error occurred while generating charts for {symbol}: {e}")
                continue

        logger.info(f"Generated a total of {len(all_chart_files)} chart images.")
        return all_chart_files
    # --- END OF MODIFIED SECTION ---
    
    #
    # The methods below this point are your original, working code and remain unchanged.
    #

    def _add_report_structure(self, pdf_generator):
        pdf_generator.add_cover_page()
        pdf_generator.add_table_of_contents()
        report_date = datetime.now().strftime("%B %d, %Y")
        title = f"{self.config.report_type.value}\n{report_date}"
        pdf_generator.story.append(Paragraph(title, pdf_generator.title_style))
        pdf_generator.story.append(Spacer(1, 30))
    
    def _fetch_comprehensive_market_data(self, symbols: Optional[List[str]] = None) -> Dict:
        logger.info("Fetching comprehensive market data summary...")
        market_data = {}
        default_symbols = {
            'indices': ['US500Roll', 'US30Roll', 'UK100Roll', 'DE40Roll', 'FRA40Roll', 'JP225Roll', 'HK50Roll', 'CHINA50Roll'],
            'currencies': ['EURUSD.sd', 'GBPUSD.sd', 'USDJPY.sd', 'AUDUSD.sd', 'USDCAD.sd', 'USDCHF.sd', 'NZDUSD.sd', 'USDCNH.sd'],
            'commodities': ['XAUUSD', 'XAGUSD', 'XPTUSD', 'USOILRoll', 'BRENT', 'NGAS'],
            'bonds': ['TLT', 'IEF', 'SHY', 'LQD'],
            'crypto': ['BTCUSD.lv', 'ETHUSD.lv', 'XRPUSD.lv', 'LTCUSD.lv', 'BCHUSD.lv', 'EOSUSD.lv'],
            'volatility': ['VIXRoll']
        }
        categorized_symbols = default_symbols
        for asset_class, symbol_list in categorized_symbols.items():
            if symbol_list:
                if asset_class == 'bonds':
                    market_data[asset_class] = self._fetch_asset_class_data(symbol_list, asset_class)
                else:
                    market_data[asset_class] = self._fetch_asset_class_data_from_csv(symbol_list, asset_class)
        market_data['calendar'] = self._fetch_calendar_data()
        market_data['correlations'] = self._fetch_correlation_data(market_data)
        logger.info("Market data fetching completed")
        return market_data
    
    def _fetch_asset_class_data(self, symbols: List[str], asset_class: str) -> pd.DataFrame:
        data_list = []
        for symbol in symbols:
            try:
                symbol_info = self.data_fetcher.get_symbol_info(symbol)
                if symbol_info:
                    data_list.append({'name': symbol_info['name'], 'ask': symbol_info['ask'], 'bid': symbol_info['bid'], 'asset_class': asset_class})
            except Exception as e:
                logger.warning(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame(data_list)
    
    def _fetch_asset_class_data_from_csv(self, symbols: List[str], asset_class: str) -> pd.DataFrame:
        data_list = []
        for symbol in symbols:
            try:
                folder = 'forex' if asset_class == 'currencies' else asset_class
                csv_filename = f"/Users/pawan/CLI-Finance-Terminal/data/{folder}/{symbol}_data.csv"
                if os.path.exists(csv_filename):
                    df = pd.read_csv(csv_filename)
                    if not df.empty:
                        latest = df.iloc[-1]
                        data_list.append({'name': symbol, 'ask': latest.get('close', 0), 'bid': latest.get('open', 0), 'high': latest.get('high', 0), 'low': latest.get('low', 0), 'time': pd.to_datetime(latest.get('time')), 'asset_class': asset_class})
            except Exception as e:
                logger.warning(f"Error reading CSV for {symbol}: {e}")
        return pd.DataFrame(data_list)

    def _fetch_calendar_data(self) -> pd.DataFrame: return pd.DataFrame()
    def _fetch_correlation_data(self, market_data: Dict) -> pd.DataFrame: return pd.DataFrame()
    def _add_executive_summary(self, pdf_generator, market_data: Dict):
        logger.info("Adding executive summary...")
        points = ["Market opened with mixed sentiment.", "USD strengthened against major currencies.", "Gold prices rose.", "Market volatility remains contained.", "Key economic events scheduled."]
        pdf_generator.add_executive_summary(points)
    def _add_market_overview(self, pdf_generator, market_data: Dict):
        logger.info("Adding market overview...")
        status = {'status': 'Open', 'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'timezone': 'UTC'}
        pdf_generator.add_market_overview(status, market_data.get('indices', pd.DataFrame()))
    def _add_detailed_analysis(self, pdf_generator, market_data: Dict):
        logger.info("Adding detailed market analysis...")
        for name, data in market_data.items():
            if name == 'indices': pdf_generator.add_indices_table(data)
            elif name == 'currencies': pdf_generator.add_currencies_table(data)
            elif name == 'commodities': pdf_generator.add_commodities_table(data)
    def _add_top_movers_analysis(self, pdf_generator, market_data: Dict):
        logger.info("Adding top market movers analysis...")
        all_data = pd.concat([v for k, v in market_data.items() if k not in ['calendar', 'correlations']], ignore_index=True)
        if not all_data.empty:
            all_data['pct_change'] = ((all_data['ask'] - all_data['bid']) / all_data['bid'] * 100).fillna(0)
            if 'volume' not in all_data.columns: all_data['volume'] = 0
            pdf_generator.add_top_movers_table(all_data)
    def _add_calendar_analysis(self, pdf_generator, market_data: Dict):
        logger.info("Adding economic calendar analysis...")
        if 'calendar' in market_data and not market_data['calendar'].empty:
            pdf_generator.add_calendar_events(market_data['calendar'])
    def _add_risk_metrics(self, pdf_generator, market_data: Dict):
        logger.info("Adding risk metrics analysis...")
        metrics = {'sharpe_ratio': 1.25, 'sortino_ratio': 1.85, 'max_drawdown': -0.15}
        pdf_generator.add_risk_metrics(metrics)
    def _add_compliance_sections(self, pdf_generator):
        logger.info("Adding compliance sections...")
        pdf_generator.add_disclaimer()

if __name__ == "__main__":
    config = InstitutionalReportConfig(
        report_type=ReportType.DAILY_MARKET_REPORT,
        include_charts=True,
    )
    generator = ComprehensiveInstitutionalReportGenerator(config)
    print("Generating comprehensive institutional report...")
    report_path = generator.generate_comprehensive_report()
    print(f"✅ Comprehensive institutional report generated: {report_path}")