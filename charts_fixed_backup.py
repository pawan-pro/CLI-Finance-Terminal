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
        Generate matplotlib chart for a symbol

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

        # Filter out NaN values
        df = df.dropna(subset=["time", "close"])
        if df.empty:
            logger.warning(f"No valid data available for {symbol}")
            return ""

        # Create the plot
        plt.figure(figsize=(12, 6))
        plt.plot(df["time"], df["close"], linewidth=1.5, color="blue")
        plt.title(f"{symbol} Price Chart", fontsize=16)
        plt.xlabel("Date", fontsize=12)
        plt.ylabel("Price", fontsize=12)
        plt.grid(True, alpha=0.3)

        # Format x-axis dates
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=5))
        plt.gcf().autofmt_xdate()

        # Save the plot
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.close()

        return save_path

    def generate_candlestick_chart(self, df: pd.DataFrame, symbol: str, save_path: str) -> str:
        """
        Generate candlestick chart for a symbol using matplotlib, including SMAs, Volume, and RSI.
        Enhanced to handle CSV data format from data-mt5.py which includes time, open, high, low, close, tick_volume
        """
        # Check for required columns, try to map CSV column names if needed
        required_cols = ["time", "open", "high", "low", "close"]
        if not all(col in df.columns for col in required_cols):
            logger.warning(f"Missing required columns for candlestick chart for {symbol}")
            return ""

        # Handle CSV format from data-mt5.py (which uses "tick_volume" instead of "volume")
        if "tick_volume" in df.columns and "volume" not in df.columns:
            df = df.rename(columns={"tick_volume": "volume"})
        elif "volume" not in df.columns:
            # Create a volume column with default values if not available
            df["volume"] = 0

        # Ensure datetime format for time column
        if df["time"].dtype == "object":
            try:
                df["time"] = pd.to_datetime(df["time"])
            except:
                logger.warning(f"Could not convert time column to datetime for {symbol}")
                return ""

        df = df.dropna().sort_values("time")
        if df.empty:
            logger.warning(f"No valid data available for {symbol}")
            return ""

        # Calculate Technical Indicators
        try:
            # Use pandas-ta for technical indicators
            df["SMA_20"] = df["close"].rolling(window=20).mean()
            df["SMA_50"] = df["close"].rolling(window=50).mean()
            df["EMA_9"] = df["close"].ewm(span=9).mean()
            
            # Calculate RSI
            delta = df["close"].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df["RSI_14"] = 100 - (100 / (1 + rs))
            
        except Exception as e:
            logger.warning(f"Error calculating technical indicators for {symbol}: {e}")

        # Ensure proper width for 15-minute intervals
        if len(df) > 0:
            # Calculate appropriate width based on the time range
            time_diff = (df["time"].max() - df["time"].min()).total_seconds() / 3600  # in hours
            if time_diff <= 24:  # Less than 24 hours (e.g., 15-minute intervals for 24 hours)
                width = 0.01  # Small width for intraday data
            else:
                width = 0.6  # Standard width for daily data
        else:
            width = 0.6

        # Create figure with subplots
        fig = plt.figure(figsize=(14, 10))
        gs = fig.add_gridspec(3, 1, height_ratios=[3, 1, 1], hspace=0.05)
        ax1 = fig.add_subplot(gs[0])
        ax2 = fig.add_subplot(gs[1], sharex=ax1)
        ax3 = fig.add_subplot(gs[2], sharex=ax1)

        # Main Candlestick Chart
        for i, row in df.iterrows():
            color = "green" if row["close"] >= row["open"] else "red"
            # Draw wick
            ax1.plot([row["time"], row["time"]], [row["low"], row["high"]], color="black", linewidth=0.5)
            # Draw body
            ax1.add_patch(plt.Rectangle((row["time"] - pd.Timedelta(minutes=7.5) if width < 0.1 else 
                                         row["time"] - timedelta(days=width/2)), 
                                        min(row["open"], row["close"]),
                                        pd.Timedelta(minutes=15) if width < 0.1 else timedelta(days=width), 
                                        abs(row["open"] - row["close"]),
                                        facecolor=color, edgecolor="black", linewidth=0.5))

        # Plot technical indicators
        if "SMA_20" in df.columns and not df["SMA_20"].isna().all():
            ax1.plot(df["time"], df["SMA_20"], color="orange", linewidth=1, label="20-period SMA")
        if "SMA_50" in df.columns and not df["SMA_50"].isna().all():
            ax1.plot(df["time"], df["SMA_50"], color="purple", linewidth=1, label="50-period SMA")
        if "EMA_9" in df.columns and not df["EMA_9"].isna().all():
            ax1.plot(df["time"], df["EMA_9"], color="red", linewidth=1, label="9-period EMA")

        ax1.set_ylabel("Price")
        ax1.set_title(f"{symbol} Technical Analysis")
        ax1.legend(loc="best")
        ax1.grid(True, alpha=0.3)
        plt.setp(ax1.get_xticklabels(), visible=False)

        # Volume Subplot
        colors = df["close"].diff().apply(lambda x: "green" if x >= 0 else "red")
        ax2.bar(df["time"], df["volume"], color=colors, width=width, alpha=0.6)
        ax2.set_ylabel("Volume")
        ax2.grid(True, alpha=0.3)
        plt.setp(ax2.get_xticklabels(), visible=False)

        # RSI Subplot
        if "RSI_14" in df.columns and not df["RSI_14"].isna().all():
            ax3.plot(df["time"], df["RSI_14"], color="green", linewidth=1)
            ax3.axhline(70, color="r", linestyle="--", linewidth=0.8, alpha=0.7, label="Overbought (70)")
            ax3.axhline(30, color="g", linestyle="--", linewidth=0.8, alpha=0.7, label="Oversold (30)")
            ax3.axhline(50, color="gray", linestyle="--", linewidth=0.5, alpha=0.5)
            ax3.set_ylabel("RSI (14)")
            ax3.set_ylim(0, 100)
            ax3.legend(loc="best")
        else:
            ax3.text(0.5, 0.5, "RSI not available", horizontalalignment="center", 
                     verticalalignment="center", transform=ax3.transAxes)
        ax3.grid(True, alpha=0.3)

        # Format X-axis with better time formatting for 15-minute intervals
        if len(df) > 0:
            ax3.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d %H:%M"))
            plt.xticks(rotation=45, ha="right")

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
