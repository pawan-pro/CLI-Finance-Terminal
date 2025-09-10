import typer
from rich.console import Console
from src.data.providers.news import NewsAPI
from src.cli.formatters.news import format_news
from src.config.settings import settings

console = Console()

def news():
    """
    Display top financial news headlines.
    """
    try:
        client = NewsAPI()
    except ValueError as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        raise typer.Exit(code=1)

    max_headlines = settings.get("features", {}).get("max_headlines", 5)

    with console.status("[bold green]Fetching news headlines...", spinner="dots"):
        articles = client.get_top_headlines(page_size=max_headlines)

    if articles:
        news_group = format_news(articles)
        console.print(news_group)
    else:
        console.print("[bold red]Could not retrieve news headlines.[/bold red]")
