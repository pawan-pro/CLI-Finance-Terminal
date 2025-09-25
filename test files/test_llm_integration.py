#!/usr/bin/env python3
"""
Test script for LLM integration
"""

import pandas as pd
from src.analysis.llm_integration import LLMExecutiveSummaryGenerator

def create_sample_data():
    """Create sample market data for testing"""
    # Sample indices data
    indices_data = pd.DataFrame([
        {'name': 'US500Roll', 'Price': 5820.50, 'pct_change_24h': 0.75},
        {'name': 'US30Roll', 'Price': 39850.25, 'pct_change_24h': -0.25},
        {'name': 'UT100Roll', 'Price': 22450.75, 'pct_change_24h': 1.10},
        {'name': 'DE40Roll', 'Price': 18750.30, 'pct_change_24h': 0.45},
        {'name': 'UK100Roll', 'Price': 8250.60, 'pct_change_24h': -0.15}
    ])
    
    # Sample currency data
    currency_data = pd.DataFrame([
        {'name': 'EURUSD', 'Price': 1.0850, 'pct_change_24h': 0.25},
        {'name': 'GBPUSD', 'Price': 1.2725, 'pct_change_24h': -0.10},
        {'name': 'USDJPY', 'Price': 149.85, 'pct_change_24h': 0.35},
        {'name': 'USDCHF', 'Price': 0.9120, 'pct_change_24h': -0.05},
        {'name': 'AUDUSD', 'Price': 0.6520, 'pct_change_24h': 0.15}
    ])
    
    # Sample commodities data
    commodities_data = pd.DataFrame([
        {'name': 'XAUUSD', 'Price': 2350.75, 'pct_change_24h': 0.55},
        {'name': 'XAGUSD', 'Price': 27.85, 'pct_change_24h': -0.30},
        {'name': 'USOIL', 'Price': 78.45, 'pct_change_24h': 1.20},
        {'name': 'UKOIL', 'Price': 82.30, 'pct_change_24h': 0.95}
    ])
    
    # Sample top movers data
    top_movers = pd.DataFrame([
        {'name': 'USOIL', 'Price': 78.45, 'pct_change': 1.20},
        {'name': 'UT100Roll', 'Price': 22450.75, 'pct_change': 1.10},
        {'name': 'USDJPY', 'Price': 149.85, 'pct_change': 0.35},
        {'name': 'XAUUSD', 'Price': 2350.75, 'pct_change': 0.55},
        {'name': 'DE40Roll', 'Price': 18750.30, 'pct_change': 0.45}
    ])
    
    # Sample calendar data
    calendar_data = pd.DataFrame([
        {
            'Name': 'US Non-Farm Payrolls',
            'Currency': 'USD',
            'Impact': 'High',
            'Actual': '250K',
            'Forecast': '200K',
            'Previous': '175K'
        },
        {
            'Name': 'Eurozone CPI',
            'Currency': 'EUR',
            'Impact': 'High',
            'Actual': '2.4%',
            'Forecast': '2.6%',
            'Previous': '2.8%'
        },
        {
            'Name': 'Bank of England Interest Rate Decision',
            'Currency': 'GBP',
            'Impact': 'High',
            'Actual': '5.00%',
            'Forecast': '5.00%',
            'Previous': '5.00%'
        }
    ])
    
    return indices_data, currency_data, commodities_data, top_movers, calendar_data

def test_llm_integration():
    """Test the LLM integration"""
    print("Testing LLM integration...")
    
    # Create sample data
    indices_data, currency_data, commodities_data, top_movers, calendar_data = create_sample_data()
    
    # Initialize LLM generator
    llm_generator = LLMExecutiveSummaryGenerator()
    
    # Generate executive summary
    print("\nGenerating AI-powered executive summary...")
    summary_points = llm_generator.generate_executive_summary(
        indices_data, currency_data, commodities_data, top_movers, calendar_data
    )
    
    # Print results
    print("\nAI-Generated Executive Summary:")
    print("-" * 40)
    for i, point in enumerate(summary_points, 1):
        print(f"{i}. {point}")

if __name__ == "__main__":
    test_llm_integration()