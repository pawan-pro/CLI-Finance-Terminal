from rich.table import Table
from rich.text import Text

def format_market_status(status_data: list[dict]) -> Table:
    """Formats market status data into a Rich table."""

    table = Table(title="Market Status", show_header=True, header_style="bold magenta")
    table.add_column("Market", style="dim")
    table.add_column("Region")
    table.add_column("Primary Exchanges")
    table.add_column("Status", justify="right")

    for market in status_data:
        status = market.get("current_status", "N/A")
        color = "green" if status == "open" else "red"

        table.add_row(
            market.get("market_type", "N/A"),
            market.get("region", "N/A"),
            market.get("primary_exchanges", "N/A"),
            Text(status, style=color),
        )

    return table
