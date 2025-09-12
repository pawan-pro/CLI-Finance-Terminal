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