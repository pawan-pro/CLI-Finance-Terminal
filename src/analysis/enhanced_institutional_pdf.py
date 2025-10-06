"""
Enhanced Institutional-Grade PDF Report Generator

This module generates professional PDF reports with bulge-bracket investment
bank formatting, color schemes, and analytical depth.
"""

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
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import numpy as np
from src.data.providers.mt5_data import MT5DataFetcher
from src.data.providers.alpha_vantage_data import AlphaVantageData

# Define font variables with defaults
FONT_REGULAR = 'Helvetica'
FONT_BOLD = 'Helvetica-Bold'

# Try to register Century Gothic fonts but only if the files exist
try:
    import os
    font_path = '/Users/pawan/Desktop/fonts/Century Gothic/centurygothic.tff'
    font_bold_path = '/Users/pawan/Desktop/fonts/Century Gothic/centurygothic_bold.tff'
    
    if os.path.exists(font_path) and os.path.exists(font_bold_path):
        pdfmetrics.registerFont(TTFont('CenturyGothic', font_path))
        pdfmetrics.registerFont(TTFont('CenturyGothic-Bold', font_bold_path))
        FONT_REGULAR = 'CenturyGothic'
        FONT_BOLD = 'CenturyGothic-Bold'
    else:
        print(f"Century Gothic font files not found. Regular: {font_path} Bold: {font_bold_path}")
except Exception as e:
    print(f"Could not register Century Gothic fonts, falling back to Helvetica: {e}")
    FONT_REGULAR = 'Helvetica'
    FONT_BOLD = 'Helvetica-Bold'

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedInstitutionalPDFReportGenerator:
    """Enhanced PDF generator with institutional-grade formatting"""
    
    def __init__(self, filename: str):
        """
        Initialize PDF generator with institutional styling
        
        Args:
            filename: Output PDF filename
        """
        self.filename = filename
        self.doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=54,
            leftMargin=54,
            topMargin=54,
            bottomMargin=36
        )
        
        self.mt5_data_fetcher = MT5DataFetcher()
        self.alpha_vantage_data = AlphaVantageData()
        
        # Define institutional color palette
        self.colors = {
            'primary_dark': colors.HexColor("#1a3c6c"),      # Deep navy blue
            'primary_medium': colors.HexColor("#2c5282"),   # Medium blue
            'primary_light': colors.HexColor("#4299e1"),    # Light blue
            'accent_gold': colors.HexColor("#d69e2e"),     # Gold accent
            'accent_red': colors.HexColor("#e53e3e"),       # Red accent
            'accent_green': colors.HexColor("#38a169"),     # Green accent
            'text_dark': colors.HexColor("#2d3748"),        # Dark gray text
            'text_medium': colors.HexColor("#4a5568"),      # Medium gray text
            'text_light': colors.HexColor("#718096"),       # Light gray text
            'background_light': colors.HexColor("#f7fafc"), # Light background
            'background_medium': colors.HexColor("#edf2f7"), # Medium background
        }
        
        # Create professional styles
        self._create_professional_styles()
        
        # Initialize story (document content)
        self.story = []
        
        # Track section headers for TOC
        self.section_headers = []
        
        # Symbol mapping for user-friendly names
        self.symbol_map = {
            "US500Roll": "S&P 500 (CFD)",
            "US30Roll": "Dow Jones 30 (CFD)",
            "UT100Roll": "Nasdaq 100 (CFD)",
            "DE40Roll": "DAX 40 (CFD)",
            "UK100Roll": "FTSE 100 (CFD)",
            "EURUSD": "EUR/USD",
            "GBPUSD": "GBP/USD",
            "USDJPY": "USD/JPY",
            "USDCHF": "USD/CHF",
            "AUDUSD": "AUD/USD",
            "XAUUSD": "Gold (Spot)",
            "XAGUSD": "Silver (Spot)",
            "USOIL": "WTI Crude Oil",
            "UKOIL": "Brent Crude Oil",
            "VIX": "VIX Volatility Index",
            "NIFTY_50": "NIFTY 50",
            "SENSEX": "BSE SENSEX"
        }
        
        # Indian indices integration has been removed to resolve data structure conflicts
        # A separate solution for Indian market data will be developed
        pass
        
    # Indian indices integration has been removed to resolve data structure conflicts
    # A separate solution for Indian market data will be developed
    pass
        
    def _create_professional_styles(self):
        """Create professional styling for institutional reports"""
        self.styles = getSampleStyleSheet()

        # Title styles
        self.title_style = ParagraphStyle(
            'InstitutionalTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            spaceAfter=30,
            alignment=1,  # Center alignment
            textColor=self.colors['primary_dark'],
            fontName=FONT_BOLD
        )
        
        self.subtitle_style = ParagraphStyle(
            'InstitutionalSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=25,
            spaceBefore=15,
            textColor=self.colors['primary_medium'],
            fontName=FONT_BOLD,
            alignment=1 # Center alignment
        )
        
        self.executive_summary_style = ParagraphStyle(
            'ExecutiveSummary',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            leading=14,
            textColor=self.colors['text_dark'],
            fontName=FONT_REGULAR,
            # justify the text
            alignment=4  # Justified alignment
        )
        
        self.section_header_style = ParagraphStyle(
            'SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=18,
            spaceAfter=20,
            spaceBefore=25,
            textColor=self.colors['primary_dark'],
            fontName=FONT_BOLD,
            backColor=self.colors['background_medium'],
            borderPadding=10,
            borderRadius=5
        )
        
        self.subsection_header_style = ParagraphStyle(
            'SubsectionHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=15,
            spaceBefore=20,
            textColor=self.colors['primary_medium'],
            fontName=FONT_BOLD
        )
        
        self.body_text_style = ParagraphStyle(
            'BodyText',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=8,
            leading=12,
            textColor=self.colors['text_dark'],
            fontName=FONT_REGULAR
        )
        
        self.small_text_style = ParagraphStyle(
            'SmallText',
            parent=self.styles['Normal'],
            fontSize=8,
            spaceAfter=6,
            leading=10,
            textColor=self.colors['text_medium'],
            fontName=FONT_REGULAR
        )
        
        self.highlight_box_style = ParagraphStyle(
            'HighlightBox',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=10,
            leading=12,
            textColor=self.colors['text_dark'],
            fontName=FONT_REGULAR,
            backColor=self.colors['background_light'],
            borderPadding=10,
            borderColor=self.colors['primary_light'],
            borderWidth=1,
            borderRadius=5
        )
        
        self.disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=self.styles['Normal'],
            fontSize=7,
            spaceAfter=4,
            leading=8,
            textColor=self.colors['text_light'],
            fontName=FONT_REGULAR # Changed to Italic
        )
        
        self.table_header_style = ParagraphStyle(
            'TableHeader',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=0,
            textColor=colors.white,
            fontName=FONT_BOLD
        )
        
        self.table_cell_style = ParagraphStyle(
            'TableCell',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=0,
            textColor=self.colors['text_dark'],
            fontName=FONT_REGULAR
        )
    
    def add_cover_page(self):
        """Add professional cover page"""
        # Company header
        self.story.append(Spacer(1, 2*inch))
        self.story.append(Paragraph("QUANTWATER TECH INVESTMENTS", self.title_style))
        self.story.append(Spacer(1, 0.2*inch))
        self.story.append(Paragraph("DAILY INVESTMENT RESEARCH NOTE", self.subtitle_style))
        self.story.append(Spacer(1, 0.5*inch))
        
        # Date
        report_date = datetime.now().strftime("%B %d, %Y")
        date_style = ParagraphStyle(
            'CoverDate',
            parent=self.styles['Normal'],
            fontSize=14,
            spaceAfter=2*inch,
            alignment=1,
            textColor=self.colors['text_medium'],
            fontName=FONT_REGULAR
        )
        self.story.append(Paragraph(report_date, date_style))
        
        # Disclaimer
        disclaimer_style = ParagraphStyle(
            'CoverDisclaimer',
            parent=self.styles['Normal'],
            fontSize=8,
            spaceAfter=10,
            alignment=1,
            textColor=self.colors['text_light'],
            fontName='Helvetica'
        )
        self.story.append(Paragraph(
            "This document is prepared for informational purposes only and should not be construed as investment advice.",
            disclaimer_style
        ))
        
        self.story.append(PageBreak())
    
    def add_table_of_contents(self):
        """Add table of contents"""
        self.story.append(Paragraph("TABLE OF CONTENTS", self.section_header_style))
        self.story.append(Spacer(1, 20))
        
        # In a real implementation, you would dynamically generate TOC
        # For now, we'll add placeholder entries
        toc_entries = [
            "Executive Summary",
            "Market Overview",
            "Major Indices Performance",
            "Currency Markets",
            "Commodities",
            "Bonds/ETFs",
            "Market Volatility",
            "Top Market Movers",
            "Market Regime Analysis",
            "Economic Calendar",
            "Risk Metrics",
            "Technical Charts"
        ]
        
        for i, entry in enumerate(toc_entries, 1):
            toc_style = ParagraphStyle(
                'TOCEntry',
                parent=self.styles['Normal'],
                fontSize=10,
                spaceAfter=8,
                leftIndent=20,
                textColor=self.colors['text_dark'],
                fontName='Helvetica'
            )
            self.story.append(Paragraph(f"{i}. {entry}", toc_style))
        
        self.story.append(PageBreak())
    
    def add_title(self, title: str):
        """Add title to the report"""
        # Remove "Institutional Grade" from the main title and ensure lowercase except proper nouns
        clean_title = title.replace("Institutional Grade", "").strip()
        self.story.append(Paragraph(clean_title.title(), self.title_style)) # Convert to title case
        self.story.append(Spacer(1, 12))
    
    def add_executive_summary(self, summary_points: List[str]):
        """
        Add executive summary section with institutional insights
        
        Args:
            summary_points: List of executive summary bullet points
        """
        self._add_section_header("EXECUTIVE SUMMARY")
        
        # Add summary box with fully justified text
        summary_content = []
        for point in summary_points:
            # Apply justified alignment to each point in the summary
            justified_style = ParagraphStyle(
                'JustifiedExecutiveSummary',
                parent=self.styles['Normal'],
                fontSize=11,
                spaceAfter=12,
                leading=14,
                textColor=self.colors['text_dark'],
                fontName=FONT_REGULAR,
                alignment=4  # Justified alignment
            )
            summary_content.append(Paragraph(f"• {point}", justified_style))
            summary_content.append(Spacer(1, 6)) # Add a small gap between points
        
        # Remove the last spacer if it exists
        if summary_content and isinstance(summary_content[-1], Spacer):
            summary_content.pop()
            
        self.story.extend(summary_content)
        self.story.append(Spacer(1, 15))
        
        # Add key insights boxes with more sophisticated institutional commentary
        insights_boxes = [
            {
                "title": "KEY MARKET INSIGHT",
                "content": "Proprietary trading desks are observing strong directional conviction in technology and growth sectors, driven by robust earnings and favorable macro indicators. Day traders should focus on intraday breakouts in high-volume tech stocks. Swing traders may find opportunities in sector rotation plays, while position traders could consider long-term exposure to AI and renewable energy. Portfolio managers are advised to maintain diversified exposure with a tactical overweight in innovation-driven equities.",
                "color": self.colors['accent_green']
            },
            {
                "title": "BIGGEST RISK",
                "content": "The primary risk for proprietary trading is unexpected central bank hawkishness, potentially leading to sharp market corrections. Day traders face heightened volatility around economic data releases. Swing traders must manage event risk from geopolitical developments. Position traders should monitor long-term inflation trends and their impact on bond yields. Portfolio managers need to stress-test portfolios against stagflationary scenarios and geopolitical escalations.",
                "color": self.colors['accent_red']
            },
            {
                "title": "CONVICTION TRADE",
                "content": "Proprietary trading favors long positions in large-cap technology with defined risk parameters. Day traders are targeting quick scalps on momentum plays. Swing traders are looking for mean-reversion opportunities in oversold quality names. Position traders are building core long positions in undervalued defensive sectors. Portfolio managers are increasing allocations to alternative assets for diversification and inflation hedging.",
                "color": self.colors['accent_gold']
            },
            {
                "title": "PORTFOLIO IMPLICATION",
                "content": "For proprietary trading, dynamic hedging strategies are crucial to manage tail risk. Day trading requires strict risk-reward ratios and rapid execution. Swing trading benefits from technical analysis and pattern recognition. Position trading emphasizes fundamental analysis and long-term trend identification. Portfolio management focuses on strategic asset allocation, risk budgeting, and active rebalancing to optimize returns and minimize drawdowns.",
                "color": self.colors['primary_medium']
            }
        ]
        
        for box in insights_boxes:
            # Apply justified alignment to insight box content
            justified_insight_style = ParagraphStyle(
                'JustifiedInsightBox',
                parent=self.styles['Normal'],
                fontSize=9,
                spaceAfter=10,
                leading=11,
                textColor=self.colors['text_dark'],
                fontName='Helvetica-Bold'
            )
            
            content_style = ParagraphStyle(
                'JustifiedInsightContent',
                parent=self.styles['Normal'],
                fontSize=9,
                spaceAfter=0,
                leading=11,
                textColor=self.colors['text_dark'],
                fontName='Helvetica',
                alignment=4  # Justified alignment
            )
            
            # Add box content with justified text
            full_content = f"<b>{box['title']}:</b> {box['content']}"
            self.story.append(Paragraph(full_content, justified_insight_style))
            self.story.append(Spacer(1, 10))
        
        self.story.append(Spacer(1, 20))
    
    
    
    def _add_section_header(self, title: str):
        """
        Add section header with institutional styling
        
        Args:
            title: Section title
        """
        self.story.append(Paragraph(title.upper(), self.section_header_style))
        self.section_headers.append(title)
    
    def add_market_overview(self, market_status: Dict, indices_data: pd.DataFrame):
        """Add market overview section with institutional insights"""
        self._add_section_header("MARKET OVERVIEW")
        
        # Market status
        # Removed market status line as per meta-prompt directive
        # Market status information has been removed from the report
        self.story.append(Spacer(1, 15))
        
        # Key indices performance - reordered by region (Asia, Euro Area+UK, Americas)
        if not indices_data.empty:
            self.story.append(Paragraph("<b>Key Market Indices Performance:</b>", self.subsection_header_style))
            
            # Define regional groupings
            asia_indices = ['JP225Roll', 'HK50Roll', 'CHINA50Roll']  # Asia-Pacific indices
            euro_uk_indices = ['DE40Roll', 'FRA40Roll', 'UK100Roll']  # Euro area + UK indices
            americas_indices = ['US500Roll', 'US30Roll', 'UT100Roll']  # Americas indices
            
            # Reorder the indices data based on regional groupings
            reordered_indices = []
            
            # Add Asia indices first
            for idx in asia_indices:
                idx_row = indices_data[indices_data['name'] == idx]
                if not idx_row.empty:
                    reordered_indices.append(idx_row.iloc[0])
            
            # Add Euro Area + UK indices next
            for idx in euro_uk_indices:
                idx_row = indices_data[indices_data['name'] == idx]
                if not idx_row.empty:
                    reordered_indices.append(idx_row.iloc[0])
            
            # Add Americas indices last
            for idx in americas_indices:
                idx_row = indices_data[indices_data['name'] == idx]
                if not idx_row.empty:
                    reordered_indices.append(idx_row.iloc[0])
            
            # Add any remaining indices that weren't in our predefined lists
            existing_names = [row['name'] if isinstance(row, pd.Series) else row['name'] for row in reordered_indices]
            for _, row in indices_data.iterrows():
                row_name = row.get('name', row.name if hasattr(row, 'name') else str(row))
                if row_name not in existing_names:
                    reordered_indices.append(row)
            
            # Create table of indices in regional order
            table_data = [['Index', 'Last', 'Chg', 'Chg %']]
            for row in reordered_indices[:8]:  # Limit to first 8 after reordering
                name = str(row.get('name', 'N/A'))
                display_name = self.symbol_map.get(name, name)
                ask = float(row.get('ask', 0))
                bid = float(row.get('bid', 0))
                last = (ask + bid) / 2
                change, pct_change = self.mt5_data_fetcher.get_24h_change(name)
                
                # Store raw values to be formatted later with direct color application
                table_data.append([
                    display_name,
                    f"{last:.2f}",
                    f"{change:+.2f}",
                    f"{pct_change:+.2f}%"
                ])
            
            # Create table with styling
            table = Table(table_data)
            table.setStyle(TableStyle([
                # Header styling
                ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary_dark']),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                # Data rows styling
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('FONTNAME', (0, 1), (-1, -1), FONT_REGULAR),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, self.colors['background_medium']),
                ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            # Apply color formatting to the percentage change column after table creation
            for i, (_, _, _, pct_change_str) in enumerate(table_data[1:], start=1):  # Skip header row
                try:
                    pct_value = float(pct_change_str.rstrip('%'))
                    if pct_value > 0:
                        table.setStyle(TableStyle([('TEXTCOLOR', (3, i), (3, i), self.colors['accent_green'])]))
                    elif pct_value < 0:
                        table.setStyle(TableStyle([('TEXTCOLOR', (3, i), (3, i), self.colors['accent_red'])]))
                    else:
                        table.setStyle(TableStyle([('TEXTCOLOR', (3, i), (3, i), self.colors['text_dark'])]))
                except:
                    # If conversion fails, use default text color
                    table.setStyle(TableStyle([('TEXTCOLOR', (3, i), (3, i), self.colors['text_dark'])]))
            
            # Apply color formatting to the change column
            for i, (_, _, change_str, _) in enumerate(table_data[1:], start=1):  # Skip header row
                try:
                    change_value = float(change_str)
                    if change_value > 0:
                        table.setStyle(TableStyle([('TEXTCOLOR', (2, i), (2, i), self.colors['accent_green'])]))
                    elif change_value < 0:
                        table.setStyle(TableStyle([('TEXTCOLOR', (2, i), (2, i), self.colors['accent_red'])]))
                    else:
                        table.setStyle(TableStyle([('TEXTCOLOR', (2, i), (2, i), self.colors['text_dark'])]))
                except:
                    # If conversion fails, use default text color
                    table.setStyle(TableStyle([('TEXTCOLOR', (2, i), (2, i), self.colors['text_dark'])]))
            
            self.story.append(table)
            self.story.append(Spacer(1, 20))
    
    def add_indices_table(self, indices_data: pd.DataFrame):
        """
        Add major indices table
        
        Args:
            indices_data: Indices data DataFrame
        """
        if indices_data.empty:
            return
            
        self._add_section_header("MAJOR INDICES PERFORMANCE")
        
        # Define regional groupings
        asia_indices = ['JP225Roll', 'HK50Roll', 'CHINA50Roll']  # Asia-Pacific indices
        euro_uk_indices = ['DE40Roll', 'FRA40Roll', 'UK100Roll']  # Euro area + UK indices
        americas_indices = ['US500Roll', 'US30Roll', 'UT100Roll']  # Americas indices
        
        # Reorder the indices data based on regional groupings
        reordered_indices = []
        
        # Add Asia indices first
        for idx in asia_indices:
            idx_row = indices_data[indices_data['name'] == idx]
            if not idx_row.empty:
                reordered_indices.append(idx_row.iloc[0])
        
        # Add Euro Area + UK indices next
        for idx in euro_uk_indices:
            idx_row = indices_data[indices_data['name'] == idx]
            if not idx_row.empty:
                reordered_indices.append(idx_row.iloc[0])
        
        # Add Americas indices last
        for idx in americas_indices:
            idx_row = indices_data[indices_data['name'] == idx]
            if not idx_row.empty:
                reordered_indices.append(idx_row.iloc[0])
        
        # Add any remaining indices that weren't in our predefined lists
        existing_names = [row['name'] if isinstance(row, pd.Series) else row['name'] for row in reordered_indices]
        for _, row in indices_data.iterrows():
            row_name = row.get('name', row.name if hasattr(row, 'name') else str(row))
            if row_name not in existing_names:
                reordered_indices.append(row)
        
        # Now create table rows with reordered indices
        table_data = [['Index', 'Price', '24h Change', '24h Change %']]
        for row in reordered_indices[:15]:  # Limit to first 15 after reordering
            name = str(row.get('name', 'N/A'))
            display_name = self.symbol_map.get(name, name)
            # Add a smaller, italicized line beneath the market name to show the CFD symbol
            full_name = f"{display_name}<br/><i>({name})</i>"
            price = f"{row.get('Price', 'N/A'):.2f}" if isinstance(row.get('Price'), (int, float)) else str(row.get('Price', 'N/A'))
            change, pct_change = self.mt5_data_fetcher.get_24h_change(name)
            
            # Format numbers with appropriate precision
            table_data.append([
                full_name,
                price,
                f"{change:+.2f}",
                f"{pct_change:+.2f}%"
            ])

        table = Table(table_data)
        table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary_dark']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            # Data rows styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, self.colors['background_medium']),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ]))
        
        # Apply color formatting to the percentage change column after table creation
        for i, (_, _, _, pct_change_str) in enumerate(table_data[1:], start=1):  # Skip header row
            try:
                pct_value = float(pct_change_str.rstrip('%'))
                if pct_value > 0:
                    table.setStyle(TableStyle([('TEXTCOLOR', (3, i), (3, i), self.colors['accent_green'])]))
                elif pct_value < 0:
                    table.setStyle(TableStyle([('TEXTCOLOR', (3, i), (3, i), self.colors['accent_red'])]))
                else:
                    table.setStyle(TableStyle([('TEXTCOLOR', (3, i), (3, i), self.colors['text_dark'])]))
            except:
                # If conversion fails, use default text color
                table.setStyle(TableStyle([('TEXTCOLOR', (3, i), (3, i), self.colors['text_dark'])]))
        
        # Apply color formatting to the change column
        for i, (_, _, change_str, _) in enumerate(table_data[1:], start=1):  # Skip header row
            try:
                change_value = float(change_str)
                if change_value > 0:
                    table.setStyle(TableStyle([('TEXTCOLOR', (2, i), (2, i), self.colors['accent_green'])]))
                elif change_value < 0:
                    table.setStyle(TableStyle([('TEXTCOLOR', (2, i), (2, i), self.colors['accent_red'])]))
                else:
                    table.setStyle(TableStyle([('TEXTCOLOR', (2, i), (2, i), self.colors['text_dark'])]))
            except:
                # If conversion fails, use default text color
                table.setStyle(TableStyle([('TEXTCOLOR', (2, i), (2, i), self.colors['text_dark'])]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 20))
    
    def add_currencies_table(self, currency_data: pd.DataFrame):
        """
        Add currencies table
        
        Args:
            currency_data: Currency data DataFrame
        """
        if currency_data.empty:
            return
            
        self._add_section_header("CURRENCY MARKETS")
        
        # Create currencies table (without Description column)
        table_data = [['Pair', 'Price', '24h Change', '24h Change %']]

        for _, row in currency_data.head(15).iterrows():
            name = str(row.get('name', 'N/A'))
            display_name = self.symbol_map.get(name, name)
            # Add a smaller, italicized line beneath the market name to show the CFD symbol
            full_name = f"{display_name}<br/><i>({name})</i>"
            price = f"{row.get('Price', 'N/A'):.4f}" if isinstance(row.get('Price'), (int, float)) else str(row.get('Price', 'N/A'))
            change, pct_change = self.mt5_data_fetcher.get_24h_change(name)

            table_data.append([
                full_name,
                price,
                f"{change:+.4f}",
                f"{pct_change:+.2f}%"
            ])

        table = Table(table_data)
        table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary_medium']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            # Data rows styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, self.colors['background_medium']),
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        # Apply color formatting to the percentage change column after table creation
        for i, (_, _, _, pct_change_str) in enumerate(table_data[1:], start=1):  # Skip header row
            try:
                pct_value = float(pct_change_str.rstrip('%'))
                if pct_value > 0:
                    table.setStyle(TableStyle([('TEXTCOLOR', (3, i), (3, i), self.colors['accent_green'])]))
                elif pct_value < 0:
                    table.setStyle(TableStyle([('TEXTCOLOR', (3, i), (3, i), self.colors['accent_red'])]))
                else:
                    table.setStyle(TableStyle([('TEXTCOLOR', (3, i), (3, i), self.colors['text_dark'])]))
            except:
                # If conversion fails, use default text color
                table.setStyle(TableStyle([('TEXTCOLOR', (3, i), (3, i), self.colors['text_dark'])]))
        
        # Apply color formatting to the change column
        for i, (_, _, change_str, _) in enumerate(table_data[1:], start=1):  # Skip header row
            try:
                change_value = float(change_str)
                if change_value > 0:
                    table.setStyle(TableStyle([('TEXTCOLOR', (2, i), (2, i), self.colors['accent_green'])]))
                elif change_value < 0:
                    table.setStyle(TableStyle([('TEXTCOLOR', (2, i), (2, i), self.colors['accent_red'])]))
                else:
                    table.setStyle(TableStyle([('TEXTCOLOR', (2, i), (2, i), self.colors['text_dark'])]))
            except:
                # If conversion fails, use default text color
                table.setStyle(TableStyle([('TEXTCOLOR', (2, i), (2, i), self.colors['text_dark'])]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 20))    
    def add_commodities_table(self, commodities_data: pd.DataFrame):
        """
        Add commodities table
        
        Args:
            commodities_data: Commodities data DataFrame
        """
        if commodities_data.empty:
            return
            
        self._add_section_header("COMMODITIES")
        
        # Create commodities table (without Description column)
        table_data = [['Commodity', 'Price', '24h Change', '24h Change %']]

        for _, row in commodities_data.head(15).iterrows():
            name = str(row.get('name', 'N/A'))
            display_name = self.symbol_map.get(name, name)
            # Add a smaller, italicized line beneath the market name to show the CFD symbol
            full_name = f"{display_name}<br/><i>({name})</i>"
            price = f"{row.get('Price', 'N/A'):.2f}" if isinstance(row.get('Price'), (int, float)) else str(row.get('Price', 'N/A'))
            change, pct_change = self.mt5_data_fetcher.get_24h_change(name)
            
            table_data.append([
                full_name,
                price,
                f"{change:+.2f}",
                f"{pct_change:+.2f}%"
            ])

        table = Table(table_data)
        table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['accent_gold']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            # Data rows styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, self.colors['background_medium']),
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        # Apply color formatting to the percentage change column after table creation
        for i, (_, _, _, pct_change_str) in enumerate(table_data[1:], start=1):  # Skip header row
            try:
                pct_value = float(pct_change_str.rstrip('%'))
                if pct_value > 0:
                    table.setStyle(TableStyle([('TEXTCOLOR', (3, i), (3, i), self.colors['accent_green'])]))
                elif pct_value < 0:
                    table.setStyle(TableStyle([('TEXTCOLOR', (3, i), (3, i), self.colors['accent_red'])]))
                else:
                    table.setStyle(TableStyle([('TEXTCOLOR', (3, i), (3, i), self.colors['text_dark'])]))
            except:
                # If conversion fails, use default text color
                table.setStyle(TableStyle([('TEXTCOLOR', (3, i), (3, i), self.colors['text_dark'])]))
        
        # Apply color formatting to the change column
        for i, (_, _, change_str, _) in enumerate(table_data[1:], start=1):  # Skip header row
            try:
                change_value = float(change_str)
                if change_value > 0:
                    table.setStyle(TableStyle([('TEXTCOLOR', (2, i), (2, i), self.colors['accent_green'])]))
                elif change_value < 0:
                    table.setStyle(TableStyle([('TEXTCOLOR', (2, i), (2, i), self.colors['accent_red'])]))
                else:
                    table.setStyle(TableStyle([('TEXTCOLOR', (2, i), (2, i), self.colors['text_dark'])]))
            except:
                # If conversion fails, use default text color
                table.setStyle(TableStyle([('TEXTCOLOR', (2, i), (2, i), self.colors['text_dark'])]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 20))
    
    def add_bonds_table(self, bonds_data: pd.DataFrame):
        """
        Add bonds/ETFs table - Prioritizes Alpha Vantage data with MT5 as fallback
        
        Args:
            bonds_data: Bonds data DataFrame
        """
        if bonds_data.empty:
            # Prioritize Alpha Vantage for bonds/ETFs data
            logger.info("Fetching bonds/ETFs data from Alpha Vantage")
            
            # Define comprehensive list of bond/ETF symbols
            bond_etf_symbols = [
                # Treasury ETFs
                'TLT', 'IEF', 'SHY', 'IEI', 'TLH',  # US Treasury ETFs
                # Corporate Bond ETFs  
                'LQD', 'TLTD', 'IGIB', 'TLTE', 'CBON',  # Corporate Bond ETFs
                # International Bond ETFs
                'BNDX', 'VWOY', 'EMB', 'EMLC', 'WIP',  # International/EM Bond ETFs
                # Commodity ETFs
                'GLD', 'SLV', 'PPLT', 'IAU', 'SLV',  # Precious Metals
                'USO', 'UNG', 'DBO', 'DBP', 'JJC',   # Energy & Agriculture
                # Inflation-Protected Securities
                'TIP', 'VTIAX', 'SCHP', 'VTIP', 'BIL' # TIPS & Short-term Treasuries
            ]
            
            # Fetch from Alpha Vantage
            alpha_vantage_bonds_data = self.alpha_vantage_data.get_bond_etf_data(bond_etf_symbols)
            
            # If Alpha Vantage fails, use MT5 as fallback
            if alpha_vantage_bonds_data.empty:
                logger.warning("Alpha Vantage bonds/ETFs data fetch failed, using MT5 as fallback")
                # Try to get some bond/ETF data from MT5 as a fallback
                available_symbols = self.mt5_data_fetcher.get_available_symbols()
                # Find symbols that look like bonds or ETFs (this is a simplified approach)
                mt5_bond_symbols = [s for s in available_symbols if any(keyword in s for keyword in ['BOND', 'ETF', 'TREAS', 'GOVT', 'CORP'])]
                
                mt5_bonds_data = []
                for symbol in mt5_bond_symbols[:15]:  # Limit to first 15
                    info = self.mt5_data_fetcher.get_symbol_info(symbol)
                    if info:
                        change, pct_change = self.mt5_data_fetcher.get_24h_change(symbol)
                        mt5_bonds_data.append({
                            'name': info.get('name', symbol),
                            'description': info.get('description', f'{symbol} Bond/ETF'),
                            'Price': (info.get('ask', 0) + info.get('bid', 0)) / 2,
                            'change': change,
                            'pct_change': pct_change
                        })
                
                bonds_data = pd.DataFrame(mt5_bonds_data)
            else:
                logger.info(f"Successfully fetched {len(alpha_vantage_bonds_data)} bonds/ETFs from Alpha Vantage")
                bonds_data = alpha_vantage_bonds_data
            
        if bonds_data.empty:
            return
        
        self._add_section_header("BONDS/ETFs")
        
        # Create bonds table (without Description column) - include 24H change and change % as requested
        table_data = [['Bond/ETF', 'Price', '24h Change', '24h Change %']]

        for _, row in bonds_data.head(15).iterrows():
            name = str(row.get('name', 'N/A'))
            price = f"{row.get('Price', 'N/A'):.2f}" if isinstance(row.get('Price'), (int, float)) else str(row.get('Price', 'N/A'))
            
            # Get 24h change and percentage
            change = row.get('change', 0) if 'change' in row else 0
            pct_change = row.get('pct_change', 0) if 'pct_change' in row else 0
            
            # Format change values
            change_str = f"{change:+.2f}" if change != 0 else "0.00"
            pct_change_str = f"{pct_change:+.2f}%" if pct_change != 0 else "0.00%"
            
            table_data.append([
                name,
                price,
                change_str,
                pct_change_str
            ])

        table = Table(table_data)
        table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary_dark']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            # Data rows styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, self.colors['background_medium']),
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        # Apply color formatting to the percentage change column after table creation
        for i, (_, _, _, pct_change_str) in enumerate(table_data[1:], start=1):  # Skip header row
            try:
                pct_value = float(pct_change_str.rstrip('%'))
                if pct_value > 0:
                    table.setStyle(TableStyle([('TEXTCOLOR', (3, i), (3, i), self.colors['accent_green'])]))
                elif pct_value < 0:
                    table.setStyle(TableStyle([('TEXTCOLOR', (3, i), (3, i), self.colors['accent_red'])]))
                else:
                    table.setStyle(TableStyle([('TEXTCOLOR', (3, i), (3, i), self.colors['text_dark'])]))
            except:
                # If conversion fails, use default text color
                table.setStyle(TableStyle([('TEXTCOLOR', (3, i), (3, i), self.colors['text_dark'])]))
        
        # Apply color formatting to the change column
        for i, (_, _, change_str, _) in enumerate(table_data[1:], start=1):  # Skip header row
            try:
                change_value = float(change_str)
                if change_value > 0:
                    table.setStyle(TableStyle([('TEXTCOLOR', (2, i), (2, i), self.colors['accent_green'])]))
                elif change_value < 0:
                    table.setStyle(TableStyle([('TEXTCOLOR', (2, i), (2, i), self.colors['accent_red'])]))
                else:
                    table.setStyle(TableStyle([('TEXTCOLOR', (2, i), (2, i), self.colors['text_dark'])]))
            except:
                # If conversion fails, use default text color
                table.setStyle(TableStyle([('TEXTCOLOR', (2, i), (2, i), self.colors['text_dark'])]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 20))
    
    def add_volatility_table(self, volatility_data: pd.DataFrame):
        """
        Add volatility indices table
        
        Args:
            volatility_data: Volatility data DataFrame
        """
        if volatility_data.empty:
            return
            
        self._add_section_header("MARKET VOLATILITY")
        
        # Create volatility table with VIX description update
        table_data = [['Volatility Index', 'Description', 'Price']]

        for _, row in volatility_data.head(10).iterrows():
            name = str(row.get('name', 'N/A'))
            description = str(row.get('description', 'N/A'))
            
            # Add VIX description if VIX is the index
            if name.upper() == 'VIX' or 'VIX' in name.upper():
                description = "CBOE Volatility Index - Market's expectation of 30-day volatility"
            elif description == 'N/A' or not description or description.strip() == '':
                # Provide generic descriptions based on symbol patterns
                if 'VOL' in name.upper():
                    description = "Volatility Index"
                elif 'INDEX' in name.upper():
                    description = "Market Volatility Indicator"
                else:
                    description = "Volatility Index"
            
            price = f"{row.get('Price', 'N/A'):.2f}" if isinstance(row.get('Price'), (int, float)) else str(row.get('Price', 'N/A'))
            
            table_data.append([
                name,
                description[:30] + "..." if len(description) > 30 else description,
                price
            ])

        table = Table(table_data)
        table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['accent_red']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            # Data rows styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, self.colors['background_medium']),
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        self.story.append(table)
        self.story.append(Spacer(1, 20))
    
    def add_top_movers_table(self, top_movers: pd.DataFrame):
        """
        Add top market movers table
        
        Args:
            top_movers: Top movers DataFrame
        """
        if top_movers.empty:
            return
            
        self._add_section_header("TOP MARKET MOVERS (24h)")
        
        # Create top movers table
        table_data = [['Symbol', 'Name', 'Price', '24h Change %', 'Volume', 'Attribution', 'Confidence']]

        for _, row in top_movers.head(15).iterrows():
            name = str(row.get('name', 'N/A'))
            symbol = str(row.get('symbol', name))
            price = f"{row.get('Price', 'N/A'):.2f}" if isinstance(row.get('Price'), (int, float)) else str(row.get('Price', 'N/A'))
            pct_change = float(row.get('pct_change', 0))
            volume = float(row.get('volume', 0))
            
            # Determine attribution with more sophistication
            if abs(pct_change) > 3.0:
                attribution = "Macro Event Driven"
                confidence = "High"
            elif abs(pct_change) > 2.0:
                attribution = "Technical Breakout"
                confidence = "Medium-High"
            elif abs(pct_change) > 1.0:
                attribution = "Sector Rotation"
                confidence = "Medium"
            elif volume > 1000000:  # High volume
                attribution = "Flow Driven"
                confidence = "Medium"
            else:
                attribution = "Normal Volatility"
                confidence = "Low"

            table_data.append([
                symbol,
                name[:20] + "..." if len(name) > 20 else name,
                price,
                f"{pct_change:+.2f}%",
                f"{volume:,.0f}",
                attribution,
                confidence
            ])

        table = Table(table_data)
        table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary_medium']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            # Data rows styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, self.colors['background_medium']),
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        # Apply color formatting to the percentage change column after table creation
        for i, (_, _, _, pct_change_str, _, _, _) in enumerate(table_data[1:], start=1):  # Skip header row
            try:
                pct_value = float(pct_change_str.rstrip('%'))
                if pct_value > 0:
                    table.setStyle(TableStyle([('TEXTCOLOR', (3, i), (3, i), self.colors['accent_green'])]))
                elif pct_value < 0:
                    table.setStyle(TableStyle([('TEXTCOLOR', (3, i), (3, i), self.colors['accent_red'])]))
                else:
                    table.setStyle(TableStyle([('TEXTCOLOR', (3, i), (3, i), self.colors['text_dark'])]))
            except:
                # If conversion fails, use default text color
                table.setStyle(TableStyle([('TEXTCOLOR', (3, i), (3, i), self.colors['text_dark'])]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 20))
    
    def add_market_regime_analysis(self, regime_info: Dict):
        """
        Add market regime analysis section
        
        Args:
            regime_info: Market regime information
        """
        self._add_section_header("MARKET REGIME ANALYSIS")
        
        if not regime_info:
            self.story.append(Paragraph("No market regime information available.", self.body_text_style))
            self.story.append(Spacer(1, 20))
            return

        regime = regime_info.get("regime", "Unknown")
        confidence = regime_info.get("confidence", 0.0)
        driver = regime_info.get("driver", "No specific driver")
        
        # Add regime summary box
        regime_text = f"<b>Current Market Regime:</b> {regime}<br/>"
        regime_text += f"<b>Confidence Level:</b> {confidence:.0%}<br/>"
        regime_text += f"<b>Primary Driver:</b> {driver}"
        
        self.story.append(Paragraph(regime_text, self.highlight_box_style))
        self.story.append(Spacer(1, 15))
        
        # Add institutional commentary
        if regime == "Risk-On":
            commentary = "Market exhibiting strong risk-on sentiment. Favorable environment for growth assets and cyclical sectors. Consider increasing equity exposure with emphasis on quality names."
        elif regime == "Risk-Off":
            commentary = "Market showing pronounced risk-off behavior. Defensive positioning recommended with emphasis on quality assets and defensive sectors. Consider increasing cash allocation and defensive hedges."
        elif regime == "High Volatility":
            commentary = "Market experiencing elevated volatility conditions. Increased hedging activity and reduced net exposures advisable. Focus on volatility trading opportunities and dynamic risk management."
        elif regime == "Range-Bound":
            commentary = "Market displaying range-bound characteristics. Tactical trading opportunities within established ranges. Consider mean-reversion strategies and active management."
        else:
            commentary = "Market in normal conditions. Standard risk management protocols appropriate. Maintain diversified portfolio positioning."

        self.story.append(Paragraph(f"<b>Institutional Commentary:</b> {commentary}", self.executive_summary_style))
        self.story.append(Spacer(1, 20))
    
    def add_calendar_events(self, calendar_data: pd.DataFrame):
        """
        Add economic calendar events
        
        Args:
            calendar_data: Calendar events DataFrame
        """
        if calendar_data.empty:
            return
            
        self._add_section_header("ECONOMIC CALENDAR")
        
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
            from reportlab.platypus import Paragraph
            from reportlab.lib import colors
            self.story.append(Paragraph("No economic events scheduled for today.", self.body_text_style))
            self.story.append(Spacer(1, 20))
            return

        # Create calendar table without Notes column and with shortened headers
        table_data = [['Date/Time', 'Imp.', 'Curr.', 'Event', 'Actual', 'Forecast', 'Previous']]

        # Convert time properly - apply timezone adjustments
        import pytz
        from datetime import datetime, timedelta

        # Define the target timezone (IST)
        target_tz = pytz.timezone('Asia/Kolkata')  # IST

        for _, row in filtered_data.iterrows():
            # Extract data
            date = str(row.get('date', 'N/A'))
            time = str(row.get('time', 'N/A'))
            currency = str(row.get('currency', 'N/A'))
            event = str(row.get('event', 'N/A'))
            actual = str(row.get('actual', 'N/A'))
            forecast = str(row.get('forecast', 'N/A'))
            previous = str(row.get('previous', 'N/A'))
            importance = str(row.get('importance', 'Medium')) if 'importance' in row else str(row.get('Impact', 'Medium'))
            country = str(row.get('country', 'N/A')) if 'country' in row else 'N/A'
            
            # Combine date and time
            datetime_str = f"{date} {time}" if date != 'N/A' and time != 'N/A' else (date if date != 'N/A' else time)

            # Convert to IST with appropriate adjustments
            if datetime_str != "N/A" and datetime_str is not None and datetime_str.strip():
                try:
                    # Parse the datetime
                    dt = pd.to_datetime(datetime_str, errors='coerce')

                    if pd.notna(dt):
                        # Special handling for CFTC events
                        if "CFTC" in event:
                            # CFTC events have a specific 3-hour shift pattern
                            # 22:30 in source data should be displayed as 01:00 IST next day
                            # Apply 3-hour shift and move to next day if needed
                            dt_adjusted = dt + timedelta(hours=3)
                            # Format as IST string
                            datetime_str = dt_adjusted.strftime('%Y-%m-%d %H:%M:%S IST')
                        # Apply timezone conversion based on country
                        elif country == 'JP':
                            # Special handling for Japanese events
                            # Japanese events are typically in JST (UTC+9)
                            # IST is UTC+5:30
                            # So we need to subtract 3.5 hours to convert from JST to IST
                            dt_adjusted = dt - timedelta(hours=3, minutes=30)
                            # Format as IST string
                            datetime_str = dt_adjusted.strftime('%Y-%m-%d %H:%M:%S IST')
                        else:
                            # For other countries, assume the data is in EST/EDT and convert to IST
                            source_tz = pytz.timezone('US/Eastern')
                            if dt.tzinfo is None:
                                dt_localized = source_tz.localize(dt)
                            else:
                                dt_localized = dt

                            # Convert to IST
                            dt_ist = dt_localized.astimezone(target_tz)
                            datetime_str = dt_ist.strftime('%Y-%m-%d %H:%M:%S IST')
                except Exception as e:
                    # Keep original datetime string if conversion fails
                    pass

            # Handle NaN values by leaving them blank
            importance = "" if importance == "nan" or pd.isna(importance) else importance
            currency = "" if currency == "nan" or pd.isna(currency) else currency
            actual = "" if actual == "nan" or pd.isna(actual) else actual
            forecast = "" if forecast == "nan" or pd.isna(forecast) else forecast
            previous = "" if previous == "nan" or pd.isna(previous) else previous

            # Truncate long event names to prevent text overflow
            max_event_length = 60  # Increased from 30 to 60 characters
            if len(event) > max_event_length:
                event = event[:max_event_length-3] + "..."

            table_data.append([
                datetime_str,
                importance,
                currency,
                event,
                actual,
                forecast,
                previous
            ])

        from reportlab.platypus import Table, TableStyle
        from reportlab.lib import colors
        table = Table(table_data)
        table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary_dark']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            # Data rows styling with row height adjustment
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, self.colors['background_medium']),

            # Row height adjustment to prevent text overflow
            ('TOPPADDING', (0, 1), (-1, -1), 8),    # Increased padding
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8), # Increased padding

            # Column-specific alignment (increased Event column width)
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),      # Date/Time - left aligned
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),    # Imp. - center aligned
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),    # Curr. - center aligned
            ('ALIGN', (3, 1), (3, -1), 'LEFT'),      # Event - left aligned
            ('ALIGN', (4, 1), (6, -1), 'RIGHT'),     # Actual, Forecast, Previous - right aligned

            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

            # Word wrapping for long text in Event column
            ('WORDWRAP', (3, 1), (3, -1)),  # Word wrap for Event column
        ]))

        self.story.append(table)
        self.story.append(Spacer(1, 20))
    
    def add_volatility_summary(self, volatility_summary: pd.DataFrame):
        """
        Add volatility summary table
        
        Args:
            volatility_summary: Volatility summary DataFrame
        """
        if volatility_summary.empty:
            return
            
        self._add_section_header("VOLATILITY ANALYSIS")
        
        # Create volatility summary table
        table_data = [['Symbol', 'ATR', 'Volatility', 'Regime', 'Confidence']]

        for _, row in volatility_summary.head(15).iterrows():
            symbol = str(row.get('symbol', 'N/A'))
            atr = float(row.get('current_atr', 0))
            volatility = float(row.get('current_volatility', 0))
            regime = str(row.get('regime', 'Normal Market'))
            confidence = float(row.get('confidence', 0))
            
            table_data.append([
                symbol,
                f"{atr:.4f}",
                f"{volatility:.4f}",
                regime,
                f"{confidence:.0%}"
            ])

        table = Table(table_data)
        table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['accent_gold']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            # Data rows styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, self.colors['background_medium']),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        self.story.append(table)
        self.story.append(Spacer(1, 20))
    
    def add_risk_metrics(self, risk_metrics: Dict):
        """
        Add risk metrics section
        
        Args:
            risk_metrics: Risk metrics dictionary
        """
        self._add_section_header("RISK METRICS")
        
        if not risk_metrics:
            self.story.append(Paragraph("No risk metrics available.", self.body_text_style))
            self.story.append(Spacer(1, 20))
            return

        # Create risk metrics table
        table_data = [['Metric', 'Value', 'Description']]

        # Add key risk metrics
        key_metrics = [
            ('Sharpe Ratio', 'sharpe_ratio', 'Risk-adjusted return measure'),
            ('Sortino Ratio', 'sortino_ratio', 'Downside risk-adjusted return'),
            ('Max Drawdown', 'max_drawdown', 'Largest peak-to-trough decline'),
            ('Value at Risk (95%)', 'value_at_risk_95', 'Loss not exceeded 95% of time'),
            ('Value at Risk (99%)', 'value_at_risk_99', 'Loss not exceeded 99% of time'),
            ('Conditional VaR (95%)', 'conditional_var_95', 'Expected loss beyond VaR threshold'),
            ('Beta', 'market_beta', 'Market sensitivity measure'),
            ('Volatility (Annualized)', 'indices_volatility_annualized', 'Annualized price volatility'),
            ('Average Correlation', 'average_correlation', 'Average correlation between assets'),
            ('Market Stress Indicator', 'market_stress_indicator', 'Current market stress level'),
            ('Market Regime Confidence', 'market_regime_confidence', 'Confidence in detected market regime'),
        ]

        for metric_name, metric_key, description in key_metrics:
            value = risk_metrics.get(metric_key, 'N/A')
            if isinstance(value, (int, float)):
                if 'ratio' in metric_key:
                    formatted_value = f"{value:.2f}"
                elif 'var' in metric_key or 'drawdown' in metric_key or 'volatility' in metric_key or 'indicator' in metric_key:
                    formatted_value = f"{value:.2%}"
                elif 'beta' in metric_key or 'alpha' in metric_key or 'correlation' in metric_key or 'confidence' in metric_key:
                    formatted_value = f"{value:.3f}"
                else:
                    formatted_value = f"{value:.2f}"
            else:
                formatted_value = str(value)

            table_data.append([metric_name, formatted_value, description])

        table = Table(table_data)
        table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary_medium']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            # Data rows styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, self.colors['background_medium']),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        self.story.append(table)
        self.story.append(Spacer(1, 20))
    
    def add_charts(self, chart_files: List[str]):
        """
        Add charts to the report
        
        Args:
            chart_files: List of chart file paths
        """
        # Log chart embedding attempt
        logger.info(f"Chart embedding attempt - received {len(chart_files) if chart_files else 0} chart files")
        
        if not chart_files:
            # Even if no charts are available, add a section header to maintain report structure
            logger.info("No chart files provided to add_charts method")
            self._add_section_header("TECHNICAL CHARTS")
            self.story.append(Paragraph("No technical charts are currently available in this report.", self.body_text_style))
            self.story.append(Spacer(1, 20))
            return
            
        # Filter to only include existing chart files
        existing_chart_files = [chart_path for chart_path in chart_files if os.path.exists(chart_path)]
        logger.info(f"Out of {len(chart_files)} provided chart files, {len(existing_chart_files)} exist on disk")
        
        # Log the missing files for debugging
        missing_files = [chart_path for chart_path in chart_files if not os.path.exists(chart_path)]
        if missing_files:
            logger.warning(f"Missing chart files: {missing_files}")
        
        if not existing_chart_files:
            logger.warning("No existing chart files found to embed in the report")
            self._add_section_header("TECHNICAL CHARTS")
            self.story.append(Paragraph("No technical charts are currently available in this report.", self.body_text_style))
            self.story.append(Spacer(1, 20))
            # Summarize chart embedding attempts and issues found in prompt-updates.md
            with open("/Users/pawan/CLI-Finance-Terminal/prompt-updates.md", "a") as f:
                f.write(f"\n### Chart Embedding Debug Summary\n- **Status:** Attempted embedding {len(chart_files)} files, {len(existing_chart_files)} exist on disk\n- **Missing files:** {missing_files}\n- **Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            return
            
        logger.info(f"Attempting to embed {len(existing_chart_files)} existing chart files in the report")
        self._add_section_header("TECHNICAL CHARTS")
        
        # Reorder charts according to meta-prompt specification:
        # 1. VIX Chart
        # 2. Major Global Indices (Asia, Europe+UK, Americas) in the order specified previously.
        # 3. Major Currencies
        # 4. Major Commodities
        # 5. Major Bonds/ETFs
        reordered_chart_files = []
        
        # Define symbol categories for reordering
        vix_charts = []
        asia_indices_charts = []
        euro_uk_indices_charts = []
        americas_indices_charts = []
        currency_charts = []
        commodity_charts = []
        bonds_etf_charts = []
        other_charts = []
        
        for chart_path in existing_chart_files:
            symbol = os.path.basename(chart_path).replace('_matplotlib.png', '').replace('_candlestick.png', '').replace('_ascii.txt', '')
            
            # Identify chart type based on symbol
            if 'VIX' in symbol.upper():
                vix_charts.append(chart_path)
            elif any(idx in symbol for idx in ['JP225Roll', 'HK50Roll', 'CHINA50Roll', 'NIFTY_50', 'SENSEX']):
                asia_indices_charts.append(chart_path)
            elif any(idx in symbol for idx in ['DE40Roll', 'FRA40Roll', 'UK100Roll']):
                euro_uk_indices_charts.append(chart_path)
            elif any(idx in symbol for idx in ['US500Roll', 'US30Roll', 'UT100Roll']):
                americas_indices_charts.append(chart_path)
            elif any(curr in symbol for curr in ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD']):
                currency_charts.append(chart_path)
            elif any(comm in symbol for comm in ['XAUUSD', 'XAGUSD', 'XPTUSD', 'USOIL', 'UKOIL']):
                commodity_charts.append(chart_path)
            elif any(bond in symbol for bond in ['TLT', 'IEF', 'SHY', 'IEI', 'TLH', 'LQD', 'TLTD', 'IGIB', 'TLTE', 'CBON', 'BNDX', 'VWOY', 'EMB', 'EMLC', 'WIP', 'GLD', 'SLV', 'PPLT', 'IAU', 'USO', 'UNG', 'DBO', 'DBP', 'JJC', 'TIP', 'VTIAX', 'SCHP', 'VTIP', 'BIL']):
                bonds_etf_charts.append(chart_path)
            else:
                other_charts.append(chart_path)
        
        # Combine in the required order
        reordered_chart_files.extend(vix_charts)
        reordered_chart_files.extend(asia_indices_charts)
        reordered_chart_files.extend(euro_uk_indices_charts)
        reordered_chart_files.extend(americas_indices_charts)
        reordered_chart_files.extend(currency_charts)
        reordered_chart_files.extend(commodity_charts)
        reordered_chart_files.extend(bonds_etf_charts)
        reordered_chart_files.extend(other_charts)
        
        # Add charts in groups of 2 per page for better layout
        for i in range(0, min(len(reordered_chart_files), 12), 2):  # Limit to first 12 charts
            chart_row = reordered_chart_files[i:i+2]
            
            # Add first chart
            if len(chart_row) >= 1:
                chart_path = chart_row[0]
                logger.info(f"After chart creation - confirmed chart file exists: {chart_path}")
                try:
                    # Get symbol from filename
                    symbol = os.path.basename(chart_path).replace('_matplotlib.png', '').replace('_candlestick.png', '').replace('_ascii.txt', '')
                    
                    # Create user-friendly chart titles
                    friendly_name = symbol
                    if symbol in self.symbol_map:
                        friendly_name = self.symbol_map[symbol].replace(" (CFD)", "")  # Remove CFD suffix for display
                    elif symbol == "VIX":
                        friendly_name = "VIX Volatility Index"
                    elif symbol == "NIFTY_50":
                        friendly_name = "NIFTY 50"
                    elif symbol == "SENSEX":
                        friendly_name = "BSE SENSEX"
                    elif symbol == "XAUUSD":
                        friendly_name = "Gold (XAU/USD)"
                    elif symbol == "XAGUSD":
                        friendly_name = "Silver (XAG/USD)"
                    elif symbol == "USOIL":
                        friendly_name = "Crude Oil (USOIL)"
                    elif symbol == "UKOIL":
                        friendly_name = "Brent Oil (UKOIL)"
                    # Add more mappings as needed
                    
                    logger.info(f"Before embedding in PDF - attempting to embed chart: {chart_path} for symbol {symbol}")
                    self.story.append(Paragraph(f"<b>{friendly_name}</b> Technical Analysis", self.subsection_header_style))
                    
                    # Add chart image
                    img = Image(chart_path, width=6*inch, height=3*inch)
                    logger.info(f"Created Image object for {chart_path}")
                    self.story.append(img)
                    logger.info(f"Successfully embedded chart image: {chart_path}")
                    self.story.append(Spacer(1, 15))
                except Exception as e:
                    logger.error(f"Error adding chart {chart_path}: {e}")
                    # Add a placeholder message if chart can't be added
                    self.story.append(Paragraph(f"⚠️ Chart image could not be displayed: {os.path.basename(chart_path)}", self.body_text_style))
                    self.story.append(Spacer(1, 15))
        
            # Add second chart if available
            if len(chart_row) >= 2:
                chart_path = chart_row[1]
                logger.info(f"After chart creation - confirmed chart file exists: {chart_path}")
                try:
                    # Get symbol from filename
                    symbol = os.path.basename(chart_path).replace('_matplotlib.png', '').replace('_candlestick.png', '').replace('_ascii.txt', '')
                    
                    # Create user-friendly chart titles
                    friendly_name = symbol
                    if symbol in self.symbol_map:
                        friendly_name = self.symbol_map[symbol].replace(" (CFD)", "")  # Remove CFD suffix for display
                    elif symbol == "VIX":
                        friendly_name = "VIX Volatility Index"
                    elif symbol == "NIFTY_50":
                        friendly_name = "NIFTY 50"
                    elif symbol == "SENSEX":
                        friendly_name = "BSE SENSEX"
                    elif symbol == "XAUUSD":
                        friendly_name = "Gold (XAU/USD)"
                    elif symbol == "XAGUSD":
                        friendly_name = "Silver (XAG/USD)"
                    elif symbol == "USOIL":
                        friendly_name = "Crude Oil (USOIL)"
                    elif symbol == "UKOIL":
                        friendly_name = "Brent Oil (UKOIL)"
                    # Add more mappings as needed
                    
                    logger.info(f"Before embedding in PDF - attempting to embed chart: {chart_path} for symbol {symbol}")
                    self.story.append(Paragraph(f"<b>{friendly_name}</b> Technical Analysis", self.subsection_header_style))
                    
                    # Add chart image
                    img = Image(chart_path, width=6*inch, height=3*inch)
                    logger.info(f"Created Image object for {chart_path}")
                    self.story.append(img)
                    logger.info(f"Successfully embedded chart image: {chart_path}")
                    self.story.append(Spacer(1, 15))
                except Exception as e:
                    logger.error(f"Error adding chart {chart_path}: {e}")
                    # Add a placeholder message if chart can't be added
                    self.story.append(Paragraph(f"⚠️ Chart image could not be displayed: {os.path.basename(chart_path)}", self.body_text_style))
                    self.story.append(Spacer(1, 15))
            
            self.story.append(Spacer(1, 20))
        
        logger.info(f"Successfully embedded {len(existing_chart_files)} chart files in the report")
        # Summarize chart embedding attempts and issues found in prompt-updates.md
        with open("/Users/pawan/CLI-Finance-Terminal/prompt-updates.md", "a") as f:
            f.write(f"\n### Chart Embedding Summary\n- **Status:** Successfully embedded {len(existing_chart_files)} out of {len(chart_files)} requested chart files\n- **Files processed:** {existing_chart_files}\n- **Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    def add_disclaimer(self):
        """Add legal disclaimer"""
        self._add_section_header("DISCLAIMER")
        
        disclaimer_text = (
            "This report is prepared by Quantwater Tech Investments for informational purposes only. "
            "The information contained herein is based on sources believed to be reliable, but we do not represent "
            "that it is accurate or complete. Nothing contained herein should be considered as an offer to sell or "
            "buy any securities, nor shall it be deemed to be investment advice. Past performance is not indicative "
            "of future results. Investment decisions should be made based on your own research and risk tolerance. "
            "This document contains confidential information and may not be reproduced or distributed without prior consent."
        )
        
        self.story.append(Paragraph(disclaimer_text, self.disclaimer_style))
        self.story.append(Spacer(1, 20))
    
    def add_compliance_footer(self):
        """Add compliance footer to each page"""
        # This would be implemented in a custom canvas class
        pass
    
    def generate(self):
        """Generate the professional PDF report"""
        try:
            self.doc.build(self.story)
            logger.info(f"Enhanced institutional PDF report generated: {self.filename}")
            return self.filename
        except KeyError as e:
            logger.error(f"KeyError generating enhanced institutional PDF report: Missing key {e}")
            # Try to continue with a minimal report
            raise
        except Exception as e:
            logger.error(f"Error generating enhanced institutional PDF report: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            raise

# Example usage
if __name__ == "__main__":
    # Create sample data for testing
    sample_indices = pd.DataFrame([
        {'name': 'EURUSD', 'description': 'Euro vs US Dollar', 'ask': 1.05, 'bid': 1.049, 'spread': 0.001},
        {'name': 'GBPUSD', 'description': 'British Pound vs US Dollar', 'ask': 1.25, 'bid': 1.249, 'spread': 0.001},
        {'name': 'XAUUSD', 'description': 'Gold vs US Dollar', 'ask': 1900.50, 'bid': 1900.20, 'spread': 0.30},
    ])
    
    sample_calendar = pd.DataFrame([
        {
            'date': '2023-10-15',
            'time': '13:30',
            'currency': 'USD',
            'event': 'Non-Farm Payrolls',
            'importance': 'High',
            'actual': '250K',
            'forecast': '198K',
            'previous': '229K'
        },
        {
            'date': '2023-10-15',
            'time': '14:00',
            'currency': 'USD',
            'event': 'FOMC Decision',
            'importance': 'Very High',
            'actual': '5.25%',
            'forecast': '5.25%',
            'previous': '5.25%'
        },
        {
            'date': '2025-09-19',
            'time': '22:30',
            'currency': 'USD',
            'event': 'CFTC Aluminium Non-Commercial Net Positions',
            'importance': 'Low',
            'actual': '1.2K',
            'forecast': '',
            'previous': '1.2K'
        }
    ])
    
    # Create enhanced report generator
    pdf_gen = EnhancedInstitutionalPDFReportGenerator("enhanced_institutional_report.pdf")
    
    # Add cover page
    pdf_gen.add_cover_page()
    
    # Add table of contents
    pdf_gen.add_table_of_contents()
    
    # Add title
    pdf_gen.story.append(Paragraph("Daily Investment Report", pdf_gen.title_style))
    pdf_gen.story.append(Spacer(1, 20))
    
    # Add executive summary
    summary_points = [
        "Markets opened with mixed sentiment amid ongoing geopolitical tensions",
        "S&P 500 futures indicate a potential 0.3% gain at market open",
        "Oil prices rose 1.2% following supply concerns in the Middle East",
        "USD weakened against major currencies ahead of Federal Reserve decision"
    ]
    pdf_gen.add_executive_summary(summary_points)
    
    # Add market overview
    market_status = {
        'status': 'Open',
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), # Use UTC time
        'timezone': 'UTC'
    }
    pdf_gen.add_market_overview(market_status, sample_indices)
    
    # Add indices table
    pdf_gen.add_indices_table(sample_indices)
    
    # Add currencies table
    pdf_gen.add_currencies_table(sample_indices)
    
    # Add commodities table
    pdf_gen.add_commodities_table(sample_indices)
    
    # Add bonds table
    pdf_gen.add_bonds_table(sample_indices)
    
    # Add volatility table
    pdf_gen.add_volatility_table(sample_indices)
    
    # Add top movers table
    top_movers = sample_indices.copy()
    top_movers['change'] = [0.001, 0.002, 5.0]
    top_movers['pct_change'] = [0.1, 0.16, 0.26]
    top_movers['volume'] = [1000000, 500000, 50000]
    top_movers['symbol'] = ['EURUSD', 'GBPUSD', 'XAUUSD']
    pdf_gen.add_top_movers_table(top_movers)
    
    # Add calendar events
    pdf_gen.add_calendar_events(sample_calendar)
    
    # Add volatility summary
    volatility_summary = pd.DataFrame([
        {
            'symbol': 'EURUSD',
            'current_atr': 0.0030,
            'current_volatility': 0.0026,
            'regime': 'Normal Market',
            'confidence': 0.85
        }
    ])
    pdf_gen.add_volatility_summary(volatility_summary)
    
    # Add risk metrics
    risk_metrics = {
        'sharpe_ratio': 1.25,
        'sortino_ratio': 1.85,
        'max_drawdown': -0.15,
        'var_95': -0.035,
        'cvar_95': -0.052,
        'beta': 1.15,
        'alpha': 0.02,
        'volatility_annualized': 0.22
    }
    pdf_gen.add_risk_metrics(risk_metrics)
    
    # Add disclaimer
    pdf_gen.add_disclaimer()
    
    # Generate PDF
    pdf_gen.generate()
    
    print("✅ Enhanced institutional PDF report generated successfully!")
