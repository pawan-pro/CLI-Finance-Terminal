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
        bond_query = conn.execute("""
            SELECT 
                (SELECT close FROM m15_bars WHERE symbol = 'US10Y.px' ORDER BY time_utc DESC LIMIT 1) as p10,
                (SELECT close FROM m15_bars WHERE symbol = 'US02Y.px' ORDER BY time_utc DESC LIMIT 1) as p02
        """).df()
        conn.close()
        
        if not bond_query.empty and bond_query['p02'].iloc[0] > 0:
            ratio = bond_query['p10'].iloc[0] / bond_query['p02'].iloc[0]
            bond_context = f"Bond Price Ratio (10Y/2Y): {ratio:.4f}. (Falling ratio = Yield Curve Steepening)."
        else:
            bond_context = "Bond Term Structure: Data Pending"

        prompt = f"""
        You are the Quantwater Head Strategist.
        MARKET DATA: {market_data}
        TOP MOVER NEWS ({top_symbol}): {headlines}
        FIXED INCOME CONTEXT: {bond_context}
        
        TASK: Write a 3-bullet briefing.
        1. NARRATIVE: Explain {top_symbol} move using news.
        2. MACRO: Define the regime (Reflation vs Recession) using Bond Context.
        3. RISK: Identify the most 'dangerous' trade based on velocity.
        """
        response = self.model.generate_content(prompt)
        return response.text