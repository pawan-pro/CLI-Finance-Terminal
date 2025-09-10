from rich.table import Table
from rich.text import Text

def format_sector_performance(sector_data: dict) -> Table:
    """Formats sector performance data into a Rich table."""

    table = Table(title="Sector Performance", show_header=True, header_style="bold magenta")
    table.add_column("Rank", style="dim")
    table.add_column("Sector")
    table.add_column("Change", justify="right")

    ranks = [key for key in sector_data.keys() if "Rank" in key]

    for rank_key in sorted(ranks):
        rank_title = rank_key.split(": ")[1]
        table.add_row(f"[bold]{rank_title}[/bold]", "", "")

        sector_performance = sector_data[rank_key]
        for sector, change in sector_performance.items():
            change_val = float(change.strip('%'))
            color = "green" if change_val >= 0 else "red"
            table.add_row("", sector, Text(change, style=color))

        if rank_key != ranks[-1]:
             table.add_row("---", "---", "---") # separator

    return table
