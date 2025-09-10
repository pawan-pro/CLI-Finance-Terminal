import typer
from rich.console import Console
from src.data.providers.alpha_vantage import AlphaVantage
from src.cli.formatters.quote import format_quote_data

console = Console()

def quote(
    symbols: list[str] = typer.Argument(..., help="One or more stock symbols to get quotes for.")
):
    """
    Get real-time quotes for one or more stock symbols.
    """
    try:
        client = AlphaVantage()
    except ValueError as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        raise typer.Exit(code=1)

    with console.status("[bold green]Fetching quotes...", spinner="dots") as status:
        for symbol in symbols:
            status.update(f"[bold green]Fetching quote for {symbol}...")
            quote_data = client.get_quote(symbol)

            # The get_quote method returns a dict {symbol: data}
            data = quote_data.get(symbol)

            if data:
                table = format_quote_data(data)
                console.print(table)
            else:
                console.print(f"[bold red]Could not retrieve quote for {symbol}. It might be an invalid symbol or an API error.[/bold red]")
