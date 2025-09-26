import plotille
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import pandas as pd
import pandas_ta as ta
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
        Generate candlestick chart for a symbol using matplotlib, including SMAs, Volume, and RSI.
        """
        if df.empty or not all(col in df.columns for col in ['time', 'open', 'high', 'low', 'close', 'volume']):
            logger.warning(f"Incomplete data for candlestick chart for {symbol}")
            return ""

        df = df.dropna().sort_values('time')
        if df.empty:
            logger.warning(f"No valid data available for {symbol}")
            return ""

        # Calculate Technical Indicators
        df.ta.sma(length=50, append=True)
        df.ta.sma(length=200, append=True)
        df.ta.rsi(length=14, append=True)

        # Create figure with subplots
        fig = plt.figure(figsize=(12, 9))
        gs = fig.add_gridspec(3, 1, height_ratios=[3, 1, 1], hspace=0.05)
        ax1 = fig.add_subplot(gs[0])
        ax2 = fig.add_subplot(gs[1], sharex=ax1)
        ax3 = fig.add_subplot(gs[2], sharex=ax1)

        # Main Candlestick Chart
        width = 0.8
        for i, row in df.iterrows():
            color = 'green' if row['close'] >= row['open'] else 'red'
            ax1.plot([row['time'], row['time']], [row['low'], row['high']], color='black', linewidth=1)
            ax1.add_patch(plt.Rectangle((row['time'] - timedelta(days=width/2), min(row['open'], row['close'])),
                                        timedelta(days=width), abs(row['open'] - row['close']),
                                        facecolor=color, edgecolor='black'))

        # Plot SMAs
        ax1.plot(df['time'], df['SMA_50'], color='orange', linewidth=1, label='50-period SMA')
        ax1.plot(df['time'], df['SMA_200'], color='purple', linewidth=1, label='200-period SMA')
        ax1.set_ylabel('Price')
        ax1.set_title(f'{symbol} Technical Analysis')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        plt.setp(ax1.get_xticklabels(), visible=False)

        # Volume Subplot
        ax2.bar(df['time'], df['volume'], color='grey', width=width, alpha=0.6)
        ax2.set_ylabel('Volume')
        ax2.grid(True, alpha=0.3)
        plt.setp(ax2.get_xticklabels(), visible=False)

        # RSI Subplot
        ax3.plot(df['time'], df['RSI_14'], color='green', linewidth=1)
        ax3.axhline(70, color='r', linestyle='--', linewidth=1, alpha=0.5)
        ax3.axhline(30, color='g', linestyle='--', linewidth=1, alpha=0.5)
        ax3.set_ylabel('RSI (14)')
        ax3.set_ylim(0, 100)
        ax3.grid(True, alpha=0.3)

        # Format X-axis
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.xticks(rotation=45)

        # Save the plot
        fig.tight_layout()
        plt.savefig(save_path, dpi=300)
        plt.close(fig)

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