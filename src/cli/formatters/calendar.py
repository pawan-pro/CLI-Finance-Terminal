from rich.table import Table
from rich.console import Group
from src.data.models.economic_event import EconomicEvent

def format_economic_calendar(calendar_data: list[EconomicEvent]) -> Group:
    """Formats economic calendar data into a Rich table."""

    if not calendar_data:
        return Group("No economic calendar data found.", style="bold red")

    table = Table(title="Economic Calendar", show_header=True, header_style="bold magenta")
    table.add_column("Date", style="dim", width=12)
    table.add_column("Time", style="dim", width=8)
    table.add_column("Event", width=35)
    table.add_column("Currency", justify="center", width=8)
    table.add_column("Importance", justify="center", width=10)
    table.add_column("Forecast", justify="right", width=10)
    table.add_column("Previous", justify="right", width=10)

    for event in calendar_data:
        # Map importance level to text
        importance_text = {1: "Low", 2: "Medium", 3: "High"}.get(event.importance, "Unknown")
        
        table.add_row(
            event.date,
            event.time_ist,
            event.event_name,
            event.currency,
            importance_text,
            event.forecast,
            event.previous,
        )

    return Group(table)
