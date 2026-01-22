from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import sys
import duckdb
import pandas as pd
from datetime import datetime, timedelta

# Path Setup: Ensure FastAPI can find your internal modules
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(base_dir, 'src'))

from analytics.metrics_engine import MarketPulse
from ai.research_copilot import ResearchCopilot

# Master DB Path
DB_PATH = "/Users/pawan/CLI-Finance-Terminal/approach 3.0/Hackathon/data/silver/market_data.duckdb"

app = FastAPI(title="Quantwater Nexus Bridge")

# 1. Enable CORS (Essential for React to talk to this server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local development
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Market Snapshot Endpoint
@app.get("/api/market")
async def get_market_data():
    """Returns the master board for the dashboard watchlist and sectors."""
    try:
        engine = MarketPulse()
        df = engine.get_snapshot()
        if df.empty:
            return []
        
        # Clean up timestamps for JSON serialization
        df['sync_ist'] = df['sync_ist'].dt.strftime('%H:%M %d %b')
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 3. Macro Calendar Endpoint
@app.get("/api/calendar")
async def get_calendar_data():
    """Returns high impact economic events from the lake."""
    try:
        conn = duckdb.connect(DB_PATH)
        df = conn.execute("""
            SELECT 
                time_utc + INTERVAL 5 HOURS + INTERVAL 30 MINUTES as time_ist,
                currency, event_name, impact, actual, forecast 
            FROM economic_events 
            WHERE impact = 'High' 
            ORDER BY time_utc DESC 
            LIMIT 20
        """).df()
        conn.close()
        
        if df.empty:
            return []

        df['time_ist'] = df['time_ist'].dt.strftime('%H:%M %d %b')
        return df.to_dict(orient="records")
    except Exception as e:
        return {"error": "Calendar table not yet initialized", "details": str(e)}

# 4. AI Research Briefing Endpoint
@app.get("/api/research")
async def get_ai_research():
    """Calls Gemini 1.5 to synthesize the latest market movement."""
    try:
        copilot = ResearchCopilot()
        note = copilot.generate_intelligence_note()
        return {"report": note, "generated_at": datetime.now().strftime('%H:%M:%S UTC')}
    except Exception as e:
        return {"report": "AI Strategist offline. Check API keys.", "error": str(e)}

# 5. Sparkline/Trend Data Endpoint
@app.get("/api/sparkline/{symbol}")
async def get_sparkline(symbol: str):
    """Returns last 10 points for the visual trendlines."""
    try:
        engine = MarketPulse()
        history = engine.get_sparkline_data(symbol)
        return {"symbol": symbol, "data": history}
    except Exception as e:
        return {"symbol": symbol, "data": []}

if __name__ == "__main__":
    # Start the server on port 8000
    print("🌊 Quantwater API Bridge Online | Listening on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)