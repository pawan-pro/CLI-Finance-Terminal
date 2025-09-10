import typer
from rich.console import Console
from src.data.providers.alpha_vantage import AlphaVantage
from src.cli.formatters.status import format_market_status

console = Console()

def status():
    """
    Display the current market status.
    """
    try:
        client = AlphaVantage()
    except ValueError as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        raise typer.Exit(code=1)

    with console.status("[bold green]Fetching market status...", spinner="dots"):
        status_data = client.get_market_status()

    if status_data:
        status_table = format_market_status(status_data)
        console.print(status_table)
    else:
        console.print("[bold red]Could not retrieve market status.[/bold red]")
