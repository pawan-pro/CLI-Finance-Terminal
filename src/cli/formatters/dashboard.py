from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

def format_dashboard(data: dict) -> Group:
    """Formats the entire dashboard data into a Rich Group."""

    # Indices
    indices_table = Table(title="Watchlist", show_header=True, header_style="bold magenta")
    indices_table.add_column("Symbol", style="dim")
    indices_table.add_column("Price", justify="right")
    indices_table.add_column("Change", justify="right")
    indices_table.add_column("Change %", justify="right")

    watchlist_symbols = [s for s in data.keys() if s not in ["USD/EUR", "USD/JPY", "10Y Treasury", "BTC", "DXY"]]

    for symbol in watchlist_symbols:
        quote = data.get(symbol)
        if quote:
            price = float(quote.get("05. price", 0))
            change = float(quote.get("09. change", 0))
            change_percent_str = quote.get("10. change percent", "0%")
            change_percent = float(change_percent_str.strip('%'))
            color = "green" if change >= 0 else "red"
            indices_table.add_row(
                symbol,
                f"${price:.2f}",
                Text(f"{change:+.2f}", style=color),
                Text(f"{change_percent:+.2f}%", style=color),
            )

    # Commodities
    commodities_table = Table(title="Commodities", show_header=True, header_style="bold magenta")
    commodities_table.add_column("Asset", style="dim")
    commodities_table.add_column("Price", justify="right")

    if data.get("GLD"):
        gld_price = float(data["GLD"].get("05. price", 0))
        commodities_table.add_row("Gold (GLD)", f"${gld_price:.2f}")
    if data.get("USO"):
        uso_price = float(data["USO"].get("05. price", 0))
        commodities_table.add_row("Oil (USO)", f"${uso_price:.2f}")
    if data.get("BTC"):
        btc_price = float(data["BTC"].get("05. price", 0))
        commodities_table.add_row("Bitcoin (BTC)", f"${btc_price:,.2f}")

    # Forex & Bonds
    other_table = Table(title="Forex & Bonds", show_header=True, header_style="bold magenta")
    other_table.add_column("Asset", style="dim")
    other_table.add_column("Value", justify="right")

    if data.get("USD/EUR"):
        eur_rate = float(data["USD/EUR"].get("5. Exchange Rate", 0))
        other_table.add_row("USD/EUR", f"{eur_rate:.4f}")
    if data.get("USD/JPY"):
        jpy_rate = float(data["USD/JPY"].get("5. Exchange Rate", 0))
        other_table.add_row("USD/JPY", f"{jpy_rate:.2f}")
    if data.get("DXY"):
        dxy_price = float(data["DXY"].get("05. price", 0))
        other_table.add_row("DXY (UUP)", f"{dxy_price:.2f}")
    if data.get("10Y Treasury"):
        yield_val = float(data["10Y Treasury"].get("value", 0))
        other_table.add_row("10Y Treasury Yield", f"{yield_val:.2f}%")


    return Group(
        Panel(indices_table, expand=False),
        Panel(commodities_table, expand=False),
        Panel(other_table, expand=False),
    )
