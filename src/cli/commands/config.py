import typer
from rich.console import Console
import yaml
from pathlib import Path

app = typer.Typer()
console = Console()

CONFIG_DIR = Path("config")
USER_CONFIG_PATH = CONFIG_DIR / "user.yaml"

def load_user_config():
    """Loads the user configuration."""
    if not USER_CONFIG_PATH.exists():
        return {}
    with open(USER_CONFIG_PATH, "r") as f:
        return yaml.safe_load(f) or {}

def save_user_config(config: dict):
    """Saves the user configuration."""
    CONFIG_DIR.mkdir(exist_ok=True)
    with open(USER_CONFIG_PATH, "w") as f:
        yaml.dump(config, f)

@app.command("add-watchlist")
def add_watchlist(
    symbol: str = typer.Argument(..., help="The stock symbol to add to the watchlist.")
):
    """Add a symbol to the watchlist."""
    config = load_user_config()
    watchlist = config.get("assets", {}).get("watchlist", [])

    if symbol.upper() not in watchlist:
        watchlist.append(symbol.upper())
        if "assets" not in config:
            config["assets"] = {}
        config["assets"]["watchlist"] = watchlist
        save_user_config(config)
        console.print(f"[bold green]Added {symbol.upper()} to the watchlist.[/bold green]")
    else:
        console.print(f"[bold yellow]{symbol.upper()} is already in the watchlist.[/bold yellow]")

@app.command("remove-watchlist")
def remove_watchlist(
    symbol: str = typer.Argument(..., help="The stock symbol to remove from the watchlist.")
):
    """Remove a symbol from the watchlist."""
    config = load_user_config()
    watchlist = config.get("assets", {}).get("watchlist", [])

    if symbol.upper() in watchlist:
        watchlist.remove(symbol.upper())
        config["assets"]["watchlist"] = watchlist
        save_user_config(config)
        console.print(f"[bold green]Removed {symbol.upper()} from the watchlist.[/bold green]")
    else:
        console.print(f"[bold red]{symbol.upper()} not found in the watchlist.[/bold red]")

@app.command("show")
def show_config():
    """Show the current user configuration."""
    config = load_user_config()
    console.print(config)
