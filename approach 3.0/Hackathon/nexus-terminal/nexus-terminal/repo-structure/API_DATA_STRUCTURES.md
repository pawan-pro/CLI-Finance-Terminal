# Nexus Terminal - API and Data Structures

## Backend API Endpoints

The application communicates with a local backend service at `http://localhost:8000`:

### GET `/api/market`
Returns current market data for all tracked instruments.

**Response Format:**
```json
[
  {
    "symbol": "string",
    "friendly_name": "string",
    "price": "number",
    "change_24h": "number | null",
    "asset_class": "string",
    "status": "string"
  }
]
```

### POST `/api/vision/analyze`
Analyzes financial chart images using Gemini 3 Flash vision capabilities.

**Request Format:**
```json
{
  "image": "base64-encoded PNG image string",
  "symbol": "string (optional)",
  "context": "string (optional)"
}
```

**Response Format:**
```json
{
  "analysis": "string containing AI-generated analysis of the chart"
}
```
```

## Type Definitions

### User Interface
```typescript
interface User {
  id: string;
  username: string;
}
```

### Market Data Types
```typescript
interface StockQuote {
  symbol: string;
  name: string;
  price: number;
  change: number;
  percent_change: number;
  volume: number;
  timestamp: number;
  is_market_open: boolean;
  status?: string;
}

interface OHLCPoint {
  datetime: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}
```

### News and Content Types
```typescript
interface NewsItem {
  id: string;
  title: string;
  source: string;
  time: string;
  summary: string;
  url: string;
  symbol?: string;
  sentiment?: 'positive' | 'neutral' | 'negative';
}
```

### Chat System Types
```typescript
interface ChatMessage {
  id: string;
  userId: string;
  username: string;
  content: string;
  timestamp: number;
}

interface AIChatMessage {
  id: string;
  role: 'user' | 'model';
  content: string;
  timestamp: number;
}
```

### Macro Economics Types
```typescript
interface MarketInstrument {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  category: 'future' | 'bond' | 'fx' | 'spread' | 'em' | 'stock';
  status?: string;
}

interface EconomicEvent {
  id: string;
  name: string;
  country: string;
  importance: 'high' | 'medium' | 'low';
  forecast: string;
  previous: string;
  actual?: string;
  time: string;
  unit?: string;
}

interface RateProbability {
  rate: number;
  probability: number;
}
```

### Context and Range Types
```typescript
interface MarketContext {
  symbol: string;
  quote: StockQuote | null;
  selectedRange: DateRange;
  recentHistory: OHLCPoint[];
  visionAnalysis?: string | null;
}

interface DateRange {
  startDate: Date | null;
  endDate: Date | null;
}
```

## Component Props Interfaces

### StockChart Props
```typescript
interface StockChartProps {
  quote: StockQuote | null;
  history: OHLCPoint[];
  error?: string | null;
  onRangeChange: (range: DateRange) => void;
  timeRange?: '1D' | '1W';
  onTimeRangeChange?: (range: '1D' | '1W') => void;
}
```

### AIAssistant Props
```typescript
interface AIAssistantProps {
  marketContext: MarketContext;
}
```

### MacroDashboard Props
```typescript
interface MacroDashboardProps {
  instruments: MarketInstrument[];
  econEvents: EconomicEvent[];
  rateProbs: RateProbability[];
}
```

### PublicChat Props
```typescript
interface PublicChatProps {
  currentUser: User;
}
```

## API Service Methods

### marketDataService.ts
- `fetchMarketData(): Promise<BackendAsset[]>` - Fetches all market assets
- `convertToMarketInstrument(asset: BackendAsset): MarketInstrument` - Converts backend format to UI format
- `fetchQuote(symbol: string): Promise<StockQuote>` - Fetches individual quote
- `fetchBatchQuotes(symbols: string[]): Promise<Record<string, StockQuote>>` - Fetches multiple quotes
- `fetchTimeSeries(symbol: string, interval: string, days: number): Promise<OHLCPoint[]>` - Fetches historical data
- `fetchNews(symbol: string): Promise<NewsItem[]>` - Fetches news for symbol

### geminiService.ts
- `sendMessageToGemini(history: AIChatMessage[], newMessage: string, marketContext: MarketContext): Promise<string>` - Sends message to AI and gets response

### dataService.ts
- `generateHistory(symbol: string, days: number): StockHistoryPoint[]` - Generates simulated history
- `generateStocks(): Stock[]` - Generates simulated stock data
- `generateMacroData(): MarketInstrument[]` - Generates macro instrument data
- `updateMacroInstrument(instrument: MarketInstrument): MarketInstrument` - Updates instrument values
- `generateEconomicEvents(): EconomicEvent[]` - Generates economic calendar
- `generateRateProbs(): RateProbability[]` - Generates rate probabilities

### storage.ts
- `getUsers(): User[]` - Gets stored users
- `saveUser(user: User)` - Saves user to storage
- `getCurrentUser(): User | null` - Gets current user
- `setCurrentUser(user: User | null)` - Sets current user
- `sendPublicMessage(message: ChatMessage)` - Sends chat message
- `getChatHistory(): ChatMessage[]` - Gets chat history
- `subscribeToChat(callback: (message: ChatMessage) => void): () => void` - Subscribes to chat updates

### t12Service.ts (Deprecated/Local)
- `fetchQuote(symbol: string): Promise<StockQuote>` - Twelve Data quote API
- `fetchBatchQuotes(symbols: string[]): Promise<Record<string, StockQuote>>` - Twelve Data batch API
- `fetchTimeSeries(symbol: string, interval: string, days: number): Promise<OHLCPoint[]>` - Twelve Data time series
- `fetchNews(symbol: string): Promise<NewsItem[]>` - Twelve Data news API

## Configuration Constants

### Polling Intervals
- Active Asset: 15,000ms (15 seconds)
- Watchlist: 15,000ms (15 seconds)
- News: 120,000ms (2 minutes)
- Macro Ticker: 3,000ms (3 seconds)

### Default Watchlist
- AAPL, TSLA, NVDA, MSFT, META, GOOGL, JPM, V

### AI Model
- Model: gemini-3-flash-preview
- Features: Technical analysis, market context awareness, Google Search integration