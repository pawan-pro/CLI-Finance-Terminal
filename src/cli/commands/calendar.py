import typer
from rich.console import Console
from src.data.providers.quantwater import QuantwaterScraper
from src.cli.formatters.calendar import format_economic_calendar

console = Console()

def calendar():
    """
    Display the economic calendar.
    """
    try:
        client = QuantwaterScraper()
    except Exception as e:
        console.print(f"[bold red]Error initializing scraper: {e}[/bold red]")
        raise typer.Exit(code=1)

    with console.status("[bold green]Fetching economic calendar from Quantwater.tech...", spinner="dots"):
        calendar_data = client.get_economic_calendar()

    if calendar_data:
        calendar_group = format_economic_calendar(calendar_data)
        console.print(calendar_group)
    else:
        console.print("[bold red]Could not retrieve economic calendar.[/bold red]")
