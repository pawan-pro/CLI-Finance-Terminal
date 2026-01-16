import warnings
import os
import duckdb
import requests
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

warnings.filterwarnings("ignore")
os.environ["GRPC_VERBOSITY"] = "NONE"

import google.generativeai as genai
from analytics.metrics_engine import MarketPulse

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class ResearchCopilot:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-3-flash-preview')

    def _get_headlines(self, symbol):
        """Zero-dependency news fetcher using Google News RSS"""
        mapping = {"US500Roll": "S&P500", "UT100Roll": "Nasdaq", "XAUUSD.sd": "Gold", "XAGUSD.sd": "Silver"}
        query = mapping.get(symbol, symbol.split('.')[0])
        url = f"https://news.google.com/rss/search?q={query}+finance&hl=en-US&gl=US&ceid=US:en"
        
        try:
            response = requests.get(url, timeout=5)
            root = ET.fromstring(response.content)
            return [item.find('title').text for item in root.findall('.//item')[:3]]
        except:
            return ["No recent headlines found."]

    def generate_intelligence_note(self):
        pulse = MarketPulse()
        df = pulse.get_snapshot(limit=10)
        if df.empty: return "No market data available."
        
        market_data = df.to_json(orient='records')
        top_symbol = df.iloc[0]['symbol']
        headlines = self._get_headlines(top_symbol)

        conn = duckdb.connect(pulse.db_path)
        # Fetch the spread we will ingest in Step 2
        spread_query = conn.execute("""
            SELECT 
                (SELECT close FROM m15_bars WHERE symbol = 'US10Y' ORDER BY time_utc DESC LIMIT 1) -
                (SELECT close FROM m15_bars WHERE symbol = 'US02Y' ORDER BY time_utc DESC LIMIT 1) as spread
        """).df()
        conn.close()
        
        yield_spread = f"{spread_query['spread'].iloc[0]:.4f}" if not spread_query.empty else "Data Pending"

        prompt = f"""
        You are the Quantwater Head Strategist.
        MARKET MOVERS: {market_data}
        TOP MOVER HEADLINES ({top_symbol}): {headlines}
        US 10Y-02Y YIELD SPREAD: {yield_spread}
        
        TASK: Write a 3-bullet briefing.
        1. NARRATIVE: Explain the {top_symbol} move using headlines.
        2. MACRO: Link the Yield Spread ({yield_spread}) to market regime (Recession vs Growth).
        3. RISK: Identify the most dangerous 'overcrowded' trade.
        """
        
        response = self.model.generate_content(prompt)
        return response.text