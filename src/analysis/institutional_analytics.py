"""
Comprehensive Institutional-Grade Market Analytics Module

This module provides advanced quantitative analysis and institutional-grade insights
for daily investment reports, with metrics and methodologies used by top-tier
investment banks and asset managers.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
import logging
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import warnings
warnings.filterwarnings('ignore')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InstitutionalMarketAnalytics:
    """Comprehensive analytics with institutional-grade metrics and insights"""
    
    def __init__(self):
        """Initialize institutional analytics engine"""
        self.risk_free_rate = 0.03  # 3% annual risk-free rate
        self.trading_days_per_year = 252
    
    def calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = None) -> float:
        """
        Calculate Sharpe Ratio - risk-adjusted return measure
        
        Args:
            returns: Series of returns
            risk_free_rate: Annual risk-free rate (default 3%)
            
        Returns:
            Sharpe ratio (annualized)
        """
        if risk_free_rate is None:
            risk_free_rate = self.risk_free_rate
            
        if len(returns) == 0:
            return 0.0
            
        # Calculate excess returns
        excess_returns = returns - (risk_free_rate / self.trading_days_per_year)
        
        # Calculate Sharpe ratio
        if returns.std() != 0:
            sharpe = excess_returns.mean() / returns.std() * np.sqrt(self.trading_days_per_year)
        else:
            sharpe = 0.0
            
        return sharpe
    
    def calculate_sortino_ratio(self, returns: pd.Series, risk_free_rate: float = None) -> float:
        """
        Calculate Sortino Ratio - downside risk-adjusted return measure
        
        Args:
            returns: Series of returns
            risk_free_rate: Annual risk-free rate (default 3%)
            
        Returns:
            Sortino ratio (annualized)
        """
        if risk_free_rate is None:
            risk_free_rate = self.risk_free_rate
            
        if len(returns) == 0:
            return 0.0
            
        # Calculate excess returns
        excess_returns = returns - (risk_free_rate / self.trading_days_per_year)
        
        # Calculate downside deviation (standard deviation of negative returns)
        negative_returns = returns[returns < 0]
        if len(negative_returns) > 0:
            downside_deviation = negative_returns.std()
        else:
            downside_deviation = 1e-10  # Small value to avoid division by zero
            
        # Calculate Sortino ratio
        if downside_deviation != 0:
            sortino = excess_returns.mean() / downside_deviation * np.sqrt(self.trading_days_per_year)
        else:
            sortino = 0.0
            
        return sortino
    
    def calculate_max_drawdown(self, prices: pd.Series) -> Tuple[float, datetime, datetime]:
        """
        Calculate maximum drawdown and its duration
        
        Args:
            prices: Series of prices
            
        Returns:
            Tuple of (Max drawdown, Peak date, Trough date)
        """
        if len(prices) == 0:
            return 0.0, datetime.now(), datetime.now()
            
        # Calculate cumulative returns
        cumulative_returns = (1 + prices.pct_change()).cumprod()
        
        # Calculate running maximum
        running_max = cumulative_returns.expanding().max()
        
        # Calculate drawdown
        drawdown = (cumulative_returns - running_max) / running_max
        
        # Find maximum drawdown
        max_drawdown = drawdown.min()
        
        # Find peak and trough dates
        peak_date = drawdown.idxmax()
        trough_date = drawdown.idxmin()
        
        return max_drawdown, peak_date, trough_date
    
    def calculate_value_at_risk(self, returns: pd.Series, confidence_level: float = 0.95) -> float:
        """
        Calculate Value at Risk (VaR) using historical simulation method
        
        Args:
            returns: Series of returns
            confidence_level: Confidence level (default 95%)
            
        Returns:
            Value at Risk
        """
        if len(returns) == 0:
            return 0.0
            
        # Calculate VaR using percentile
        var = np.percentile(returns, (1 - confidence_level) * 100)
        return var
    
    def calculate_conditional_value_at_risk(self, returns: pd.Series, confidence_level: float = 0.95) -> float:
        """
        Calculate Conditional Value at Risk (CVaR) - expected shortfall
        
        Args:
            returns: Series of returns
            confidence_level: Confidence level (default 95%)
            
        Returns:
            Conditional Value at Risk
        """
        if len(returns) == 0:
            return 0.0
            
        # Calculate VaR first
        var = self.calculate_value_at_risk(returns, confidence_level)
        
        # Calculate CVaR as average of losses exceeding VaR
        exceedances = returns[returns <= var]
        if len(exceedances) > 0:
            cvar = exceedances.mean()
        else:
            cvar = var
            
        return cvar
    
    def calculate_beta(self, asset_returns: pd.Series, market_returns: pd.Series) -> float:
        """
        Calculate market beta (systematic risk)
        
        Args:
            asset_returns: Series of asset returns
            market_returns: Series of market returns
            
        Returns:
            Market beta
        """
        if len(asset_returns) == 0 or len(market_returns) == 0:
            return 0.0
            
        # Align returns
        aligned_returns = pd.concat([asset_returns, market_returns], axis=1).dropna()
        if len(aligned_returns) < 2:
            return 0.0
            
        # Calculate beta using linear regression
        X = aligned_returns.iloc[:, 1].values.reshape(-1, 1)  # Market returns
        y = aligned_returns.iloc[:, 0].values  # Asset returns
        
        try:
            model = LinearRegression().fit(X, y)
            beta = model.coef_[0]
            return beta
        except Exception as e:
            logger.warning(f"Error calculating beta: {e}")
            return 0.0
    
    def calculate_rolling_volatility(self, returns: pd.Series, window: int = 30) -> pd.Series:
        """
        Calculate rolling volatility
        
        Args:
            returns: Series of returns
            window: Rolling window (default 30 days)
            
        Returns:
            Rolling volatility series
        """
        if len(returns) == 0:
            return pd.Series(dtype=float)
            
        rolling_vol = returns.rolling(window=window).std() * np.sqrt(self.trading_days_per_year)
        return rolling_vol
    
    def detect_regime_shifts(self, prices: pd.Series, window: int = 20) -> Dict[str, Union[str, float]]:
        """
        Detect market regime shifts (risk-on/risk-off)
        
        Args:
            prices: Series of prices
            window: Lookback window for regime detection
            
        Returns:
            Dictionary with regime information
        """
        if len(prices) < window:
            return {"regime": "Insufficient Data", "confidence": 0.0, "driver": "Not enough data"}
            
        # Calculate recent performance
        recent_returns = prices.pct_change().tail(window)
        avg_return = recent_returns.mean()
        volatility = recent_returns.std()
        
        # Calculate z-scores for regime detection
        return_zscore = (avg_return - recent_returns.mean()) / recent_returns.std() if recent_returns.std() != 0 else 0
        vol_zscore = (volatility - recent_returns.std()) / recent_returns.std() if recent_returns.std() != 0 else 0
        
        # Determine regime based on return and volatility characteristics
        if return_zscore > 1.0 and vol_zscore < -0.5:
            regime = "Risk-On"
            driver = "Positive returns with low volatility"
        elif return_zscore < -1.0 and vol_zscore > 0.5:
            regime = "Risk-Off"
            driver = "Negative returns with high volatility"
        elif vol_zscore > 1.0:
            regime = "High Volatility"
            driver = "Elevated market uncertainty"
        elif abs(return_zscore) < 0.5:
            regime = "Range-Bound"
            driver = "Sideways market movement"
        else:
            regime = "Normal Market"
            driver = "Stable market conditions"
            
        # Calculate confidence based on strength of signals
        confidence = min(1.0, (abs(return_zscore) + abs(vol_zscore)) / 4.0)
        
        return {
            "regime": regime,
            "confidence": confidence,
            "driver": driver,
            "return_zscore": return_zscore,
            "volatility_zscore": vol_zscore
        }
    
    def calculate_correlation_matrix(self, data_dict: Dict[str, pd.Series]) -> pd.DataFrame:
        """
        Calculate correlation matrix between multiple assets
        
        Args:
            data_dict: Dictionary mapping asset names to price series
            
        Returns:
            Correlation matrix DataFrame
        """
        if not data_dict:
            return pd.DataFrame()
            
        # Create DataFrame from dictionary
        df = pd.DataFrame(data_dict)
        
        # Calculate correlation matrix
        correlation_matrix = df.corr()
        
        return correlation_matrix
    
    def identify_cross_asset_impacts(self, asset_returns: Dict[str, pd.Series]) -> Dict[str, List[Dict]]:
        """
        Identify cross-asset impacts and spillovers
        
        Args:
            asset_returns: Dictionary mapping asset names to return series
            
        Returns:
            Dictionary of cross-asset impact analysis
        """
        impacts = {}
        
        # For each asset, analyze its relationship with others
        for asset_name, returns in asset_returns.items():
            if len(returns) < 10:
                continue
                
            asset_impacts = []
            
            # Compare with other assets
            for other_asset, other_returns in asset_returns.items():
                if asset_name == other_asset or len(other_returns) < 10:
                    continue
                    
                # Align returns
                aligned_returns = pd.concat([returns, other_returns], axis=1).dropna()
                if len(aligned_returns) < 10:
                    continue
                    
                # Calculate correlation
                correlation = aligned_returns.iloc[:, 0].corr(aligned_returns.iloc[:, 1])
                
                # Calculate lead-lag relationship
                lead_lag = self._calculate_lead_lag_relationship(
                    aligned_returns.iloc[:, 0], 
                    aligned_returns.iloc[:, 1]
                )
                
                asset_impacts.append({
                    "related_asset": other_asset,
                    "correlation": correlation,
                    "lead_lag": lead_lag,
                    "strength": abs(correlation)
                })
            
            # Sort by strength
            asset_impacts.sort(key=lambda x: x["strength"], reverse=True)
            impacts[asset_name] = asset_impacts[:3]  # Top 3 relationships
            
        return impacts
    
    def _calculate_lead_lag_relationship(self, series1: pd.Series, series2: pd.Series) -> str:
        """
        Calculate lead-lag relationship between two time series
        
        Args:
            series1: First time series
            series2: Second time series
            
        Returns:
            Lead-lag relationship description
        """
        if len(series1) < 10 or len(series2) < 10:
            return "No relationship"
            
        # Simplified lead-lag detection
        # In a real implementation, you would use cross-correlation or Granger causality
        correlation = series1.corr(series2)
        
        if correlation > 0.5:
            return "Positively correlated"
        elif correlation < -0.5:
            return "Negatively correlated"
        else:
            return "Weakly correlated"
    
    def generate_institutional_insights(self, data: pd.DataFrame, asset_class: str) -> Dict[str, str]:
        """
        Generate institutional-grade insights and commentary for an asset class
        
        Args:
            data: DataFrame with market data
            asset_class: Type of asset class
            
        Returns:
            Dictionary with institutional insights
        """
        insights = {}
        
        if data.empty:
            return {
                "trend_context": "Insufficient data for analysis",
                "recent_drivers": "No recent data available",
                "cross_asset_implications": "Unable to determine cross-asset effects",
                "forward_outlook": "Outlook uncertain due to data limitations",
                "key_risks": "Data availability risk"
            }
        
        # Calculate key metrics
        if 'close' in data.columns:
            prices = data['close']
            returns = prices.pct_change().dropna()
            
            # Trend analysis
            if len(prices) >= 20:
                short_term_trend = (prices.tail(5).mean() - prices.tail(20).mean()) / prices.tail(20).mean()
                long_term_trend = (prices.iloc[-1] - prices.iloc[0]) / prices.iloc[0] if len(prices) > 0 else 0
                
                if short_term_trend > 0.02 and long_term_trend > 0:
                    trend_context = f"Bullish momentum with {short_term_trend*100:.1f}% short-term upside"
                elif short_term_trend < -0.02 and long_term_trend < 0:
                    trend_context = f"Bearish pressure with {abs(short_term_trend)*100:.1f}% short-term downside"
                else:
                    trend_context = "Mixed trend signals with consolidation"
            else:
                trend_context = "Insufficient data for trend analysis"
            
            # Recent drivers analysis
            if len(returns) >= 10:
                recent_volatility = returns.tail(10).std()
                avg_return = returns.tail(10).mean()
                
                if recent_volatility > returns.std() * 1.5:
                    recent_drivers = "Heightened volatility driving price action"
                elif abs(avg_return) > abs(returns.mean()) * 2:
                    recent_drivers = "Significant price moves outside normal parameters"
                else:
                    recent_drivers = "Market moving within normal parameters"
            else:
                recent_drivers = "Limited recent activity data"
            
            # Cross-asset implications
            cross_asset_implications = f"Impacting {asset_class} positioning and risk management"
            
            # Forward outlook
            if len(returns) >= 5:
                recent_performance = returns.tail(5).sum()
                if recent_performance > 0.05:
                    forward_outlook = "Positive near-term outlook with continued upside potential"
                elif recent_performance < -0.05:
                    forward_outlook = "Cautious outlook with downside risks monitored"
                else:
                    forward_outlook = "Neutral bias with range-bound expectations"
            else:
                forward_outlook = "Unclear directional bias pending further data"
            
            # Key risks
            max_dd, _, _ = self.calculate_max_drawdown(prices)
            var_95 = self.calculate_value_at_risk(returns, 0.95)
            
            key_risks = f"Maximum drawdown risk: {abs(max_dd)*100:.1f}%, VaR(95%): {abs(var_95)*100:.1f}%"
            
        else:
            trend_context = "No price data available"
            recent_drivers = "Unable to identify recent drivers"
            cross_asset_implications = "Cross-asset effects undetermined"
            forward_outlook = "Forward outlook unclear"
            key_risks = "Risk metrics unavailable"
        
        return {
            "trend_context": trend_context,
            "recent_drivers": recent_drivers,
            "cross_asset_implications": cross_asset_implications,
            "forward_outlook": forward_outlook,
            "key_risks": key_risks
        }
    
    def generate_regime_commentary(self, regime_info: Dict) -> str:
        """
        Generate commentary for detected market regime
        
        Args:
            regime_info: Dictionary with regime information
            
        Returns:
            Commentary string
        """
        regime = regime_info.get("regime", "Unknown")
        confidence = regime_info.get("confidence", 0.0)
        driver = regime_info.get("driver", "No specific driver")
        
        if regime == "Risk-On":
            commentary = f"Market exhibiting strong risk-on sentiment ({confidence*100:.0f}% confidence). {driver}. Favorable for growth assets and cyclical sectors."
        elif regime == "Risk-Off":
            commentary = f"Market showing pronounced risk-off behavior ({confidence*100:.0f}% confidence). {driver}. Defensive positioning recommended with emphasis on quality assets."
        elif regime == "High Volatility":
            commentary = f"Market experiencing elevated volatility conditions ({confidence*100:.0f}% confidence). {driver}. Increased hedging activity and reduced net exposures advisable."
        elif regime == "Range-Bound":
            commentary = f"Market displaying range-bound characteristics ({confidence*100:.0f}% confidence). {driver}. Tactical trading opportunities within established ranges."
        else:
            commentary = f"Market in normal conditions ({confidence*100:.0f}% confidence). {driver}. Standard risk management protocols appropriate."
            
        return commentary

# Example usage
if __name__ == "__main__":
    # Create sample data for testing
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    sample_prices = pd.Series(np.random.randn(100).cumsum() + 100, index=dates)
    sample_returns = sample_prices.pct_change().dropna()
    
    # Initialize analytics engine
    analytics = InstitutionalMarketAnalytics()
    
    # Test Sharpe ratio
    sharpe = analytics.calculate_sharpe_ratio(sample_returns)
    print(f"Sharpe Ratio: {sharpe:.2f}")
    
    # Test Sortino ratio
    sortino = analytics.calculate_sortino_ratio(sample_returns)
    print(f"Sortino Ratio: {sortino:.2f}")
    
    # Test max drawdown
    max_dd, peak_date, trough_date = analytics.calculate_max_drawdown(sample_prices)
    print(f"Max Drawdown: {max_dd:.2%}")
    
    # Test VaR
    var_95 = analytics.calculate_value_at_risk(sample_returns)
    print(f"VaR(95%): {var_95:.2%}")
    
    # Test regime detection
    regime_info = analytics.detect_regime_shifts(sample_prices)
    print(f"Regime: {regime_info['regime']}")
    print(f"Regime Commentary: {analytics.generate_regime_commentary(regime_info)}")