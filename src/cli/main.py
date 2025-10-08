import typer
from rich.console import Console
from src.cli.commands.quote import quote
from src.cli.commands.news import news
from src.cli.commands.calendar import calendar
from src.cli.commands.status import status
from src.cli.commands.sector import sector
from src.cli.commands.report import generate as report_generate
from src.cli.commands import config as config_command
from src.data.providers.alphavantage_data import AlphaVantageDataFetcher
from src.cli.formatters.dashboard import format_dashboard
from src.config.settings import settings

app = typer.Typer(
    name="finterm",
    help="A CLI for finance.",
)

console = Console()

# Add commands
app.command("quote")(quote)
app.command("news")(news)
app.command("calendar")(calendar)
app.command("status")(status)
app.command("sector")(sector)
app.command("report")(report_generate)
app.add_typer(config_command.app, name="config")

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """
    Finance Terminal CLI. Shows a dashboard by default.
    """
    if ctx.invoked_subcommand is None:
        dashboard()

@app.command(name="dashboard")
def dashboard():
    """
    Show a comprehensive daily market report.
    """
    console.print("[bold cyan]Welcome to the Finance Terminal![/bold cyan]")

    try:
        client = AlphaVantageDataFetcher()
    except ValueError as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        raise typer.Exit(code=1)

    with console.status("[bold green]Fetching market data...", spinner="dots"):
        # Use watchlist from settings or provide defaults
        symbols = settings.get("assets", {}).get("watchlist", [])
        if not symbols:
            console.print("[yellow]No symbols in watchlist. Using defaults.[/yellow]")
            symbols = ['US500Roll', 'US30Roll', 'EURUSD', 'BTCUSD']

        data = {}
        for symbol in symbols:
            quote = client.get_global_quote(symbol)
            if quote:
                # Structure data to be compatible with the existing formatter
                data[symbol] = {
                    '01. symbol': quote.get('symbol'),
                    '05. price': quote.get('price'),
                    '10. change percent': str(quote.get('change_percent')) + '%'
                }

    # Format and display
    if data:
        dashboard_group = format_dashboard(data)
        console.print(dashboard_group)
    else:
        console.print("[bold red]Could not retrieve dashboard data.[/bold red]")


if __name__ == "__main__":
    app()