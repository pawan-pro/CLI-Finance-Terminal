import plotille
import matplotlib.pyplot as plt
import mplfinance as mpf
from datetime import datetime, timedelta
import pandas as pd
import pandas_ta as ta
import numpy as np
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
            df: DataFrame with "time" and "close" columns
            symbol: Symbol name
            width: Chart width
            height: Chart height

        Returns:
            ASCII chart as string
        """
        if df.empty or "time" not in df.columns or "close" not in df.columns:
            return f"No data available for {symbol}"

        # Filter out NaN values
        df = df.dropna(subset=["time", "close"])
        if df.empty:
            return f"No valid data available for {symbol}"

        # Convert to lists for plotille
        times = df["time"].tolist()
        prices = df["close"].tolist()

        # Create figure
        fig = plotille.Figure()
        fig.width = width
        fig.height = height
        fig.x_label = "Date"
        fig.y_label = "Price"
        fig.color_mode = "rgb"

        # Plot data
        fig.plot(times, prices, lc="blue", marker="."
        )

        # Set title
        fig.set_title(f"{symbol} Price Chart")

        return fig.show()

    def generate_matplotlib_chart(self, df: pd.DataFrame, symbol: str, save_path: str) -> str:
        """
        Generate a simple line chart for a symbol using matplotlib (no mdates dependency).
        Args:
            df: DataFrame with "time" and "close" columns
            symbol: Symbol name
            save_path: Path to save the chart
        Returns:
            Path to saved chart
        """
        if df.empty or "time" not in df.columns or "close" not in df.columns:
            logger.warning(f"No data available for {symbol}")
            return ""
        df = df.dropna(subset=["time", "close"])
        if df.empty:
            logger.warning(f"No valid data available for {symbol}")
            return ""
        # Optionally drop weekends for non-crypto
        is_crypto_line = ('.lv' in symbol.lower()) or (symbol.lower().startswith('btc'))
        if not is_crypto_line:
            try:
                df = df[pd.to_datetime(df['time']).dt.weekday < 5]
            except Exception:
                pass
        # Set up professional color scheme and font
        plt.rcParams.update({
            'font.family': 'DejaVu Sans',  # Default professional font
            'axes.facecolor': '#ffffff',
            'figure.facecolor': '#ffffff',
            'axes.edgecolor': '#e2e8f0',
            'axes.labelcolor': '#2d3748',
            'xtick.color': '#4a5568',
            'ytick.color': '#4a5568',
            'grid.color': '#e2e8f0'
        })
        
        # Create figure with professional colors
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Use professional muted colors
        ax.plot(df['time'], df['close'], linewidth=1.5, color='#2c5282', linestyle='-', marker='', markersize=0)  # Muted blue
        
        # Professional styling
        ax.set_xlabel("Date", fontsize=12, color='#2d3748')
        ax.set_ylabel("Price", fontsize=12, color='#2d3748')
        ax.grid(True, alpha=0.3, color='#a0aec0', linestyle='--', linewidth=0.5)
        
        # Set professional background
        ax.set_facecolor('#ffffff')
        fig.patch.set_facecolor('#ffffff')
        
        # Set tick label colors
        ax.tick_params(axis='x', colors='#4a5568', labelsize=10, rotation=45)
        ax.tick_params(axis='y', colors='#4a5568', labelsize=10)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches="tight", facecolor='#ffffff', edgecolor='none')
        plt.close()
        return save_path

    def generate_candlestick_chart(self, df: pd.DataFrame, symbol: str, save_path: str) -> str:
        """
        Generate candlestick chart for a symbol using mplfinance, including SMAs, Volume, and RSI.
        Handles CSV data format from data-mt5.py (time, open, high, low, close, tick_volume).
        """
        import warnings
        warnings.filterwarnings("ignore", category=UserWarning, module="mplfinance")

        # Check for required columns
        required_cols = ["time", "open", "high", "low", "close"]
        if not all(col in df.columns for col in required_cols):
            logger.warning(f"Missing required columns for candlestick chart for {symbol}")
            return ""

        # Handle CSV format from data-mt5.py (which uses "tick_volume" instead of "volume")
        if "tick_volume" in df.columns and "volume" not in df.columns:
            df = df.rename(columns={"tick_volume": "volume"})
        elif "volume" not in df.columns:
            df["volume"] = 0

        # Ensure datetime format for time column
        if not pd.api.types.is_datetime64_any_dtype(df["time"]):
            try:
                df["time"] = pd.to_datetime(df["time"])
            except Exception:
                logger.warning(f"Could not convert time column to datetime for {symbol}")
                return ""

        df = df.dropna().sort_values("time")
        if df.empty:
            logger.warning(f"No valid data available for {symbol}")
            return ""

        # Calculate technical indicators
        try:
            df["SMA_20"] = df["close"].rolling(window=20).mean()
            df["SMA_50"] = df["close"].rolling(window=50).mean()
            df["EMA_9"] = df["close"].ewm(span=9).mean()
            # RSI
            delta = df["close"].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df["RSI_14"] = 100 - (100 / (1 + rs))
        except Exception as e:
            logger.warning(f"Error calculating technical indicators for {symbol}: {e}")

        # Set index for mplfinance
        df = df.set_index("time")

        # Prepare additional plots (SMA, EMA)
        apds = [
            mpf.make_addplot(df["SMA_20"], color="orange", width=1, panel=0, ylabel="SMA 20"),
            mpf.make_addplot(df["SMA_50"], color="purple", width=1, panel=0, ylabel="SMA 50"),
            mpf.make_addplot(df["EMA_9"], color="red", width=1, panel=0, ylabel="EMA 9"),
            mpf.make_addplot(df["RSI_14"], color="green", width=1, panel=1, ylabel="RSI 14"),
        ]

        # RSI panel config
        panel_ratios = (3, 1)

        # Plot with mplfinance using professional styling
        try:
            # Use the standard mplfinance API that is compatible with most versions
            s = mpf.make_mpf_style(
                base_mpf_style='yahoo',  # Base style
                gridstyle='--',
                gridcolor='#e2e8f0',  # Light gray grid
                y_on_right=True,
                rc={
                    'font.family': 'DejaVu Sans',  # Professional font
                    'axes.facecolor': '#ffffff',
                    'figure.facecolor': '#ffffff',
                    'axes.edgecolor': '#e2e8f0',
                    'axes.labelcolor': '#2d3748',
                    'xtick.color': '#4a5568',
                    'ytick.color': '#4a5568'
                }
            )
            
            mpf.plot(
                df,
                type="candle",
                style=s,
                addplot=apds,
                volume=True,
                panel_ratios=panel_ratios,
                figratio=(14, 8),
                figscale=1.1,
                title="",  # Remove title overlay on chart as per meta-prompt directive
                ylabel="Price",
                ylabel_lower="Volume",
                savefig=save_path,
                tight_layout=True,
            )
        except Exception as e:
            logger.warning(f"mplfinance failed for {symbol}: {e}")
            return ""

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
            with open(ascii_path, "w") as f:
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
__all__ = ["MarketChartGenerator", "generate_chart"]
