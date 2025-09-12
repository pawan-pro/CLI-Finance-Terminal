"""
Enhanced Institutional Visualization with Storytelling

This module provides advanced charting and visualization capabilities
with institutional storytelling elements and professional formatting.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as patches
from matplotlib.gridspec import GridSpec
import seaborn as sns
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

# Configure matplotlib style for institutional appearance
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class ChartType(Enum):
    """Enum for chart types"""
    PRICE_CHART = "Price Chart"
    VOLATILITY_CHART = "Volatility Chart"
    CORRELATION_MATRIX = "Correlation Matrix"
    REGIME_DETECTION = "Regime Detection"
    RISK_METRICS = "Risk Metrics"
    SEASONALITY_ANALYSIS = "Seasonality Analysis"

@dataclass
class InstitutionalChartConfig:
    """Configuration for institutional charts"""
    figsize: Tuple[int, int] = (12, 8)
    dpi: int = 300
    font_family: str = "Arial"
    font_size: int = 10
    title_font_size: int = 14
    axis_label_font_size: int = 12
    color_scheme: str = "institutional"
    watermark_text: str = "QUANTWATER TECH INVESTMENTS"
    confidentiality_level: str = "INTERNAL USE ONLY"

class EnhancedInstitutionalVisualizer:
    """Enhanced visualizer with institutional storytelling capabilities"""
    
    def __init__(self, config: Optional[InstitutionalChartConfig] = None):
        """
        Initialize institutional visualizer
        
        Args:
            config: Chart configuration (optional)
        """
        self.config = config or InstitutionalChartConfig()
        self.color_palettes = self._define_institutional_color_palettes()
        
    def _define_institutional_color_palettes(self) -> Dict[str, List[str]]:
        """
        Define institutional color palettes
        
        Returns:
            Dictionary of color palettes
        """
        return {
            # Goldman Sachs-inspired palette
            "goldman": ["#E91D0E", "#FFD700", "#000000", "#FFFFFF", "#808080"],
            # JPMorgan-inspired palette
            "jpmorgan": ["#1A3C6C", "#D4AF37", "#FFFFFF", "#000000", "#C0C0C0"],
            # BlackRock-inspired palette
            "blackrock": ["#1B1E27", "#6CB8FF", "#FFFFFF", "#000000", "#E6E6E6"],
            # Generic institutional palette
            "institutional": ["#1a3c6c", "#2c5282", "#4299e1", "#63b3ed", "#90cdf4"],
            # Risk heatmap palette
            "risk_heatmap": ["#38a169", "#68d391", "#faf089", "#f6ad55", "#e53e3e"],
        }
    
    def create_professional_price_chart(self, data: pd.DataFrame, 
                                       symbol: str,
                                       annotations: Optional[Dict] = None,
                                       regime_info: Optional[Dict] = None) -> plt.Figure:
        """
        Create professional price chart with institutional storytelling elements
        
        Args:
            data: DataFrame with OHLCV data
            symbol: Symbol name
            annotations: Dictionary of chart annotations
            regime_info: Market regime information
            
        Returns:
            Matplotlib figure
        """
        # Create figure with subplots
        fig = plt.figure(figsize=self.config.figsize, dpi=self.config.dpi)
        gs = GridSpec(3, 1, height_ratios=[3, 1, 1], hspace=0.1)
        
        # Main price chart
        ax1 = fig.add_subplot(gs[0])
        
        # Plot price data
        if 'close' in data.columns:
            ax1.plot(data.index, data['close'], 
                    color=self.color_palettes[self.config.color_scheme][0], 
                    linewidth=1.5, label=f"{symbol} Close")
        
        # Add moving averages if available
        if 'sma_20' in data.columns:
            ax1.plot(data.index, data['sma_20'], 
                    color='#2c5282', linewidth=1, alpha=0.8, label='20-day SMA')
        if 'sma_50' in data.columns:
            ax1.plot(data.index, data['sma_50'], 
                    color='#4299e1', linewidth=1, alpha=0.8, label='50-day SMA')
        
        # Add volume subplot
        ax2 = fig.add_subplot(gs[1], sharex=ax1)
        if 'volume' in data.columns:
            ax2.bar(data.index, data['volume'], 
                   color=self.color_palettes[self.config.color_scheme][2], 
                   alpha=0.6, width=0.8)
            ax2.set_ylabel('Volume', fontsize=self.config.axis_label_font_size)
        
        # Add technical indicators subplot
        ax3 = fig.add_subplot(gs[2], sharex=ax1)
        if 'rsi' in data.columns:
            ax3.plot(data.index, data['rsi'], 
                    color=self.color_palettes[self.config.color_scheme][3], 
                    linewidth=1, label='RSI')
            # Add RSI overbought/oversold levels
            ax3.axhline(y=70, color='r', linestyle='--', alpha=0.5, linewidth=0.8)
            ax3.axhline(y=30, color='g', linestyle='--', alpha=0.5, linewidth=0.8)
            ax3.set_ylabel('RSI', fontsize=self.config.axis_label_font_size)
            ax3.set_ylim(0, 100)
        
        # Add annotations
        self._add_professional_annotations(ax1, annotations)
        
        # Add regime information
        if regime_info:
            self._add_regime_overlay(ax1, regime_info)
        
        # Format axes
        ax1.set_ylabel('Price', fontsize=self.config.axis_label_font_size)
        ax1.legend(loc='upper left', fontsize=self.config.font_size)
        ax1.grid(True, alpha=0.3)
        
        # Remove x-axis labels from top plots
        plt.setp(ax1.get_xticklabels(), visible=False)
        plt.setp(ax2.get_xticklabels(), visible=False)
        
        # Format x-axis
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        ax3.set_xlabel('Date', fontsize=self.config.axis_label_font_size)
        
        # Add title
        fig.suptitle(f'{symbol} Professional Analysis Chart', 
                     fontsize=self.config.title_font_size,
                     fontweight='bold')
        
        # Add watermark
        self._add_watermark(fig)
        
        # Add institutional footer
        self._add_institutional_footer(fig)
        
        return fig
    
    def create_correlation_heatmap(self, correlation_matrix: pd.DataFrame,
                                 title: str = "Asset Correlation Matrix") -> plt.Figure:
        """
        Create professional correlation heatmap
        
        Args:
            correlation_matrix: Correlation matrix DataFrame
            title: Chart title
            
        Returns:
            Matplotlib figure
        """
        # Create figure
        fig, ax = plt.subplots(figsize=self.config.figsize, dpi=self.config.dpi)
        
        # Create heatmap with custom styling
        sns.heatmap(correlation_matrix, 
                   annot=True, 
                   cmap='RdBu_r', 
                   center=0,
                   vmin=-1, vmax=1,
                   square=True,
                   fmt='.2f',
                   cbar_kws={"shrink": .8},
                   ax=ax)
        
        # Style the heatmap
        ax.set_title(title, fontsize=self.config.title_font_size, fontweight='bold', pad=20)
        ax.set_xlabel('Assets', fontsize=self.config.axis_label_font_size)
        ax.set_ylabel('Assets', fontsize=self.config.axis_label_font_size)
        
        # Rotate labels for better readability
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        
        # Add watermark
        self._add_watermark(fig)
        
        # Add institutional footer
        self._add_institutional_footer(fig)
        
        return fig
    
    def create_risk_metrics_dashboard(self, risk_metrics: Dict[str, float],
                                    symbol: str) -> plt.Figure:
        """
        Create professional risk metrics dashboard
        
        Args:
            risk_metrics: Dictionary of risk metrics
            symbol: Symbol name
            
        Returns:
            Matplotlib figure
        """
        # Create figure with subplots
        fig = plt.figure(figsize=(14, 10), dpi=self.config.dpi)
        gs = GridSpec(2, 3, hspace=0.3, wspace=0.3)
        
        # Risk metrics summary table
        ax1 = fig.add_subplot(gs[0, :2])
        self._create_risk_metrics_table(ax1, risk_metrics, symbol)
        
        # Risk-return scatter plot
        ax2 = fig.add_subplot(gs[0, 2])
        self._create_risk_return_scatter(ax2, risk_metrics)
        
        # Drawdown profile
        ax3 = fig.add_subplot(gs[1, 0])
        self._create_drawdown_profile(ax3, risk_metrics)
        
        # Volatility term structure
        ax4 = fig.add_subplot(gs[1, 1])
        self._create_volatility_term_structure(ax4, risk_metrics)
        
        # VaR visualization
        ax5 = fig.add_subplot(gs[1, 2])
        self._create_var_visualization(ax5, risk_metrics)
        
        # Add watermark
        self._add_watermark(fig)
        
        # Add institutional footer
        self._add_institutional_footer(fig)
        
        return fig
    
    def _create_risk_metrics_table(self, ax, risk_metrics: Dict[str, float], symbol: str):
        """Create risk metrics summary table with institutional commentary"""
        ax.axis('tight')
        ax.axis('off')
        
        # Enhanced risk metrics with institutional commentary
        enhanced_metrics = {
            'sharpe_ratio': {
                'display_name': 'Sharpe Ratio',
                'commentary': 'Risk-adjusted return measure. >1.0 excellent, 0.5-1.0 good, <0.5 suboptimal.',
                'interpretation': 'Measures excess return per unit of risk. Higher values indicate better risk-adjusted performance.'
            },
            'sortino_ratio': {
                'display_name': 'Sortino Ratio',
                'commentary': 'Downside risk-adjusted return. Focuses on negative volatility only.',
                'interpretation': 'Similar to Sharpe ratio but penalizes only downside deviation. Better for asymmetric return distributions.'
            },
            'max_drawdown': {
                'display_name': 'Max Drawdown',
                'commentary': 'Largest peak-to-trough decline. Measures worst-case loss scenario.',
                'interpretation': 'Indicates maximum historical loss from peak to trough. Critical for risk management.'
            },
            'volatility_annualized': {
                'display_name': 'Annualized Volatility',
                'commentary': 'Standard deviation of returns (annualized). Higher = more risk.',
                'interpretation': 'Measures price variation over time. Essential for portfolio construction and risk budgeting.'
            },
            'value_at_risk_95': {
                'display_name': 'VaR (95%)',
                'commentary': 'Loss not exceeded 95% of time. Daily risk measure.',
                'interpretation': 'Statistical measure of potential loss at 95% confidence level. Used for capital allocation.'
            },
            'conditional_var_95': {
                'display_name': 'CVaR (95%)',
                'commentary': 'Expected loss beyond VaR threshold. Measures tail risk.',
                'interpretation': 'Average loss in worst 5% of cases. More conservative than VaR for tail risk assessment.'
            },
            'beta': {
                'display_name': 'Beta',
                'commentary': 'Market sensitivity. >1 aggressive, <1 defensive.',
                'interpretation': 'Measures sensitivity to market movements. Used for systematic risk assessment.'
            },
            'alpha': {
                'display_name': 'Alpha',
                'commentary': 'Excess return vs benchmark. >0 outperformance.',
                'interpretation': 'Measures active return relative to benchmark. Indicates skill of investment strategy.'
            }
        }
        
        # Prepare data for table
        metrics_data = []
        commentary_data = []
        interpretation_data = []
        
        for key, value in risk_metrics.items():
            if key in enhanced_metrics:
                metric_info = enhanced_metrics[key]
                formatted_key = metric_info['display_name']
                commentary = metric_info['commentary']
                interpretation = metric_info['interpretation']
            else:
                formatted_key = key.replace('_', ' ').title()
                commentary = 'Standard risk metric'
                interpretation = 'Generic risk measurement'
            
            formatted_value = self._format_metric_value(key, value)
            metrics_data.append([formatted_key, formatted_value])
            commentary_data.append(commentary)
            interpretation_data.append(interpretation)
        
        # Create table
        table = ax.table(cellText=metrics_data,
                        colLabels=['Metric', 'Value'],
                        cellLoc='left',
                        loc='center',
                        colWidths=[0.4, 0.2])
        
        # Style the table
        table.auto_set_font_size(False)
        table.set_fontsize(self.config.font_size)
        table.scale(1.2, 1.8)
        
        # Style header cells
        for i in range(len(metrics_data) + 1):  # +1 for header
            for j in range(2):
                cell = table[(i, j)]
                if i == 0:  # Header row
                    cell.set_facecolor('#1a3c6c')
                    cell.set_text_props(color='white', weight='bold')
                else:  # Data rows
                    cell.set_facecolor('#f0f0f0' if i % 2 == 0 else 'white')
        
        # Add commentary as separate text
        commentary_text = "\n".join([f"• {comment}" for comment in commentary_data[:5]])
        ax.text(0.02, 0.02, f"Institutional Commentary:\n{commentary_text}",
               transform=ax.transAxes,
               verticalalignment='bottom',
               fontsize=7,
               color='#4a5568',
               linespacing=1.2,
               bbox=dict(boxstyle='round,pad=0.3', facecolor='#ebf8ff', alpha=0.8))
        
        ax.set_title(f'{symbol} Risk Metrics Summary', 
                     fontsize=self.config.title_font_size, 
                     fontweight='bold', pad=20)
    
    def _format_metric_value(self, metric_name: str, value: float) -> str:
        """
        Format metric value based on metric type
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            
        Returns:
            Formatted string value
        """
        if 'ratio' in metric_name.lower():
            return f"{value:.2f}"
        elif 'percent' in metric_name.lower() or '%' in metric_name:
            return f"{value:.2f}%"
        elif 'volatility' in metric_name.lower() or 'var' in metric_name.lower():
            return f"{value:.2f}%"
        elif 'drawdown' in metric_name.lower():
            return f"{value:.2f}%"
        else:
            return f"{value:.4f}"
    
    def _add_professional_annotations(self, ax, annotations: Optional[Dict] = None):
        """
        Add professional annotations to chart with institutional storytelling
        
        Args:
            ax: Matplotlib axes
            annotations: Dictionary of annotations
        """
        if not annotations:
            return
            
        # Add breakout points with institutional commentary
        if 'breakouts' in annotations:
            for breakout in annotations['breakouts']:
                level = breakout.get('level', 'N/A')
                date = breakout.get('date')
                significance = breakout.get('significance', 'Technical Breakout')
                impact = breakout.get('impact', 'Market Impact Uncertain')
                
                # Add annotation with professional styling
                ax.annotate(f"{significance}\nLevel: {level}\nImpact: {impact}",
                           xy=(date, level),
                           xytext=(15, 15),
                           textcoords='offset points',
                           bbox=dict(boxstyle='round,pad=0.5', facecolor='#1a3c6c', alpha=0.8, edgecolor='#4299e1'),
                           arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0', color='#4299e1'),
                           fontsize=8,
                           color='white',
                           weight='bold')
        
        # Add support/resistance levels with institutional commentary
        if 'support_levels' in annotations:
            for level in annotations['support_levels']:
                ax.axhline(y=level, color='#38a169', linestyle='--', alpha=0.7, linewidth=1.2)
                ax.text(ax.get_xlim()[1], level, f'Support {level:.2f}', 
                       verticalalignment='bottom', horizontalalignment='right',
                       color='#38a169', fontsize=9, weight='bold',
                       bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))
                       
        if 'resistance_levels' in annotations:
            for level in annotations['resistance_levels']:
                ax.axhline(y=level, color='#e53e3e', linestyle='--', alpha=0.7, linewidth=1.2)
                ax.text(ax.get_xlim()[1], level, f'Resistance {level:.2f}', 
                       verticalalignment='top', horizontalalignment='right',
                       color='#e53e3e', fontsize=9, weight='bold',
                       bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))
        
        # Add volatility clusters with institutional commentary
        if 'volatility_clusters' in annotations:
            for cluster in annotations['volatility_clusters']:
                start_date = cluster.get('start_date')
                end_date = cluster.get('end_date')
                reason = cluster.get('reason', 'High Volatility Period')
                ax.axvspan(start_date, end_date, alpha=0.3, color='#f6ad55', label=reason)
                # Add annotation text
                mid_date = start_date + (end_date - start_date) / 2
                ax.text(mid_date, ax.get_ylim()[1], reason,
                       verticalalignment='top', horizontalalignment='center',
                       color='#f6ad55', fontsize=9, weight='bold',
                       rotation=90,
                       bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))
        
        # Add fundamental driver annotations
        if 'fundamental_drivers' in annotations:
            for driver in annotations['fundamental_drivers']:
                date = driver.get('date')
                event = driver.get('event', 'Fundamental Event')
                impact = driver.get('impact', 'Market Impact')
                ax.axvline(x=date, color='#805ad5', linestyle='-.', alpha=0.7, linewidth=1)
                ax.text(date, ax.get_ylim()[0], event,
                       verticalalignment='bottom', horizontalalignment='center',
                       color='#805ad5', fontsize=8, weight='bold',
                       rotation=90,
                       bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))
        
        # Add central bank event annotations
        if 'central_bank_events' in annotations:
            for event in annotations['central_bank_events']:
                date = event.get('date')
                name = event.get('name', 'Central Bank Event')
                policy_impact = event.get('policy_impact', 'Policy Impact')
                ax.axvline(x=date, color='#2c5282', linestyle=':', alpha=0.8, linewidth=1.5)
                ax.text(date, ax.get_ylim()[1], f"{name}\n{policy_impact}",
                       verticalalignment='top', horizontalalignment='center',
                       color='#2c5282', fontsize=8, weight='bold',
                       rotation=90,
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='#ebf8ff', alpha=0.9))
    
    def _add_regime_overlay(self, ax, regime_info: Dict):
        """
        Add market regime overlay to chart with institutional storytelling
        
        Args:
            ax: Matplotlib axes
            regime_info: Market regime information
        """
        regime = regime_info.get('regime', 'Normal Market')
        confidence = regime_info.get('confidence', 0.0)
        driver = regime_info.get('driver', 'No specific driver')
        commentary = regime_info.get('commentary', 'Market conditions stable')
        
        # Add background color based on regime with institutional styling
        if regime == 'Risk-On':
            ax.patch.set_facecolor('#e6ffe6')  # Light green for bullish sentiment
            ax.patch.set_alpha(0.15)
            regime_color = '#38a169'  # Green for positive sentiment
            regime_text = f"📈 RISK-ON REGIME ({confidence*100:.0f}% CONFIDENCE)"
        elif regime == 'Risk-Off':
            ax.patch.set_facecolor('#ffe6e6')  # Light red for bearish sentiment
            ax.patch.set_alpha(0.15)
            regime_color = '#e53e3e'  # Red for negative sentiment
            regime_text = f"📉 RISK-OFF REGIME ({confidence*100:.0f}% CONFIDENCE)"
        elif regime == 'High Volatility':
            ax.patch.set_facecolor('#fff3cd')  # Light yellow for high volatility
            ax.patch.set_alpha(0.2)
            regime_color = '#f6ad55'  # Orange for volatility
            regime_text = f"⚠️ HIGH VOLATILITY REGIME ({confidence*100:.0f}% CONFIDENCE)"
        elif regime == 'Range-Bound':
            ax.patch.set_facecolor('#f0fff4')  # Light mint for range-bound
            ax.patch.set_alpha(0.1)
            regime_color = '#38b2ac'  # Teal for range-bound
            regime_text = f"↔️ RANGE-BOUND REGIME ({confidence*100:.0f}% CONFIDENCE)"
        else:
            ax.patch.set_facecolor('#f7fafc')  # Light blue for normal market
            ax.patch.set_alpha(0.1)
            regime_color = '#4299e1'  # Blue for neutral
            regime_text = f"🔵 NORMAL MARKET REGIME ({confidence*100:.0f}% CONFIDENCE)"
        
        # Add comprehensive regime annotation with institutional commentary
        regime_annotation = f"{regime_text}\n\n{commentary}\n\nPrimary Driver: {driver}"
        
        ax.text(0.02, 0.98, 
               regime_annotation,
               transform=ax.transAxes,
               verticalalignment='top',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9, edgecolor=regime_color, linewidth=1.5),
               fontsize=8,
               color=regime_color,
               weight='bold',
               linespacing=1.2)
    
    def _add_watermark(self, fig):
        """
        Add institutional watermark to figure
        
        Args:
            fig: Matplotlib figure
        """
        fig.text(0.5, 0.5, self.config.watermark_text,
                fontsize=20, color='gray', alpha=0.1, ha='center', va='center',
                rotation=45, weight='bold')
    
    def _add_institutional_footer(self, fig):
        """
        Add institutional footer to figure
        
        Args:
            fig: Matplotlib figure
        """
        # Add confidentiality notice
        fig.text(0.02, 0.02, self.config.confidentiality_level,
                fontsize=8, color='gray', alpha=0.7)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        fig.text(0.98, 0.02, f"Generated: {timestamp}",
                fontsize=8, color='gray', alpha=0.7, ha='right')
    
    def save_institutional_chart(self, fig: plt.Figure, filename: str, 
                                 format: str = 'png') -> str:
        """
        Save chart with institutional formatting
        
        Args:
            fig: Matplotlib figure
            filename: Output filename
            format: File format (default 'png')
            
        Returns:
            Saved filename
        """
        # Ensure tight layout
        fig.tight_layout()
        
        # Save with high quality
        output_filename = f"{filename}.{format}"
        fig.savefig(output_filename, 
                   dpi=self.config.dpi,
                   bbox_inches='tight',
                   facecolor='white',
                   edgecolor='none')
        
        return output_filename

# Example usage
if __name__ == "__main__":
    # Create sample data for testing
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    sample_data = pd.DataFrame({
        'close': np.random.randn(100).cumsum() + 100,
        'volume': np.random.randint(1000, 10000, 100),
        'sma_20': np.random.randn(100).cumsum() + 100,
        'sma_50': np.random.randn(100).cumsum() + 100,
        'rsi': np.random.randint(30, 70, 100)
    }, index=dates)
    
    # Create sample correlation matrix
    assets = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD']
    corr_data = np.random.rand(4, 4)
    corr_data = (corr_data + corr_data.T) / 2  # Make symmetric
    np.fill_diagonal(corr_data, 1)  # Diagonal = 1
    correlation_matrix = pd.DataFrame(corr_data, index=assets, columns=assets)
    
    # Create sample risk metrics
    risk_metrics = {
        'sharpe_ratio': 1.25,
        'sortino_ratio': 1.85,
        'max_drawdown': -0.15,
        'volatility_annualized': 0.22,
        'value_at_risk_95': -0.035,
        'conditional_var_95': -0.052,
        'beta': 1.15,
        'alpha': 0.02
    }
    
    # Initialize visualizer
    visualizer = EnhancedInstitutionalVisualizer()
    
    # Create professional price chart
    print("Creating professional price chart...")
    price_fig = visualizer.create_professional_price_chart(
        sample_data, 
        "EURUSD",
        annotations={
            'breakouts': [{'date': dates[50], 'level': sample_data['close'].iloc[50]}],
            'support_levels': [95, 90],
            'resistance_levels': [105, 110]
        },
        regime_info={'regime': 'Risk-On', 'confidence': 0.85}
    )
    visualizer.save_institutional_chart(price_fig, 'institutional_price_chart')
    plt.close(price_fig)
    print("✓ Professional price chart saved as 'institutional_price_chart.png'")
    
    # Create correlation heatmap
    print("Creating correlation heatmap...")
    corr_fig = visualizer.create_correlation_heatmap(correlation_matrix, "FX Correlation Matrix")
    visualizer.save_institutional_chart(corr_fig, 'correlation_heatmap')
    plt.close(corr_fig)
    print("✓ Correlation heatmap saved as 'correlation_heatmap.png'")
    
    # Create risk metrics dashboard
    print("Creating risk metrics dashboard...")
    risk_fig = visualizer.create_risk_metrics_dashboard(risk_metrics, "EURUSD")
    visualizer.save_institutional_chart(risk_fig, 'risk_metrics_dashboard')
    plt.close(risk_fig)
    print("✓ Risk metrics dashboard saved as 'risk_metrics_dashboard.png'")
    
    print("\n🎉 All institutional visualizations created successfully!")