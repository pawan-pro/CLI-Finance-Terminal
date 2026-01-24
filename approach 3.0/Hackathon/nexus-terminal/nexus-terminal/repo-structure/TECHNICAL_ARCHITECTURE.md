# Nexus Terminal - Technical Architecture

## System Architecture

Nexus Terminal follows a client-side React application architecture with simulated backend services. The application integrates multiple data sources and services to provide a comprehensive financial dashboard.

## Data Flow

### Market Data Pipeline
1. **Data Sources**: 
   - Local backend API (`http://localhost:8000/api/market`)
   - Simulated data generators
   - Twelve Data API (fallback/deprecated)

2. **Data Processing**:
   - Raw market data → Backend API → Frontend services → UI Components

3. **Update Intervals**:
   - Active Asset: Every 15 seconds
   - Watchlist: Every 15 seconds  
   - News: Every 120 seconds
   - Macro Ticker: Every 3 seconds (simulated)

### Component Hierarchy

```
App.tsx (State Management)
├── Auth.tsx (Authentication Layer)
├── StockChart.tsx (Equity View)
│   └── Recharts Library (Visualization)
├── PublicChat.tsx (Social Layer)
│   └── BroadcastChannel (Tab Communication)
├── AIAssistant.tsx (AI Integration)
│   └── Google GenAI (Gemini API)
└── MacroDashboard.tsx (Macro View)
    └── Instrument Cards
```

## State Management

The application uses React hooks for state management:

- **Global State**: Managed in App.tsx using useState
- **Component State**: Individual component state management
- **Persistent State**: Browser localStorage via services/storage.ts

### Key State Variables:
- `user`: Current authenticated user
- `activeSymbol`: Selected stock symbol
- `view`: Current view (EQUITY | MACRO)
- `quote`: Current stock quote data
- `history`: Historical price data
- `news`: Financial news items
- `watchlistQuotes`: Multiple stock quotes
- `macroInstruments`: Economic instruments
- `econEvents`: Economic calendar events

## Service Layer

### marketDataService.ts
Handles fetching market data from the backend API:
- `fetchMarketData()`: Retrieves all active assets
- `convertToMarketInstrument()`: Transforms backend data to UI format
- `fetchQuote()`: Gets individual stock quote
- `fetchBatchQuotes()`: Gets multiple stock quotes
- `fetchTimeSeries()`: Gets historical data

### geminiService.ts
Integrates with Google's Gemini AI:
- `sendMessageToGemini()`: Sends user queries to AI
- Processes market context for intelligent responses
- Uses Google Search tools for enhanced analysis

### dataService.ts
Generates simulated market data:
- `generateHistory()`: Creates historical price series
- `generateStocks()`: Creates mock stock data
- `generateMacroData()`: Creates economic instruments
- `generateEconomicEvents()`: Creates calendar events
- `generateRateProbs()`: Creates rate probability data

### storage.ts
Client-side persistence layer:
- User authentication state
- Chat history storage
- Cross-tab communication via BroadcastChannel
- Local data persistence

## UI Components Deep Dive

### StockChart.tsx
- Uses Recharts for visualization
- Supports 1D and 1W time ranges
- Implements brush functionality for date range selection
- Shows OHLC data with volume bars
- Responsive design for different screen sizes

### AIAssistant.tsx
- Maintains chat history with initialization message
- Integrates market context into AI queries
- Real-time scrolling for new messages
- Loading states during AI processing
- Error handling for API failures

### MacroDashboard.tsx
- Displays economic instruments in card format
- Shows price changes with directional indicators
- Visual status indicators (LIVE/INACTIVE)
- Category-specific formatting (bonds show %, FX shows 4 decimals)

## Configuration (config.ts)

```typescript
{
  BACKEND_API_BASE: 'http://localhost:8000',
  AI_MODEL: 'gemini-3-flash-preview',
  POLLING: {
    ACTIVE_ASSET: 15000,
    WATCHLIST: 15000,
    NEWS: 120000,
    MACRO_TICKER: 3000
  }
}
```

## Styling and Theming

- **Tailwind CSS**: Primary styling framework
- **Custom Theme**: Defined in index.html with Nexus color palette
- **Font Stack**: Inter (UI) + JetBrains Mono (monospace)
- **Color Scheme**: Dark theme with Bloomberg-style amber accents

## Error Handling Strategy

The application implements granular error states:
- `chartError`: Chart-specific errors
- `newsError`: News feed errors
- `watchlistError`: Watchlist errors
- Component-level error boundaries
- Fallback UI for data loading states

## Performance Considerations

- Virtualized lists for chat and news
- Memoization for expensive calculations
- Efficient polling intervals
- Lazy loading of heavy components
- Optimized chart rendering