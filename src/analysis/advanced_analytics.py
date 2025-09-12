import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedMarketAnalytics:
    """Class to perform advanced market analytics for investment reports"""
    
    @staticmethod
    def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index (RSI)
        
        Args:
            prices: Series of prices
            period: RSI period (default 14)
            
        Returns:
            RSI values
        """
        if len(prices) < period:
            return pd.Series(dtype=float)
        
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_macd(prices: pd.Series, fast_period: int = 12, slow_period: int = 26, 
                      signal_period: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        Args:
            prices: Series of prices
            fast_period: Fast EMA period (default 12)
            slow_period: Slow EMA period (default 26)
            signal_period: Signal line period (default 9)
            
        Returns:
            Tuple of (MACD line, Signal line, Histogram)
        """
        if len(prices) < max(fast_period, slow_period, signal_period):
            return pd.Series(dtype=float), pd.Series(dtype=float), pd.Series(dtype=float)
        
        # Calculate EMAs
        ema_fast = prices.ewm(span=fast_period).mean()
        ema_slow = prices.ewm(span=slow_period).mean()
        
        # Calculate MACD line
        macd_line = ema_fast - ema_slow
        
        # Calculate signal line
        signal_line = macd_line.ewm(span=signal_period).mean()
        
        # Calculate histogram
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def calculate_bollinger_bands(prices: pd.Series, period: int = 20, 
                                num_std: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate Bollinger Bands
        
        Args:
            prices: Series of prices
            period: Period for moving average (default 20)
            num_std: Number of standard deviations (default 2.0)
            
        Returns:
            Tuple of (Upper band, Middle band, Lower band)
        """
        if len(prices) < period:
            return pd.Series(dtype=float), pd.Series(dtype=float), pd.Series(dtype=float)
        
        # Calculate middle band (SMA)
        middle_band = prices.rolling(window=period).mean()
        
        # Calculate standard deviation
        std_dev = prices.rolling(window=period).std()
        
        # Calculate upper and lower bands
        upper_band = middle_band + (std_dev * num_std)
        lower_band = middle_band - (std_dev * num_std)
        
        return upper_band, middle_band, lower_band
    
    @staticmethod
    def calculate_support_resistance(prices: pd.Series, window: int = 20) -> Tuple[float, float]:
        """
        Calculate basic support and resistance levels
        
        Args:
            prices: Series of prices
            window: Window size for calculation
            
        Returns:
            Tuple of (Support level, Resistance level)
        """
        if len(prices) < window:
            return 0.0, 0.0
        
        recent_prices = prices.tail(window)
        support = recent_prices.min()
        resistance = recent_prices.max()
        
        return support, resistance
    
    @staticmethod
    def calculate_moving_averages(prices: pd.Series, periods: List[int] = [10, 20, 50]) -> Dict[int, float]:
        """
        Calculate multiple moving averages
        
        Args:
            prices: Series of prices
            periods: List of periods for moving averages
            
        Returns:
            Dictionary mapping period to moving average value
        """
        mas = {}
        for period in periods:
            if len(prices) >= period:
                mas[period] = prices.tail(period).mean()
            else:
                mas[period] = np.nan
        return mas
    
    @staticmethod
    def calculate_correlation_matrix(data_dict: Dict[str, pd.Series]) -> pd.DataFrame:
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
    
    @staticmethod
    def identify_market_regime(prices: pd.Series, volatility_window: int = 20, 
                              trend_window: int = 50) -> str:
        """
        Identify current market regime (trending, mean-reverting, volatile, etc.)
        
        Args:
            prices: Series of prices
            volatility_window: Window for volatility calculation
            trend_window: Window for trend calculation
            
        Returns:
            Market regime classification
        """
        if len(prices) < max(volatility_window, trend_window):
            return "Insufficient Data"
        
        # Calculate recent volatility
        recent_volatility = prices.pct_change().tail(volatility_window).std()
        
        # Calculate trend strength
        prices_trend = prices.tail(trend_window)
        trend_slope = np.polyfit(range(len(prices_trend)), prices_trend, 1)[0]
        trend_strength = abs(trend_slope) * len(prices_trend)
        
        # Classify regime
        if recent_volatility > prices.pct_change().std() * 1.5:
            return "High Volatility"
        elif abs(trend_strength) > prices.diff().mean() * 2:
            return "Strong Trend" if trend_slope > 0 else "Strong Downtrend"
        elif recent_volatility < prices.pct_change().std() * 0.5:
            return "Low Volatility"
        else:
            return "Normal Market"
    
    @staticmethod
    def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """
        Calculate Sharpe Ratio
        
        Args:
            returns: Series of returns
            risk_free_rate: Annual risk-free rate (default 2%)
            
        Returns:
            Sharpe ratio
        """
        if len(returns) == 0:
            return 0.0
        
        # Calculate excess returns
        excess_returns = returns - (risk_free_rate / 252)  # Daily risk-free rate
        
        # Calculate Sharpe ratio
        if returns.std() != 0:
            sharpe_ratio = excess_returns.mean() / returns.std() * np.sqrt(252)  # Annualized
        else:
            sharpe_ratio = 0.0
        
        return sharpe_ratio
    
    @staticmethod
    def calculate_sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """
        Calculate Sortino Ratio (considering only downside deviation)
        
        Args:
            returns: Series of returns
            risk_free_rate: Annual risk-free rate (default 2%)
            
        Returns:
            Sortino ratio
        """
        if len(returns) == 0:
            return 0.0
        
        # Calculate excess returns
        excess_returns = returns - (risk_free_rate / 252)  # Daily risk-free rate
        
        # Calculate downside deviation
        negative_returns = returns[returns < 0]
        if len(negative_returns) > 0:
            downside_deviation = negative_returns.std()
        else:
            downside_deviation = 1e-10  # Small value to avoid division by zero
        
        # Calculate Sortino ratio
        if downside_deviation != 0:
            sortino_ratio = excess_returns.mean() / downside_deviation * np.sqrt(252)  # Annualized
        else:
            sortino_ratio = 0.0
        
        return sortino_ratio
    
    @staticmethod
    def calculate_max_drawdown(prices: pd.Series) -> Tuple[float, datetime, datetime]:
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

# Example usage
if __name__ == "__main__":
    # Create sample data for testing
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    sample_prices = pd.Series(np.random.randn(100).cumsum() + 100, index=dates)
    
    # Calculate RSI
    rsi = AdvancedMarketAnalytics.calculate_rsi(sample_prices)
    print(f"Latest RSI: {rsi.iloc[-1]:.2f}")
    
    # Calculate MACD
    macd_line, signal_line, histogram = AdvancedMarketAnalytics.calculate_macd(sample_prices)
    print(f"Latest MACD: {macd_line.iloc[-1]:.2f}")
    
    # Calculate Bollinger Bands
    upper_band, middle_band, lower_band = AdvancedMarketAnalytics.calculate_bollinger_bands(sample_prices)
    print(f"Latest Bollinger Bands: Upper={upper_band.iloc[-1]:.2f}, Middle={middle_band.iloc[-1]:.2f}, Lower={lower_band.iloc[-1]:.2f}")
    
    # Calculate support and resistance
    support, resistance = AdvancedMarketAnalytics.calculate_support_resistance(sample_prices)
    print(f"Support: {support:.2f}, Resistance: {resistance:.2f}")
    
    # Calculate moving averages
    mas = AdvancedMarketAnalytics.calculate_moving_averages(sample_prices)
    print("Moving Averages:")
    for period, ma in mas.items():
        print(f"  {period}-day MA: {ma:.2f}")
    
    # Identify market regime
    regime = AdvancedMarketAnalytics.identify_market_regime(sample_prices)
    print(f"Market Regime: {regime}")
    
    # Calculate Sharpe ratio
    returns = sample_prices.pct_change().dropna()
    sharpe = AdvancedMarketAnalytics.calculate_sharpe_ratio(returns)
    print(f"Sharpe Ratio: {sharpe:.2f}")
    
    # Calculate Sortino ratio
    sortino = AdvancedMarketAnalytics.calculate_sortino_ratio(returns)
    print(f"Sortino Ratio: {sortino:.2f}")
    
    # Calculate max drawdown
    max_dd, peak_date, trough_date = AdvancedMarketAnalytics.calculate_max_drawdown(sample_prices)
    print(f"Max Drawdown: {max_dd:.2%}")