from rich.table import Table
from rich.text import Text

def format_quote_data(data: dict) -> Table:
    """Formats a single stock quote into a Rich table."""

    symbol = data.get("01. symbol", "N/A")
    price = float(data.get("05. price", 0))
    change = float(data.get("09. change", 0))
    change_percent_str = data.get("10. change percent", "0%")
    change_percent = float(change_percent_str.strip('%'))

    # Determine color based on change
    color = "green" if change >= 0 else "red"

    table = Table(
        title=f"[bold cyan]Quote for {symbol}[/bold cyan]",
        show_header=True,
        header_style="bold magenta"
    )

    table.add_column("Metric", style="dim", width=20)
    table.add_column("Value", justify="right")

    table.add_row("Price", f"${price:.2f}")

    change_text = Text(f"{change:+.2f}", style=color)
    table.add_row("Change", change_text)

    change_percent_text = Text(f"{change_percent:+.2f}%", style=color)
    table.add_row("Change Percent", change_percent_text)

    table.add_row("Open", f"${float(data.get('02. open', 0)):.2f}")
    table.add_row("High", f"${float(data.get('03. high', 0)):.2f}")
    table.add_row("Low", f"${float(data.get('04. low', 0)):.2f}")
    table.add_row("Volume", f"{int(data.get('06. volume', 0)):,}")
    table.add_row("Latest Trading Day", data.get("07. latest trading day", "N/A"))

    return table
