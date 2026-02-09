import os
import requests
from google import genai
from google.genai import types
from dotenv import load_dotenv
from analytics.metrics_engine import MarketPulse

load_dotenv()

class ResearchCopilot:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model_id = "gemini-3-flash-preview"
        self.news_api_key = "4ac357ac9bf64b83ba8bfb5fc86f11b6"

    def fetch_live_news(self, symbol):
        """Fetches real headlines from NewsAPI.org - FORCED ENGLISH & FINANCE"""
        query_map = {
            "US10Y": "Treasury yields", "GOLD": "Gold prices", 
            "UT100": "Nasdaq 100", "US500": "S&P 500", "WTI": "Crude Oil"
        }
        query = query_map.get(symbol, symbol)
        
        # Tightened query for English, PublishedAt, and Finance context
        url = (
            f"https://newsapi.org/v2/everything?"
            f"q={query}%20finance&" 
            f"language=en&"
            f"sortBy=publishedAt&"
            f"pageSize=5&"
            f"apiKey={self.news_api_key}"
        )
        try:
            r = requests.get(url).json()
            articles = r.get("articles", [])
            return [{"title": a["title"], "source": a["source"]["name"]} for a in articles]
        except:
            return []

    def generate_intelligence_note(self):
        pulse = MarketPulse()
        df = pulse.get_snapshot(limit=10)
        market_data = df.to_json(orient='records')
        
        # SYSTEM PROMPT REFINEMENT: Remove excessive asterisks
        prompt = f"""
        You are the QUANTWATER LEAD STRATEGIST. Write a crisp market brief.
        DATA LAKE SNAPSHOT: {market_data}.
        
        STRICT STYLE GUIDE:
        1. Use '#' for main headers and '##' for sub-headers.
        2. DO NOT use double asterisks (**) for emphasis. Use ALL CAPS for asset names instead.
        3. Use bullet points for causal links.
        4. Output must look like a high-end financial wire (Reuters/Bloomberg).
        """

        try:
            # Fixed configuration for Gemini 3 Flash
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"Strategist is reviewing deep-book liquidity. (Note: {str(e)})"