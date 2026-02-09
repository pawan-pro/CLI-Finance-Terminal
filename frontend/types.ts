
export interface User {
  id: string;
  username: string;
}

export interface StockQuote {
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

export interface OHLCPoint {
  datetime: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface MarketContext {
  symbol: string;
  quote: StockQuote | null;
  selectedRange: DateRange;
  recentHistory: OHLCPoint[];
  visionAnalysis?: string | null;
}

export interface NewsItem {
  id: string;
  title: string;
  source: string;
  time: string;
  summary: string;
  url: string;
  symbol?: string;
  sentiment?: 'positive' | 'neutral' | 'negative';
  category?: string;
}

export interface DateRange {
  startDate: string | null;
  endDate: string | null;
}

export interface AIChatMessage {
  id: string;
  role: 'user' | 'model';
  content: string;
  timestamp: number;
  isError?: boolean;
}

export interface ChatMessage {
  id: string;
  userId: string;
  username: string;
  content: string;
  timestamp: number;
}

// Additional types for market data services
export interface StockHistoryPoint {
  date: string;
  price: number;
  volume: number;
}

export interface Stock {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  history: StockHistoryPoint[];
}

export interface MarketInstrument {
  symbol: string;
  name: string;
  category: 'future' | 'bond' | 'fx' | 'spread' | 'em' | 'stock';
  assetClass?: string;
  price: number;
  change: number;
  changePercent: number;
  status?: string;
}

export interface EconomicEvent {
  id: string;
  time: string;
  country: string;
  event: string;
  actual: string;
  forecast: string;
  previous: string;
  impact: 'low' | 'medium' | 'high';
}

export interface RateProbability {
  meeting: string;
  hike: number;
  hold: number;
  cut: number;
}
