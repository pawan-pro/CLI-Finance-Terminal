import typer
from rich.console import Console
from datetime import datetime
from src.cli.formatters.status import format_market_status

console = Console()

def status():
    """
    Display the current market status (based on typical US market hours).
    """
    console.print("[bold green]Fetching market status...[/bold green]")

    # This is a simplified, placeholder implementation as Alpha Vantage
    # does not provide a direct market status endpoint for all markets.
    now = datetime.now()
    is_open = (now.weekday() < 5) and (datetime.strptime("09:30", "%H:%M").time() <= now.time() <= datetime.strptime("16:00", "%H:%M").time())

    status_data = {
        "markets": [
            {
                "market_type": "Equity",
                "region": "United States",
                "primary_exchanges": "NYSE, NASDAQ",
                "current_status": "open" if is_open else "closed",
                "notes": "Based on typical US market hours (9:30 AM - 4:00 PM ET)."
            }
        ]
    }

    status_table = format_market_status(status_data)
    console.print(status_table)