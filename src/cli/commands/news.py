import typer
from rich.console import Console
from src.data.providers.alphavantage_data import AlphaVantageDataFetcher
from src.cli.formatters.news import format_news
from src.config.settings import settings

console = Console()

def news():
    """
    Display top financial news headlines using Alpha Vantage.
    """
    try:
        client = AlphaVantageDataFetcher()
    except ValueError as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        raise typer.Exit(code=1)

    max_headlines = settings.get("features", {}).get("max_headlines", 10)

    with console.status("[bold green]Fetching news headlines...", spinner="dots"):
        articles = client.get_news_sentiment()

    if articles:
        # The format_news function expects a list of articles with 'title', 'summary', etc.
        # The get_news_sentiment method returns a list of dictionaries that should be compatible.
        news_group = format_news(articles[:max_headlines])
        console.print(news_group)
    else:
        console.print("[bold red]Could not retrieve news headlines.[/bold red]")