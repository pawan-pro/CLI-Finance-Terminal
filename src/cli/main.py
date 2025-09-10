import typer
from rich.console import Console
from src.cli.commands.quote import quote
from src.cli.commands.chart import chart
from src.cli.commands.news import news
from src.cli.commands.calendar import calendar
from src.cli.commands.status import status
from src.cli.commands.sector import sector
from src.cli.commands import config as config_command
from src.data.providers.alpha_vantage import AlphaVantage
from src.cli.formatters.dashboard import format_dashboard
from src.config.settings import settings

app = typer.Typer(
    name="finterm",
    help="A CLI for finance.",
)

console = Console()

# Add commands
app.command("quote")(quote)
app.command("chart")(chart)
app.command("news")(news)
app.command("calendar")(calendar)
app.command("status")(status)
app.command("sector")(sector)
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
        client = AlphaVantage()
    except ValueError as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        raise typer.Exit(code=1)

    with console.status("[bold green]Fetching market data...", spinner="dots"):
        # Use watchlist from settings
        symbols = settings["assets"]["watchlist"]

        # Fetch all data
        data = client.get_dashboard_data(symbols)
        data["USD/EUR"] = client.get_forex_rate("USD", "EUR")
        data["USD/JPY"] = client.get_forex_rate("USD", "JPY")
        data["10Y Treasury"] = client.get_treasury_yield()

        # Map BTC-USD to BTC and UUP to DXY for the formatter
        if data.get("BTC-USD"):
            data["BTC"] = data["BTC-USD"]
        if data.get("UUP"):
            data["DXY"] = data["UUP"]

    # Format and display
    if data:
        dashboard_group = format_dashboard(data)
        console.print(dashboard_group)
    else:
        console.print("[bold red]Could not retrieve dashboard data.[/bold red]")


if __name__ == "__main__":
    app()
