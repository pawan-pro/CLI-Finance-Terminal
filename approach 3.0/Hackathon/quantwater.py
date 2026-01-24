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

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from analytics.metrics_engine import MarketPulse
from ai.research_copilot import ResearchCopilot

console = Console()
DB_PATH = "/Users/pawan/CLI-Finance-Terminal/approach 3.0/Hackathon/data/silver/market_data.duckdb"

def generate_sparkline(data):
    """Generates a crisp 10-character ASCII trendline."""
    if not data or len(data) < 2: return "───"
    chars = " ▂▃▄▅▆▇█"
    mn, mx = min(data), max(data)
    if mx == mn: return "───"
    return "".join([chars[int(((v - mn) / (mx - mn)) * 7)] for v in data])

@click.group()
def cli():
    """🌊 Quantwater Terminal: Institutional AI Workstation"""
    pass

@cli.command()
def board():
    """📈 Master Board: All assets."""
    df = MarketPulse().get_snapshot()
    if not df.empty:
        # Rename columns to match expected names in the rest of the code
        df = df.rename(columns={'name': 'friendly_name', 'price': 'display_price', 'change_24h': 'return_24h'})
        # Sort by absolute value of return_24h (magnitude) in descending order
        df = df.sort_values(by='return_24h', key=abs, ascending=False)
        render_table(df, "Quantwater Master Board")

@cli.command()
def sector():
    """🏢 Sector View: Priority Flow."""
    df = MarketPulse().get_snapshot()
    # Rename columns to match expected names in the rest of the code
    df = df.rename(columns={'name': 'friendly_name', 'price': 'display_price', 'change_24h': 'return_24h'})
    order = ['BONDS', 'INDEX', 'SECTORS', 'METALS', 'FX', 'CRYPTO', 'STOCK']
    for a_class in [o for o in order if o in df['asset_class'].unique()]:
        render_table(df[df['asset_class'] == a_class], f"Sector Group: {a_class}")

@cli.command()
def bonds():
    """🏦 Fixed Income: Treasury Yield Estimates."""
    engine = MarketPulse()
    df = engine.get_snapshot()
    # Rename columns to match expected names in the rest of the code
    df = df.rename(columns={'name': 'friendly_name', 'price': 'display_price', 'change_24h': 'return_24h'})
    bond_df = df[df['asset_class'] == 'BONDS'].sort_values(by='symbol')

    table = Table(title="Calibrated Fixed Income [Yield %]", style="bold green")
    table.add_column("Symbol", style="cyan")
    table.add_column("Name", style="white")
    table.add_column("Est. Yield", justify="right", style="bold yellow")
    table.add_column("24H (Price %)", justify="right")
    table.add_column("Trend", justify="center")

    for _, row in bond_df.iterrows():
        color = "green" if row['return_24h'] > 0 else "red"
        table.add_row(
            row['symbol'], row['friendly_name'],
            f"{row['display_price']:.3f}%",
            f"[{color}]{row['return_24h']:+.2f}%[/{color}]",
            generate_sparkline(engine.get_sparkline_data(row['symbol']))
        )
    console.print(table)

@cli.command()
def sectors():
    """🏢 Sectors: Detailed Industry Performance."""
    df = MarketPulse().get_snapshot()
    # Rename columns to match expected names in the rest of the code
    df = df.rename(columns={'name': 'friendly_name', 'price': 'display_price', 'change_24h': 'return_24h'})
    render_table(df[df['asset_class'] == 'SECTORS'], "Industry Benchmarks")

@cli.command()
def research():
    """🤖 Research: Gemini 1.5 Synthesis."""
    with console.status("[bold cyan]Consulting Knowledge Graph..."):
        try:
            copilot = ResearchCopilot()
            note = copilot.generate_intelligence_note()
            console.print(Panel(note, title="[bold yellow]QUANTWATER RESEARCH[/bold yellow]", border_style="yellow"))
        except Exception as e:
            console.print(f"[bold red]AI Error:[/bold red] {e}")

@cli.command()
@click.option('--impact', default='High')
def calendar(impact):
    """📅 Calendar: Macro triggers."""
    conn = duckdb.connect(DB_PATH)
    try:
        df = conn.execute(f"SELECT * FROM economic_events WHERE impact = '{impact}' ORDER BY time_utc DESC LIMIT 15").df()
        table = Table(title=f"Macro Calendar [{impact}]", style="yellow")
        table.add_column("Time (IST)"); table.add_column("Event"); table.add_column("Actual")
        for _, row in df.iterrows():
            ist = row['time_utc'] + timedelta(hours=5, minutes=30)
            table.add_row(ist.strftime('%H:%M %d %b'), row['event_name'], str(row['actual']))
        console.print(table)
    except:
        console.print("[red]Calendar empty.[/red]")
    finally: conn.close()

def render_table(df, title):
    if df.empty: return
    # Make sure columns are properly named if not already renamed
    if 'return_24h' not in df.columns and 'change_24h' in df.columns:
        df = df.rename(columns={'name': 'friendly_name', 'price': 'display_price', 'change_24h': 'return_24h'})

    engine = MarketPulse()
    table = Table(title=title, style="magenta")
    table.add_column("Symbol"); table.add_column("Name"); table.add_column("Price/Yield"); table.add_column("Return %"); table.add_column("Trend"); table.add_column("Status")
    for _, row in df.iterrows():
        color = "green" if row['return_24h'] > 0 else "red"
        status_color = "green" if row['status'] == 'LIVE' else "dim red"
        price_val = f"{row['display_price']:.3f}%" if row['asset_class'] == 'BONDS' else f"{row['display_price']:.2f}"
        table.add_row(row['symbol'], row['friendly_name'], price_val, f"[{color}]{row['return_24h']:+.2f}%[/{color}]", generate_sparkline(engine.get_sparkline_data(row['symbol'])), f"[{status_color}]{row['status']}[/]")
    console.print(table)

if __name__ == "__main__":
    cli()