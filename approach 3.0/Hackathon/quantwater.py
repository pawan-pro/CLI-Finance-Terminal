import click
import os
import sys
import duckdb 
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from datetime import datetime, timedelta

# Suppress library warnings
import warnings
warnings.filterwarnings("ignore")

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from analytics.metrics_engine import MarketPulse
from ai.research_copilot import ResearchCopilot

console = Console()

@click.group()
def cli():
    """🌊 Quantwater Terminal: Institutional AI Workstation"""
    pass

@cli.command()
def pulse():
    """📊 Heatmap: Top 15 Market Movers by Magnitude."""
    df = MarketPulse().get_snapshot(limit=15)
    render_table(df, "Market Pulse [High Velocity]")

@cli.command()
def board():
    """📈 Overall Board: All assets sorted by absolute movement."""
    # We sort the entire dataframe by return magnitude for the main board
    df = MarketPulse().get_snapshot(limit=100)
    if not df.empty:
        df = df.sort_values(by='return_magnitude', ascending=False)
    render_table(df, "Quantwater Master Board [Sorted by Velocity]")

@cli.command()
def sector():
    """🏢 Sector View: Performance grouped by Asset Class (Priority Flow)."""
    df = MarketPulse().get_snapshot(limit=200)
    if df.empty: 
        console.print("[yellow]Empty Data Lake.[/yellow]")
        return
    
    # We use the 'sector_priority' column to determine the order of the tables
    # Priority: 1.INDEX, 2.METALS, 3.FX, 4.CRYPTO, 5.STOCK
    priorities = sorted(df['sector_priority'].unique())
    
    for p in priorities:
        class_df = df[df['sector_priority'] == p].sort_values(by='return_24h', ascending=False)
        if class_df.empty: continue
        
        a_class = class_df['asset_class'].iloc[0]
        render_table(class_df, f"Sector: {a_class}")
        console.print(" ")

@cli.command()
@click.option('--impact', default='High', help='High/Medium/Low')
def calendar(impact):
    """📅 Calendar: Macro triggers (IST)."""
    db_path = os.path.join(os.path.dirname(__file__), "data/silver/market_data.duckdb")
    conn = duckdb.connect(db_path)
    df = conn.execute(f"SELECT * FROM economic_events WHERE impact = '{impact}' ORDER BY time_utc DESC LIMIT 15").df()
    
    table = Table(title=f"Macro Calendar [{impact} Impact]", style="yellow")
    table.add_column("Time (IST)", style="cyan")
    table.add_column("Event", style="white")
    table.add_column("Actual", justify="right")
    table.add_column("Forecast", justify="right")

    for _, row in df.iterrows():
        ist = row['time_utc'] + timedelta(hours=5, minutes=30)
        
        # FIXED: Clean up 'nan' for a professional look
        actual = f"[green]{row['actual']}[/green]" if pd.notnull(row['actual']) else "[dim]---[/dim]"
        forecast = str(row['forecast']) if pd.notnull(row['forecast']) else "---"
        
        table.add_row(ist.strftime('%H:%M %d %b'), row['event_name'], actual, forecast)
    
    console.print(table)
    conn.close()

@cli.command()
def research():
    """🤖 Research: Gemini 3 Intelligence Synthesis."""
    with console.status("[bold cyan]Consulting Quantwater Knowledge Graph..."):
        try:
            copilot = ResearchCopilot()
            note = copilot.generate_intelligence_note()
            console.print(Panel(note, title="[bold yellow]QUANTWATER RESEARCH[/bold yellow]", border_style="yellow"))
        except Exception as e:
            console.print(f"[bold red]AI Error:[/bold red] {e}")

def render_table(df, title):
    if df.empty: return
        
    table = Table(title=title, style="bold magenta")
    table.add_column("Symbol", style="cyan", width=12)
    table.add_column("Price", justify="right", width=10)
    table.add_column("Return %", justify="right", width=10)
    table.add_column("Last Sync (IST)", justify="center", width=16)
    table.add_column("Reference Time", justify="center", style="dim", width=16)

    for _, row in df.iterrows():
        color = "green" if row['return_24h'] > 0 else "red"
        fmt = "%H:%M %d %b"
        
        # Dynamic precision
        price_val = f"{row['last_price']:.2f}" if row['last_price'] > 10 else f"{row['last_price']:.4f}"
        
        table.add_row(
            row['symbol'], 
            price_val, 
            f"[{color}]{row['return_24h']:+.2f}%[/{color}]", 
            row['sync_ist'].strftime(fmt),
            row['reference_ist'].strftime(fmt)
        )
    console.print(table)

if __name__ == "__main__":
    cli()