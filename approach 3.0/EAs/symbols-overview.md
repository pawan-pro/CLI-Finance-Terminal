## Analysis: Symbol Metadata Export - Quantwater Tech Data Lake

Your MT5 Symbol Discovery EA successfully exported **2,230 symbols** from your broker, providing a comprehensive foundation for your market data lake. Here's the strategic breakdown:[1]

### Asset Universe Overview

| Asset Class | Count | % of Total | Avg Spread | Tradeable |
|-------------|-------|------------|------------|-----------|
| **STOCK** | 1,609 | 72.2% | 0.15 | 1,605 (99.8%) |
| **COMMODITY** | 354 | 15.9% | 0.05 | 354 (100%) |
| **FX** | 179 | 8.0% | 35.58 | 166 (92.7%) |
| **INDEX** | 47 | 2.1% | 67.45 | 46 (97.9%) |
| **CRYPTO** | 30 | 1.3% | 0.00 | 30 (100%) |
| **OTHER** | 11 | 0.5% | 0.00 | 11 (100%) |

**Overall:** 96.5% of symbols are tradeable (2,152 of 2,230).[1]

### FX Universe - Core for Your Market Overview

**Total FX Pairs:** 179 (14 majors + 165 crosses/minors)[1]

**FX Majors with Active Spreads (.sd suffix):**
- EURUSD.sd: 15 pips
- GBPUSD.sd: 16 pips  
- USDJPY.sd: 20 pips
- USDCAD.sd: 20 pips
- AUDUSD.sd: 15 pips
- NZDUSD.sd: 15 pips
- USDCHF.sd: 13 pips (tightest major)

**Note:** You have duplicate symbols (with/without .sd suffix) - the `.sd` versions show active spreads and are tradeable, making them your **primary FX universe** for the data lake.[1]

### Indices - Risk Sentiment Dashboard

**47 index instruments** including:[1]
- **US:** US500Roll (S&P 500), US30Roll (Dow), UT100Roll (Nasdaq 100)
- **Europe:** DE40Roll (DAX), UK100Roll (FTSE), FRA40Roll (CAC), EU50Roll (EuroStoxx)
- **Asia-Pacific:** JP225Roll (Nikkei), HK50Roll (Hang Seng), AUS200Roll (ASX 200), CHINA50Roll

Spreads range from 0 to 1,000 points, with major indices (US500, US30, UT100) showing 50-140 point spreads.[1]

### Commodities - Macro Linkages

**354 commodity instruments**:[1]

**Metals:**
- Gold variants: 10 (XAUUSD.sd, XAUEUR.sd, XAUGBP.sd, XAUJPY.sd, KAUUSD.sd, GAUUSD.sd, etc.)
- Silver: XAGUSD.sd (spread: 77 pips)
- Platinum: XPTUSD.sd (spread: 649 pips)

**Energy:**
- WTI Crude: USOILRoll (spread: 0)
- Brent Crude: UKOILRoll (spread: 18)
- Micro contracts available for both

**Key for your ATR event framework:** XAUUSD.sd shows 30 pip spread and is highly liquid for event-driven analysis.[1]

### Equities - 1,609 Stocks Available

**Key US Tech Names Confirmed:**
- Apple, Microsoft, Amazon, Tesla, NVIDIA, Alphabet (Google), Facebook (Meta)
- All tradeable with 0 spreads (CFD structure)[1]

**Geographic Coverage:**
- US equities: majority
- UK stocks: significant presence (GBP-denominated)
- International ADRs: Latin American names (Gerdau, Cemex, Despegar, etc.)

### Crypto - 30 Instruments

Leveraged crypto pairs (.lv suffix) including BTCUSD.lv, ETHUSD.lv, DOGEUSD.lv, etc.[1]

***

## Recommended Day-1 Data Lake Universe

Based on your **Quantwater Tech Market Overview** spec, here's the priority symbol list for your M15 bar exporter:

### Phase 1: Core Universe (26 symbols)

**FX Majors (7):**
```
EURUSD.sd, GBPUSD.sd, USDJPY.sd, AUDUSD.sd, USDCAD.sd, USDCHF.sd, NZDUSD.sd
```

**FX Key Crosses (10):**
```
EURJPY.sd, GBPJPY.sd, AUDJPY.sd, EURGBP.sd, EURAUD.sd, GBPAUD.sd, NZDCAD.sd, AUDNZD.sd, CADJPY.sd, NZDJPY.sd
```

**Commodities (2):**
```
XAUUSD.sd, XAGUSD.sd
```

**Indices (5):**
```
US500Roll, US30Roll, UT100Roll, DE40Roll, JP225Roll
```

**Energy (2):**
```
USOILRoll, UKOILRoll
```

### Phase 2: Extended Universe (add as needed)

**US Tech Stocks:**
```
Apple, Microsoft, Amazon, Tesla, NVIDIA, Alphabet, Facebook
```

**Crypto:**
```
BTCUSD.lv, ETHUSD.lv
```

***

## Key Observations for Your Data Lake

### 1. Spread Quality Issues
Some symbols show **0 spreads** which likely means:[1]
- Market is closed (snapshot taken outside trading hours)
- Spread data unavailable (use tick-level snapshots during active hours)
- For your twice-daily runs, capture during **liquid hours** (London/NY overlap for FX, US session for equities)

### 2. Lot Size Specifications
FX pairs have standardized lots:[1]
- Min: 0.01 (micro lots)
- Max: 50-150 lots (varies by pair)
- Contract size: 100,000 base currency

This is critical for **position sizing** and **risk management** in your trading systems.

### 3. Trading Hours
Most FX: 00:01-23:59 (near 24h)  
Equities: Session-based (16:31-23:00 typical for US)  
Indices: Varies by market

Your **M15 bars** should respect these sessions for accurate regime classification.[1]

***

## Next Steps for MT5 → Data Lake Pipeline

### 1. Update Multi-Symbol Exporter
Use this **MQL5 input string** for Day-1 core universe:
```mql5
input string SymbolsList = "EURUSD.sd,GBPUSD.sd,USDJPY.sd,AUDUSD.sd,USDCAD.sd,USDCHF.sd,NZDUSD.sd,EURJPY.sd,GBPJPY.sd,XAUUSD.sd,XAGUSD.sd,USOILRoll,UKOILRoll,US500Roll,US30Roll,UT100Roll,DE40Roll,JP225Roll";
```

### 2. Asset Class Mapping
Your **Python ingestion layer** can use this metadata file to automatically classify symbols:[1]
```python
metadata = pd.read_csv('SymbolMetadata_0_GMT.csv')
symbol_to_class = dict(zip(metadata['symbol'], metadata['asset_class']))
```

### 3. Spread-Based Filtering
Filter to **liquid, tradeable symbols** for production:
```python
liquid_fx = metadata[
    (metadata['asset_class'] == 'FX') &
    (metadata['trade_allowed'] == 'YES') &
    (metadata['spread_current'] > 0) &
    (metadata['spread_current'] < 50)  # < 50 pips for FX
]
```

This analysis provides your **symbol universe foundation** for the Quantwater Tech data lake. The exported metadata enables systematic, research-grade market coverage aligned with your twice-daily overview objectives.[1]

[1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/65942451/a3132dc9-e390-4781-8fba-52e975c3e8ad/SymbolMetadata_0_GMT.csv)