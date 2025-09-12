"""
Enhanced Economic Calendar Analyzer with Institutional Commentary

This module provides advanced analysis of economic calendar events with
institutional-grade commentary and market impact assessment.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
from enum import Enum

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketImpact(Enum):
    """Enum for market impact levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    VERY_HIGH = 4

class AssetClass(Enum):
    """Enum for asset classes"""
    EQUITIES = "Equities"
    FIXED_INCOME = "Fixed Income"
    CURRENCIES = "Currencies"
    COMMODITIES = "Commodities"
    VOLATILITY = "Volatility"

@dataclass
class CalendarEventAnalysis:
    """Data class for calendar event analysis"""
    event_name: str
    currency: str
    date: str
    time: str
    actual: str
    forecast: str
    previous: str
    impact: MarketImpact
    market_expectation: str
    typical_impact: str
    surprise_analysis: str
    cross_asset_spillover: str
    commentary: str
    priority_score: float

class InstitutionalCalendarAnalyzer:
    """Enhanced economic calendar analyzer with institutional-grade insights"""
    
    def __init__(self):
        """Initialize calendar analyzer"""
        # Market convention expectations by currency and event type
        self.currency_expectations = {
            'USD': {'GDP': 0.02, 'CPI': 0.025, 'Employment': 150000},
            'EUR': {'GDP': 0.01, 'CPI': 0.02, 'Employment': 50000},
            'GBP': {'GDP': 0.01, 'CPI': 0.02, 'Employment': 10000},
            'JPY': {'GDP': 0.01, 'CPI': 0.01, 'Employment': 10000},
            'CHF': {'GDP': 0.01, 'CPI': 0.01, 'Employment': 5000},
            'AUD': {'GDP': 0.01, 'CPI': 0.02, 'Employment': 5000},
            'CAD': {'GDP': 0.01, 'CPI': 0.02, 'Employment': 10000},
        }
        
        # Market-moving event categories
        self.market_moving_events = [
            'FOMC', 'ECB', 'BOE', 'BOJ', 'SNB', 'RBA',
            'Non-Farm Payrolls', 'GDP', 'CPI', 'PPI', 'Retail Sales',
            'Manufacturing PMI', 'Services PMI', 'Unemployment Rate',
            'Interest Rate Decision', 'Policy Statement'
        ]
    
    def analyze_calendar_events(self, calendar_data: pd.DataFrame) -> List[CalendarEventAnalysis]:
        """
        Analyze calendar events and generate institutional-grade commentary
        
        Args:
            calendar_data: DataFrame with calendar events
            
        Returns:
            List of analyzed calendar events
        """
        if calendar_data.empty:
            return []
            
        analyzed_events = []
        
        # Process each event
        for _, event in calendar_data.iterrows():
            try:
                analysis = self._analyze_single_event(event)
                analyzed_events.append(analysis)
            except Exception as e:
                logger.warning(f"Error analyzing calendar event: {e}")
                continue
                
        # Sort by priority score (highest first)
        analyzed_events.sort(key=lambda x: x.priority_score, reverse=True)
        
        return analyzed_events
    
    def _analyze_single_event(self, event: pd.Series) -> CalendarEventAnalysis:
        """
        Analyze a single calendar event
        
        Args:
            event: Series representing a single calendar event
            
        Returns:
            CalendarEventAnalysis object
        """
        # Extract event details
        event_name = str(event.get('event', 'Unnamed Event'))
        currency = str(event.get('currency', 'USD'))
        date = str(event.get('date', datetime.now().strftime('%Y-%m-%d')))
        time = str(event.get('time', '00:00'))
        actual = str(event.get('actual', 'N/A'))
        forecast = str(event.get('forecast', 'N/A'))
        previous = str(event.get('previous', 'N/A'))
        
        # Determine market impact
        impact = self._determine_market_impact(event_name, currency)
        
        # Generate market expectation
        market_expectation = self._generate_market_expectation(event_name, currency, forecast)
        
        # Generate typical impact
        typical_impact = self._generate_typical_impact(event_name, currency)
        
        # Generate surprise analysis
        surprise_analysis = self._generate_surprise_analysis(actual, forecast, previous)
        
        # Generate cross-asset spillover
        cross_asset_spillover = self._generate_cross_asset_spillover(event_name, currency)
        
        # Generate commentary
        commentary = self._generate_commentary(event_name, currency, actual, forecast, previous, impact)
        
        # Calculate priority score
        priority_score = self._calculate_priority_score(impact, event_name, date)
        
        return CalendarEventAnalysis(
            event_name=event_name,
            currency=currency,
            date=date,
            time=time,
            actual=actual,
            forecast=forecast,
            previous=previous,
            impact=impact,
            market_expectation=market_expectation,
            typical_impact=typical_impact,
            surprise_analysis=surprise_analysis,
            cross_asset_spillover=cross_asset_spillover,
            commentary=commentary,
            priority_score=priority_score
        )
    
    def _determine_market_impact(self, event_name: str, currency: str) -> MarketImpact:
        """
        Determine market impact level for an event
        
        Args:
            event_name: Name of the event
            currency: Currency of the event
            
        Returns:
            MarketImpact enum value
        """
        # Check if it's a central bank policy event
        if any(cb in event_name.upper() for cb in ['FOMC', 'ECB', 'BOE', 'BOJ', 'SNB', 'RBA']):
            return MarketImpact.VERY_HIGH
            
        # Check if it's a major economic indicator
        if any(indicator in event_name.upper() for indicator in [
            'NON-FARM', 'PAYROLL', 'GDP', 'CPI', 'PPI', 'RETAIL', 'PMI'
        ]):
            return MarketImpact.HIGH
            
        # Check if it's a medium impact event
        if any(indicator in event_name.upper() for indicator in [
            'UNEMPLOYMENT', 'INFLATION', 'MANUFACTURING', 'SERVICES'
        ]):
            return MarketImpact.MEDIUM
            
        # Default to low impact
        return MarketImpact.LOW
    
    def _generate_market_expectation(self, event_name: str, currency: str, forecast: str) -> str:
        """
        Generate market expectation for an event
        
        Args:
            event_name: Name of the event
            currency: Currency of the event
            forecast: Forecast value
            
        Returns:
            Market expectation string
        """
        # Get currency-specific expectations
        currency_exp = self.currency_expectations.get(currency, {})
        
        # Generate expectation based on event type
        if 'GDP' in event_name.upper():
            exp_val = currency_exp.get('GDP', 0.01)
            return f"Consensus expects {exp_val:+.2%} GDP growth"
        elif 'CPI' in event_name.upper() or 'INFLATION' in event_name.upper():
            exp_val = currency_exp.get('CPI', 0.02)
            return f"Market anticipates {exp_val:+.2%} inflation rate"
        elif 'EMPLOYMENT' in event_name.upper() or 'PAYROLL' in event_name.upper():
            exp_val = currency_exp.get('Employment', 50000)
            return f"Expectations for {exp_val:,.0f} job additions"
        elif 'PMI' in event_name.upper():
            return "Market expects expansionary reading above 50"
        elif 'INTEREST' in event_name.upper() or 'RATE' in event_name.upper():
            return "Focus on policy guidance and forward-looking statements"
        else:
            return f"Market consensus forecast: {forecast}"
    
    def _generate_typical_impact(self, event_name: str, currency: str) -> str:
        """
        Generate typical market impact for an event type
        
        Args:
            event_name: Name of the event
            currency: Currency of the event
            
        Returns:
            Typical impact string
        """
        if 'FOMC' in event_name.upper():
            return "Typically drives significant USD moves, with spillovers to equities and Treasuries"
        elif 'ECB' in event_name.upper():
            return "Usually impacts EUR and European equity markets significantly"
        elif 'GDP' in event_name.upper():
            return "Key driver of currency and sovereign bond markets"
        elif 'CPI' in event_name.upper():
            return "Highly influential on central bank policy expectations and fixed income"
        elif 'PAYROLL' in event_name.upper():
            return "Market-moving for USD, Treasury yields, and risk assets"
        elif 'PMI' in event_name.upper():
            return "Leading indicator for economic cycle and corporate earnings"
        else:
            return "Standard market impact for economic release"
    
    def _generate_surprise_analysis(self, actual: str, forecast: str, previous: str) -> str:
        """
        Generate surprise analysis for an event
        
        Args:
            actual: Actual value
            forecast: Forecast value
            previous: Previous value
            
        Returns:
            Surprise analysis string
        """
        try:
            # Try to convert to numeric values
            actual_num = self._convert_to_numeric(actual)
            forecast_num = self._convert_to_numeric(forecast)
            previous_num = self._convert_to_numeric(previous)
            
            if actual_num is not None and forecast_num is not None:
                surprise = actual_num - forecast_num
                
                if abs(surprise) < abs(forecast_num * 0.05):  # Within 5% of forecast
                    return "Result broadly in line with expectations"
                elif surprise > 0:
                    return f"Beat expectations by {surprise:+.2f} ({surprise/forecast_num*100:+.1f}%)"
                else:
                    return f"Missed expectations by {surprise:.2f} ({surprise/forecast_num*100:.1f}%)"
            else:
                return "Unable to quantify surprise due to non-numeric data"
                
        except Exception as e:
            logger.warning(f"Error in surprise analysis: {e}")
            return "Surprise analysis unavailable"
    
    def _convert_to_numeric(self, value: str) -> Optional[float]:
        """
        Convert string value to numeric
        
        Args:
            value: String value to convert
            
        Returns:
            Numeric value or None if conversion fails
        """
        if value in ['N/A', '', None]:
            return None
            
        # Remove common non-numeric characters
        clean_value = str(value).strip().replace('%', '').replace(',', '')
        
        # Handle special cases
        if clean_value.lower() in ['unchanged', 'same']:
            return 0.0
            
        try:
            return float(clean_value)
        except ValueError:
            return None
    
    def _generate_cross_asset_spillover(self, event_name: str, currency: str) -> str:
        """
        Generate cross-asset spillover analysis
        
        Args:
            event_name: Name of the event
            currency: Currency of the event
            
        Returns:
            Cross-asset spillover string
        """
        if currency == 'USD':
            if 'PAYROLL' in event_name.upper():
                return "Positive surprises typically strengthen USD, boost Treasuries, and pressure risk assets"
            elif 'CPI' in event_name.upper():
                return "Higher-than-expected inflation usually supports USD and sells bonds; mixed equity impact"
            elif 'GDP' in event_name.upper():
                return "Strong GDP supports USD and risk assets; may pressure bonds"
        elif currency == 'EUR':
            if 'ECB' in event_name.upper():
                return "Policy changes drive EUR, European equities, and peripheral bonds"
            elif 'PMI' in event_name.upper():
                return "Manufacturing strength supports EUR and European cyclicals"
        elif currency == 'GBP':
            if 'BOE' in event_name.upper():
                return "Policy decisions impact GBP, UK equities, and gilts"
            elif 'PMI' in event_name.upper():
                return "Services PMI particularly influential for GBP and UK markets"
                
        return "Broad market impact across currencies, bonds, and equities"
    
    def _generate_commentary(self, event_name: str, currency: str, actual: str, 
                           forecast: str, previous: str, impact: MarketImpact) -> str:
        """
        Generate institutional-grade commentary for an event
        
        Args:
            event_name: Name of the event
            currency: Currency of the event
            actual: Actual value
            forecast: Forecast value
            previous: Previous value
            impact: Market impact level
            
        Returns:
            Commentary string
        """
        # Start with impact-based opening
        if impact == MarketImpact.VERY_HIGH:
            commentary = f"[VERY HIGH IMPACT] {event_name} represents a market-defining moment. "
        elif impact == MarketImpact.HIGH:
            commentary = f"[HIGH IMPACT] {event_name} carries significant market weight. "
        elif impact == MarketImpact.MEDIUM:
            commentary = f"[MEDIUM IMPACT] {event_name} merits attention for market positioning. "
        else:
            commentary = f"[LOW IMPACT] {event_name} has limited market relevance. "
            
        # Add context based on event type
        if 'FOMC' in event_name.upper() or 'ECB' in event_name.upper():
            commentary += "Central bank policy decisions directly influence monetary conditions, asset allocation, and risk sentiment. "
            commentary += "Market participants closely monitor forward guidance and dot plots for future policy trajectory signals."
        elif 'GDP' in event_name.upper():
            commentary += "Real economic growth figures serve as key barometers of economic health. "
            commentary += "GDP revisions can significantly alter recession/inflation outlook assessments and central bank reaction functions."
        elif 'CPI' in event_name.upper():
            commentary += "Inflation readings are pivotal for monetary policy formation and real rate expectations. "
            commentary += "Core measures exclude volatile food/energy components to reveal underlying price trends."
        elif 'PAYROLL' in event_name.upper():
            commentary += "Labor market conditions reflect economic momentum and consumer spending capacity. "
            commentary += "Wage growth components provide insight on inflationary pressures and Fed policy calibration."
        else:
            commentary += "This release contributes to the broader macroeconomic narrative and influences positioning decisions."
            
        # Add outlook perspective
        commentary += " Results will inform tactical asset allocation and risk management decisions across portfolios."
        
        return commentary
    
    def _calculate_priority_score(self, impact: MarketImpact, event_name: str, date: str) -> float:
        """
        Calculate priority score for sorting events
        
        Args:
            impact: Market impact level
            event_name: Name of the event
            date: Date of the event
            
        Returns:
            Priority score (higher = more important)
        """
        # Base score from impact level
        base_score = impact.value * 10
        
        # Boost for market-moving events
        if any(mme in event_name.upper() for mme in self.market_moving_events):
            base_score += 5
            
        # Boost for today's events
        try:
            event_date = datetime.strptime(date, '%Y-%m-%d').date()
            today = datetime.now().date()
            if event_date == today:
                base_score += 3
        except:
            pass
            
        return float(base_score)
    
    def identify_portfolio_relevant_events(self, calendar_data: pd.DataFrame, 
                                          portfolio_exposures: List[str]) -> List[CalendarEventAnalysis]:
        """
        Identify calendar events relevant to specific portfolio exposures
        
        Args:
            calendar_data: DataFrame with calendar events
            portfolio_exposures: List of portfolio currency/exposure areas
            
        Returns:
            List of portfolio-relevant calendar events
        """
        if calendar_data.empty or not portfolio_exposures:
            return []
            
        relevant_events = []
        
        # Process each event
        for _, event in calendar_data.iterrows():
            currency = str(event.get('currency', 'USD'))
            
            # Check if event currency matches portfolio exposures
            if currency in portfolio_exposures:
                try:
                    analysis = self._analyze_single_event(event)
                    relevant_events.append(analysis)
                except Exception as e:
                    logger.warning(f"Error analyzing portfolio-relevant event: {e}")
                    continue
                    
        # Sort by priority score
        relevant_events.sort(key=lambda x: x.priority_score, reverse=True)
        
        return relevant_events

# Example usage
if __name__ == "__main__":
    # Create sample calendar data
    sample_data = pd.DataFrame({
        'event': ['FOMC Decision', 'Non-Farm Payrolls', 'CPI Release'],
        'currency': ['USD', 'USD', 'USD'],
        'date': ['2023-10-15', '2023-10-16', '2023-10-17'],
        'time': ['14:00', '13:30', '08:30'],
        'actual': ['5.25%', '250K', '3.2%'],
        'forecast': ['5.25%', '198K', '3.1%'],
        'previous': ['5.25%', '229K', '3.0%'],
    })
    
    # Initialize analyzer
    analyzer = InstitutionalCalendarAnalyzer()
    
    # Analyze events
    analyzed_events = analyzer.analyze_calendar_events(sample_data)
    
    # Print results
    print("=== Institutional Calendar Analysis ===")
    for event in analyzed_events:
        print(f"\n{event.event_name} ({event.currency})")
        print(f"  Date/Time: {event.date} {event.time}")
        print(f"  Impact: {event.impact.name}")
        print(f"  Actual: {event.actual} | Forecast: {event.forecast} | Previous: {event.previous}")
        print(f"  Commentary: {event.commentary}")
        print(f"  Priority Score: {event.priority_score}")