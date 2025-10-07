import typer
from rich.console import Console

console = Console()

def chart(symbol: str):
    """
    Generate charts for a given symbol.
    """
    console.print(f"[bold yellow]Chart generation for {symbol} is not implemented yet.[/bold yellow]")
    console.print("[bold yellow]The system currently uses pre-generated charts from CSV data.[/bold yellow]")