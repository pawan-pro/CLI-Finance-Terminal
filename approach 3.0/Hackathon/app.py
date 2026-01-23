from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import sys
import duckdb
import pandas as pd
from datetime import datetime, timedelta

# Path Setup
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(base_dir, 'src'))

from analytics.metrics_engine import MarketPulse
from ai.research_copilot import ResearchCopilot

DB_PATH = "/Users/pawan/CLI-Finance-Terminal/approach 3.0/Hackathon/data/silver/market_data.duckdb"

# AI CACHE: Prevents 429 Errors
ai_cache = {"report": None, "expiry": datetime.now()}

app = FastAPI(title="Quantwater Nexus Bridge")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/market")
async def get_market_data():
    try:
        engine = MarketPulse()
        df = engine.get_snapshot()
        if df.empty: return []
        # Return exact keys expected by Nexus UI
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/calendar")
async def get_calendar_data():
    try:
        conn = duckdb.connect(DB_PATH)
        # Ensure 'ctry' uses the Currency code and 'event' is the clean name
        df = conn.execute("""
            SELECT 
                strftime(time_utc + INTERVAL 5 HOURS + INTERVAL 30 MINUTES, '%H:%M') as time,
                currency as ctry,
                event_name as event,
                COALESCE(CAST(actual AS VARCHAR), '---') as act,
                COALESCE(CAST(forecast AS VARCHAR), '---') as fcst
            FROM economic_events 
            ORDER BY time_utc DESC 
            LIMIT 10
        """).df()
        conn.close()
        return df.to_dict(orient="records")
    except:
        return []

@app.get("/api/research")
async def get_ai_research():
    global ai_cache
    # Return cached report if valid (10 min cache)
    if ai_cache["report"] and datetime.now() < ai_cache["expiry"]:
        return {"report": ai_cache["report"], "cached": True}
    
    try:
        copilot = ResearchCopilot()
        note = copilot.generate_intelligence_note()
        # Update cache
        ai_cache["report"] = note
        ai_cache["expiry"] = datetime.now() + timedelta(minutes=10)
        return {"report": note, "generated_at": datetime.now().strftime('%H:%M:%S UTC')}
    except Exception as e:
        # Fallback to cache even if expired if we hit 429
        if ai_cache["report"]:
            return {"report": ai_cache["report"], "error": "Rate limit hit, showing cached data."}
        return {"report": "AI Strategist currently busy. Please wait.", "error": str(e)}

@app.get("/api/sparkline/{symbol}")
async def get_sparkline(symbol: str):
    try:
        engine = MarketPulse()
        history = engine.get_sparkline_data(symbol)
        return {"symbol": symbol, "data": history}
    except:
        return {"symbol": symbol, "data": []}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)