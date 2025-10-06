import typer
from typing import Optional
from datetime import datetime
import logging
import subprocess
import sys
import os

from src.analysis.daily_report import DailyInvestmentReportGenerator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = typer.Typer()

def update_market_data(use_wine: bool = False):
    """Update market data by running data-mt5.py.

    If use_wine is True, run the script under Wine (wine python).
    """
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        data_script_path = os.path.join(project_root, "data", "data-mt5.py")

        # Build command
        if use_wine:
            cmd = ["wine", "python", data_script_path]
        else:
            # use the current python executable to run the script
            cmd = [sys.executable if 'sys' in globals() else 'python', data_script_path]

        logger.info(f"Running data update script: {' '.join(cmd)} (cwd={project_root})")
        result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True)
        logger.info(f"Data update script stdout: {result.stdout}")
        if result.stderr:
            logger.error(f"Data update script stderr: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        logger.error(f"Error running data update script: {e}")
        return False

@app.command()
def generate(
    save_dir: str = typer.Option("./reports", help="Directory to save the report"),
    format: str = typer.Option("pdf", help="Report format (txt or pdf)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    wine_mt5: bool = typer.Option(False, "--wine-mt5", help="Use Wine MT5 for data fetching"),
    institutional_grade: bool = typer.Option(False, "--institutional", "-i", help="Generate institutional-grade report")
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
        report_type = "institutional-grade daily investment report" if institutional_grade else "daily investment report"
        typer.echo(f"Generating {report_type} at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")
        typer.echo(f"Format: {format.upper()}")
        if institutional_grade:
            typer.echo("Institutional-grade report enabled")
        if wine_mt5:
            typer.echo("Using Wine MT5 for data fetching")
        
        # Update market data before generating institutional report
        if institutional_grade:
            typer.echo("Updating market data from MT5...")
            # If user asked to use Wine MT5, run data-mt5.py under wine so it can access the Windows MT5
            success = update_market_data(use_wine=wine_mt5)
            if not success:
                typer.echo("⚠️  Warning: Could not update market data, proceeding with existing data...")
            else:
                typer.echo("✅ Market data updated successfully")
        
        # Initialize report generator
        report_gen = DailyInvestmentReportGenerator(use_wine_mt5=wine_mt5)
        
        # Generate report
        report_path = report_gen.generate_report(save_dir, format, institutional_grade)
        
        # Shutdown
        report_gen.shutdown()
        
        typer.echo(f"✅ Daily investment report generated successfully!")
        typer.echo(f"📄 Report saved to: {report_path}")
        
    except Exception as e:
        typer.echo(f"❌ Error generating report: {e}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
