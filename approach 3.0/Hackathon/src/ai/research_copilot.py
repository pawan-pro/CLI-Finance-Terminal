import warnings
import os
import duckdb
from dotenv import load_dotenv

# Silence library warnings for clean CLI
warnings.filterwarnings("ignore")
os.environ["GRPC_VERBOSITY"] = "NONE"

import google.generativeai as genai
from analytics.metrics_engine import MarketPulse

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class ResearchCopilot:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-3-flash-preview')

    def generate_intelligence_note(self):
        pulse = MarketPulse()
        market_data = pulse.get_snapshot(limit=10).to_json(orient='records')
        
        # Fetch high-impact events from the last 24h
        conn = duckdb.connect(pulse.db_path)
        events = conn.execute("""
            SELECT event_name, actual, forecast, currency
            FROM economic_events 
            WHERE impact = 'High' 
            ORDER BY time_utc DESC LIMIT 5
        """).df().to_json(orient='records')
        conn.close()

        prompt = f"""
        You are the Quantwater Head Market Strategist. 
        Analyze this session data from our Proprietary Lake.
        
        MARKET MOVERS (JSON): {market_data}
        MACRO EVENTS (JSON): {events}

        TASK: Write a 3-bullet Institutional Briefing.
        1. CORRELATION: Link the top price move to the most relevant macro event if applicable.
        2. ANOMALY: Flag any move that seems technical (no matching event).
        3. RISK: Identify the most 'crowded' or 'overheated' trade right now.
        """
        
        response = self.model.generate_content(prompt)
        return response.text