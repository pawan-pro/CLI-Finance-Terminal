"""
Enhanced Top Movers Analyzer with Attribution Analysis

This module identifies top market movers with detailed attribution analysis,
combining statistical factors, fundamental drivers, and calendar event impacts.
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

class MoveAttribution(Enum):
    """Enum for move attribution types"""
    ECONOMIC_DATA = "Economic Data"
    TECHNICAL = "Technical Factors"
    FUNDAMENTAL = "Fundamental News"
    CENTRAL_BANK = "Central Bank Policy"
    GEOGRAPHIC = "Geographic Exposure"
    SECTOR_ROTATION = "Sector Rotation"
    VOLATILITY_REGIME = "Volatility Regime"
    MARKET_SENTIMENT = "Market Sentiment"

@dataclass
class TopMoverAnalysis:
    """Data class for top mover analysis"""
    symbol: str
    name: str
    price: float
    change: float
    pct_change: float
    volume: float
    attribution_factors: List[Tuple[MoveAttribution, float, str]]  # (factor, weight, explanation)
    statistical_confidence: float
    fundamental_impact: str
    technical_signals: str
    cross_asset_impact: str
    outlook: str
    risk_metrics: Dict[str, float]

class EnhancedTopMoversAnalyzer:
    """Enhanced top movers analyzer with detailed attribution"""
    
    def __init__(self):
        """Initialize top movers analyzer"""
        self.volatility_threshold = 2.0  # 2 standard deviations
        self.volume_threshold = 1.5  # 1.5x average volume
        self.confidence_threshold = 0.7  # 70% confidence minimum for inclusion
        
    def analyze_top_movers(self, market_data: pd.DataFrame, 
                          calendar_events: pd.DataFrame = None,
                          correlation_data: Dict[str, pd.Series] = None) -> List[TopMoverAnalysis]:
        """
        Analyze top market movers with detailed attribution
        
        Args:
            market_data: DataFrame with market data (columns: name, ask, bid, volume, etc.)
            calendar_events: DataFrame with calendar events
            correlation_data: Dictionary of correlated assets/prices
            
        Returns:
            List of top mover analyses
        """
        if market_data.empty:
            return []
            
        top_movers = []
        
        # Calculate percentage changes and identify top movers
        if 'ask' in market_data.columns and 'bid' in market_data.columns:
            market_data = market_data.copy()
            market_data['price'] = (market_data['ask'] + market_data['bid']) / 2
            market_data['change'] = market_data['ask'] - market_data['bid']
            market_data['pct_change'] = (market_data['change'] / market_data['bid'] * 100).fillna(0)
        else:
            logger.warning("Missing required price columns for top movers analysis")
            return []
            
        # Rank by absolute percentage change
        market_data = market_data.sort_values('pct_change', key=abs, ascending=False)
        
        # Analyze top 20 movers
        for idx, (_, row) in enumerate(market_data.head(20).iterrows()):
            try:
                analysis = self._analyze_single_mover(row, calendar_events, correlation_data)
                if analysis and analysis.statistical_confidence >= self.confidence_threshold:
                    top_movers.append(analysis)
            except Exception as e:
                logger.warning(f"Error analyzing top mover {row.get('name', 'Unknown')}: {e}")
                continue
                
        # Sort by confidence and magnitude
        top_movers.sort(key=lambda x: x.statistical_confidence * abs(x.pct_change), reverse=True)
        
        return top_movers[:15]  # Return top 15 with highest confidence-weighted moves
    
    def _analyze_single_mover(self, row: pd.Series, 
                              calendar_events: pd.DataFrame = None,
                              correlation_data: Dict[str, pd.Series] = None) -> Optional[TopMoverAnalysis]:
        """
        Analyze a single market mover
        
        Args:
            row: Series representing a single market instrument
            calendar_events: DataFrame with calendar events
            correlation_data: Dictionary of correlated assets
            
        Returns:
            TopMoverAnalysis object or None
        """
        # Extract basic information
        symbol = str(row.get('name', 'Unknown'))
        name = str(row.get('description', symbol))
        price = float(row.get('ask', 0))
        change = float(row.get('change', 0)) if 'change' in row else 0
        pct_change = float(row.get('pct_change', 0))
        volume = float(row.get('volume', 0))
        
        # Calculate attribution factors
        attribution_factors = self._calculate_attribution_factors(
            row, calendar_events, correlation_data
        )
        
        # Calculate statistical confidence
        statistical_confidence = self._calculate_statistical_confidence(
            row, attribution_factors
        )
        
        # Generate fundamental impact analysis
        fundamental_impact = self._generate_fundamental_impact(symbol, pct_change)
        
        # Generate technical signals
        technical_signals = self._generate_technical_signals(row)
        
        # Generate cross-asset impact
        cross_asset_impact = self._generate_cross_asset_impact(symbol, pct_change, correlation_data)
        
        # Generate outlook
        outlook = self._generate_outlook(pct_change, attribution_factors)
        
        # Calculate risk metrics
        risk_metrics = self._calculate_risk_metrics(row)
        
        return TopMoverAnalysis(
            symbol=symbol,
            name=name,
            price=price,
            change=change,
            pct_change=pct_change,
            volume=volume,
            attribution_factors=attribution_factors,
            statistical_confidence=statistical_confidence,
            fundamental_impact=fundamental_impact,
            technical_signals=technical_signals,
            cross_asset_impact=cross_asset_impact,
            outlook=outlook,
            risk_metrics=risk_metrics
        )
    
    def _calculate_attribution_factors(self, row: pd.Series,
                                      calendar_events: pd.DataFrame = None,
                                      correlation_data: Dict[str, pd.Series] = None) -> List[Tuple[MoveAttribution, float, str]]:
        """
        Calculate attribution factors for a market move
        
        Args:
            row: Series representing a market instrument
            calendar_events: DataFrame with calendar events
            correlation_data: Dictionary of correlated assets
            
        Returns:
            List of attribution factors (factor, weight, explanation)
        """
        factors = []
        symbol = str(row.get('name', 'Unknown'))
        
        # 1. Economic Data Attribution (if recent relevant events)
        if calendar_events is not None and not calendar_events.empty:
            relevant_events = calendar_events[
                (calendar_events['currency'] == symbol[:3]) |  # Match currency
                (calendar_events['event'].str.contains(symbol.split('/')[0] if '/' in symbol else symbol, na=False))
            ]
            
            if not relevant_events.empty:
                # Weight based on recency and impact
                recent_events = relevant_events.head(3)  # Top 3 recent events
                weight = min(0.4, len(recent_events) * 0.15)  # Max 40% weight
                explanation = f"{len(recent_events)} recent relevant economic releases"
                factors.append((MoveAttribution.ECONOMIC_DATA, weight, explanation))
        
        # 2. Technical Attribution (based on volatility and volume)
        if 'volume' in row and 'pct_change' in row:
            volume = float(row['volume'])
            pct_change = float(row['pct_change'])
            
            # High volume moves get technical attribution
            if volume > self.volume_threshold:  # Above threshold volume
                weight = min(0.3, abs(pct_change) / 10)  # Up to 30% weight
                explanation = f"High volume ({volume:.0f}) driving price action"
                factors.append((MoveAttribution.TECHNICAL, weight, explanation))
        
        # 3. Fundamental Attribution (based on symbol type)
        symbol_type_weight = self._assess_symbol_fundamental_weight(symbol)
        if symbol_type_weight > 0:
            factors.append((
                MoveAttribution.FUNDAMENTAL, 
                symbol_type_weight,
                f"Inherent {symbol} fundamental characteristics"
            ))
        
        # 4. Correlation-Based Attribution
        if correlation_data and symbol in correlation_data:
            correlations = correlation_data[symbol]
            if len(correlations) > 0:
                # Strong correlations indicate market-wide moves
                strong_corr_count = len([c for c in correlations if abs(c) > 0.7])
                if strong_corr_count > 0:
                    weight = min(0.25, strong_corr_count * 0.05)
                    explanation = f"Correlated with {strong_corr_count} major assets"
                    factors.append((MoveAttribution.MARKET_SENTIMENT, weight, explanation))
        
        # 5. Default attribution (catch-all)
        remaining_weight = 1.0 - sum(weight for _, weight, _ in factors)
        if remaining_weight > 0:
            factors.append((
                MoveAttribution.MARKET_SENTIMENT,
                remaining_weight,
                "General market sentiment and positioning"
            ))
        
        return factors
    
    def _assess_symbol_fundamental_weight(self, symbol: str) -> float:
        """
        Assess fundamental weight based on symbol characteristics
        
        Args:
            symbol: Market symbol
            
        Returns:
            Fundamental weight (0.0 to 0.3)
        """
        # Currency pairs
        if '/' in symbol:
            base_currency = symbol[:3]
            if base_currency in ['USD', 'EUR', 'GBP', 'JPY']:
                return 0.2  # Major currencies have fundamental weight
            else:
                return 0.1  # Minor currencies
        
        # Stock indices
        if any(idx in symbol.upper() for idx in ['SPX', 'DJI', 'NDX', 'DAX', 'FTSE']):
            return 0.25  # Indices have high fundamental weight
            
        # Commodities
        if any(com in symbol.upper() for com in ['XAU', 'XAG', 'OIL', 'GOLD', 'SILVER']):
            return 0.2  # Commodities have fundamental drivers
            
        # Bonds/Treasuries
        if any(bond in symbol.upper() for bond in ['TLT', 'IEF', 'SHY', 'LQD']):
            return 0.15  # Bonds have moderate fundamental weight
            
        return 0.05  # Default low weight
    
    def _calculate_statistical_confidence(self, row: pd.Series, 
                                        attribution_factors: List[Tuple[MoveAttribution, float, str]]) -> float:
        """
        Calculate statistical confidence in the move analysis
        
        Args:
            row: Series representing market instrument
            attribution_factors: List of attribution factors
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        confidence = 0.5  # Base confidence
        
        # Factor 1: Magnitude of move
        if 'pct_change' in row:
            pct_change = abs(float(row['pct_change']))
            # Higher moves increase confidence (up to 2% = 0.3 additional confidence)
            confidence += min(0.3, pct_change / 2 * 0.3)
        
        # Factor 2: Attribution diversity
        if len(attribution_factors) > 1:
            # More diverse attributions increase confidence
            diversity_bonus = min(0.2, (len(attribution_factors) - 1) * 0.1)
            confidence += diversity_bonus
        
        # Factor 3: Volume confirmation
        if 'volume' in row and 'pct_change' in row:
            volume = float(row['volume'])
            pct_change = abs(float(row['pct_change']))
            # High volume moves with significant price action get bonus
            if volume > 1.0 and pct_change > 0.5:
                confidence += 0.1
        
        # Cap at 1.0
        return min(1.0, confidence)
    
    def _generate_fundamental_impact(self, symbol: str, pct_change: float) -> str:
        """
        Generate fundamental impact analysis
        
        Args:
            symbol: Market symbol
            pct_change: Percentage change
            
        Returns:
            Fundamental impact string
        """
        direction = "gains" if pct_change > 0 else "losses"
        magnitude = abs(pct_change)
        
        if magnitude > 3.0:
            strength = "extraordinary"
        elif magnitude > 2.0:
            strength = "significant"
        elif magnitude > 1.0:
            strength = "notable"
        else:
            strength = "modest"
        
        # Currency pairs
        if '/' in symbol:
            base_currency = symbol[:3]
            quote_currency = symbol[3:]
            return f"{symbol} {direction} reflect {strength} {base_currency}/{quote_currency} valuation adjustment driven by differential economic fundamentals and central bank policies."
        
        # Stock indices
        if any(idx in symbol.upper() for idx in ['SPX', 'DJI', 'NDX']):
            market_direction = "bullish" if pct_change > 0 else "bearish"
            return f"{symbol} {direction} signal {market_direction} investor sentiment toward U.S. equities, reflecting corporate earnings outlook and monetary policy expectations."
        
        # Commodities
        if any(com in symbol.upper() for com in ['XAU', 'XAG', 'GOLD', 'SILVER', 'OIL']):
            commodity_type = "precious metals" if "AU" in symbol or "AG" in symbol else "energy commodities"
            return f"{symbol} {direction} driven by {strength} {commodity_type} demand-supply dynamics and safe-haven flows."
        
        # Bonds
        if any(bond in symbol.upper() for bond in ['TLT', 'IEF', 'SHY', 'LQD']):
            return f"{symbol} {direction} reflect changing expectations for interest rate policy and credit market conditions."
        
        return f"{symbol} {direction} representing {strength} price discovery in {symbol} markets."
    
    def _generate_technical_signals(self, row: pd.Series) -> str:
        """
        Generate technical signals analysis
        
        Args:
            row: Series representing market instrument
            
        Returns:
            Technical signals string
        """
        signals = []
        
        if 'pct_change' in row:
            pct_change = float(row['pct_change'])
            
            if abs(pct_change) > 2.0:
                signals.append("Breakout move exceeding 2% threshold")
            elif abs(pct_change) > 1.0:
                signals.append("Strong intraday momentum")
            else:
                signals.append("Normal price action within ranges")
        
        if 'volume' in row:
            volume = float(row['volume'])
            if volume > self.volume_threshold:
                signals.append("Above-average trading activity confirming move validity")
        
        if 'high' in row and 'low' in row and 'ask' in row and 'bid' in row:
            high = float(row['high'])
            low = float(row['low'])
            ask = float(row['ask'])
            bid = float(row['bid'])
            
            # Check for volatility compression/expansion
            range_size = high - low
            spread = ask - bid
            
            if range_size > 0:
                normalized_spread = spread / range_size
                if normalized_spread < 0.1:
                    signals.append("Tight bid-ask spread indicating liquid market conditions")
                else:
                    signals.append("Wider spreads suggesting increased market friction")
        
        return "; ".join(signals) if signals else "Standard technical characteristics"
    
    def _generate_cross_asset_impact(self, symbol: str, pct_change: float,
                                   correlation_data: Dict[str, pd.Series] = None) -> str:
        """
        Generate cross-asset impact analysis
        
        Args:
            symbol: Market symbol
            pct_change: Percentage change
            correlation_data: Correlation data dictionary
            
        Returns:
            Cross-asset impact string
        """
        direction = "positive" if pct_change > 0 else "negative"
        
        # Currency pairs
        if '/' in symbol:
            base_currency = symbol[:3]
            quote_currency = symbol[3:]
            
            if base_currency == 'USD':
                return f"{direction} USD impact on {quote_currency} positions; strengthening dollar pressures emerging market currencies and dollar-denominated debt."
            elif quote_currency == 'USD':
                return f"{direction} {base_currency} impact on USD positions; influencing commodity pricing and global trade flows."
            else:
                return f"{direction} cross-currency impact on USD funding conditions and carry trade dynamics."
        
        # Stock indices
        if any(idx in symbol.upper() for idx in ['SPX', 'DJI', 'NDX']):
            return f"{direction} equity impact on risk sentiment, credit spreads, and volatility surface; influencing portfolio rebalancing flows."
        
        # Commodities
        if any(com in symbol.upper() for com in ['XAU', 'XAG', 'GOLD', 'SILVER']):
            return f"{direction} precious metal impact on inflation expectations, real interest rates, and defensive asset allocation."
        
        # Bonds
        if any(bond in symbol.upper() for bond in ['TLT', 'IEF', 'SHY']):
            return f"{direction} fixed income impact on duration positioning, yield curve dynamics, and pension fund liability management."
        
        return f"{direction} spillover effects across correlated asset classes and geographic regions."
    
    def _generate_outlook(self, pct_change: float, 
                        attribution_factors: List[Tuple[MoveAttribution, float, str]]) -> str:
        """
        Generate outlook based on move characteristics
        
        Args:
            pct_change: Percentage change
            attribution_factors: Attribution factors
            
        Returns:
            Outlook string
        """
        magnitude = abs(pct_change)
        direction = "upside" if pct_change > 0 else "downside"
        
        # Determine persistence based on attribution factors
        technical_weight = sum(weight for factor, weight, _ in attribution_factors 
                              if factor == MoveAttribution.TECHNICAL)
        fundamental_weight = sum(weight for factor, weight, _ in attribution_factors 
                                if factor in [MoveAttribution.FUNDAMENTAL, MoveAttribution.ECONOMIC_DATA])
        
        if fundamental_weight > 0.5:
            persistence = "likely to persist" if magnitude > 1.0 else "may consolidate"
        elif technical_weight > 0.4:
            persistence = "momentum-driven near term" if magnitude > 0.5 else "mean-reversion likely"
        else:
            persistence = "unclear near-term trajectory"
        
        # Generate outlook
        if magnitude > 3.0:
            outlook = f"Extraordinary {direction} move suggests {persistence}; monitor for exhaustion or acceleration signals."
        elif magnitude > 2.0:
            outlook = f"Significant {direction} move indicates {persistence}; key support/resistance levels critical."
        elif magnitude > 1.0:
            outlook = f"Notable {direction} move with {persistence}; tactical opportunities may emerge."
        else:
            outlook = f"Modest {direction} move in line with normal market volatility; {persistence}."
        
        return outlook
    
    def _calculate_risk_metrics(self, row: pd.Series) -> Dict[str, float]:
        """
        Calculate risk metrics for the mover
        
        Args:
            row: Series representing market instrument
            
        Returns:
            Dictionary of risk metrics
        """
        metrics = {}
        
        # Basic metrics
        if 'pct_change' in row:
            pct_change = float(row['pct_change'])
            metrics['daily_return'] = pct_change / 100  # Convert to decimal
            metrics['volatility_drag'] = (pct_change / 100) ** 2 / 2  # Volatility drag effect
            
        if 'spread' in row and 'ask' in row:
            spread = float(row['spread'])
            ask = float(row['ask'])
            if ask != 0:
                metrics['bid_ask_spread_bp'] = (spread / ask) * 10000  # In basis points
        
        if 'volume' in row:
            metrics['volume_normalized'] = float(row['volume'])  # Normalized volume metric
        
        # Beta approximation (simplified)
        metrics['beta_approx'] = 1.0  # Default market beta
        
        # Sharpe ratio approximation (very simplified)
        if 'pct_change' in metrics:
            metrics['sharpe_approx'] = metrics['daily_return'] / 0.02 if 0.02 != 0 else 0  # Assuming 2% daily vol
        
        return metrics

# Example usage
if __name__ == "__main__":
    # Create sample market data
    sample_data = pd.DataFrame({
        'name': ['EURUSD', 'GBPUSD', 'XAUUSD', 'SPX500'],
        'description': ['Euro vs US Dollar', 'British Pound vs US Dollar', 'Gold vs US Dollar', 'S&P 500 Index'],
        'ask': [1.05, 1.25, 1900.50, 4350.25],
        'bid': [1.049, 1.249, 1900.20, 4349.75],
        'volume': [1000000, 500000, 50000, 2000000],
        'change': [0.001, 0.001, 0.30, 5.0],
        'pct_change': [0.1, 0.08, 0.016, 0.115],
        'high': [1.052, 1.252, 1901.00, 4352.00],
        'low': [1.048, 1.248, 1899.00, 4348.00],
        'spread': [0.0001, 0.0001, 0.30, 0.50]
    })
    
    # Create sample calendar events
    sample_calendar = pd.DataFrame({
        'event': ['ECB Policy Meeting', 'US CPI Release'],
        'currency': ['EUR', 'USD'],
        'date': ['2023-10-15', '2023-10-16'],
        'time': ['13:45', '08:30'],
        'actual': ['4.50%', '3.2%'],
        'forecast': ['4.50%', '3.1%'],
        'previous': ['4.50%', '3.0%'],
    })
    
    # Initialize analyzer
    analyzer = EnhancedTopMoversAnalyzer()
    
    # Analyze top movers
    top_movers = analyzer.analyze_top_movers(sample_data, sample_calendar)
    
    # Print results
    print("=== Enhanced Top Movers Analysis ===")
    for mover in top_movers:
        print(f"\n{mover.symbol} ({mover.pct_change:+.2f}%)")
        print(f"  Price: ${mover.price:.2f}")
        print(f"  Volume: {mover.volume:,.0f}")
        print(f"  Attribution Factors:")
        for factor, weight, explanation in mover.attribution_factors:
            print(f"    - {factor.value}: {weight:.0%} ({explanation})")
        print(f"  Statistical Confidence: {mover.statistical_confidence:.0%}")
        print(f"  Fundamental Impact: {mover.fundamental_impact}")
        print(f"  Technical Signals: {mover.technical_signals}")
        print(f"  Cross-Asset Impact: {mover.cross_asset_impact}")
        print(f"  Outlook: {mover.outlook}")
        print(f"  Risk Metrics:")
        for metric, value in mover.risk_metrics.items():
            if 'bp' in metric:
                print(f"    - {metric}: {value:.1f}")
            else:
                print(f"    - {metric}: {value:.4f}")