import typer
from rich.console import Console
import pandas as pd
from src.analysis.daily_report import DailyInvestmentReportGenerator
from src.cli.formatters.calendar import format_economic_calendar
from src.data.models.economic_event import EconomicEvent

console = Console()

def calendar():
    """
    Display the economic calendar.
    """
    try:
        # Initialize report generator with Alpha Vantage data provider
        report_gen = DailyInvestmentReportGenerator()
    except Exception as e:
        console.print(f"[bold red]Error initializing report generator: {e}[/bold red]")
        raise typer.Exit(code=1)

    with console.status("[bold green]Fetching economic calendar... (CSV-based data)", spinner="dots"):
        calendar_df = report_gen.get_economic_calendar()

    if not calendar_df.empty:
        # Convert DataFrame to list of EconomicEvent objects
        calendar_data = []
        for _, row in calendar_df.iterrows():
            # Handle time formatting
            time_str = ""
            if 'Time' in row:
                time_obj = row['Time']
                if hasattr(time_obj, 'strftime'):
                    time_str = time_obj.strftime("%H:%M")
                elif isinstance(time_obj, str):
                    # Try to parse the time from string
                    try:
                        from datetime import datetime
                        time_parsed = datetime.strptime(time_obj.split()[-1], "%H:%M")
                        time_str = time_parsed.strftime("%H:%M")
                    except:
                        time_str = str(time_obj)
            
            # Handle importance mapping
            importance_map = {
                'High': 3,
                'Medium': 2,
                'Low': 1,
                'None': 1
            }
            importance = 1
            if 'Impact' in row:
                impact = str(row['Impact']).strip()
                importance = importance_map.get(impact, 1)
            
            # Handle date extraction from Time column
            date_str = ''
            if 'Time' in row and pd.notna(row['Time']):
                date_str = row['Time'].strftime('%Y-%m-%d')
            
            # Create EconomicEvent object
            event = EconomicEvent(
                date=date_str,
                time_ist=time_str,
                currency=row.get('Currency', ''),
                event_name=row.get('Name', ''),
                importance=importance,
                forecast=str(row.get('Forecast', '')) if pd.notna(row.get('Forecast', '')) else '',
                previous=str(row.get('Previous', '')) if pd.notna(row.get('Previous', '')) else '',
                notes=f"Country: {row.get('Country', '')}" if 'Country' in row else ''
            )
            calendar_data.append(event)
        
        calendar_group = format_economic_calendar(calendar_data)
        console.print(calendar_group)
    else:
        console.print("[bold red]Could not retrieve economic calendar.[/bold red]")
