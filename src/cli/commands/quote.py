import typer
from rich.console import Console
from src.data.providers.alphavantage_data import AlphaVantageDataFetcher
from src.cli.formatters.quote import format_quote_data

console = Console()

def quote(
    symbols: list[str] = typer.Argument(..., help="One or more stock symbols to get quotes for.")
):
    """
    Get real-time quotes for one or more stock symbols.
    """
    try:
        # Use the new, consolidated data fetcher
        client = AlphaVantageDataFetcher()
    except ValueError as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        raise typer.Exit(code=1)

    with console.status("[bold green]Fetching quotes...", spinner="dots") as status:
        for symbol in symbols:
            status.update(f"[bold green]Fetching quote for {symbol}...")
            # Use the get_global_quote method, which is now the standard
            quote_data = client.get_global_quote(symbol)

            if quote_data:
                # The new method returns a dictionary directly, which we can format
                # We need to adapt the format_quote_data function or the data passed to it
                # For now, let's create a dictionary that matches the old format expected by the formatter
                formatted_data = {
                    '01. symbol': quote_data.get('symbol'),
                    '05. price': quote_data.get('price'),
                    '09. change': 'N/A', # Not available in the new simplified quote
                    '10. change percent': quote_data.get('change_percent')
                }
                table = format_quote_data(formatted_data)
                console.print(table)
            else:
                console.print(f"[bold red]Could not retrieve quote for {symbol}. It might be an invalid symbol or an API error.[/bold red]")