import typer
from rich.console import Console
from src.data.providers.alpha_vantage import AlphaVantage
from src.analysis.charts import generate_chart

console = Console()

def chart(
    symbol: str = typer.Argument(..., help="The stock symbol to chart."),
):
    """
    Display an ASCII price chart for a given stock symbol.
    """
    try:
        client = AlphaVantage()
    except ValueError as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        raise typer.Exit(code=1)

    with console.status(f"[bold green]Fetching historical data for {symbol}...", spinner="dots"):
        historical_data = client.get_historical_data(symbol)

    if historical_data:
        # The data is returned with the most recent date first. Reverse it for charting.
        dates = list(historical_data.keys())
        dates.reverse()
        prices = [float(day_data["4. close"]) for day_data in reversed(historical_data.values())]

        chart_str = generate_chart(dates, prices)
        console.print(f"\n[bold green]Price Chart for {symbol}[/bold green]")
        console.print(chart_str)
    else:
        console.print(f"[bold red]Could not retrieve historical data for {symbol}.[/bold red]")
