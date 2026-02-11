from typing import List
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import sys
import duckdb
import pandas as pd
from datetime import datetime, timedelta

# Path Setup
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(base_dir, 'backend'))

from analytics.metrics_engine import MarketPulse
from ai.research_copilot import ResearchCopilot
from google.genai import types

DB_PATH = os.path.join(base_dir, "market_data.duckdb")

# AI CACHE: Prevents 429 Errors
ai_cache = {"report": None, "expiry": datetime.now()}
last_ai_request_time = datetime.now() - timedelta(seconds=10)

app = FastAPI(title="Quantwater Nexus Bridge")

@app.post("/api/ai/chat")
async def ai_chat_bridge(data: dict):
    try:
        user_message = data.get("message")
        context = data.get("context", {})
        symbol = context.get("symbol", "Global")
        history = data.get("history", [])
        
        copilot = ResearchCopilot()
        news = copilot.fetch_live_news(symbol)
        
        # Inject conversation history if available
        history_str = ""
        if history:
            history_str = "Conversation History:\n" + "\n".join([f"{m.get('role').upper()}: {m.get('content')}" for m in history]) + "\n\n"

        system_instruction = (
            "You are the Quantwater Lead Strategist. Write a crisp, institutional research note. "
            "STRICT FORMATTING RULES: "
            "1. DO NOT use excessive bolding (**). Only use bolding for section headers. "
            "2. Use UPPERCASE for major asset names. "
            "3. Focus on 'Causal Reasoning'—link price moves to specific macro drivers. "
            "4. Output must look like a Bloomberg terminal brief, not a conversational chat."
        )
        prompt = f"{history_str}Market Context: {context}\nRecent Headlines: {news}\n\nUser Question: {user_message}"
        
        response = copilot.client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction
            )
        )
        return {"response": response.text}
    except Exception as e:
        return {"response": "Strategist busy.", "error": str(e)}

@app.get("/api/news/{symbol:path}")
async def get_news(symbol: str):
    copilot = ResearchCopilot()
    headlines = copilot.fetch_live_news(symbol)
    return {"headlines": headlines}

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
async def get_calendar():
    try:
        conn = duckdb.connect(DB_PATH)
        # Use strftime to include the Day and Month
        # Use COALESCE and NULLIF to force 'nan' strings into '---'
        df = conn.execute("""
            SELECT 
                strftime(time_utc + INTERVAL 5 HOURS + INTERVAL 30 MINUTES, '%d %b %H:%M') as time, 
                currency as ctry, 
                event_name as event, 
                CASE 
                    WHEN actual IS NULL OR CAST(actual AS VARCHAR) = 'nan' THEN '---' 
                    ELSE CAST(actual AS VARCHAR) 
                END as act, 
                CASE 
                    WHEN forecast IS NULL OR CAST(forecast AS VARCHAR) = 'nan' THEN '---' 
                    ELSE CAST(forecast AS VARCHAR) 
                END as fcst 
            FROM economic_events 
            WHERE impact = 'High'
            ORDER BY time_utc DESC 
            LIMIT 15
        """).df()
        conn.close()
        return df.to_dict(orient="records")
    except Exception as e:
        print(f"Calendar API Error: {e}")
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
        ai_cache["expiry"] = datetime.now() + timedelta(minutes=15)
        return {"report": note, "generated_at": datetime.now().strftime('%H:%M:%S UTC')}
    except Exception as e:
        # Fallback to cache even if expired if we hit 429
        if ai_cache["report"]:
            return {"report": ai_cache["report"], "error": "Rate limit hit, showing cached data."}
        return {"report": "AI Strategist currently busy. Please wait.", "error": str(e)}

@app.get("/api/sparkline/{symbol:path}")
async def get_sparkline(symbol: str, range: str = Query("1D")):
    try:
        # LOGGING: See what the frontend is actually asking for
        print(f"📊 Requesting {symbol} with range: {range}")
        
        engine = MarketPulse()
        history = engine.get_sparkline_data(symbol, timeframe_range=range)
        return {"symbol": symbol, "data": history, "count": len(history)}
    except Exception as e:
        return {"symbol": symbol, "data": [], "error": str(e)}

@app.get("/api/correlation")
async def get_correlation():
    """Calculates Pearson correlation for core global assets."""
    try:
        conn = duckdb.connect(DB_PATH)
        # Select core assets for the 6x6 matrix
        symbols = ['US500Roll', 'UT100Roll', 'XAUUSD.sd', 'USOILRoll', 'US10Y.px', 'EURUSD.sd']

        # Pull last 100 bars and pivot
        df = conn.execute(f"""
            PIVOT (SELECT time_utc, symbol, close FROM m15_bars WHERE symbol IN {tuple(symbols)})
            ON symbol USING AVG(close) GROUP BY time_utc ORDER BY time_utc DESC LIMIT 100
        """).df().dropna()

        # Calculate matrix and convert to format React expects
        corr_matrix = df[symbols].corr().round(2).to_dict()
        conn.close()
        return corr_matrix
    except Exception as e:
        print(f"Correlation Error: {e}")
        return {}

@app.get("/api/multiple-market-data")
def get_multiple_market_data(
    symbols: str = Query(..., description="Comma-separated list of symbols"),
    timeframe: str = Query("15min", enum=["tick", "1min", "5min", "15min", "1H", "1D"]),
    limit: int = Query(100, ge=1, le=10000),
):
    """Get market data for multiple symbols."""
    try:
        conn = duckdb.connect(DB_PATH)

        # Map timeframe to table
        table_map = {
            "tick": "ticks",
            "1min": "m1_bars",
            "5min": "m5_bars",
            "15min": "m15_bars",
            "1H": "h1_bars",
            "1D": "d1_bars",
        }

        table = table_map.get(timeframe, "m15_bars")

        # Parse symbols from comma-separated string
        symbol_list = [s.strip() for s in symbols.split(',')]

        # Query data for multiple symbols
        placeholders = ",".join(["?" for _ in symbol_list])
        query = f"""
        SELECT time_utc, symbol, open, high, low, close, volume
        FROM {table}
        WHERE symbol IN ({placeholders})
        ORDER BY time_utc DESC, symbol
        LIMIT ?
        """
        result = conn.execute(query, symbol_list + [limit * len(symbol_list)]).fetchall()

        # Convert to list of dictionaries
        columns = ["time_utc", "symbol", "open", "high", "low", "close", "volume"]
        data = [dict(zip(columns, row)) for row in result]

        # Group by symbol
        grouped_data = {}
        for item in data[::-1]:  # Reverse to chronological order
            symbol = item["symbol"]
            if symbol not in grouped_data:
                grouped_data[symbol] = []
            grouped_data[symbol].append(item)

        conn.close()
        return {"data": grouped_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# New Vision Endpoint
@app.post("/api/vision/analyze")
async def analyze_chart_vision(data: dict):
    """
    Receives a base64 image of the chart.
    Uses Gemini 3 Flash Agentic Vision to analyze it.
    """
    import base64
    try:
        # Extract the base64 string
        image_str = data.get("image", "")
        if image_str.startswith('data:image'):
            image_data = image_str.split(",")[1]
        else:
            image_data = image_str

        # Decode the image
        image_bytes = base64.b64decode(image_data)

        # Use the ResearchCopilot client (already configured with GEMINI_API_KEY)
        copilot = ResearchCopilot()
        
        prompt = (
            "ACT AS THE QUANTWATER VISION ANALYST. "
            "STYLE: INSTITUTIONAL RESEARCH BRIEF. "
            "STRICT RULES: "
            "1. NO DOUBLE ASTERISKS (**). "
            "2. Use '#' for main headers and '##' for sub-headers. "
            "3. Use ALL CAPS for asset names (e.g., NASDAQ 100, GOLD). "
            "4. Structure: # VISION REPORT, ## TREND ANALYSIS, ## KEY LEVELS, ## CONCLUSION. "
            "5. Focus on visual evidence from the provided chart image."
        )

        # Create Part for image
        image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/png")

        # Generate content using the new SDK
        response = copilot.client.models.generate_content(
            model=copilot.model_id,
            contents=[prompt, image_part]
        )

        return {"analysis": response.text}
    except Exception as e:
        print(f"Vision error: {str(e)}")
        return {"analysis": f"Vision Module Error: {str(e)}"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)