# Quantwater Cognitive Terminal

**The Future of Institutional Intelligence for the Gemini 3 Era**

Quantwater Cognitive Terminal is a high-density, agentic financial research workstation designed for global macro desks. It leverages the cutting-edge reasoning and vision capabilities of **Gemini 3 Flash** to transform raw market data into institutional-grade intelligence notes.

---

## 🚀 Key Gemini 3 Integrations

### 🧠 High-Level Thinking & Causal Reasoning
The terminal uses **Gemini 3 Flash** with `Thinking Level: High` to perform deep-link analysis. Instead of just stating price moves, the agent identifies **causal links** between macro drivers (Fed policy, yields, geopolitics) and market reactions, outputting a Reuters-style intelligence wire.

### 👁️ Agentic Vision Reports
Directly from the UI, analysts can trigger **Agentic Vision**. The terminal captures the current state of market charts and sends them to Gemini 3 for visual evidence-based analysis. The model identifies trends, support/resistance levels, and patterns that traditional quantitative scripts might miss.

### 💻 Precision Code Execution
The backend utilizes Python-based analytics to process millions of ticks stored in **DuckDB**, ensuring the AI strategist always has the ground-truth data lake at its fingertips.

---

## 🛠️ Architecture

- **Data Lake**: DuckDB (Columnar high-performance OLAP).
- **Backend**: FastAPI (Python 3.12 gateway).
- **Core Intelligence**: Gemini 3 Flash (Research & Vision Analyst).
- **Frontend**: React 19 (High-density, low-latency UI).
- **Market Data**: MetaTrader 5 -> DuckDB pipeline.

---

## 📦 Setup & Installation

### 1. Prerequisites
- Python 3.10+
- Node.js 18+
- Gemini API Key

### 2. Backend Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Launch the FastAPI server
python app.py
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 📊 Submission Components
- `/backend`: Core analytics engine and ingestion logic.
- `/frontend`: High-density React terminal.
- `app.py`: Central bridge for AI and Data Lake.
- `market_data.duckdb`: Pre-populated sample data lake.

**Quantwater Terminal: Bridging the gap between raw data and cognitive alpha.**
