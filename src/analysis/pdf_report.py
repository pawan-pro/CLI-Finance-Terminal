import pandas as pd
from datetime import datetime
import logging
from typing import Dict, List
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# adding mt5 path    
mt5_path = os.getenv("MT5_PATH")

class PDFReportGenerator:
    """Class to generate PDF reports"""
    
    def __init__(self, filename: str):
        """Initialize PDF generator"""
        self.filename = filename
        self.doc = SimpleDocTemplate(filename, pagesize=A4)
        self.styles = getSampleStyleSheet()
        self.story = []
        
        # Create custom styles
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
        self.section_style = ParagraphStyle(
            'CustomSection',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20
        )
        
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6
        )
    
    def add_title(self, title: str):
        """Add title to the report"""
        self.story.append(Paragraph(title, self.title_style))
        self.story.append(Spacer(1, 12))
    
    def add_section(self, title: str):
        """Add section header"""
        self.story.append(Paragraph(title, self.section_style))
    
    def add_paragraph(self, text: str):
        """Add paragraph text"""
        self.story.append(Paragraph(text, self.normal_style))
        self.story.append(Spacer(1, 6))
    
    def add_table(self, data: List[List], headers: List[str] = None):
        """Add table data"""
        if headers:
            data = [headers] + data
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 12))
    
    def add_image(self, image_path: str, width: float = 6*inch, height: float = 3*inch):
        """Add image to the report"""
        if os.path.exists(image_path):
            img = Image(image_path, width=width, height=height)
            self.story.append(img)
            self.story.append(Spacer(1, 12))
        else:
            logger.warning(f"Image not found: {image_path}")
    
    def add_market_status(self, market_status: Dict):
        """Add market status section"""
        self.add_section("Market Status")
        self.add_paragraph(f"Status: {market_status.get('status', 'Unknown')}")
        self.add_paragraph(f"Timestamp: {market_status.get('timestamp', 'N/A')}")
        self.add_paragraph(f"Timezone: {market_status.get('timezone', 'N/A')}")
    
    def add_indices_table(self, indices_data: pd.DataFrame):
        """Add major indices table"""
        if indices_data.empty:
            return
            
        self.add_section("Major Indices")
        data = []
        for _, row in indices_data.head(10).iterrows():
            data.append([
                str(row.get('name', 'N/A')),
                f"{row.get('ask', 'N/A'):.4f}" if isinstance(row.get('ask'), (int, float)) else str(row.get('ask', 'N/A')),
                f"{row.get('bid', 'N/A'):.4f}" if isinstance(row.get('bid'), (int, float)) else str(row.get('bid', 'N/A'))
            ])
        
        self.add_table(data, ["Symbol", "Ask", "Bid"])
    
    def add_currencies_table(self, currency_data: pd.DataFrame):
        """Add currencies table"""
        if currency_data.empty:
            return
            
        self.add_section("Major Currencies")
        data = []
        for _, row in currency_data.head(10).iterrows():
            data.append([
                str(row.get('name', 'N/A')),
                f"{row.get('ask', 'N/A'):.4f}" if isinstance(row.get('ask'), (int, float)) else str(row.get('ask', 'N/A')),
                f"{row.get('bid', 'N/A'):.4f}" if isinstance(row.get('bid'), (int, float)) else str(row.get('bid', 'N/A'))
            ])
        
        self.add_table(data, ["Symbol", "Ask", "Bid"])
    
    def add_commodities_table(self, commodities_data: pd.DataFrame):
        """Add commodities table"""
        if commodities_data.empty:
            return
            
        self.add_section("Commodities")
        data = []
        for _, row in commodities_data.head(10).iterrows():
            data.append([
                str(row.get('name', 'N/A')),
                f"{row.get('ask', 'N/A'):.4f}" if isinstance(row.get('ask'), (int, float)) else str(row.get('ask', 'N/A')),
                f"{row.get('bid', 'N/A'):.4f}" if isinstance(row.get('bid'), (int, float)) else str(row.get('bid', 'N/A'))
            ])
        
        self.add_table(data, ["Symbol", "Ask", "Bid"])
    
    def add_volatility_table(self, volatility_data: pd.DataFrame):
        """Add volatility indices table"""
        if volatility_data.empty:
            return
            
        self.add_section("Market Volatility")
        data = []
        for _, row in volatility_data.head(10).iterrows():
            data.append([
                str(row.get('name', 'N/A')),
                f"{row.get('ask', 'N/A'):.4f}" if isinstance(row.get('ask'), (int, float)) else str(row.get('ask', 'N/A')),
                f"{row.get('bid', 'N/A'):.4f}" if isinstance(row.get('bid'), (int, float)) else str(row.get('bid', 'N/A'))
            ])
        
        self.add_table(data, ["Symbol", "Ask", "Bid"])
    
    def add_top_movers_table(self, top_movers: pd.DataFrame):
        """Add top movers table"""
        if top_movers.empty:
            return
            
        self.add_section("Top Movers")
        data = []
        for _, row in top_movers.iterrows():
            pct_change = row.get('pct_change', 0)
            direction = "+" if pct_change >= 0 else ""
            data.append([
                str(row.get('name', 'N/A')),
                f"{row.get('ask', 'N/A'):.4f}" if isinstance(row.get('ask'), (int, float)) else str(row.get('ask', 'N/A')),
                f"{direction}{pct_change:.2f}%"
            ])
        
        self.add_table(data, ["Symbol", "Price", "Change"])
    
    def add_calendar_events(self, calendar_data: pd.DataFrame):
        """Add economic calendar events"""
        if calendar_data.empty:
            return
            
        self.add_section("Economic Calendar")
        data = []
        for _, row in calendar_data.iterrows():
            data.append([
                f"{row.get('date', 'N/A')} {row.get('time', 'N/A')}",
                str(row.get('currency', 'N/A')),
                str(row.get('event', 'N/A'))
            ])
        
        self.add_table(data, ["Date/Time", "Currency", "Event"])
    
    def add_volatility_summary(self, volatility_summary: pd.DataFrame):
        """Add volatility summary"""
        if volatility_summary.empty:
            return
            
        self.add_section("Volatility Summary")
        data = []
        for _, row in volatility_summary.iterrows():
            data.append([
                str(row.get('symbol', 'N/A')),
                f"{row.get('current_atr', 0):.4f}",
                f"{row.get('current_volatility', 0):.4f}"
            ])
        
        self.add_table(data, ["Symbol", "ATR", "Volatility"])
    
    def add_charts(self, chart_files: List[str]):
        """Add charts to the report"""
        if not chart_files:
            return
            
        self.add_section("Market Charts")
        self.add_paragraph(f"Included {len(chart_files)} charts")
        
        # Add first few charts
        for chart_file in chart_files[:3]:  # Limit to first 3 for demo
            self.add_image(chart_file)
    
    def generate(self):
        """Generate the PDF report"""
        try:
            self.doc.build(self.story)
            logger.info(f"PDF report generated: {self.filename}")
            return self.filename
        except Exception as e:
            logger.error(f"Error generating PDF report: {e}")
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
        {'name': 'SPX500', 'ask': 4500.50, 'bid': 4499.75},
        {'name': 'DJI30', 'ask': 35000.25, 'bid': 34999.50},
        {'name': 'NDX100', 'ask': 15000.75, 'bid': 14999.25}
    ])
    
    # Generate sample PDF report
    pdf_gen = PDFReportGenerator("sample_report.pdf")
    pdf_gen.add_title("DAILY INVESTMENT REPORT")
    pdf_gen.add_market_status(market_status)
    pdf_gen.add_indices_table(indices_data)
    pdf_gen.generate()
    
    print("Sample PDF report generated: sample_report.pdf")