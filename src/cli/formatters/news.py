from rich.panel import Panel
from rich.text import Text
from rich.console import Group
from datetime import datetime

def format_news(articles: list[dict]) -> Group:
    """Formats a list of news articles into a Rich Group."""

    if not articles:
        return Group(Text("No news articles found.", style="bold red"))

    panels = []
    for article in articles:
        title = article.get("title", "No Title")
        source = article.get("source", {}).get("name", "N/A")
        published_at = article.get("publishedAt", "")

        # Format the date
        try:
            if published_at:
                date_obj = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                published_at_str = date_obj.strftime("%Y-%m-%d %H:%M")
            else:
                published_at_str = "N/A"
        except:
            published_at_str = published_at # Keep original string if parsing fails

        panel_content = Text()
        panel_content.append(f"{title}\n", style="bold")
        panel_content.append(f"Source: {source} | Published: {published_at_str}", style="dim")

        panels.append(Panel(panel_content, border_style="cyan"))

    return Group(*panels)
