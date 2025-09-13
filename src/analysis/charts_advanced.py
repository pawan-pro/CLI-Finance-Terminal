import plotille
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import pandas as pd
import os
from typing import List, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketChartGenerator:
    """Class to generate market charts"""
    
    def __init__(self):
        """Initialize chart generator"""
        pass
    
    def generate_ascii_chart(self, df: pd.DataFrame, symbol: str, width: int = 80, height: int = 20) -> str:
        """
        Generate ASCII chart for a symbol using plotille
        
        Args:
            df: DataFrame with 'time' and 'close' columns
            symbol: Symbol name
            width: Chart width
            height: Chart height
            
        Returns:
            ASCII chart as string
        """
        if df.empty or 'time' not in df.columns or 'close' not in df.columns:
            return f"No data available for {symbol}"
        
        # Filter out NaN values
        df = df.dropna(subset=['time', 'close'])
        if df.empty:
            return f"No valid data available for {symbol}"
        
        # Convert to lists for plotille
        times = df['time'].tolist()
        prices = df['close'].tolist()
        
        # Create figure
        fig = plotille.Figure()
        fig.width = width
        fig.height = height
        fig.x_label = "Date"
        fig.y_label = "Price"
        fig.color_mode = "rgb"
        
        # Plot data
        fig.plot(times, prices, lc='blue', marker='.')
        
        # Set title
        fig.set_title(f"{symbol} Price Chart")
        
        return fig.show()
    
    def generate_matplotlib_chart(self, df: pd.DataFrame, symbol: str, save_path: str) -> str:
        """
        Generate matplotlib chart for a symbol
        
        Args:
            df: DataFrame with 'time' and 'close' columns
            symbol: Symbol name
            save_path: Path to save the chart
            
        Returns:
            Path to saved chart
        """
        if df.empty or 'time' not in df.columns or 'close' not in df.columns:
            logger.warning(f"No data available for {symbol}")
            return ""
        
        # Filter out NaN values
        df = df.dropna(subset=['time', 'close', 'open', 'high', 'low'])
        if df.empty:
            logger.warning(f"No valid data available for {symbol}")
            return ""

        df['time'] = pd.to_datetime(df['time'])
        df = df.set_index('time')

        # Calculate SMAs
        df['SMA50'] = df['close'].rolling(window=50).mean()
        df['SMA200'] = df['close'].rolling(window=200).mean()

        # Create the plot
        import mplfinance as mpf
        mpf.plot(df, type='candle', style='yahoo',
                 title=f"{symbol} Price Chart",
                 ylabel='Price',
                 mav=(50, 200),
                 volume=True,
                 savefig=save_path)
        
        return save_path
    
    def generate_dashboard(self, df: pd.DataFrame, symbol: str, save_path_base: str) -> List[str]:
        """
        Generate dashboard with both ASCII and matplotlib charts
        
        Args:
            df: DataFrame with market data
            symbol: Symbol name
            save_path_base: Base path for saving charts (without extension)
            
        Returns:
            List of paths to generated charts
        """
        generated_charts = []
        
        try:
            # Generate ASCII chart
            ascii_chart = self.generate_ascii_chart(df, symbol)
            ascii_path = f"{save_path_base}_ascii.txt"
            with open(ascii_path, 'w') as f:
                f.write(ascii_chart)
            generated_charts.append(ascii_path)
        except Exception as e:
            logger.warning(f"Error generating ASCII chart for {symbol}: {e}")
        
        try:
            # Generate matplotlib chart
            matplotlib_path = f"{save_path_base}_matplotlib.png"
            chart_path = self.generate_matplotlib_chart(df, symbol, matplotlib_path)
            if chart_path:
                generated_charts.append(chart_path)
        except Exception as e:
            logger.warning(f"Error generating matplotlib chart for {symbol}: {e}")
        
        return generated_charts

def generate_chart(dates: list[str], prices: list[float], width=80, height=20) -> str:
    """
    Generates an ASCII chart from historical price data.
    """
    # Convert date strings to datetime objects
    date_objects = [datetime.strptime(d, "%Y-%m-%d") for d in dates]

    # Create the plot
    fig = plotille.Figure()
    fig.width = width
    fig.height = height
    fig.x_label = "Date"
    fig.y_label = "Price"

    # Add data to the plot
    fig.plot(
        [d.timestamp() for d in date_objects],
        prices,
        lc="cyan",
    )

    # Customize x-axis ticks to show dates
    # This is a bit tricky with plotille, we might need a more sophisticated approach
    # For now, let's just show the first and last date
    if date_objects:
        fig.set_x_ticks(
            [date_objects[0].timestamp(), date_objects[-1].timestamp()],
            [dates[0], dates[-1]]
        )

    return fig.show()

# Keep the original function for backward compatibility
__all__ = ['MarketChartGenerator', 'generate_chart']