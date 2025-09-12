import typer
from typing import Optional
from datetime import datetime
import logging

from src.analysis.daily_report import DailyInvestmentReportGenerator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = typer.Typer()

@app.command()
def generate(
    save_dir: str = typer.Option("./reports", help="Directory to save the report"),
    format: str = typer.Option("pdf", help="Report format (txt or pdf)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    wine_mt5: bool = typer.Option(False, "--wine-mt5", help="Use Wine MT5 for data fetching")
):
    """
    Generate a daily investment report
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate format
    if format.lower() not in ["txt", "pdf"]:
        typer.echo(f"❌ Invalid format: {format}. Supported formats: txt, pdf")
        raise typer.Exit(code=1)
    
    try:
        typer.echo(f"Generating daily investment report at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        typer.echo(f"Format: {format.upper()}")
        if wine_mt5:
            typer.echo("Using Wine MT5 for data fetching")
        
        # Initialize report generator
        report_gen = DailyInvestmentReportGenerator(use_wine_mt5=wine_mt5)
        
        # Generate report
        report_path = report_gen.generate_report(save_dir, format)
        
        # Shutdown
        report_gen.shutdown()
        
        typer.echo(f"✅ Daily investment report generated successfully!")
        typer.echo(f"📄 Report saved to: {report_path}")
        
    except Exception as e:
        typer.echo(f"❌ Error generating report: {e}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()