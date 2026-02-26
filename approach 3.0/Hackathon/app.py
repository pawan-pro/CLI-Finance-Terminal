import os
import sys
import urllib.request
import duckdb
import pandas as pd
import uvicorn
from typing import List
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

# ---------------------------------------------------------------------------
# Snapshot Loader — runs at process start before any route is served
# ---------------------------------------------------------------------------
_IS_CLOUD = not os.path.exists("/Users/pawan")

DB_PATH = os.environ.get(
    "DB_PATH",
    "data/silver/market_data.duckdb" if _IS_CLOUD
    else "/Users/pawan/CLI-Finance-Terminal/approach 3.0/Hackathon/data/silver/market_data.duckdb"
)

def _fetch_snapshot() -> None:
    if not _IS_CLOUD:
        print(f"[snapshot] Local mode — using {DB_PATH}")
        return

    import boto3
    from botocore.config import Config

    access_key = os.environ.get("R2_ACCESS_KEY_ID")
    secret_key = os.environ.get("R2_SECRET_ACCESS_KEY")
    endpoint   = os.environ.get("R2_ENDPOINT_URL")

    if not all([access_key, secret_key, endpoint]):
        raise RuntimeError("[snapshot] R2 credentials not set")

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    tmp_path = DB_PATH + ".tmp"

    print(f"[snapshot] Downloading via R2 S3 API")
    s3 = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=Config(signature_version="s3v4"),
    )
    s3.download_file("market-db", "market_data_latest.duckdb", tmp_path)

    size = os.path.getsize(tmp_path)
    if size < 512 * 1024:
        os.remove(tmp_path)
        raise RuntimeError(f"[snapshot] File too small ({size} bytes)")

    os.replace(tmp_path, DB_PATH)
    print(f"[snapshot] Ready: {size / 1024 / 1024:.1f} MB")

_fetch_snapshot()

# ---------------------------------------------------------------------------
# Path Setup
# ---------------------------------------------------------------------------
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(base_dir, 'src'))

from analytics.metrics_engine import MarketPulse
from ai.research_copilot import ResearchCopilot

# AI CACHE: Prevents 429 Errors
ai_cache = {"report": None, "expiry": datetime.now()}

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(title="Quantwater Nexus Bridge")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Health / Status
# ---------------------------------------------------------------------------
@app.get("/status")
async def status():
    try:
        conn = duckdb.connect(DB_PATH, read_only=True)
        row = conn.execute("SELECT MAX(time_utc) FROM m15_bars").fetchone()
        conn.close()
        latest = row[0].isoformat() if row and row[0] else "unknown"
        size_mb = round(os.path.getsize(DB_PATH) / 1024 / 1024, 1)
        return {
            "status": "ok",
            "db_path": DB_PATH,
            "db_size_mb": size_mb,
            "latest_bar_utc": latest,
            "snapshot_url": os.environ.get("DB_SNAPSHOT_URL", "local"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------------------------------------------------------
# Market Data
# ---------------------------------------------------------------------------
@app.get("/api/market")
async def get_market_data():
    try:
        engine = MarketPulse()
        df = engine.get_snapshot()
        if df.empty:
            return []
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/calendar")
async def get_calendar_data():
    try:
        conn = duckdb.connect(DB_PATH, read_only=True)
        df = conn.execute("""
            SELECT
                time_utc,
                currency as ctry,
                event_name as event,
                actual,
                forecast,
                impact
            FROM economic_events
            WHERE time_utc >= CURRENT_DATE - INTERVAL 2 DAY
            ORDER BY time_utc DESC
            LIMIT 20
        """).df()
        conn.close()

        formatted_events = []
        for _, row in df.iterrows():
            event_time = row['time_utc']
            time_formatted = event_time.strftime('%H:%M') if pd.notna(event_time) else 'TBD'
            formatted_events.append({
                'time': time_formatted,
                'ctry': row['ctry'] if pd.notna(row['ctry']) else 'N/A',
                'event': row['event'] if pd.notna(row['event']) else 'N/A',
                'act': str(row['actual']) if pd.notna(row['actual']) else '---',
                'fcst': str(row['forecast']) if pd.notna(row['forecast']) else '---',
                'impact': row['impact'] if pd.notna(row['impact']) else 'Low',
            })
        return formatted_events[:10]
    except Exception as e:
        print(f"Calendar Error: {e}")
        return []

@app.get("/api/research")
async def get_ai_research():
    global ai_cache
    if ai_cache["report"] and datetime.now() < ai_cache["expiry"]:
        return {"report": ai_cache["report"], "cached": True}
    try:
        copilot = ResearchCopilot()
        note = copilot.generate_intelligence_note()
        ai_cache["report"] = note
        ai_cache["expiry"] = datetime.now() + timedelta(minutes=10)
        return {"report": note, "generated_at": datetime.now().strftime('%H:%M:%S UTC')}
    except Exception as e:
        if ai_cache["report"]:
            return {"report": ai_cache["report"], "error": "Rate limit hit, showing cached data."}
        return {"report": "AI Strategist currently busy. Please wait.", "error": str(e)}

@app.get("/api/sparkline/{symbol}")
async def get_sparkline(symbol: str):
    try:
        engine = MarketPulse()
        history = engine.get_sparkline_data(symbol)
        return {"symbol": symbol, "data": history}
    except Exception:
        return {"symbol": symbol, "data": []}

@app.get("/api/historical/{symbol}")
async def get_historical_data(symbol: str, timeframe: str = "15min", limit: int = 100):
    """Returns OHLC data for charting purposes."""
    try:
        conn = duckdb.connect(DB_PATH, read_only=True)

        table_map = {
            "tick": "ticks", "1min": "m1_bars", "5min": "m5_bars",
            "15min": "m15_bars", "1H": "h1_bars", "1D": "d1_bars",
        }
        table = table_map.get(timeframe, "m15_bars")

        mapping = {
            "AAPL": "Apple", "TSLA": "Tesla", "NVDA": "NVIDIA",
            "MSFT": "Microsoft", "AMZN": "Amazon", "GOOGL": "Alphabet",
            "META": "Facebook", "C": "Citigroup", "US02Y": "US02Y.px",
            "US10Y": "US10Y.px", "US30Y": "US30Y.px", "US500": "US500Roll",
            "UT100": "UT100Roll", "USOIL": "USOILRoll", "UKOIL": "UKOILRoll",
            "US30": "US30Roll", "JP225": "JP225Roll", "HK50": "HK50Roll",
            "UK100": "UK100Roll", "DE40": "DE40Roll", "VIX": "VIXRoll",
            "GOLD": "XAUUSD.sd", "WTI": "USOILRoll", "XAU": "XAUUSD.sd",
            "US10YBOND": "US10Y.px", "BOND10Y": "US10Y.px",
        }
        lookup = mapping.get(symbol, symbol)

        result = conn.execute(
            f"SELECT time_utc, open, high, low, close, volume FROM {table} WHERE symbol = ? ORDER BY time_utc DESC LIMIT ?",
            [lookup, limit]
        ).fetchall()

        if not result:
            print(f"No data for {lookup} in {table}")
            conn.close()
            return {"symbol": symbol, "data": []}

        columns = ["datetime", "open", "high", "low", "close", "volume"]
        data = []
        for row in result:
            time_str = row[0].strftime('%d %b %H:%M') if hasattr(row[0], 'strftime') else str(row[0])
            data.append(dict(zip(columns, [time_str] + list(row[1:]))))

        conn.close()
        return {"symbol": symbol, "data": data[::-1]}
    except Exception as e:
        print(f"Historical Error [{symbol}]: {e}")
        return {"symbol": symbol, "data": []}

@app.get("/api/correlation")
async def get_correlation():
    try:
        conn = duckdb.connect(DB_PATH, read_only=True)
        symbols = ['US500Roll', 'UT100Roll', 'XAUUSD.sd', 'USOILRoll', 'US10Y.px', 'EURUSD.sd']
        df = conn.execute(f"""
            PIVOT (SELECT time_utc, symbol, close FROM m15_bars WHERE symbol IN {tuple(symbols)})
            ON symbol USING AVG(close) GROUP BY time_utc ORDER BY time_utc DESC LIMIT 100
        """).df().dropna()
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
    try:
        conn = duckdb.connect(DB_PATH, read_only=True)
        table_map = {
            "tick": "ticks", "1min": "m1_bars", "5min": "m5_bars",
            "15min": "m15_bars", "1H": "h1_bars", "1D": "d1_bars",
        }
        table = table_map.get(timeframe, "m15_bars")
        symbol_list = [s.strip() for s in symbols.split(',')]
        placeholders = ",".join(["?" for _ in symbol_list])
        result = conn.execute(
            f"SELECT time_utc, symbol, open, high, low, close, volume FROM {table} WHERE symbol IN ({placeholders}) ORDER BY time_utc DESC, symbol LIMIT ?",
            symbol_list + [limit * len(symbol_list)]
        ).fetchall()

        columns = ["time_utc", "symbol", "open", "high", "low", "close", "volume"]
        data = [dict(zip(columns, row)) for row in result]

        grouped_data: dict = {}
        for item in data[::-1]:
            sym = item["symbol"]
            grouped_data.setdefault(sym, []).append(item)

        conn.close()
        return {"data": grouped_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/api/vision/analyze")
async def analyze_chart_vision(data: dict):
    import base64
    from dotenv import load_dotenv
    import google.generativeai as genai

    load_dotenv()
    try:
        image_str = data.get("image", "")
        image_data = image_str.split(",")[1] if image_str.startswith('data:image') else image_str

        api_key = os.getenv("API_KEY")
        if not api_key:
            return {"analysis": "Vision Module Error: API_KEY not configured"}

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-3-flash-preview')
        image_bytes = base64.b64decode(image_data)

        prompt = (
            "You are the Quantwater Agentic Vision module. Look at this financial chart image. "
            "1. Identify the primary trend (bullish/bearish/consolidating). "
            "2. Note any visible support and resistance levels. "
            "3. Describe any recognizable chart patterns (e.g., head and shoulders, triangles, etc.). "
            "4. Highlight any significant volume patterns if visible. "
            "Return a concise, institutional-grade analysis with specific observations."
        )

        response = model.generate_content([prompt, {'mime_type': 'image/png', 'data': image_bytes}])
        return {"analysis": response.text}
    except Exception as e:
        return {"analysis": f"Vision Module Error: {str(e)}"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)