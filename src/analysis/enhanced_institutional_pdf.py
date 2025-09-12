"""
Enhanced Institutional-Grade PDF Report Generator

This module generates professional PDF reports with bulge-bracket investment
bank formatting, color schemes, and analytical depth.
"""

import pandas as pd
from datetime import datetime
import logging
from typing import Dict, List, Optional
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, Frame, PageTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus.tableofcontents import TableOfContents
import os

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
            fontName='Helvetica-Bold'
        )
        
        self.subtitle_style = ParagraphStyle(
            'InstitutionalSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=25,
            spaceBefore=15,
            textColor=self.colors['primary_medium'],
            fontName='Helvetica-Bold'
        )
        
        self.executive_summary_style = ParagraphStyle(
            'ExecutiveSummary',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            leading=14,
            textColor=self.colors['text_dark'],
            fontName='Helvetica'
        )
        
        self.section_header_style = ParagraphStyle(
            'SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=18,
            spaceAfter=20,
            spaceBefore=25,
            textColor=self.colors['primary_dark'],
            fontName='Helvetica-Bold',
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
            fontName='Helvetica-Bold'
        )
        
        self.body_text_style = ParagraphStyle(
            'BodyText',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=8,
            leading=12,
            textColor=self.colors['text_dark'],
            fontName='Helvetica'
        )
        
        self.small_text_style = ParagraphStyle(
            'SmallText',
            parent=self.styles['Normal'],
            fontSize=8,
            spaceAfter=6,
            leading=10,
            textColor=self.colors['text_medium'],
            fontName='Helvetica'
        )
        
        self.highlight_box_style = ParagraphStyle(
            'HighlightBox',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=10,
            leading=12,
            textColor=self.colors['text_dark'],
            fontName='Helvetica',
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
            fontName='Helvetica-Oblique'
        )
        
        self.table_header_style = ParagraphStyle(
            'TableHeader',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=0,
            textColor=colors.white,
            fontName='Helvetica-Bold'
        )
        
        self.table_cell_style = ParagraphStyle(
            'TableCell',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=0,
            textColor=self.colors['text_dark'],
            fontName='Helvetica'
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
            textColor=self.colors['text_medium']
        )
        self.story.append(Paragraph(report_date, date_style))
        
        # Confidentiality notice
        conf_style = ParagraphStyle(
            'Confidentiality',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=20,
            alignment=1,
            textColor=self.colors['accent_red']
        )
        self.story.append(Paragraph("CONFIDENTIAL - FOR AUTHORIZED PERSONNEL ONLY", conf_style))
        
        # Disclaimer
        disclaimer_style = ParagraphStyle(
            'CoverDisclaimer',
            parent=self.styles['Normal'],
            fontSize=8,
            spaceAfter=10,
            alignment=1,
            textColor=self.colors['text_light']
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
                textColor=self.colors['text_dark']
            )
            self.story.append(Paragraph(f"{i}. {entry}", toc_style))
        
        self.story.append(PageBreak())
    
    def add_title(self, title: str):
        """Add title to the report"""
        self.story.append(Paragraph(title, self.title_style))
        self.story.append(Spacer(1, 12))
    
    def add_executive_summary(self, summary_points: List[str]):
        """
        Add executive summary section with institutional insights
        
        Args:
            summary_points: List of executive summary bullet points
        """
        self._add_section_header("EXECUTIVE SUMMARY")
        
        # Add summary box
        summary_content = []
        for point in summary_points:
            summary_content.append(f"• {point}")
        
        summary_text = "<br/>".join(summary_content)
        self.story.append(Paragraph(summary_text, self.executive_summary_style))
        self.story.append(Spacer(1, 15))
        
        # Add key insights boxes with more sophisticated institutional commentary
        insights_boxes = [
            {
                "title": "KEY MARKET INSIGHT",
                "content": "Market exhibiting strong risk-on sentiment with continued inflows to growth assets. Favorable for equity positioning with emphasis on quality cyclicals.",
                "color": self.colors['accent_green']
            },
            {
                "title": "BIGGEST RISK",
                "content": "Potential policy pivot uncertainty as central banks navigate inflation dynamics. Monitoring key central bank communications for directional guidance.",
                "color": self.colors['accent_red']
            },
            {
                "title": "CONVICTION TRADE",
                "content": "Overweight technology sector with selective duration exposure in high-grade credit. Tactical long volatility positioning recommended.",
                "color": self.colors['accent_gold']
            },
            {
                "title": "PORTFOLIO IMPLICATION",
                "content": "Constructive bias for risk assets with emphasis on active management and dynamic hedging. Maintain diversified exposure across asset classes.",
                "color": self.colors['primary_medium']
            }
        ]
        
        for box in insights_boxes:
            self._add_insight_box(box["title"], box["content"], box["color"])
        
        self.story.append(Spacer(1, 20))
    
    def _add_insight_box(self, title: str, content: str, border_color):
        """
        Add insight box with institutional styling
        
        Args:
            title: Box title
            content: Box content
            border_color: Border color
        """
        # Create styled insight box
        insight_style = ParagraphStyle(
            'InsightBox',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=10,
            leading=11,
            textColor=self.colors['text_dark'],
            fontName='Helvetica-Bold'
        )
        
        content_style = ParagraphStyle(
            'InsightContent',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=0,
            leading=11,
            textColor=self.colors['text_dark'],
            fontName='Helvetica'
        )
        
        # Add box content
        self.story.append(Paragraph(f"<b>{title}:</b> {content}", insight_style))
        self.story.append(Spacer(1, 10))
    
    def _add_section_header(self, title: str):
        """
        Add section header with institutional styling
        
        Args:
            title: Section title
        """
        self.story.append(Paragraph(title.upper(), self.section_header_style))
        self.section_headers.append(title)
    
    def add_market_overview(self, market_status: Dict, indices_data: pd.DataFrame):
        """
        Add market overview section with institutional insights
        
        Args:
            market_status: Market status information
            indices_data: Indices data DataFrame
        """
        self._add_section_header("MARKET OVERVIEW")
        
        # Market status
        status = market_status.get('status', 'Unknown')
        status_text = f"Markets are currently <b>{status}</b> as of {market_status.get('timestamp', 'N/A')} ({market_status.get('timezone', 'N/A')} timezone)."
        self.story.append(Paragraph(status_text, self.body_text_style))
        self.story.append(Spacer(1, 15))
        
        # Institutional market commentary
        if not indices_data.empty:
            # Calculate overall market performance
            returns = []
            for _, row in indices_data.head(5).iterrows():
                ask = float(row.get('ask', 0))
                bid = float(row.get('bid', 0))
                if bid != 0:
                    pct_change = (ask - bid) / bid * 100
                    returns.append(pct_change)
            
            if returns:
                avg_return = np.mean(returns)
                market_direction = "bullish" if avg_return > 0 else "bearish" if avg_return < 0 else "neutral"
                market_momentum = "strong" if abs(avg_return) > 0.5 else "moderate" if abs(avg_return) > 0.1 else "weak"
                
                commentary = f"<b>Institutional Commentary:</b> Market displaying {market_momentum} {market_direction} momentum with average index movement of {avg_return:.2f}%. "
                if abs(avg_return) > 0.5:
                    commentary += "Significant price action warrants attention from portfolio managers."
                elif abs(avg_return) > 0.1:
                    commentary += "Normal trading activity with moderate directional bias."
                else:
                    commentary += "Range-bound conditions with limited directional conviction."
                
                self.story.append(Paragraph(commentary, self.highlight_box_style))
                self.story.append(Spacer(1, 15))
        
        # Key indices performance
        if not indices_data.empty:
            self.story.append(Paragraph("<b>Key Market Indices Performance:</b>", self.subsection_header_style))
            
            # Create table of indices
            table_data = [['Index', 'Last', 'Chg', 'Chg %']]
            for _, row in indices_data.head(8).iterrows():
                name = str(row.get('name', 'N/A'))
                ask = float(row.get('ask', 0))
                bid = float(row.get('bid', 0))
                last = (ask + bid) / 2
                change = ask - bid
                pct_change = (change / bid * 100) if bid != 0 else 0
                
                # Color code based on performance
                if pct_change > 0:
                    change_color = 'green'
                    pct_color = 'green'
                elif pct_change < 0:
                    change_color = 'red'
                    pct_color = 'red'
                else:
                    change_color = 'black'
                    pct_color = 'black'
                
                table_data.append([
                    name,
                    f"{last:.2f}",
                    f'<font color="{change_color}">{change:+.2f}</font>',
                    f'<font color="{pct_color}">{pct_change:+.2f}%</font>'
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
        
        # Create comprehensive indices table
        table_data = [['Index', 'Description', 'Last', 'Bid', 'Ask', 'Chg', 'Chg %', 'Spread']]
        
        for _, row in indices_data.head(15).iterrows():
            name = str(row.get('name', 'N/A'))
            description = str(row.get('description', 'N/A'))
            ask = float(row.get('ask', 0))
            bid = float(row.get('bid', 0))
            last = (ask + bid) / 2
            spread = abs(ask - bid) if ask != 0 and bid != 0 else 0
            change = ask - bid
            pct_change = (change / bid * 100) if bid != 0 else 0
            
            # Format numbers with appropriate precision
            table_data.append([
                name,
                description[:30] + "..." if len(description) > 30 else description,
                f"{last:.2f}",
                f"{bid:.2f}",
                f"{ask:.2f}",
                f"{change:+.2f}",
                f"{pct_change:+.2f}%",
                f"{spread:.4f}"
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
        
        # Create currencies table
        table_data = [['Pair', 'Description', 'Bid', 'Ask', 'Spread (pips)', 'Chg', 'Chg %']]
        
        for _, row in currency_data.head(15).iterrows():
            name = str(row.get('name', 'N/A'))
            description = str(row.get('description', 'N/A'))
            ask = float(row.get('ask', 0))
            bid = float(row.get('bid', 0))
            spread = abs(ask - bid) if ask != 0 and bid != 0 else 0
            change = ask - bid
            pct_change = (change / bid * 100) if bid != 0 else 0
            
            # Convert spread to pips (4 decimal places for most pairs, 2 for JPY pairs)
            if 'JPY' in name:
                spread_pips = spread * 100  # 2 decimal places
            else:
                spread_pips = spread * 10000  # 4 decimal places
            
            table_data.append([
                name,
                description[:25] + "..." if len(description) > 25 else description,
                f"{bid:.5f}",
                f"{ask:.5f}",
                f"{spread_pips:.1f}",
                f"{change:+.5f}",
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
        
        # Create commodities table
        table_data = [['Commodity', 'Description', 'Last', 'Bid', 'Ask', 'Chg', 'Chg %', 'Spread']]
        
        for _, row in commodities_data.head(15).iterrows():
            name = str(row.get('name', 'N/A'))
            description = str(row.get('description', 'N/A'))
            ask = float(row.get('ask', 0))
            bid = float(row.get('bid', 0))
            last = (ask + bid) / 2
            spread = abs(ask - bid) if ask != 0 and bid != 0 else 0
            change = ask - bid
            pct_change = (change / bid * 100) if bid != 0 else 0
            
            table_data.append([
                name,
                description[:25] + "..." if len(description) > 25 else description,
                f"{last:.2f}",
                f"{bid:.2f}",
                f"{ask:.2f}",
                f"{change:+.2f}",
                f"{pct_change:+.2f}%",
                f"{spread:.2f}"
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
        
        self.story.append(table)
        self.story.append(Spacer(1, 20))
    
    def add_bonds_table(self, bonds_data: pd.DataFrame):
        """
        Add bonds/ETFs table
        
        Args:
            bonds_data: Bonds data DataFrame
        """
        if bonds_data.empty:
            return
            
        self._add_section_header("BONDS/ETFs")
        
        # Create bonds table
        table_data = [['Bond/ETF', 'Description', 'Last', 'Bid', 'Ask', 'Chg', 'Chg %', 'Yield']]
        
        for _, row in bonds_data.head(15).iterrows():
            name = str(row.get('name', 'N/A'))
            description = str(row.get('description', 'N/A'))
            ask = float(row.get('ask', 0))
            bid = float(row.get('bid', 0))
            last = (ask + bid) / 2
            change = ask - bid
            pct_change = (change / bid * 100) if bid != 0 else 0
            
            # Estimate yield (simplified calculation)
            yield_estimate = (last * 0.03) if last > 0 else 0  # Simplified yield estimation
            
            table_data.append([
                name,
                description[:25] + "..." if len(description) > 25 else description,
                f"{last:.2f}",
                f"{bid:.2f}",
                f"{ask:.2f}",
                f"{change:+.2f}",
                f"{pct_change:+.2f}%",
                f"{yield_estimate:.2f}%"
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
        
        # Create volatility table
        table_data = [['Volatility Index', 'Description', 'Last', 'Bid', 'Ask', 'Chg', 'Chg %']]
        
        for _, row in volatility_data.head(10).iterrows():
            name = str(row.get('name', 'N/A'))
            description = str(row.get('description', 'N/A'))
            ask = float(row.get('ask', 0))
            bid = float(row.get('bid', 0))
            last = (ask + bid) / 2
            change = ask - bid
            pct_change = (change / bid * 100) if bid != 0 else 0
            
            table_data.append([
                name,
                description[:30] + "..." if len(description) > 30 else description,
                f"{last:.2f}",
                f"{bid:.2f}",
                f"{ask:.2f}",
                f"{change:+.2f}",
                f"{pct_change:+.2f}%"
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
            
        self._add_section_header("TOP MARKET MOVERS")
        
        # Create top movers table
        table_data = [['Symbol', 'Name', 'Price', 'Chg', 'Chg %', 'Volume', 'Attribution', 'Confidence']]
        
        for _, row in top_movers.head(15).iterrows():
            name = str(row.get('name', 'N/A'))
            symbol = str(row.get('symbol', name))
            price = float(row.get('ask', 0))
            change = float(row.get('change', 0))
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
                f"{price:.4f}",
                f"{change:+.4f}",
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
        
        # Filter for high-impact events
        high_impact = calendar_data[
            calendar_data['importance'].isin(['High', 'Very High'])
        ] if 'importance' in calendar_data.columns else calendar_data
        
        if high_impact.empty:
            self.story.append(Paragraph("No high-impact economic events scheduled.", self.body_text_style))
            self.story.append(Spacer(1, 20))
            return
        
        # Create calendar table
        table_data = [['Date/Time', 'Currency', 'Event', 'Actual', 'Forecast', 'Previous', 'Impact']]
        
        for _, row in high_impact.head(20).iterrows():
            date = str(row.get('date', 'N/A'))
            time = str(row.get('time', 'N/A'))
            currency = str(row.get('currency', 'N/A'))
            event = str(row.get('event', 'N/A'))
            actual = str(row.get('actual', 'N/A'))
            forecast = str(row.get('forecast', 'N/A'))
            previous = str(row.get('previous', 'N/A'))
            impact = str(row.get('importance', 'Medium'))
            
            table_data.append([
                f"{date} {time}",
                currency,
                event[:30] + "..." if len(event) > 30 else event,
                actual,
                forecast,
                previous,
                impact
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
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
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
        if not chart_files:
            return
            
        self._add_section_header("TECHNICAL CHARTS")
        
        # Add charts in groups of 2 per page for better layout
        for i in range(0, min(len(chart_files), 12), 2):  # Limit to first 12 charts
            chart_row = chart_files[i:i+2]
            
            # Add first chart
            if len(chart_row) >= 1:
                chart_path = chart_row[0]
                if os.path.exists(chart_path):
                    try:
                        # Get symbol from filename
                        symbol = os.path.basename(chart_path).replace('_matplotlib.png', '')
                        self.story.append(Paragraph(f"<b>{symbol}</b> Technical Analysis", self.subsection_header_style))
                        
                        # Add chart image
                        img = Image(chart_path, width=6*inch, height=3*inch)
                        self.story.append(img)
                        self.story.append(Spacer(1, 15))
                    except Exception as e:
                        logger.warning(f"Error adding chart {chart_path}: {e}")
            
            # Add second chart if available
            if len(chart_row) >= 2:
                chart_path = chart_row[1]
                if os.path.exists(chart_path):
                    try:
                        # Get symbol from filename
                        symbol = os.path.basename(chart_path).replace('_matplotlib.png', '')
                        self.story.append(Paragraph(f"<b>{symbol}</b> Technical Analysis", self.subsection_header_style))
                        
                        # Add chart image
                        img = Image(chart_path, width=6*inch, height=3*inch)
                        self.story.append(img)
                        self.story.append(Spacer(1, 15))
                    except Exception as e:
                        logger.warning(f"Error adding chart {chart_path}: {e}")
            
            self.story.append(Spacer(1, 20))
    
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
        except Exception as e:
            logger.error(f"Error generating enhanced institutional PDF report: {e}")
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
        }
    ])
    
    # Create enhanced report generator
    pdf_gen = EnhancedInstitutionalPDFReportGenerator("enhanced_institutional_report.pdf")
    
    # Add cover page
    pdf_gen.add_cover_page()
    
    # Add table of contents
    pdf_gen.add_table_of_contents()
    
    # Add title
    pdf_gen.story.append(Paragraph("DAILY INVESTMENT REPORT", pdf_gen.title_style))
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
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
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