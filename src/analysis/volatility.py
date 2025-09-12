import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VolatilityCalculator:
    """Class to calculate various volatility metrics"""
    
    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        Calculate Average True Range (ATR)
        """
        if df.empty:
            return df
            
        df = df.copy()
        df['tr1'] = df['high'] - df['low']
        df['tr2'] = (df['high'] - df['close'].shift()).abs()
        df['tr3'] = (df['low'] - df['close'].shift()).abs()
        df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
        df['atr'] = df['tr'].rolling(window=period).mean()
        return df
    
    @staticmethod
    def calculate_volatility(df: pd.DataFrame, column: str = 'close', period: int = 14) -> pd.Series:
        """
        Calculate volatility as standard deviation of returns
        """
        if df.empty:
            return pd.Series(dtype=float)
            
        returns = df[column].pct_change()
        volatility = returns.rolling(window=period).std()
        return volatility
    
    @staticmethod
    def calculate_realized_volatility(df: pd.DataFrame, column: str = 'close', period: int = 21) -> float:
        """
        Calculate realized volatility (annualized)
        """
        if df.empty:
            return 0.0
            
        returns = df[column].pct_change().dropna()
        if len(returns) < period:
            period = len(returns)
            
        realized_vol = returns[-period:].std() * np.sqrt(252)  # Annualized
        return realized_vol
    
    @staticmethod
    def calculate_volatility_cone(df: pd.DataFrame, column: str = 'close', 
                                periods: List[int] = [14, 30, 60, 90]) -> Dict[int, Dict[str, float]]:
        """
        Calculate volatility cone (min, max, avg volatility for different periods)
        """
        if df.empty:
            return {}
            
        returns = df[column].pct_change().dropna()
        cone = {}
        
        for period in periods:
            if len(returns) >= period:
                vol_series = returns.rolling(window=period).std() * np.sqrt(252)  # Annualized
                vol_series = vol_series.dropna()
                if not vol_series.empty:
                    cone[period] = {
                        'min': vol_series.min(),
                        'max': vol_series.max(),
                        'avg': vol_series.mean()
                    }
        
        return cone
    
    @staticmethod
    def calculate_vix_like_index(price_data: pd.DataFrame, 
                                lookback_period: int = 30) -> float:
        """
        Calculate a VIX-like index based on price volatility
        This is a simplified version - real VIX calculation is more complex
        """
        if price_data.empty:
            return 0.0
            
        # Calculate realized volatility over the lookback period
        volatility = VolatilityCalculator.calculate_realized_volatility(
            price_data, 'close', lookback_period)
        return volatility * 100  # Scale to percentage
    
    @staticmethod
    def get_volatility_summary(df: pd.DataFrame, symbol: str = "") -> Dict[str, float]:
        """
        Get a summary of volatility metrics for a given dataframe
        """
        if df.empty:
            return {}
            
        # Calculate various volatility measures
        atr_df = VolatilityCalculator.calculate_atr(df)
        volatility_series = VolatilityCalculator.calculate_volatility(df)
        realized_vol = VolatilityCalculator.calculate_realized_volatility(df)
        volatility_cone = VolatilityCalculator.calculate_volatility_cone(df)
        
        summary = {
            'symbol': symbol,
            'current_atr': atr_df['atr'].iloc[-1] if not atr_df.empty and 'atr' in atr_df.columns else 0,
            'current_volatility': volatility_series.iloc[-1] if not volatility_series.empty else 0,
            'realized_volatility': realized_vol,
            'volatility_cone': volatility_cone
        }
        
        return summary

# Example usage
if __name__ == "__main__":
    # Create sample data for testing
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    sample_data = pd.DataFrame({
        'open': np.random.rand(100) * 100 + 1000,
        'high': np.random.rand(100) * 100 + 1010,
        'low': np.random.rand(100) * 100 + 990,
        'close': np.random.rand(100) * 100 + 1005,
        'volume': np.random.randint(1000, 10000, 100)
    })
    sample_data.index = dates
    
    # Calculate volatility metrics
    calculator = VolatilityCalculator()
    
    # ATR calculation
    atr_df = calculator.calculate_atr(sample_data)
    print("ATR calculation:")
    print(atr_df[['close', 'tr', 'atr']].tail())
    
    # Volatility calculation
    vol_series = calculator.calculate_volatility(sample_data)
    print("\nVolatility calculation:")
    print(vol_series.tail())
    
    # Realized volatility
    realized_vol = calculator.calculate_realized_volatility(sample_data)
    print(f"\nRealized volatility (annualized): {realized_vol:.4f}")
    
    # Volatility cone
    vol_cone = calculator.calculate_volatility_cone(sample_data)
    print("\nVolatility cone:")
    for period, stats in vol_cone.items():
        print(f"  {period} days: Min={stats['min']:.4f}, Max={stats['max']:.4f}, Avg={stats['avg']:.4f}")
    
    # VIX-like index
    vix_like = calculator.calculate_vix_like_index(sample_data)
    print(f"\nVIX-like index: {vix_like:.2f}")
    
    # Summary
    summary = calculator.get_volatility_summary(sample_data, "SAMPLE")
    print("\nVolatility summary:")
    for key, value in summary.items():
        if key != 'volatility_cone':
            print(f"  {key}: {value}")