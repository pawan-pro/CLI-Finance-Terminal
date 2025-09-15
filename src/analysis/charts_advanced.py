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
        df = df.dropna(subset=['time', 'close'])
        if df.empty:
            logger.warning(f"No valid data available for {symbol}")
            return ""

        # Create the plot
        plt.figure(figsize=(12, 6))
        plt.plot(df['time'], df['close'], linewidth=1.5, color='blue')
        plt.title(f"{symbol} Price Chart", fontsize=16)
        plt.xlabel("Date", fontsize=12)
        plt.ylabel("Price", fontsize=12)
        plt.grid(True, alpha=0.3)
        
        # Format x-axis dates
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=5))
        plt.gcf().autofmt_xdate()
        
        # Save the plot
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return save_path

    def generate_candlestick_chart(self, df: pd.DataFrame, symbol: str, save_path: str) -> str:
        """
        Generate candlestick chart for a symbol using matplotlib
        
        Args:
            df: DataFrame with OHLC data ('time', 'open', 'high', 'low', 'close')
            symbol: Symbol name
            save_path: Path to save the chart
            
        Returns:
            Path to saved chart
        """
        if df.empty:
            logger.warning(f"No data available for {symbol}")
            return ""
            
        # Required columns for candlestick chart
        required_columns = ['time', 'open', 'high', 'low', 'close']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.warning(f"Missing columns for candlestick chart {symbol}: {missing_columns}")
            return ""
            
        # Filter out NaN values
        df = df.dropna(subset=required_columns)
        if df.empty:
            logger.warning(f"No valid data available for {symbol}")
            return ""
            
        # Sort by time to ensure proper order
        df = df.sort_values('time')
        
        # Create the candlestick chart
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Plot candlesticks
        width = 0.6  # Width of candles
        for i, (_, row) in enumerate(df.iterrows()):
            # Draw the high-low line (wick)
            ax.plot([i, i], [row['low'], row['high']], color='black', linewidth=1)
            
            # Determine colors (green for up, red for down)
            color = 'green' if row['close'] >= row['open'] else 'red'
            
            # Draw the body
            body_height = abs(row['close'] - row['open'])
            body_bottom = min(row['close'], row['open'])
            ax.bar(i, body_height, bottom=body_bottom, width=width, color=color, edgecolor='black')
        
        # Format x-axis
        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel("Price", fontsize=12)
        ax.set_title(f"{symbol} Candlestick Chart", fontsize=16)
        ax.grid(True, alpha=0.3)
        
        # Set x-axis labels to show dates at regular intervals
        num_points = len(df)
        step = max(1, num_points // 10)  # Show approximately 10 date labels
        xticks = list(range(0, num_points, step))
        xtick_labels = [df.iloc[i]['time'].strftime('%m/%d') for i in xticks]
        ax.set_xticks(xticks)
        ax.set_xticklabels(xtick_labels, rotation=45)
        
        # Save the plot
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
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