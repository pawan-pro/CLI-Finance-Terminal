import click
import os
import sys
import duckdb
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from datetime import datetime, timedelta

import warnings
warnings.filterwarnings("ignore")

# Path injection for internal modules
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
    """📈 Master Board: All assets sorted by absolute velocity."""
    df = MarketPulse().get_snapshot(limit=100)
    if not df.empty:
        df = df.sort_values(by='return_magnitude', ascending=False)
        render_table(df, "Quantwater Master Board [Sorted by Velocity]")

@cli.command()
def sector():
    """🏢 Sector View: Grouped by Institutional Flow Priority."""
    df = MarketPulse().get_snapshot(limit=200)
    if df.empty:
        console.print("[yellow]Empty Data Lake.[/yellow]")
        return

    # Institutional Priority Order
    INSTITUTIONAL_ORDER = ['INDEX', 'METALS', 'FX', 'CRYPTO', 'ENERGY', 'STOCK']
    
    found_classes = df['asset_class'].unique()
    # Add any classes found in data but not in our list
    final_order = [c for c in INSTITUTIONAL_ORDER if c in found_classes]
    final_order += [c for c in found_classes if c not in INSTITUTIONAL_ORDER]

    for a_class in final_order:
        class_df = df[df['asset_class'] == a_class].sort_values(by='return_24h', ascending=False)
        if class_df.empty: continue
        
        render_table(class_df, f"Sector: {a_class}")
        console.print(" ")

@cli.command()
@click.option('--impact', default='High', help='High/Medium/Low')
def calendar(impact):
    """📅 Calendar: IST-normalized macro triggers."""
    db_path = os.path.join(os.path.dirname(__file__), "data/silver/market_data.duckdb")
    conn = duckdb.connect(db_path)
    df = conn.execute(f"SELECT * FROM economic_events WHERE impact = '{impact}' ORDER BY time_utc DESC LIMIT 15").df()
    
    table = Table(title=f"Macro Calendar [{impact} Impact]", style="yellow")
    table.add_column("Time (IST)", style="cyan")
    table.add_column("Currency", style="bold white")
    table.add_column("Event", style="white")
    table.add_column("Actual", justify="right")
    table.add_column("Forecast", justify="right")

    for _, row in df.iterrows():
        ist = row['time_utc'] + timedelta(hours=5, minutes=30)
        actual = f"[green]{row['actual']}[/green]" if pd.notnull(row['actual']) and row['actual'] != 0 else "[dim]---[/dim]"
        forecast = str(row['forecast']) if pd.notnull(row['forecast']) and row['forecast'] != 0 else "---"
        table.add_row(
            ist.strftime('%H:%M %d %b'), 
            str(row['currency']), 
            row['event_name'], 
            actual, 
            forecast
        )

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

@cli.command()
@click.argument('cluster') # e.g. python3 quantwater.py thematic ai
def thematic(cluster):
    """🔥 Thematic Clusters: [ai / metals / energy]"""
    clusters = {
        "ai": ["NVIDIA", "Microsoft", "Alphabet", "Apple", "Tesla", "Amazon", "Facebook"],
        "metals": ["XAUUSD.sd", "XAGUSD.sd", "XPTUSD.sd"],
        "energy": ["USOILRoll", "UKOILRoll", "Exxon", "Chevron"]
    }
    
    target_list = clusters.get(cluster.lower())
    if not target_list:
        console.print(f"[red]Cluster {cluster} not found.[/red]")
        return
        
    df = MarketPulse().get_snapshot(limit=200)
    filtered = df[df['symbol'].isin(target_list)]
    
    render_table(filtered, f"Thematic Deep-Dive: {cluster.upper()}")

def render_table(df, title):
    if df.empty: return
    
    table = Table(title=title, style="bold magenta", header_style="bold white")
    table.add_column("Symbol", style="cyan", width=14)
    table.add_column("Price", justify="right", width=12)
    table.add_column("Return %", justify="right", width=10)
    table.add_column("Last Sync (IST)", justify="center", width=16)
    table.add_column("Status", justify="center", width=10)

    for _, row in df.iterrows():
        color = "green" if row['return_24h'] > 0 else "red"
        status_color = "green" if row['status'] == 'LIVE' else "dim red"
        fmt = "%H:%M %d %b"
        
        price_val = f"{row['last_price']:.2f}" if row['last_price'] > 10 else f"{row['last_price']:.4f}"
        
        table.add_row(
            row['symbol'], 
            price_val, 
            f"[{color}]{row['return_24h']:+.2f}%[/{color}]", 
            row['sync_ist'].strftime(fmt),
            f"[{status_color}]{row['status']}[/{status_color}]"
        )
    console.print(table)

if __name__ == "__main__":
    cli()