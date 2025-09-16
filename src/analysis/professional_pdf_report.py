import pandas as pd
from datetime import datetime
import logging
from typing import Dict, List
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProfessionalPDFReportGenerator:
    """Class to generate professional PDF reports in bulge-bracket investment firm style"""
    
    def __init__(self, filename: str):
        """Initialize PDF generator with professional styling"""
        self.filename = filename
        self.doc = SimpleDocTemplate(
            filename, 
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        self.styles = getSampleStyleSheet()
        self.story = []
        
        # Create professional styles
        self.title_style = ParagraphStyle(
            'ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1,  # Center alignment
            textColor=colors.HexColor("#1a3c6c"),  # Dark blue
            fontName='Helvetica-Bold'
        )
        
        self.subtitle_style = ParagraphStyle(
            'ReportSubtitle',
            parent=self.styles['Heading2'],
            fontSize=18,
            spaceAfter=20,
            spaceBefore=15,
            alignment=1,  # Center alignment
            textColor=colors.HexColor("#1a3c6c"),  # Dark blue
            fontName='Helvetica-Bold'
        )
        
        self.section_style = ParagraphStyle(
            'SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=15,
            spaceBefore=25,
            textColor=colors.HexColor("#2c5282"),  # Medium blue
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=colors.HexColor("#e2e8f0"),  # Light gray
            borderPadding=10
        )
        
        self.executive_summary_style = ParagraphStyle(
            'ExecutiveSummary',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=10,
            leading=14,
            textColor=colors.HexColor("#2d3748"),  # Dark gray
            fontName='Helvetica'
        )
        
        self.normal_style = ParagraphStyle(
            'NormalText',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=8,
            leading=12,
            textColor=colors.black,
            fontName='Helvetica'
        )
        
        self.footer_style = ParagraphStyle(
            'Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            spaceAfter=4,
            textColor=colors.gray,
            fontName='Helvetica'
        )
        
        # Company information
        self.company_name = "Quantwater Tech Investments"
        self.report_title = "DAILY INVESTMENT REPORT"
        self.confidentiality_notice = "CONFIDENTIAL - FOR AUTHORIZED PERSONNEL ONLY"
        
    def add_header_footer(self, canvas, doc):
        """Add header and footer to each page"""
        canvas.saveState()
        
        # Header
        canvas.setFont("Helvetica-Bold", 12)
        canvas.setFillColor(colors.HexColor("#1a3c6c"))
        canvas.drawString(72, 800, self.company_name)
        
        # Footer
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.gray)
        canvas.drawString(72, 36, self.confidentiality_notice)
        canvas.drawRightString(540, 36, f"Page {doc.page}")
        
        canvas.restoreState()
    
    def add_cover_page(self):
        """Add professional cover page"""
        # Company logo placeholder
        self.story.append(Spacer(1, 200))
        
        # Company name
        self.story.append(Paragraph(self.company_name, self.title_style))
        self.story.append(Spacer(1, 20))
        
        # Report title
        self.story.append(Paragraph(self.report_title, self.subtitle_style))
        self.story.append(Spacer(1, 30))
        
        # Date
        report_date = datetime.now().strftime("%B %d, %Y")
        date_style = ParagraphStyle(
            'ReportDate',
            parent=self.styles['Normal'],
            fontSize=14,
            spaceAfter=200,
            alignment=1,  # Center alignment
            textColor=colors.HexColor("#4a5568")
        )
        self.story.append(Paragraph(report_date, date_style))
        
        # Confidentiality notice
        conf_style = ParagraphStyle(
            'Confidentiality',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=20,
            alignment=1,  # Center alignment
            textColor=colors.red
        )
        self.story.append(Paragraph(self.confidentiality_notice, conf_style))
        
        self.story.append(PageBreak())
    
    def add_table_of_contents(self):
        """Add table of contents"""
        self.story.append(Paragraph("TABLE OF CONTENTS", self.section_style))
        
        # In a real implementation, we would dynamically generate TOC
        # For now, we'll add placeholder entries
        toc_entries = [
            "Executive Summary",
            "Market Overview",
            "Major Indices Performance",
            "Currency Markets",
            "Commodities",
            "Volatility Analysis",
            "Top Market Movers",
            "Economic Calendar",
            "Risk Metrics",
            "Market Charts"
        ]
        
        for i, entry in enumerate(toc_entries, 1):
            toc_style = ParagraphStyle(
                'TOCEntry',
                parent=self.styles['Normal'],
                fontSize=10,
                spaceAfter=6,
                leftIndent=20
            )
            self.story.append(Paragraph(f"{i}. {entry}", toc_style))
        
        self.story.append(PageBreak())
    
    def add_title(self, title: str):
        """Add title to the report"""
        self.story.append(Paragraph(title, self.title_style))
        self.story.append(Spacer(1, 12))
    
    def add_executive_summary(self, summary_points: List[str]):
        """Add executive summary section"""
        self.story.append(Paragraph("EXECUTIVE SUMMARY", self.section_style))
        
        for point in summary_points:
            self.story.append(Paragraph(f"• {point}", self.executive_summary_style))
        
        self.story.append(Spacer(1, 12))
    
    def add_section(self, title: str):
        """Add section header"""
        self.story.append(Paragraph(title.upper(), self.section_style))
    
    def add_paragraph(self, text: str):
        """Add paragraph text"""
        self.story.append(Paragraph(text, self.normal_style))
        self.story.append(Spacer(1, 6))
    
    def add_rich_table(self, data: List[List], headers: List[str] = None, column_widths: List[float] = None):
        """Add professionally styled table data"""
        if headers:
            data = [headers] + data
        
        table = Table(data, colWidths=column_widths)
        
        # Table styling
        table_style = TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2c5282")),  # Dark blue header
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),  # Light gray grid
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),  # Right align numeric columns
        ])
        
        table.setStyle(table_style)
        
        self.story.append(table)
        self.story.append(Spacer(1, 15))
    
    def add_image(self, image_path: str, width: float = 6*inch, height: float = 3*inch, caption: str = None):
        """Add image to the report with optional caption"""
        if os.path.exists(image_path):
            img = Image(image_path, width=width, height=height)
            self.story.append(img)
            
            if caption:
                caption_style = ParagraphStyle(
                    'ImageCaption',
                    parent=self.styles['Normal'],
                    fontSize=9,
                    spaceAfter=10,
                    alignment=1,  # Center alignment
                    textColor=colors.HexColor("#4a5568")
                )
                self.story.append(Paragraph(caption, caption_style))
            
            self.story.append(Spacer(1, 12))
        else:
            logger.warning(f"Image not found: {image_path}")
    
    def add_market_overview(self, market_status: Dict, key_indices: pd.DataFrame):
        """Add market overview section"""
        self.add_section("Market Overview")
        
        # Market status information
        status_text = f"Markets are currently <b>{market_status.get('status', 'Unknown').upper()}</b> as of {market_status.get('timestamp', 'N/A')} ({market_status.get('timezone', 'N/A')} timezone)."
        self.add_paragraph(status_text)
        
        # Key indices performance summary
        if not key_indices.empty:
            self.add_paragraph("Key market indices performance:")
            indices_summary = []
            for _, row in key_indices.head(5).iterrows():
                name = row.get('name', 'N/A')
                price = row.get('Price', 0)
                # Show integer values for indices, decimal for others
                if any(index_name in name for index_name in ['US', 'JP', 'DE', 'UK', 'FR', 'IT', 'ES', 'AU', 'NZ', 'CA']):
                    # Format as integer for indices
                    price_formatted = f"{price:.0f}" if isinstance(price, (int, float)) else str(price)
                else:
                    # Format with decimals for currencies and others
                    price_formatted = f"{price:.2f}" if isinstance(price, (int, float)) else str(price)
                indices_summary.append(f"• {name}: {price_formatted}")
            
            for summary in indices_summary:
                self.add_paragraph(summary)
        
        self.story.append(Spacer(1, 12))
    
    def add_indices_table(self, indices_data: pd.DataFrame):
        """Add major indices table with professional styling"""
        if indices_data.empty:
            return
            
        self.add_section("Major Indices Performance")
        data = []
        for _, row in indices_data.head(15).iterrows():
            name = str(row.get('name', 'N/A'))
            # Show integer values for indices
            price_value = row.get('Price', 'N/A')
            if isinstance(price_value, (int, float)):
                # Check if this is an index symbol
                index_symbols = ['US', 'JP', 'DE', 'UK', 'FR', 'IT', 'ES', 'AU', 'NZ', 'CA']
                if any(index_name in name for index_name in index_symbols):
                    # Format as integer for indices
                    price = f"{price_value:.0f}"
                else:
                    # Format with decimals for others
                    price = f"{price_value:.2f}"
            else:
                price = str(price_value)
                
            # Add 24H % change if available
            pct_change_24h = row.get('pct_change_24h', 0)
            if isinstance(pct_change_24h, (int, float)):
                direction = "+" if pct_change_24h >= 0 else ""
                change_text = f"{direction}{pct_change_24h:.2f}%"
            else:
                change_text = "N/A"
            
            data.append([name, price, change_text])

        self.add_rich_table(data, ["Index", "Price", "24H Change"], [2.5*inch, 1.75*inch, 1.75*inch])
    
    def add_currencies_table(self, currency_data: pd.DataFrame):
        """Add currencies table with professional styling"""
        if currency_data.empty:
            return
            
        self.add_section("Currency Markets")
        data = []
        for _, row in currency_data.head(15).iterrows():
            name = str(row.get('name', 'N/A'))
            price_value = row.get('Price', 'N/A')
            if isinstance(price_value, (int, float)):
                # Format with 4 decimal places for currencies
                price = f"{price_value:.4f}"
            else:
                price = str(price_value)
                
            # Add 24H % change if available
            pct_change_24h = row.get('pct_change_24h', 0)
            if isinstance(pct_change_24h, (int, float)):
                direction = "+" if pct_change_24h >= 0 else ""
                change_text = f"{direction}{pct_change_24h:.2f}%"
            else:
                change_text = "N/A"
            
            data.append([name, price, change_text])

        self.add_rich_table(data, ["Currency Pair", "Price", "24H Change"], [2.5*inch, 1.75*inch, 1.75*inch])
    
    def add_commodities_table(self, commodities_data: pd.DataFrame):
        """Add commodities table with professional styling"""
        if commodities_data.empty:
            return
            
        self.add_section("Commodities")
        data = []
        for _, row in commodities_data.head(15).iterrows():
            name = str(row.get('name', 'N/A'))
            price_value = row.get('Price', 'N/A')
            if isinstance(price_value, (int, float)):
                # Special handling for gold (XAUUSD) - should show 4 decimal places
                if name == 'XAUUSD':
                    price = f"{price_value:.2f}"  # Show 2 decimal places for gold
                else:
                    price = f"{price_value:.2f}"  # Show 2 decimal places for other commodities
            else:
                price = str(price_value)
                
            # Add 24H % change if available
            pct_change_24h = row.get('pct_change_24h', 0)
            if isinstance(pct_change_24h, (int, float)):
                direction = "+" if pct_change_24h >= 0 else ""
                change_text = f"{direction}{pct_change_24h:.2f}%"
            else:
                change_text = "N/A"
            
            data.append([name, price, change_text])

        self.add_rich_table(data, ["Commodity", "Price", "24H Change"], [2.5*inch, 1.75*inch, 1.75*inch])
    
    def add_bonds_table(self, bonds_data: pd.DataFrame):
        """Add bonds table with professional styling"""
        if bonds_data.empty:
            return
            
        self.add_section("Bonds/ETFs")
        data = []
        for _, row in bonds_data.head(15).iterrows():
            name = str(row.get('name', 'N/A'))
            price_value = row.get('Price', 'N/A')
            if isinstance(price_value, (int, float)):
                price = f"{price_value:.2f}"
            else:
                price = str(price_value)
                
            # Add 24H % change if available
            pct_change_24h = row.get('pct_change_24h', 0)
            if isinstance(pct_change_24h, (int, float)):
                direction = "+" if pct_change_24h >= 0 else ""
                change_text = f"{direction}{pct_change_24h:.2f}%"
            else:
                change_text = "N/A"
            
            data.append([name, price, change_text])

        self.add_rich_table(data, ["Bond/ETF", "Price", "24H Change"], [2.5*inch, 1.75*inch, 1.75*inch])
    
    def add_volatility_table(self, volatility_data: pd.DataFrame):
        """Add volatility indices table with professional styling"""
        if volatility_data.empty:
            return
            
        self.add_section("Market Volatility")
        data = []
        for _, row in volatility_data.head(10).iterrows():
            name = str(row.get('name', 'N/A'))
            price_value = row.get('Price', 'N/A')
            if isinstance(price_value, (int, float)):
                price = f"{price_value:.2f}"
            else:
                price = str(price_value)
                
            # Add 24H % change if available
            pct_change_24h = row.get('pct_change_24h', 0)
            if isinstance(pct_change_24h, (int, float)):
                direction = "+" if pct_change_24h >= 0 else ""
                change_text = f"{direction}{pct_change_24h:.2f}%"
            else:
                change_text = "N/A"
            
            data.append([name, price, change_text])
        
        self.add_rich_table(data, ["Volatility Index", "Price", "24H Change"], [2.5*inch, 1.75*inch, 1.75*inch])
    
    def add_top_movers_table(self, top_movers: pd.DataFrame):
        """Add top movers table with professional styling"""
        if top_movers.empty:
            return
            
        self.add_section("Top Market Movers (24h)")
        data = []
        for _, row in top_movers.iterrows():
            name = str(row.get('name', 'N/A'))
            # Show integer values for indices
            price_value = row.get('Price', 'N/A')
            if isinstance(price_value, (int, float)):
                # Check if this is an index symbol by looking for exact matches
                # rather than partial matches to avoid false positives with currencies
                name = str(row.get('name', ''))
                is_index = False
                index_symbols = ['US30', 'US500', 'US30Roll', 'US500Roll', 'UT100', 'UT100Roll', 
                               'DE30', 'DE40', 'DE30Roll', 'DE40Roll', 'UK100', 'UK100Roll',
                               'JP225', 'FR40', 'IT50', 'ES35', 'AU200', 'NZ50', 'CA60']
                
                # Check if the name matches any index symbol exactly or as a prefix
                for index_symbol in index_symbols:
                    if name.startswith(index_symbol):
                        is_index = True
                        break
                
                if is_index:
                    # Format as integer for indices
                    price = f"{price_value:.0f}"
                else:
                    # Format with decimals for others (currencies, commodities, etc.)
                    price = f"{price_value:.2f}"
            else:
                price = str(price_value)
            pct_change = row.get('pct_change', 0)
            direction = "+" if pct_change >= 0 else ""
            change_text = f"{direction}{pct_change:.2f}%"
            
            # Color coding for changes
            data.append([name, price, change_text])
        
        self.add_rich_table(data, ["Symbol", "Price", "24h Change"], [2.5*inch, 1.75*inch, 1.75*inch])
    
    def add_calendar_events(self, calendar_data: pd.DataFrame):
        """Add economic calendar events with professional styling"""
        if calendar_data.empty:
            return
            
        self.add_section("Economic Calendar")
        
        # Filter for current day only
        from datetime import datetime
        import pandas as pd
        
        # Filter calendar data for today
        today = pd.Timestamp('today').date()
        
        # Parse datetime column and filter for today's events
        filtered_data = calendar_data.copy()
        
        # Handle datetime parsing for filtering
        if 'DateTime' in filtered_data.columns:
            filtered_data['parsed_datetime'] = pd.to_datetime(filtered_data['DateTime'], errors='coerce')
            filtered_data = filtered_data[filtered_data['parsed_datetime'].dt.date == today]
        elif 'Time' in filtered_data.columns:
            filtered_data['parsed_datetime'] = pd.to_datetime(filtered_data['Time'], errors='coerce')
            filtered_data = filtered_data[filtered_data['parsed_datetime'].dt.date == today]
        
        # Filter to show only Medium and High importance events
        importance_filter = ['Medium', 'High', 'Very High']
        if 'Impact' in filtered_data.columns:
            filtered_data = filtered_data[filtered_data['Impact'].isin(importance_filter)]
        elif 'importance' in filtered_data.columns:
            filtered_data = filtered_data[filtered_data['importance'].isin(importance_filter)]
        
        if filtered_data.empty:
            # Add a message when no events for today
            from reportlab.platypus import Paragraph
            self.story.append(Paragraph("No economic events scheduled for today.", self.normal_style))
            return
        
        # Required columns per your specification (without Notes)
        required_columns = ["Date/Time", "Imp.", "Curr.", "Event", "Actual", "Forecast", "Previous"]
        
        # Prepare data rows
        data = []
        
        # Convert time properly - assume the incoming time is in EST/EDT, not UTC
        import pytz
        from datetime import datetime
        
        # Define the source timezone (likely EST/EDT - let's use EST for now)
        # In the future, this might need to be configurable based on the data source
        source_tz = pytz.timezone('US/Eastern')  # EST/EDT
        target_tz = pytz.timezone('Asia/Kolkata')  # IST
        
        for _, row in filtered_data.iterrows():
            # Handle the new CSV format with DateTime,EventID,Name,Country,Currency,Impact,Actual,Forecast,Previous
            # Or the old format with Time,Name,Impact,Currency,Actual,Forecast,Previous
            
            # Process date/time and convert to IST
            date_time_str = "N/A"
            if 'DateTime' in filtered_data.columns:
                # New format
                date_time_value = row.get('DateTime', 'N/A')
                event_name = str(row.get('Name', 'N/A'))
                currency = str(row.get('Currency', 'N/A'))
                importance = str(row.get('Impact', 'N/A'))
                actual = str(row.get('Actual', 'N/A'))
                forecast = str(row.get('Forecast', 'N/A'))
                previous = str(row.get('Previous', 'N/A'))
            elif 'Time' in filtered_data.columns:
                # Old format
                date_time_value = row.get('Time', 'N/A')
                event_name = str(row.get('Name', 'N/A'))
                importance = str(row.get('Impact', 'N/A'))
                currency = str(row.get('Currency', 'N/A'))
                actual = str(row.get('Actual', 'N/A'))
                forecast = str(row.get('Forecast', 'N/A'))
                previous = str(row.get('Previous', 'N/A'))
            else:
                # Fallback
                date_time_value = "N/A"
                event_name = "N/A"
                importance = "N/A"
                currency = "N/A"
                actual = "N/A"
                forecast = "N/A"
                previous = "N/A"
            
            # Convert to IST properly - assume incoming time is in EST/EDT
            if date_time_value != "N/A" and date_time_value is not None:
                try:
                    # Parse the datetime
                    if isinstance(date_time_value, str):
                        # Try to parse different datetime formats
                        dt = pd.to_datetime(date_time_value, errors='coerce')
                    else:
                        dt = date_time_value
                    
                    if pd.notna(dt):
                        # Localize to source timezone (EST/EDT) instead of UTC
                        if dt.tzinfo is None:
                            dt_localized = source_tz.localize(dt)
                        else:
                            dt_localized = dt
                        
                        # Convert to IST
                        dt_ist = dt_localized.astimezone(target_tz)
                        date_time_str = dt_ist.strftime('%Y-%m-%d %H:%M:%S IST')
                    else:
                        date_time_str = str(date_time_value)
                except Exception as e:
                    # Fallback to original value if conversion fails
                    date_time_str = str(date_time_value)
            else:
                date_time_str = str(date_time_value)
            
            # Handle NaN values by leaving them blank
            importance = "" if importance == "nan" or pd.isna(importance) else importance
            currency = "" if currency == "nan" or pd.isna(currency) else currency
            actual = "" if actual == "nan" or pd.isna(actual) else actual
            forecast = "" if forecast == "nan" or pd.isna(forecast) else forecast
            previous = "" if previous == "nan" or pd.isna(previous) else previous
            
            data.append([date_time_str, importance, currency, event_name, actual, forecast, previous])
        
        # Create table with adjusted column widths (reduced Date/Time column)
        # Column widths: Date/Time, Imp., Curr., Event, Actual, Forecast, Previous
        column_widths = [1.5*inch, 0.5*inch, 0.4*inch, 2.2*inch, 0.7*inch, 0.7*inch, 0.7*inch]
        
        # Create the table with row height adjustment to prevent overflow
        from reportlab.platypus import Table, TableStyle
        table = Table([required_columns] + data, column_widths, repeatRows=1)
        
        # Apply styling with proper alignment and row height
        from reportlab.lib import colors
        table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2c5282")),  # Dark blue header
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # Header centered
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows styling with row height adjustment
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),  # Light gray grid
            
            # Row height adjustment to prevent text overflow
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            
            # Column-specific alignment
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),      # Date/Time - left aligned
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),    # Imp. - center aligned
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),    # Curr. - center aligned
            ('ALIGN', (3, 1), (3, -1), 'LEFT'),      # Event - left aligned
            ('ALIGN', (4, 1), (6, -1), 'RIGHT'),     # Actual, Forecast, Previous - right aligned
            
            # Vertical alignment for all cells
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        self.story.append(table)
    
    def add_volatility_summary(self, volatility_summary: pd.DataFrame):
        """Add volatility summary with professional styling"""
        if volatility_summary.empty:
            return
            
        self.add_section("Volatility Analysis")
        data = []
        for _, row in volatility_summary.head(15).iterrows():
            symbol = str(row.get('symbol', 'N/A'))
            atr = f"{row.get('current_atr', 0):.4f}"
            volatility = f"{row.get('current_volatility', 0):.4f}"
            data.append([symbol, atr, volatility])
        
        self.add_rich_table(data, ["Symbol", "ATR", "Volatility"], [2.5*inch, 1.75*inch, 1.75*inch])
    
    def add_risk_metrics(self, risk_data: Dict):
        """Add risk metrics section"""
        self.add_section("Risk Metrics")
        
        if not risk_data:
            self.add_paragraph("No risk metrics available.")
            return
        
        # Format risk metrics as a table
        data = []
        for key, value in risk_data.items():
            formatted_key = key.replace('_', ' ').title()
            formatted_value = f"{value:.4f}" if isinstance(value, float) else str(value)
            data.append([formatted_key, formatted_value])
        
        self.add_rich_table(data, ["Metric", "Value"], [3*inch, 3*inch])
    
    def add_charts(self, chart_files: List[str]):
        """Add charts to the report with professional styling"""
        if not chart_files:
            return
            
        self.add_section("Market Charts")
        self.add_paragraph(f"This section includes {len(chart_files)} key market charts for technical analysis.")
        
        # Add charts in pairs per page for better layout
        for i in range(0, min(len(chart_files), 6), 2):  # Limit to first 6 charts
            chart_row = chart_files[i:i+2]
            
            # Add first chart
            if len(chart_row) >= 1:
                chart_path = chart_row[0]
                symbol = os.path.basename(chart_path).replace("_matplotlib.png", "")
                self.add_image(chart_path, width=5.5*inch, height=2.5*inch, caption=f"{symbol} - Price Action")
            
            # Add second chart if available
            if len(chart_row) >= 2:
                chart_path = chart_row[1]
                symbol = os.path.basename(chart_path).replace("_matplotlib.png", "")
                self.add_image(chart_path, width=5.5*inch, height=2.5*inch, caption=f"{symbol} - Price Action")
            
            self.story.append(Spacer(1, 15))
    
    def add_disclaimer(self):
        """Add disclaimer section"""
        self.add_section("Disclaimer")
        disclaimer_text = (
            "This report is for informational purposes only and should not be considered as investment advice. "
            "The information provided is based on data available at the time of report generation and may not "
            "reflect current market conditions. Past performance is not indicative of future results. "
            "Investment decisions should be made based on your own research and risk tolerance."
        )
        self.add_paragraph(disclaimer_text)
    
    def generate(self):
        """Generate the professional PDF report"""
        try:
            # Add the custom header/footer
            self.doc.build(self.story, onFirstPage=self.add_header_footer, onLaterPages=self.add_header_footer)
            logger.info(f"Professional PDF report generated: {self.filename}")
            return self.filename
        except Exception as e:
            logger.error(f"Error generating professional PDF report: {e}")
            raise

# Example usage
if __name__ == "__main__":
    # Create sample data for testing
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Sample market status
    market_status = {
        'status': 'Open',
        'timestamp': timestamp,
        'timezone': 'UTC'
    }
    
    # Sample indices data
    indices_data = pd.DataFrame([
        {'name': 'S&P 500', 'ask': 4500.50, 'bid': 4499.75},
        {'name': 'Dow Jones', 'ask': 35000.25, 'bid': 34999.50},
        {'name': 'NASDAQ', 'ask': 15000.75, 'bid': 14999.25}
    ])
    
    # Generate sample professional PDF report
    pdf_gen = ProfessionalPDFReportGenerator("professional_sample_report.pdf")
    pdf_gen.add_cover_page()
    pdf_gen.add_table_of_contents()
    pdf_gen.add_title("DAILY INVESTMENT REPORT")
    pdf_gen.add_executive_summary([
        "Markets opened with mixed sentiment amid ongoing geopolitical tensions",
        "S&P 500 futures indicate a potential 0.3% gain at market open",
        "Oil prices rose 1.2% following supply concerns in the Middle East",
        "USD weakened against major currencies ahead of Federal Reserve decision"
    ])
    pdf_gen.add_market_overview(market_status, indices_data)
    pdf_gen.add_indices_table(indices_data)
    pdf_gen.add_disclaimer()
    pdf_gen.generate()
    
    print("Sample professional PDF report generated: professional_sample_report.pdf")