from rich.table import Table
from rich.console import Group

def format_economic_calendar(calendar_data: list[dict]) -> Group:
    """Formats economic calendar data into a Rich table."""

    if not calendar_data:
        return Group("No economic calendar data found.", style="bold red")

    table = Table(title="Economic Calendar", show_header=True, header_style="bold magenta")
    table.add_column("Date", style="dim", width=10)
    table.add_column("Time (IST)", style="dim", width=10)
    table.add_column("Event", width=40)
    table.add_column("Currency", justify="right")
    table.add_column("Forecast", justify="right")
    table.add_column("Previous", justify="right")

    for event in calendar_data:
        table.add_row(
            event.date,
            event.time_ist,
            event.event_name,
            event.currency,
            event.forecast,
            event.previous,
        )

    return Group(table)
