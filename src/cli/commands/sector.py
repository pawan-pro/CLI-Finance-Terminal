import typer
from rich.console import Console
from src.data.providers.alpha_vantage import AlphaVantage
from src.cli.formatters.sector import format_sector_performance

console = Console()

def sector():
    """
    Display sector performance data.
    """
    try:
        client = AlphaVantage()
    except ValueError as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        raise typer.Exit(code=1)

    with console.status("[bold green]Fetching sector performance...", spinner="dots"):
        sector_data = client.get_sector_performance()

    if sector_data:
        sector_table = format_sector_performance(sector_data)
        console.print(sector_table)
    else:
        console.print("[bold red]Could not retrieve sector performance data.[/bold red]")
